# Scanner Hits Report Template

Use this format for Step 7 output. Save as `network-issues-scanner-hits.md` in the
working directory. Mirror the same rows in `network-issues-scanner-hits.json`.

This is **candidate output** for `network-issues-validator` — not the final report.

```markdown
# Network Issues Scanner Hits

**Scan date:** YYYY-MM-DD
**Scope:** cisco.ios, cisco.nxos, cisco.iosxr, arista.eos (or subset)
**Modules scanned:** N
**Hits found:** M

| Repo | Module | Parameter | File:Line | Pattern | Issue | Confidence | Notes |
|------|--------|-----------|-----------|---------|-------|------------|-------|
| cisco.iosxr | iosxr_bgp_global | max_metric.router_lsa.on_startup.wait_for_bgp | plugins/.../argspec/bgp_global.py:412 | 4 | Argspec documents option but no parser comparison path covers it | likely | No compval in module; check config registration |
```

## Column rules

- **Repo** — collection name (`cisco.iosxr`)
- **Module** — full module name (`iosxr_bgp_global`)
- **Parameter** — dotted argspec path (`neighbors.shutdown.set`)
- **File:Line** — repo-relative path with line number (primary evidence location)
- **Pattern** — [patterns.md](../network-issues-knowledge/patterns.md) pattern number (1–11) or `generate-gap` / `coverage`
- **Issue** — concise description of the suspected gap and user-visible symptom
- **Confidence** — `confirmed`, `likely`, or `candidate`
- **Notes** — mitigating context, sibling parsers, config-class hints for validator

## Sort order

Sort by confidence (`confirmed` first), then severity (high first), then repo, then module.

## JSON handoff shape

**Step 3 scripts** (`--json`): each emits a JSON **array** of hit objects (same shape
from both scripts). The agent concatenates arrays from all clones, then wraps for Step 7
using `scanner_finding.wrap_hits_report()` or equivalent.

**Step 7 file** (`network-issues-scanner-hits.json`): wrapper keys `scan_date`, `scope`
(array), `modules_scanned`, and `hits[]`. Each hit object:

| Key | Type | Description |
|-----|------|-------------|
| `repo` | string | Collection name |
| `module` | string | Full module name |
| `parameter` | string | Dotted argspec path |
| `file` | string | Repo-relative path (no line suffix) |
| `line` | number | Line number in `file` |
| `pattern` | string | Pattern number (1–11) |
| `issue` | string | Suspected gap description |
| `confidence` | string | `confirmed`, `likely`, or `candidate` |
| `notes` | string | Mitigating context, integration refs (Pattern 11) |
| `potential_fix` | string | Brief fix direction for validator/resolver |

Markdown **File:Line** column = `{file}:{line}`.
