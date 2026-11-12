#!/usr/bin/env python3
"""Pattern 11: structural EXAMPLES vs argspec validator for Ansible network resource modules.

Checks per EXAMPLES task:
  1. Parameters not in argspec at that depth (removed/renamed)
  2. Type mismatches (scalar where argspec expects dict, dict where scalar expected)
  3. Invalid state values (not in argspec choices)
  4. Missing required parameters (argspec required: true but absent from task)

For each finding, locates a matching integration testcase as a replacement reference.

Outputs findings in the scanner-hits JSON schema for direct validator handoff.

Usage:
  python scripts/validate_examples.py /path/to/cisco.nxos --repo cisco.nxos --json
  python scripts/validate_examples.py /path/to/cisco.iosxr --repo cisco.iosxr --module iosxr_bgp_global
  python scripts/validate_examples.py /path/to/cisco.iosxr --repos cisco.ios,cisco.nxos --json
  python scripts/validate_examples.py /path/to/cisco.iosxr --repos-config /path/to/repos.yaml --json

Paths and collection metadata load from config/repos.yaml via scanner_config.py (override
with --repos-config). --repo and --repos scope which collection entry applies; out-of-scope
clones are skipped (exit 0).
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any

from scanner_config import (
    ReposConfig,
    add_scanner_cli_args,
    check_repo_scope,
    collection_path,
    load_repos_config,
    parse_repos_arg,
    resolve_module_prefix,
    resolve_platform,
)
from scanner_finding import dumps_hits, file_line, make_hit

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install PyYAML", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants (aligned with scan_mechanical_signals.py)
# ---------------------------------------------------------------------------

EXAMPLES_BLOCK_RE = re.compile(
    r'^EXAMPLES\s*=\s*r?(?:"""(.*?)"""|\'\'\'(.*?)\'\'\')',
    re.DOTALL | re.MULTILINE,
)

ARGS_META_KEYS = frozenset({
    "type", "elements", "choices", "required", "default", "description",
    "options", "suboptions", "mutually_exclusive", "aliases", "version_added",
    "deprecated", "removed_in_version", "fallback", "contains", "no_log",
    "removed_at_date", "removed_from_collection",
})

TASK_STRUCTURAL_KEYS = frozenset({
    "name", "register", "vars", "block", "rescue", "always", "tasks",
    "hosts", "gather_facts", "become", "become_user", "ignore_errors",
    "when", "loop", "with_items", "notify", "tags", "delegate_to",
    "no_log", "failed_when", "changed_when", "until", "retries",
    "delay", "environment", "collections", "ansible",
})

SCALAR_TYPES = frozenset({"str", "int", "bool", "float", "raw", "path", "bytes"})

SKIP_PARAMS = frozenset({"running_config", "gather_network_resources"})


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _literal_str(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _literal_bool(node: ast.AST | None) -> bool | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    return None


def _dict_field(d: ast.Dict, field: str) -> ast.AST | None:
    for k, v in zip(d.keys, d.values):
        if _literal_str(k) == field:
            return v
    return None


def _ast_list_strings(node: ast.AST | None) -> list[str]:
    if not isinstance(node, (ast.List, ast.Tuple)):
        return []
    return [s for elt in node.elts if (s := _literal_str(elt)) is not None]


# ---------------------------------------------------------------------------
# Argspec tree builder
# ---------------------------------------------------------------------------

def _parse_param_node(node: ast.Dict, depth: int = 0) -> dict[str, Any]:
    """Parse one parameter's descriptor dict into a structural tree node.

    Sentinel keys (_type, _choices, _required, _element_type) carry metadata.
    All other keys are child parameter names.
    """
    if not isinstance(node, ast.Dict) or depth > 15:
        return {}

    result: dict[str, Any] = {}

    type_val = _literal_str(_dict_field(node, "type"))
    elem_val = _literal_str(_dict_field(node, "elements"))
    req_node = _dict_field(node, "required")
    cho_node = _dict_field(node, "choices")

    if type_val:
        result["_type"] = type_val
    if elem_val:
        result["_element_type"] = elem_val
    if req_node is not None:
        b = _literal_bool(req_node)
        if b is not None:
            result["_required"] = b
    choices = _ast_list_strings(cho_node)
    if choices:
        result["_choices"] = choices

    options = _dict_field(node, "options") or _dict_field(node, "suboptions")
    if options and isinstance(options, ast.Dict):
        for k, v in zip(options.keys, options.values):
            key = _literal_str(k)
            if not key:
                continue
            # Do NOT filter by ARGS_META_KEYS here — these keys are parameter
            # names (e.g. a param named "description"), not metadata keys.
            if isinstance(v, ast.Dict):
                result[key] = _parse_param_node(v, depth + 1)

    return result


def _build_top_level(node: ast.Dict) -> dict[str, Any]:
    """Build the top-level parameter tree from an argument_spec dict node."""
    tree: dict[str, Any] = {}
    for k, v in zip(node.keys, node.values):
        key = _literal_str(k)
        if not key or key in ARGS_META_KEYS:
            continue
        if isinstance(v, ast.Dict):
            tree[key] = _parse_param_node(v)
    return tree


def build_argspec_tree(argspec_path: Path) -> dict[str, Any]:
    """Parse argspec Python file; return a nested parameter tree.

    Returns empty dict if the file cannot be parsed.
    """
    text = argspec_path.read_text(encoding="utf-8", errors="replace")
    try:
        module = ast.parse(text)
    except SyntaxError:
        return {}

    for node in ast.walk(module):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if not isinstance(item, ast.Assign):
                    continue
                for tgt in item.targets:
                    if isinstance(tgt, ast.Name) and tgt.id == "argument_spec":
                        if isinstance(item.value, ast.Dict):
                            tree = _build_top_level(item.value)
                            if tree:
                                return tree
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id in ("argument_spec", "spec"):
                    if isinstance(node.value, ast.Dict):
                        tree = _build_top_level(node.value)
                        if tree:
                            return tree
    return {}


# ---------------------------------------------------------------------------
# EXAMPLES extraction
# ---------------------------------------------------------------------------

def _strip_jinja2(text: str) -> str:
    """Replace {{ ... }} with a bare-word placeholder, preserving embedded newlines.

    Uses a bare word (no quotes) so it stays valid YAML whether the original
    expression appeared inside a quoted string, a block scalar, or bare.
    """
    def _replace(m: re.Match) -> str:
        newlines = m.group(0).count("\n")
        return "JINJA2PLACEHOLDER" + "\n" * newlines

    return re.sub(r"\{\{.*?\}\}", _replace, text, flags=re.DOTALL)


def _module_key(task: dict) -> str | None:
    """Return the first non-structural key in a task dict (the module FQCN)."""
    for k in task:
        if k not in TASK_STRUCTURAL_KEYS:
            return k
    return None


def extract_examples_tasks(module_path: Path) -> list[dict[str, Any]]:
    """Parse EXAMPLES block; return per-task dicts with line numbers.

    Each entry: {"line": int, "params": dict, "state": str|None, "module_key": str}
    Returns empty list if EXAMPLES cannot be parsed as YAML.
    """
    text = module_path.read_text(encoding="utf-8", errors="replace")
    match = EXAMPLES_BLOCK_RE.search(text)
    if not match:
        return []

    # Line number in the module file where EXAMPLES block content begins
    examples_start_line = text[: match.start()].count("\n") + 2  # +2: EXAMPLES = """ line

    raw = match.group(1) or match.group(2) or ""
    cleaned = _strip_jinja2(raw)

    try:
        # Use compose to get per-node line marks
        root_node = yaml.compose(cleaned)
    except yaml.YAMLError:
        return []

    if not isinstance(root_node, yaml.SequenceNode):
        return []

    tasks = []
    for item_node in root_node.value:
        if not isinstance(item_node, yaml.MappingNode):
            continue

        # Accurate line number from YAML parser (0-indexed → 1-indexed)
        task_line = examples_start_line + item_node.start_mark.line

        try:
            task = yaml.safe_load(yaml.serialize(item_node))
        except yaml.YAMLError:
            continue

        if not isinstance(task, dict):
            continue

        key = _module_key(task)
        if key is None:
            continue

        params = task.get(key) or {}
        if not isinstance(params, dict):
            continue

        state = params.get("state")
        tasks.append({
            "line": task_line,
            "params": params,
            "state": state,
            "module_key": key,
        })

    return tasks


