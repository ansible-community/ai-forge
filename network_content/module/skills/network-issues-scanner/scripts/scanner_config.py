"""Shared repos.yaml loader for network-issues-scanner scripts.

Used by scan_mechanical_signals.py and validate_examples.py for path templates,
platform, and module_prefix resolution.

Agent workflow (scanner Step 1): use filter_collections() to derive which
collections[] entries to clone — same scope rules as --repo / --repos on the scripts:

  python -c "
  from scanner_config import load_repos_config, filter_collections, parse_repos_arg
  cfg = load_repos_config(None)
  for c in filter_collections(cfg, repo='cisco.iosxr', repos=parse_repos_arg(None)):
      print(c.repo, c.platform)
  "
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install PyYAML", file=sys.stderr)
    sys.exit(1)

DEFAULT_REPOS_CONFIG = Path(__file__).resolve().parent.parent / "config" / "repos.yaml"

_KNOWN_PLATFORMS = frozenset({"ios", "nxos", "iosxr", "eos", "junos", "vyos", "nso", "exos"})


@dataclass(frozen=True)
class CollectionEntry:
    repo: str
    platform: str
    module_prefix: str


@dataclass(frozen=True)
class ReposConfig:
    github_org: str
    collections: tuple[CollectionEntry, ...]
    paths: dict[str, str]


def load_repos_config(path: Path | None = None) -> ReposConfig:
    config_path = path or DEFAULT_REPOS_CONFIG
    if not config_path.is_file():
        msg = f"error: repos config not found: {config_path}"
        raise FileNotFoundError(msg)

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"error: invalid repos config format in {config_path}"
        raise ValueError(msg)

    collections: list[CollectionEntry] = []
    for item in raw.get("collections", []):
        if not isinstance(item, dict):
            continue
        repo = item.get("repo")
        platform = item.get("platform")
        module_prefix = item.get("module_prefix")
        if repo and platform and module_prefix:
            collections.append(
                CollectionEntry(
                    repo=str(repo),
                    platform=str(platform),
                    module_prefix=str(module_prefix),
                )
            )

    paths = raw.get("paths", {})
    if not isinstance(paths, dict):
        paths = {}

    return ReposConfig(
        github_org=str(raw.get("github_org", "ansible-collections")),
        collections=tuple(collections),
        paths={str(k): str(v) for k, v in paths.items()},
    )


def parse_repos_arg(repos: str | None) -> list[str] | None:
    if not repos:
        return None
    return [part.strip() for part in repos.split(",") if part.strip()]


def filter_collections(
    config: ReposConfig,
    *,
    repo: str | None = None,
    repos: list[str] | None = None,
) -> list[CollectionEntry]:
    if repo:
        entry = lookup_collection(config, repo)
        return [entry] if entry else []
    if repos:
        allowed = set(repos)
        return [c for c in config.collections if c.repo in allowed]
    return list(config.collections)


def lookup_collection(config: ReposConfig, repo_name: str) -> CollectionEntry | None:
    for entry in config.collections:
        if entry.repo == repo_name:
            return entry
    return None


def infer_repo_name(collection_root: Path) -> str:
    parts = collection_root.parts
    namespaces = {"cisco", "arista", "ansible", "junipernetworks", "vyos", "frr"}
    for i, part in enumerate(parts[:-1]):
        if part in namespaces:
            return f"{part}.{parts[i + 1]}"
    return collection_root.name


def resolve_repo_name(
    collection_root: Path,
    config: ReposConfig,
    repo_override: str | None,
) -> str:
    if repo_override:
        return repo_override
    inferred = infer_repo_name(collection_root)
    if lookup_collection(config, inferred):
        return inferred
    if lookup_collection(config, collection_root.name):
        return collection_root.name
    return inferred


def is_repo_in_scope(
    resolved_repo: str,
    *,
    repo: str | None,
    repos: list[str] | None,
) -> bool:
    if repo:
        return resolved_repo == repo
    if repos:
        return resolved_repo in repos
    return True


def _scan_platform_dirs(collection_root: Path) -> list[str]:
    net_dir = collection_root / "plugins" / "module_utils" / "network"
    if not net_dir.is_dir():
        return []
    return [
        p.name
        for p in net_dir.iterdir()
        if p.is_dir() and not p.name.startswith("_") and p.name != "__pycache__"
    ]


def resolve_platform(
    collection_root: Path,
    config: ReposConfig,
    *,
    repo_name: str | None,
    platform_hint: str | None = None,
) -> str | None:
    if platform_hint:
        return platform_hint

    entry = lookup_collection(config, repo_name) if repo_name else None
    if entry:
        return entry.platform

    children = _scan_platform_dirs(collection_root)
    if len(children) == 1:
        return children[0]
    if len(children) > 1:
        known = [c for c in children if c in _KNOWN_PLATFORMS]
        if len(known) == 1:
            return known[0]
        print(
            f"warning: multiple platform dirs found under "
            f"{collection_root}/plugins/module_utils/network/: {children}. "
            "Use --platform or --repo to specify one.",
            file=sys.stderr,
        )
    return None


def resolve_module_prefix(
    config: ReposConfig,
    platform: str,
    repo_name: str | None,
) -> str:
    entry = lookup_collection(config, repo_name) if repo_name else None
    if entry:
        return entry.module_prefix
    for candidate in config.collections:
        if candidate.platform == platform:
            return candidate.module_prefix
    return f"{platform}_"


def collection_path(
    collection_root: Path,
    config: ReposConfig,
    path_key: str,
    platform: str,
) -> Path:
    template = config.paths.get(path_key)
    if not template:
        msg = f"error: path key {path_key!r} not defined in repos config"
        raise KeyError(msg)
    if "{platform}" in template:
        rel = template.format(platform=platform)
    else:
        rel = template
    return collection_root / rel


def add_scanner_cli_args(parser: Any) -> None:
    parser.add_argument(
        "--repos-config",
        type=Path,
        default=DEFAULT_REPOS_CONFIG,
        help="Path to repos.yaml (default: config/repos.yaml beside this skill)",
    )
    parser.add_argument("--repo", help="Collection repo name (e.g. cisco.iosxr)")
    parser.add_argument(
        "--repos",
        help="Comma-separated repo allowlist (e.g. cisco.ios,cisco.nxos)",
    )


def check_repo_scope(
    collection_root: Path,
    config: ReposConfig,
    *,
    repo: str | None,
    repos: list[str] | None,
) -> tuple[str, bool]:
    resolved_repo = resolve_repo_name(collection_root, config, repo)
    in_scope = is_repo_in_scope(resolved_repo, repo=repo, repos=repos)
    return resolved_repo, in_scope
