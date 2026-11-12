#!/usr/bin/env python3
"""Mechanical pre-scan for common parser gap signals in network resource modules.

This script performs fast, repo-local pattern matching across Patterns 1–10
(coverage, boolean toggles, negate capture, generate/parse symmetry, stale
parsers, compound CLI setval, and more). Pattern 11 (stale EXAMPLES) is
handled by validate_examples.py in the same Step 3 pipeline. Produces
candidate findings for agent review — not definitive gap reports.

Usage:
  python scripts/scan_mechanical_signals.py /path/to/cisco.iosxr --repo cisco.iosxr --json
  python scripts/scan_mechanical_signals.py /path/to/cisco.iosxr --repos cisco.ios,cisco.nxos --json
  python scripts/scan_mechanical_signals.py /path/to/cisco.iosxr --module iosxr_bgp_global --repo cisco.iosxr
  python scripts/scan_mechanical_signals.py /path/to/cisco.iosxr --platform iosxr --repos-config /path/to/repos.yaml

Paths and collection metadata load from config/repos.yaml via scanner_config.py (override
with --repos-config). --repo and --repos scope which collection entry applies; out-of-scope
clones are skipped (exit 0).

Requires: local clone of the collection repository; PyYAML (for repos.yaml).
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

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


SET_SUBOPTION_RE = re.compile(
    r"""['"]set['"]\s*:\s*\{[^}]*['"]type['"]\s*:\s*['"]bool['"]""",
    re.DOTALL,
)

PARSER_NAME_RE = re.compile(r"""['"]name['"]\s*:\s*['"]([^'"]+)['"]""")
COMPVAL_RE = re.compile(r"""['"]compval['"]\s*:\s*['"]([^'"]+)['"]""")

STATIC_SETVAL_RE = re.compile(
    r"""['"]setval['"]\s*:\s*['"]([^'"{][^'"]*)['"]\s*,?\s*$""",
    re.MULTILINE,
)

SET_DEFINED_ONLY_RE = re.compile(
    r"""['"]set['"]\s*:\s*['"]\{\{\s*True\s+if\s+\w+\s+is\s+defined\s*\}\}['"]""",
)

# Matches getval with triple-quoted (""" or ''') regex strings
GETVAL_BLOCK_RE = re.compile(
    r"""['"]getval['"]\s*:\s*re\.compile\(\s*r?(?:\"\"\"(.*?)\"\"\"|'''(.*?)''')""",
    re.DOTALL,
)

VALID_COMP_PATH_RE = re.compile(r"^[\w][\w.]*$")

# Matches Jinja variable expressions in setval strings
JINJA_VAR_RE = re.compile(r"\{\{[^}]+\}\}")

# Argspec metadata keys — not CLI parameter paths
ARGS_META_KEYS = frozenset(
    {
        "type",
        "elements",
        "choices",
        "required",
        "default",
        "description",
        "options",
        "suboptions",
        "mutually_exclusive",
        "aliases",
        "version_added",
        "deprecated",
        "removed_in_version",
        "fallback",
        "contains",
        "no_log",
        "removed_at_date",
        "removed_from_collection",
    }
)

MODULE_LEVEL_KEYS = frozenset({"state", "running_config", "gather_network_resources", "config"})

_COLLECTION_ROOT: Path | None = None


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def find_argspec_files(
    collection_root: Path,
    config: ReposConfig,
    platform: str,
) -> list[Path]:
    argspec_dir = collection_path(collection_root, config, "argspec", platform)
    if not argspec_dir.is_dir():
        return []
    return sorted(p for p in argspec_dir.rglob("*.py") if p.name != "__init__.py")


def find_rm_template_files(
    collection_root: Path,
    config: ReposConfig,
    platform: str,
) -> list[Path]:
    tmpl_dir = collection_path(collection_root, config, "rm_templates", platform)
    if not tmpl_dir.is_dir():
        return []
    return sorted(p for p in tmpl_dir.rglob("*.py") if p.name != "__init__.py")


def module_name_from_path(path: Path, prefix: str) -> str:
    stem = path.stem
    if stem.startswith(prefix):
        return stem
    return f"{prefix}{stem}"


# ---------------------------------------------------------------------------
# AST-based argspec parsing
# ---------------------------------------------------------------------------


def _literal_str(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _dict_field(d: ast.Dict, field: str) -> ast.AST | None:
    for k, v in zip(d.keys, d.values):
        if _literal_str(k) == field:
            return v
    return None


def walk_argspec_node(
    node: ast.AST | None,
    prefix: str = "",
    *,
    inside_list: bool = False,
) -> list[tuple[str, str, bool]]:
    """Extract (dotted_path, type, inside_list) leaves from argspec dicts."""
    if not isinstance(node, ast.Dict):
        return []

    leaves: list[tuple[str, str, bool]] = []
    elements = _literal_str(_dict_field(node, "elements"))
    in_list = inside_list or elements == "dict"

    options = _dict_field(node, "options") or _dict_field(node, "suboptions")
    if options and isinstance(options, ast.Dict):
        for k, v in zip(options.keys, options.values):
            key = _literal_str(k)
            if not key or key in ARGS_META_KEYS:
                continue
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(v, ast.Dict):
                sub_options = _dict_field(v, "options") or _dict_field(v, "suboptions")
                sub_type = _literal_str(_dict_field(v, "type"))
                if sub_options:
                    leaves.extend(walk_argspec_node(v, path, inside_list=in_list))
                elif sub_type:
                    leaves.append((path, sub_type, in_list))
    elif not prefix:
        for k, v in zip(node.keys, node.values):
            key = _literal_str(k)
            if not key or key in ARGS_META_KEYS:
                continue
            if isinstance(v, ast.Dict):
                leaves.extend(walk_argspec_node(v, key, inside_list=False))
    else:
        typ = _literal_str(_dict_field(node, "type"))
        if typ:
            leaves.append((prefix, typ, in_list))
    return leaves


def extract_argspec_leaves(argspec_path: Path) -> list[tuple[str, str, bool]]:
    """Parse argspec Python file and return leaf parameter paths with types."""
    text = argspec_path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [(p, t, False) for p, t in _extract_argspec_leaves_regex(text)]

    leaves: list[tuple[str, str, bool]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in (
                    "argument_spec",
                    "spec",
                    "options",
                ):
                    leaves.extend(walk_argspec_node(node.value))
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if not isinstance(item, ast.Assign):
                    continue
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "argument_spec":
                        leaves.extend(walk_argspec_node(item.value))
    if leaves:
        return _dedupe_leaves(leaves)
    return [(p, t, False) for p, t in _extract_argspec_leaves_regex(text)]


def _dedupe_leaves(leaves: list[tuple[str, str, bool]]) -> list[tuple[str, str, bool]]:
    seen: set[str] = set()
    out: list[tuple[str, str, bool]] = []
    for path, typ, in_list in leaves:
        if path not in seen:
            seen.add(path)
            out.append((path, typ, in_list))
    return out


def _extract_argspec_leaves_regex(text: str) -> list[tuple[str, str]]:
    """Fallback when AST parse fails — shallow leaf detection."""
    leaves: list[tuple[str, str]] = []
    for match in re.finditer(
        r"""['"](\w+)['"]\s*:\s*\{[^{}]*['"]type['"]\s*:\s*['"](\w+)['"]""",
        text,
    ):
        leaves.append((match.group(1), match.group(2)))
    return leaves


def config_relative_path(path: str) -> str:
    return path[7:] if path.startswith("config.") else path


# ---------------------------------------------------------------------------
# Template / parser utilities
# ---------------------------------------------------------------------------


def extract_parser_comparison_paths(template_text: str) -> dict[str, str]:
    """Map parser name -> effective comparison path (compval if set, else name).

    Bounds each compval search to the range between consecutive parser names to
    avoid picking up compval from an adjacent parser block.
    """
    paths: dict[str, str] = {}
    name_matches = list(PARSER_NAME_RE.finditer(template_text))
    for i, match in enumerate(name_matches):
        name = match.group(1)
        # Bound search: from this name to the start of the next name (or EOF)
        search_end = name_matches[i + 1].start() if i + 1 < len(name_matches) else len(template_text)
        chunk = template_text[match.start():search_end]
        compval_match = COMPVAL_RE.search(chunk)
        paths[name] = compval_match.group(1) if compval_match else name
    return paths


def is_valid_comparison_path(path: str) -> bool:
    """Filter Jinja/dynamic parser names from path-based heuristics."""
    if "{{" in path or "}}" in path or "{%" in path:
        return False
    return bool(VALID_COMP_PATH_RE.match(path))


def path_is_covered(leaf: str, comparison_paths: set[str]) -> bool:
    """True when a comparison path matches the leaf or is an intentional parent."""
    if leaf in comparison_paths:
        return True
    return any(leaf.startswith(f"{cp}.") for cp in comparison_paths)


def _find_parser_block_end(text: str, start: int) -> int:
    """Find end of a parser dict block using brace counting.

    Handles nested dicts and quoted strings; more reliable than searching for '}'.
    """
    depth = 0
    i = start
    in_string = False
    string_char = ""
    escape_next = False
    while i < len(text):
        c = text[i]
        if escape_next:
            escape_next = False
            i += 1
            continue
        if c == "\\" and in_string:
            escape_next = True
            i += 1
            continue
        if in_string:
            if c == string_char:
                in_string = False
        elif c in ('"', "'"):
            in_string = True
            string_char = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(text)


# ---------------------------------------------------------------------------
# Scan functions
# ---------------------------------------------------------------------------


def scan_argspec_set_comparison_path_mismatch(
    argspec_path: Path,
    template_path: Path | None,
    module: str,
    repo: str,
) -> list[dict]:
    """Pattern 1: *.set bool leaf exists but parser compares at parent (not parent.set)."""
    leaves = extract_argspec_leaves(argspec_path)

    # Collect all *.set bool leaves using the AST-derived paths (robust vs regex)
    set_bool_leaves = [
        path for path, typ, _ in leaves
        if path.endswith(".set") and typ == "bool"
    ]
    if not set_bool_leaves:
        return []

    comparison_paths: set[str] = set()
    parser_by_path: dict[str, str] = {}
    if template_path and template_path.is_file():
        template_text = template_path.read_text(encoding="utf-8", errors="replace")
        for parser_name, cp in extract_parser_comparison_paths(template_text).items():
            comparison_paths.add(cp)
            parser_by_path[cp] = parser_name

    findings: list[dict] = []
    for dotted in set_bool_leaves:
        parent = dotted[: -len(".set")]
        rel_parent = config_relative_path(parent)
        rel_dotted = config_relative_path(dotted)
        # Flag when parent is covered but parent.set is not
        if rel_parent in comparison_paths and rel_dotted not in comparison_paths:
            parser_name = parser_by_path.get(rel_parent, rel_parent)
            tmpl_line = 1
            if template_path and template_path.is_file():
                tmpl_text = template_path.read_text(encoding="utf-8", errors="replace")
                tmpl_line = _line_number(tmpl_text, f'"name": "{parser_name}"')
            findings.append(
                _finding(
                    repo,
                    module,
                    rel_dotted,
                    template_path,
                    tmpl_line,
                    (
                        f"Argspec defines '{rel_dotted}' (bool) but parser '{parser_name}' "
                        f"compares at '{rel_parent}' — likely cannot detect set:false transitions"
                    ),
                    (
                        f"Set comparison path to '{rel_dotted}' (compval or dot-namespaced name); "
                        "add negate-aware getval/result"
                    ),
                    "1",
                    "medium",
                )
            )
    return findings


def scan_argspec_coverage_gaps(
    argspec_path: Path,
    template_path: Path | None,
    module: str,
    repo: str,
) -> list[dict]:
    """Pattern 4: argspec leaves with no parser comparison path."""
    if not template_path or not template_path.is_file():
        return []

    leaves = extract_argspec_leaves(argspec_path)
    if not leaves:
        return []

    template_text = template_path.read_text(encoding="utf-8", errors="replace")
    comparison_paths = set(extract_parser_comparison_paths(template_text).values())
    argspec_text = argspec_path.read_text(encoding="utf-8", errors="replace")
    findings: list[dict] = []

    for path, typ, inside_list in leaves:
        rel_path = config_relative_path(path)

        # Skip module-level keys and list-element paths (hard to trace without runtime)
        if rel_path in MODULE_LEVEL_KEYS or path in MODULE_LEVEL_KEYS:
            continue
        if inside_list:
            continue

        if path_is_covered(rel_path, comparison_paths):
            continue

        # Conservative text check: only skip if the exact dotted path appears in template
        if rel_path in template_text:
            continue

        line = _line_number(argspec_text, f'"{rel_path.split(".")[-1]}"')
        findings.append(
            _finding(
                repo,
                module,
                rel_path,
                argspec_path,
                line,
                (
                    f"Argspec documents '{rel_path}' ({typ}) but no parser comparison path "
                    f"(name/compval) covers it — parameter may be a silent no-op"
                ),
                "Add rm_template parser with matching name/compval; register in config class",
                "4",
                "candidate",
            )
        )
    return findings


def scan_stale_parser_paths(
    argspec_path: Path,
    template_path: Path,
    module: str,
    repo: str,
) -> list[dict]:
    """Pattern 8: parser comparison paths with no matching argspec leaf."""
    leaves_list = extract_argspec_leaves(argspec_path)
    leaves = {config_relative_path(p) for p, _, _ in leaves_list}
    # Build set of all individual key segments present in argspec leaves
    all_leaf_segments = {seg for leaf in leaves for seg in leaf.split(".")}

    template_text = template_path.read_text(encoding="utf-8", errors="replace")
    findings: list[dict] = []

    for parser_name, comp_path in extract_parser_comparison_paths(template_text).items():
        if not is_valid_comparison_path(comp_path):
            continue
        # Direct or parent/child match
        if comp_path in leaves:
            continue
        if any(leaf.endswith(f".{comp_path}") for leaf in leaves):
            continue
        if any(leaf.startswith(f"{comp_path}.") for leaf in leaves):
            continue
        # Check if ALL path segments appear in argspec leaves (suggests valid but unflattened path)
        comp_segs = comp_path.split(".")
        if all(seg in all_leaf_segments for seg in comp_segs):
            continue

        line = _line_number(template_text, f'"name": "{parser_name}"')
        findings.append(
            _finding(
                repo,
                module,
                comp_path,
                template_path,
                line,
                (
                    f"Parser '{parser_name}' compares at '{comp_path}' but argspec has "
                    "no matching leaf — possible stale or misnamed parser"
                ),
                "Align parser name/compval with current argspec or remove dead parser",
                "8",
                "candidate",
            )
        )
    return findings


def scan_template_static_setval(
    template_path: Path,
    module: str,
    repo: str,
) -> list[dict]:
    """Pattern 3: static setval adjacent to a .set result that only checks 'is defined'."""
    findings: list[dict] = []
    text = template_path.read_text(encoding="utf-8", errors="replace")

    for match in STATIC_SETVAL_RE.finditer(text):
        setval = match.group(1)
        if setval in ("", " "):
            continue
        line = text[: match.start()].count("\n") + 1
        window = text[max(0, match.start() - 800) : match.end() + 800]
        if '"set"' in window and SET_DEFINED_ONLY_RE.search(window):
            findings.append(
                _finding(
                    repo,
                    module,
                    "(boolean .set toggle)",
                    template_path,
                    line,
                    (
                        f"Static setval '{setval}' adjacent to .set result that only "
                        "checks 'is defined' — negate/disable path may be missing"
                    ),
                    "Use conditional setval or comparison path parent.set with negate getval",
                    "3",
                    "medium",
                )
            )
    return findings


def scan_getval_missing_negate(
    template_path: Path,
    module: str,
    repo: str,
) -> list[dict]:
    """Pattern 2: getval regex lacks optional 'no' capture despite template handling negate."""
    findings: list[dict] = []
    text = template_path.read_text(encoding="utf-8", errors="replace")

    for match in GETVAL_BLOCK_RE.finditer(text):
        # group(1) = """ body, group(2) = ''' body
        regex_body = match.group(1) or match.group(2) or ""
        line = text[: match.start()].count("\n") + 1
        context_start = max(0, match.start() - 400)
        context_end = min(len(text), match.end() + 1200)
        context = text[context_start:context_end]

        has_negate_handling = (
            "False if" in context
            or "set: false" in context.lower()
            or SET_DEFINED_ONLY_RE.search(context)
            or ".set" in context
        )
        has_negate_group = "negate" in regex_body or r"\sno" in regex_body

        if has_negate_handling and not has_negate_group:
            findings.append(
                _finding(
                    repo,
                    module,
                    "(getval block)",
                    template_path,
                    line,
                    "getval regex lacks optional 'no' capture but template handles negate/disable",
                    "Add (?P<negate>\\sno)? before command keyword in getval",
                    "2",
                    "high",
                )
            )
    return findings


def scan_getval_without_setval(
    template_path: Path,
    module: str,
    repo: str,
) -> list[dict]:
    """Pattern 4 generate gap: parser has getval but no setval."""
    findings: list[dict] = []
    text = template_path.read_text(encoding="utf-8", errors="replace")

    for match in PARSER_NAME_RE.finditer(text):
        parser_name = match.group(1)
        block_end = _find_parser_block_end(text, match.start())
        block = text[match.start():block_end]

        has_getval = '"getval"' in block or "'getval'" in block
        has_setval = '"setval"' in block or "'setval'" in block
        if has_getval and not has_setval:
            line = text[: match.start()].count("\n") + 1
            findings.append(
                _finding(
                    repo,
                    module,
                    parser_name,
                    template_path,
                    line,
                    (
                        f"Parser '{parser_name}' has getval but no setval — "
                        "gather/parse may work but config generation is missing"
                    ),
                    "Add setval or confirm parse-only intent in docs",
                    "4",
                    "candidate",
                )
            )
    return findings


def scan_result_defined_only(
    template_path: Path,
    module: str,
    repo: str,
) -> list[dict]:
    """Pattern 1: result uses 'True if X is defined' without False branch — idempotency risk."""
    findings: list[dict] = []
    text = template_path.read_text(encoding="utf-8", errors="replace")

    for match in SET_DEFINED_ONLY_RE.finditer(text):
        line = text[: match.start()].count("\n") + 1
        window = text[max(0, match.start() - 200) : match.end() + 200]
        if "False if" in window:
            continue
        findings.append(
            _finding(
                repo,
                module,
                "(result expression)",
                template_path,
                line,
                (
                    "result sets .set via 'True if X is defined' only — "
                    "cannot distinguish enabled vs explicitly disabled"
                ),
                "Branch result for True, False, and None/absent states",
                "1",
                "medium",
            )
        )
    return findings


def scan_compound_cli_setval(
    template_path: Path,
    module: str,
    repo: str,
) -> list[dict]:
    """Pattern 10: setval with multiple Jinja vars and no 'is defined' guards — compound CLI risk.

    Flags parsers whose setval renders multiple template variables unconditionally,
    which produces 'None' tokens in generated CLI when optional sub-keys are absent.
    """
    findings: list[dict] = []
    text = template_path.read_text(encoding="utf-8", errors="replace")

    for match in PARSER_NAME_RE.finditer(text):
        parser_name = match.group(1)
        block_end = _find_parser_block_end(text, match.start())
        block = text[match.start():block_end]

        # Find setval string within the block (string form only; function setvals are fine)
        setval_str_m = re.search(
            r"""['"]setval['"]\s*:\s*['"]((?:[^'"]|\\.)*)['"]\s*,?""",
            block,
        )
        if not setval_str_m:
            continue

        setval = setval_str_m.group(1)
        jinja_vars = JINJA_VAR_RE.findall(setval)

        # Only flag when 2+ Jinja vars are rendered without conditional guards
        if len(jinja_vars) < 2:
            continue
        if "is defined" in setval or "{% if" in setval or "| default" in setval:
            continue

        line = text[: match.start()].count("\n") + 1
        findings.append(
            _finding(
                repo,
                module,
                parser_name,
                template_path,
                line,
                (
                    f"Parser '{parser_name}' setval renders {len(jinja_vars)} Jinja vars "
                    "without 'is defined' guards — absent optional sub-keys will produce "
                    "'None' tokens or malformed CLI (compound CLI Pattern 10 risk)"
                ),
                (
                    "Guard each optional sub-key with '{% if var is defined %}'; "
                    "build CLI only from present sub-keys; consult Cisco docs for negate semantics"
                ),
                "10",
                "candidate",
            )
        )
    return findings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _finding(
    repo: str,
    module: str,
    parameter: str,
    location_path: Path | None,
    line: int,
    issue: str,
    potential_fix: str,
    pattern: str,
    confidence: str,
) -> dict:
    return make_hit(
        repo=repo,
        module=module,
        parameter=parameter,
        pattern=pattern,
        issue=issue,
        confidence=confidence,
        file_path=location_path,
        collection_root=_COLLECTION_ROOT,
        line=line,
        potential_fix=potential_fix,
    )


def _line_number(text: str, needle: str) -> int:
    idx = text.find(needle)
    if idx < 0:
        return 1
    return text[:idx].count("\n") + 1


# ---------------------------------------------------------------------------
# Collection scan
# ---------------------------------------------------------------------------


def scan_collection(
    collection_root: Path,
    config: ReposConfig,
    repo: str | None = None,
    module_filter: str | None = None,
    platform_hint: str | None = None,
) -> list[dict]:
    global _COLLECTION_ROOT
    collection_root = collection_root.resolve()
    _COLLECTION_ROOT = collection_root
    try:
        repo_name = repo or collection_root.name
        platform = resolve_platform(
            collection_root,
            config,
            repo_name=repo_name,
            platform_hint=platform_hint,
        )
        if not platform:
            print(f"error: could not infer platform under {collection_root}", file=sys.stderr)
            return []

        prefix = resolve_module_prefix(config, platform, repo_name)
        argspec_files = find_argspec_files(collection_root, config, platform)
        template_files = find_rm_template_files(collection_root, config, platform)

        if module_filter:
            argspec_files = [
                f for f in argspec_files
                if module_filter in f.stem or module_filter == module_name_from_path(f, prefix)
            ]
            template_files = [
                f for f in template_files
                if module_filter in f.stem or module_filter == module_name_from_path(f, prefix)
            ]

        template_by_stem = {p.stem: p for p in template_files}
        all_findings: list[dict] = []

        for argspec_path in argspec_files:
            stem = argspec_path.stem
            module = module_name_from_path(argspec_path, prefix)
            tmpl = template_by_stem.get(stem)

            all_findings.extend(
                scan_argspec_set_comparison_path_mismatch(argspec_path, tmpl, module, repo_name)
            )
            all_findings.extend(scan_argspec_coverage_gaps(argspec_path, tmpl, module, repo_name))
            if tmpl:
                all_findings.extend(scan_stale_parser_paths(argspec_path, tmpl, module, repo_name))

        for template_path in template_files:
            module = module_name_from_path(template_path, prefix)
            all_findings.extend(scan_template_static_setval(template_path, module, repo_name))
            all_findings.extend(scan_getval_missing_negate(template_path, module, repo_name))
            all_findings.extend(scan_getval_without_setval(template_path, module, repo_name))
            all_findings.extend(scan_result_defined_only(template_path, module, repo_name))
            all_findings.extend(scan_compound_cli_setval(template_path, module, repo_name))

        return all_findings
    finally:
        _COLLECTION_ROOT = None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("collection_root", type=Path, help="Path to collection repo clone")
    add_scanner_cli_args(parser)
    parser.add_argument("--module", help="Limit scan to a single module (e.g. iosxr_bgp_global)")
    parser.add_argument("--platform", help="Platform name override (e.g. iosxr) — inferred if omitted")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of table")
    args = parser.parse_args()

    if args.repo and args.repos:
        print("warning: --repo and --repos both set; using --repo", file=sys.stderr)

    if not args.collection_root.is_dir():
        print(f"error: not a directory: {args.collection_root}", file=sys.stderr)
        return 1

    try:
        config = load_repos_config(args.repos_config)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

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
        return 0

    findings = scan_collection(
        args.collection_root,
        config,
        repo=resolved_repo,
        module_filter=args.module,
        platform_hint=args.platform,
    )

    if args.json:
        print(dumps_hits(findings))
        return 0

    if not findings:
        print("No mechanical gap signals found.")
        return 0

    headers = ["Repo", "Module", "Parameter", "File:Line", "Pattern", "Issue", "Confidence"]
    rows = [
        [
            f["repo"],
            f["module"],
            f["parameter"],
            file_line(f),
            f["pattern"],
            f["issue"],
            f["confidence"],
        ]
        for f in findings
    ]

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], min(len(cell), 60))

    def fmt_row(cells: list[str]) -> str:
        parts = []
        for i, cell in enumerate(cells):
            truncated = cell if len(cell) <= 60 else cell[:57] + "..."
            parts.append(truncated.ljust(widths[i]))
        return " | ".join(parts)

    print(fmt_row(headers))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(fmt_row(row))

    print(f"\n{len(findings)} candidate signal(s) — requires agent review.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