# ---------------------------------------------------------------------------
# Parameter validator
# ---------------------------------------------------------------------------

def _raw_finding(
    parameter: str,
    line: int,
    issue: str,
    examples_value: Any,
    expected_type: str,
    confidence: str,
) -> dict[str, Any]:
    val_str = repr(examples_value)[:80]
    return {
        "parameter": parameter,
        "line": line,
        "issue": issue,
        "examples_value": val_str,
        "expected_type": expected_type,
        "confidence": confidence,
    }


def validate_params(
    params: dict,
    tree_node: dict[str, Any],
    dotted_prefix: str,
    state_choices: list[str],
    task_line: int,
) -> list[dict[str, Any]]:
    """Recursively validate EXAMPLES task params against the argspec tree node."""
    if not tree_node:
        return []

    findings: list[dict[str, Any]] = []

    for key, value in params.items():
        if key in TASK_STRUCTURAL_KEYS or key in SKIP_PARAMS:
            continue

        dotted = f"{dotted_prefix}.{key}" if dotted_prefix else key

        # --- state: validate choices ---
        if key == "state":
            if state_choices and isinstance(value, str) and value not in state_choices:
                findings.append(_raw_finding(
                    dotted, task_line,
                    f"invalid state '{value}'; argspec choices: {state_choices}",
                    value, "str (choices)", "likely",
                ))
            continue

        # --- key absent from argspec at this level ---
        if key not in tree_node:
            findings.append(_raw_finding(
                dotted, task_line,
                f"'{key}' not in argspec at this nesting level — removed or renamed",
                value, "unknown", "candidate",
            ))
            continue

        node = tree_node[key]
        node_type = node.get("_type", "")

        # --- type mismatch: argspec dict / list but EXAMPLES shows scalar ---
        if node_type == "dict" and isinstance(value, (str, int, bool, float)):
            findings.append(_raw_finding(
                dotted, task_line,
                f"type mismatch: argspec defines '{key}' as dict but EXAMPLES shows {type(value).__name__}",
                value, "dict", "likely",
            ))
            continue

        if node_type in SCALAR_TYPES and isinstance(value, dict):
            findings.append(_raw_finding(
                dotted, task_line,
                f"type mismatch: argspec defines '{key}' as {node_type} but EXAMPLES shows a dict",
                value, node_type, "likely",
            ))
            continue

        if node_type == "list" and isinstance(value, (str, int, bool, float)):
            findings.append(_raw_finding(
                dotted, task_line,
                f"type mismatch: argspec defines '{key}' as list but EXAMPLES shows {type(value).__name__}",
                value, "list", "likely",
            ))
            continue

        # --- recurse into dict value ---
        if isinstance(value, dict) and node_type in ("dict", "list", ""):
            child_state_choices = node.get("_choices", [])
            findings.extend(validate_params(value, node, dotted, child_state_choices, task_line))

        # --- recurse into list elements ---
        if isinstance(value, list) and node_type == "list":
            for element in value:
                if isinstance(element, dict):
                    findings.extend(validate_params(element, node, dotted, [], task_line))

    # --- required params missing from EXAMPLES ---
    for key, node in tree_node.items():
        if key.startswith("_") or not isinstance(node, dict):
            continue
        if node.get("_required") and key not in params:
            dotted = f"{dotted_prefix}.{key}" if dotted_prefix else key
            findings.append(_raw_finding(
                dotted, task_line,
                f"required parameter '{key}' (argspec required: true) absent from this task",
                None, node.get("_type", ""), "candidate",
            ))

    return findings


