---
name: network-issues-validator
description: >-
  Validate network-issues-scanner hits by reading source code and tests for each
  candidate. Thoroughly verify parser and rm_template gaps, drop false positives
  and already-fixed issues, and emit a confirmed gap report. Use after a scanner
  run or when handed scanner-hits output. Prefer network-issues-orchestrator for
  end-to-end scan plus validation.
triggers:
  - validate parser gaps
  - verify scanner hits
  - filter false positives
  - confirm network issues
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
argument-hint: "[scanner-hits.md] [--module iosxr_bgp_global]"
---

# Skill: network-issues-validator

## Prerequisites

- Scanner output (`network-issues-scanner-hits.md` / `.json`) in working directory or user-provided path
- Local clone of relevant collection(s) at paths used during the scan

## Input

1. `network-issues-scanner-hits.md` / `.json` in working directory (default)
2. User-provided path to scanner output
3. Inline table or JSON pasted by the user

**Scope is defined by the scanner hits artifact** — each row carries its own `repo` and
`module`. When invoked by `network-issues-orchestrator`, validate every hit in the file;
do not re-apply scanner `--repo`/`--repos` flags. Optional `--module` filters hits to
one module when re-running the validator alone on an existing hits file.

---

## Validation Pipeline

```
Validation Progress:
- [ ] Step 1 — Load scanner hits
- [ ] Step 2 — Resolve collection source paths
- [ ] Step 3 — Verify each hit (per-hit deep review)
- [ ] Step 4 — Re-check test coverage for confirmed gaps
- [ ] Step 5 — Produce validated report
```

### Step 1 — Load scanner hits

Parse markdown table or JSON (`hits[]` array, or a bare array from Step 3 script output).
Record count by confidence and distinct repos present in the hit rows — that is the
validation scope. Each hit uses `file` + `line` (not a combined `location` field).

### Step 2 — Resolve collection source paths

Locate collection clones used during the scan. Reuse scanner paths when possible.

### Step 3 — Verify each hit

Follow [verification.md](../network-issues-knowledge/verification.md) for every hit.
For Patterns 5, 6, and 10, consult Cisco documentation before confirming or dropping.
For Pattern 11, scanner Step 3 ran `validate_examples.py` which pre-checks type
mismatches, removed parameters, invalid state, and missing required fields. Each
finding includes a `notes` integration testcase reference. Confirm by reading
the cited `file:line` in EXAMPLES and the argspec; drop if the finding is
`examples-aligned`. Documentation-only gaps: resolver reproduces the faulty
example and updates `EXAMPLES`.
Apply pattern bars from [patterns.md](../network-issues-knowledge/patterns.md).

Process `confirmed` → `likely` → `candidate`. Do not skip `candidate` hits.

### Step 4 — Re-check test coverage

For each confirmed hit, follow [checklists.md](../network-issues-knowledge/checklists.md).

### Step 5 — Produce validated report

Emit per [validated-report-template.md](reference/validated-report-template.md):

- `network-issues-report.md` (with Validation Summary and Dropped hits sections)
- `network-issues-report.json`

Handoff: [network-issues-resolver](../network-issues-resolver/SKILL.md) fixes **one** confirmed gap at a time.

## Knowledge files

| File | Use for |
|------|---------|
| [verification.md](../network-issues-knowledge/verification.md) | Per-hit procedure, verdicts, drop codes |
| [patterns.md](../network-issues-knowledge/patterns.md) | Pattern confirm/drop bars (incl. Patterns 10–11) |
| [parser-anatomy.md](../network-issues-knowledge/parser-anatomy.md) | Comparison paths, config registration |
| [crosswalk.md](../network-issues-knowledge/crosswalk.md) | Crosswalk procedure |
| [checklists.md](../network-issues-knowledge/checklists.md) | Test and compound-CLI re-check |
| [validated-report-template.md](reference/validated-report-template.md) | Step 5 — output format |
| [repos.yaml](../network-issues-scanner/config/repos.yaml) | Path layout when opening source files cited in hits |
