---
name: network-issues-scanner
description: >-
  Scan Ansible network collection resource modules (cisco.ios, cisco.nxos,
  cisco.iosxr, arista.eos) for parser and rm_template issue candidates — argspec
  coverage gaps, unregistered parsers, type mismatches, boolean toggle/idempotency
  issues, missing negate regex, stale parsers, outdated module EXAMPLES, and test
  blind spots. Casts a wide net and emits candidate hits for
  network-issues-validator. Use when raw scanner hits are needed without the full
  validation phase. Prefer network-issues-orchestrator for end-to-end scan plus
  validation.
triggers:
  - scan parser gaps
  - raw scanner hits
  - network issues scan
  - scanner phase only
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
argument-hint: "[--repo cisco.iosxr | --repos cisco.ios,cisco.nxos] [--module iosxr_bgp_global] [--repos-config PATH]"
---

# Skill: network-issues-scanner

## Prerequisites

- `gh` CLI authenticated
- Local clone of target collection(s), or network access via `gh api`
- PyYAML (required by scanner scripts for `repos.yaml`)

## Knowledge files

Read [network-issues-knowledge/README.md](../network-issues-knowledge/README.md) as needed
during the scan pipeline:

| File | Use for |
|------|---------|
| [parser-anatomy.md](../network-issues-knowledge/parser-anatomy.md) | Comparison paths, config registration |
| [patterns.md](../network-issues-knowledge/patterns.md) | Pattern classification (incl. Patterns 10–11) |
| [crosswalk.md](../network-issues-knowledge/crosswalk.md) | Argspec ↔ template crosswalk |
| [confidence-and-severity.md](../network-issues-knowledge/confidence-and-severity.md) | Hit confidence and severity |
| [checklists.md](../network-issues-knowledge/checklists.md) | Module and compound-CLI checklists |

Operational details: [config/repos.yaml](config/repos.yaml),
[reference/workflow-details.md](reference/workflow-details.md),
[reference/scanner-report-template.md](reference/scanner-report-template.md).

---

## Mode Detection

**Full scan (default):** all collections in `repos.yaml` — run automatically, no clarifying questions.

**Targeted:** user specifies `--repo` (single collection), `--repos` (comma-separated subset), `--module`, or collection name — scan that scope only. If both `--repo` and `--repos` are given, prefer `--repo`.

---

## Scan Pipeline

```
Scan Progress:
- [ ] Step 1 — Acquire collection source
- [ ] Step 2 — Enumerate resource modules
- [ ] Step 3 — Mechanical pre-scan
- [ ] Step 4 — Argspec vs template crosswalk
- [ ] Step 5 — Pattern classification (candidates)
- [ ] Step 6 — Test coverage gap check
- [ ] Step 7 — Produce scanner hits report
```

Read [workflow-details.md](reference/workflow-details.md) before Steps 2, 4, and 6.

### Step 1 — Acquire collection source

Read [config/repos.yaml](config/repos.yaml) and determine which `collections[]` entries
to clone. Scope rules (same as Step 3 script flags and `scanner_config.filter_collections()`):

- No scope flags → all collections
- `--repo cisco.iosxr` → that collection only
- `--repos cisco.ios,cisco.nxos` → those collections only
- If both `--repo` and `--repos` are given, prefer `--repo`

Optional: run `filter_collections()` from [scripts/scanner_config.py](scripts/scanner_config.py)
to list scoped entries (must run from the `scripts/` directory):

```bash
cd network_content/module/skills/network-issues-scanner/scripts
python -c "
from scanner_config import load_repos_config, filter_collections, parse_repos_arg
cfg = load_repos_config(None)
repos = parse_repos_arg('cisco.ios,cisco.nxos')  # or None for all; use repo= for single
for c in filter_collections(cfg, repo=None, repos=repos):
    print(c.repo)
"
```

Then clone each listed repo:

```bash
gh repo clone ansible-collections/cisco.iosxr /tmp/cisco.iosxr -- --depth=1 2>/dev/null || true
```

Prefer existing local clones when available.

### Step 2 — Enumerate resource modules

Glob `plugins/modules/*.py`; pair argspec and rm_template files by stem name.
See workflow-details.md for module layout.

### Step 3 — Mechanical pre-scan

Both scripts load path templates and collection metadata from `repos.yaml` via
`scripts/scanner_config.py`. Pass matching scope flags on each per-clone invocation.

```bash
python scripts/scan_mechanical_signals.py /path/to/cisco.iosxr --repo cisco.iosxr --json
python scripts/validate_examples.py /path/to/cisco.iosxr --repo cisco.iosxr --json
```

When scoped via `--repos`, pass the same value to each script call. Out-of-scope clones
are skipped (exit 0). Optional: `--repos-config PATH` to override the default config file.

Produces candidate signals for Steps 4–5. `validate_examples.py` performs
structural Pattern 11 checks (type mismatches, removed parameters, invalid state
values) with per-task findings and integration testcase references. Run
supplemental grep commands from workflow-details.md.

### Step 4 — Argspec vs template crosswalk

Follow [crosswalk.md](../network-issues-knowledge/crosswalk.md). Primary discovery step.
Pattern 11 structural checks (type mismatches, removed parameters, invalid state, missing required) are handled by `validate_examples.py` in Step 3 — do not duplicate that work here.

### Step 5 — Pattern classification (candidates)

Classify candidates per [patterns.md](../network-issues-knowledge/patterns.md),
including Pattern 10 (hardcoded compound CLI — verify against Cisco docs when flagged).
Pattern 11 findings come pre-classified from Step 3 (`validate_examples.py`) — merge them into the hits report.
Assign confidence per [confidence-and-severity.md](../network-issues-knowledge/confidence-and-severity.md).

**Do not drop hits.** Note mitigating context in `Notes` for the validator.

### Step 6 — Test coverage gap check

Follow [checklists.md](../network-issues-knowledge/checklists.md) and workflow-details.md grep commands.

### Step 7 — Produce scanner hits report

Concatenate `--json` hit arrays from both Step 3 scripts (identical object shape via
`scripts/scanner_finding.py`). Wrap with `wrap_hits_report()` for the final file.

Emit per [scanner-report-template.md](reference/scanner-report-template.md):

- `network-issues-scanner-hits.md`
- `network-issues-scanner-hits.json`

When invoked by `network-issues-orchestrator`, pass both files to the validator.