# ---------------------------------------------------------------------------
# Integration testcase lookup
# ---------------------------------------------------------------------------

def _flatten_tasks(data: Any, depth: int = 0) -> list[dict]:
    """Recursively extract task dicts from nested block/rescue/always structures."""
    if depth > 5 or not isinstance(data, list):
        return []
    result = []
    for item in data:
        if not isinstance(item, dict):
            continue
        result.append(item)
        for section in ("block", "rescue", "always", "tasks"):
            if section in item and isinstance(item[section], list):
                result.extend(_flatten_tasks(item[section], depth + 1))
    return result


def find_integration_testcase(
    collection_root: Path,
    config: ReposConfig,
    platform: str,
    module_stem: str,
    param_path: str,
    state: str | None,
) -> str | None:
    """Locate a passing integration test task that uses the flagged parameter.

    Returns a repo-relative path (e.g. tests/integration/targets/.../merged.yaml)
    or None if not found.
    """
    integration_root = collection_path(collection_root, config, "integration_tests", platform)
    if not integration_root.is_dir():
        return None

    # Match target dirs: exact stem match or platform-prefixed stem (e.g. nxos_interfaces)
    target_dirs = [
        d for d in integration_root.iterdir()
        if d.is_dir() and (d.name == module_stem or d.name.endswith(f"_{module_stem}"))
    ]
    if not target_dirs:
        return None
    target_dir = target_dirs[0]

    test_files: list[Path] = []
    for sub in ("tests/cli", "tests/common"):
        sub_dir = target_dir / sub
        if sub_dir.is_dir():
            test_files.extend(sorted(sub_dir.glob("*.yml")))

    top_param = param_path.split(".")[0]

    for test_file in test_files:
        if test_file.name.startswith("_"):
            continue
        try:
            raw = test_file.read_text(encoding="utf-8", errors="replace")
            data = yaml.safe_load(raw)
        except Exception:
            continue

        for task in _flatten_tasks(data if isinstance(data, list) else []):
            mod_key = _module_key(task)
            if mod_key is None:
                continue
            task_params = task.get(mod_key) or {}
            if not isinstance(task_params, dict):
                continue
            task_state = task_params.get("state")
            if state and task_state and task_state != state:
                continue
            if top_param in task_params:
                return str(test_file.relative_to(collection_root))

    return None


