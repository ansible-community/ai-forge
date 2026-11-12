"""Canonical scanner hit dict for Step 3 scripts and Step 7 JSON handoff."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any


def rel_file_path(file_path: Path | str | None, collection_root: Path | None) -> str:
    if not file_path:
        return ""
    path = Path(file_path)
    if collection_root and path.is_absolute():
        try:
            return str(path.resolve().relative_to(collection_root.resolve()))
        except ValueError:
            return str(path)
    return str(path)


def make_hit(
    *,
    repo: str,
    module: str,
    parameter: str,
    pattern: str,
    issue: str,
    confidence: str,
    file_path: Path | str | None = None,
    collection_root: Path | None = None,
    line: int = 1,
    notes: str = "",
    potential_fix: str = "",
) -> dict[str, Any]:
    """Build one scanner hit matching scanner-report-template.json hits[] shape."""
    return {
        "repo": repo,
        "module": module,
        "parameter": parameter,
        "file": rel_file_path(file_path, collection_root),
        "line": line,
        "pattern": str(pattern),
        "issue": issue,
        "confidence": confidence,
        "notes": notes,
        "potential_fix": potential_fix,
    }


def file_line(hit: dict[str, Any]) -> str:
    """Format file:line for markdown tables and human output."""
    file_part = hit.get("file", "")
    line_part = hit.get("line", "")
    if file_part and line_part:
        return f"{file_part}:{line_part}"
    return file_part or ""


def wrap_hits_report(
    hits: list[dict[str, Any]],
    *,
    scope: list[str],
    modules_scanned: int = 0,
    scan_date: str | None = None,
) -> dict[str, Any]:
    """Full Step 7 JSON document (agent merges per-clone script output into this)."""
    return {
        "scan_date": scan_date or date.today().isoformat(),
        "scope": scope,
        "modules_scanned": modules_scanned,
        "hits": hits,
    }


def dumps_hits(hits: list[dict[str, Any]], *, indent: int = 2) -> str:
    """JSON array of hits — per-clone --json output from both Step 3 scripts."""
    import json

    return json.dumps(hits, indent=indent)