# ---------------------------------------------------------------------------
# Finding assembler
# ---------------------------------------------------------------------------

def _build_finding(
    repo: str,
    module: str,
    raw: dict[str, Any],
    module_file: Path,
    collection_root: Path,
    integration_ref: str | None,
) -> dict[str, Any]:
    notes_parts = []
    if integration_ref:
        notes_parts.append(f"Integration ref: {integration_ref}")
    if raw.get("expected_type"):
        notes_parts.append(f"expected: {raw['expected_type']}")
    param = raw["parameter"]
    return make_hit(
        repo=repo,
        module=module,
        parameter=param,
        pattern="11",
        issue=raw["issue"],
        confidence=raw["confidence"],
        file_path=module_file,
        collection_root=collection_root,
        line=raw["line"],
        notes="; ".join(notes_parts),
        potential_fix=(
            f"Update EXAMPLES in plugins/modules/{module}.py to match current "
            f"argspec for {param}"
        ),
    )


# ---------------------------------------------------------------------------
# Collection / module discovery
# ---------------------------------------------------------------------------

def enumerate_modules(
    collection_root: Path,
    config: ReposConfig,
    platform: str,
    prefix: str,
    module_filter: str | None,
) -> list[tuple[str, Path, Path]]:
    """Return (module_stem, argspec_path, module_path) for each processable module."""
    argspec_root = collection_path(collection_root, config, "argspec", platform)
    modules_dir = collection_path(collection_root, config, "modules", platform)
    if not argspec_root.is_dir():
        return []

    results = []
    for argspec_dir in sorted(argspec_root.iterdir()):
        if not argspec_dir.is_dir():
            continue
        stem = argspec_dir.name
        if module_filter and stem not in module_filter and f"{prefix}{stem}" not in module_filter:
            continue

        argspec_path = argspec_dir / f"{stem}.py"
        if not argspec_path.is_file():
            continue

        module_path = None
        for candidate in [
            modules_dir / f"{prefix}{stem}.py",
            modules_dir / f"{stem}.py",
        ]:
            if candidate.is_file():
                module_path = candidate
                break
        if module_path is None:
            continue

        results.append((stem, argspec_path, module_path))

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(
    collection_root: Path,
    config: ReposConfig,
    repo_name: str,
    module_filter: str | None,
    as_json: bool,
    platform_hint: str | None = None,
) -> int:
    platform = resolve_platform(
        collection_root,
        config,
        repo_name=repo_name,
        platform_hint=platform_hint,
    )
    if not platform:
        print(
            f"ERROR: no platform found under {collection_root}/plugins/module_utils/network/",
            file=sys.stderr,
        )
        return 1

    prefix = resolve_module_prefix(config, platform, repo_name)
    modules = enumerate_modules(collection_root, config, platform, prefix, module_filter)
    if not modules:
        print(f"No modules found (platform={platform}, filter={module_filter!r})", file=sys.stderr)
        return 0

    all_findings: list[dict[str, Any]] = []
    scanned = skipped = 0

    for stem, argspec_path, module_path in modules:
        module_name = module_path.stem  # e.g. nxos_hsrp_interfaces

        tree = build_argspec_tree(argspec_path)
        if not tree:
            skipped += 1
            continue

        tasks = extract_examples_tasks(module_path)
        if not tasks:
            skipped += 1
            continue

        scanned += 1
        state_choices = tree.get("state", {}).get("_choices", [])

        for task in tasks:
            raw_findings = validate_params(
                task["params"], tree, "", state_choices, task["line"]
            )
            for raw in raw_findings:
                ref = find_integration_testcase(
                    collection_root, config, platform, stem, raw["parameter"], task["state"]
                )
                finding = _build_finding(repo_name, module_name, raw, module_path, collection_root, ref)
                all_findings.append(finding)

    if as_json:
        print(dumps_hits(all_findings))
    else:
        _print_table(all_findings)
        print(
            f"\nScanned {scanned} modules, {skipped} skipped. "
            f"Pattern 11 findings: {len(all_findings)}"
        )

    return 0


def _print_table(findings: list[dict]) -> None:
    if not findings:
        print("No Pattern 11 findings.")
        return

    headers = ["Module", "Parameter", "File:Line", "Conf", "Issue"]
    rows = [
        [
            f["module"],
            f["parameter"][:45],
            file_line(f),
            f["confidence"],
            f["issue"][:65],
        ]
        for f in findings
    ]
    widths = [
        max(len(h), max((len(r[i]) for r in rows), default=0))
        for i, h in enumerate(headers)
    ]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(fmt.format(*row))
    if findings and findings[0].get("notes"):
        print("\nNotes (integration refs):")
        seen: set[str] = set()
        for f in findings:
            note = f.get("notes", "")
            if note and note not in seen:
                print(f"  [{f['module']} {f['parameter']}] {note}")
                seen.add(note)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pattern 11: structural EXAMPLES vs argspec validator"
    )
    parser.add_argument("collection_root", type=Path, help="Root of the collection clone")
    add_scanner_cli_args(parser)
    parser.add_argument("--module", help="Only check this module (stem or full name)")
    parser.add_argument("--platform", help="Platform name override (e.g. iosxr)")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.repo and args.repos:
        print("warning: --repo and --repos both set; using --repo", file=sys.stderr)

    try:
        config = load_repos_config(args.repos_config)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    repos_list = parse_repos_arg(args.repos)
    resolved_repo, in_scope = check_repo_scope(
        args.collection_root,
        config,
        repo=args.repo,
        repos=repos_list,
    )
    if not in_scope:
        print(
            f"skip: {resolved_repo} not in scope "
            f"(repo={args.repo!r}, repos={repos_list!r})",
            file=sys.stderr,
        )
        sys.exit(0)

    sys.exit(
        run(
            args.collection_root,
            config,
            resolved_repo,
            args.module,
            args.as_json,
            platform_hint=args.platform,
        )
    )


if __name__ == "__main__":
    main()
