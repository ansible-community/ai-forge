---
name: network-issues-orchestrator
description: >-
  End-to-end network collection parser and rm_template issue audit. Runs
  network-issues-scanner first to collect candidate hits across collections
  listed in repos.yaml, then network-issues-validator to verify each hit and
  drop false positives. Delivers a validated gap report.
  Use when asked to scan parser gaps, audit resource modules, or find template
  bugs with confirmed results.
triggers:
  - network issues audit
  - confirmed gap report
  - scan and validate parser gaps
  - audit resource modules
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
argument-hint: "[--repo cisco.iosxr | --repos cisco.ios,cisco.nxos] [--module iosxr_bgp_global]"
---

# Skill: network-issues-orchestrator

## Prerequisites

- `gh` CLI authenticated
- Local clone of target collection(s), or network access via `gh api`

---

## Mode Detection

### Full audit mode (default)

No `--repo`, `--repos`, or `--module` provided. Scan **all collections** in
`repos.yaml`, then validate every hit in the scanner output. Do NOT ask clarifying
questions — run the full pipeline automatically.

### Targeted mode

User specifies `--repo` (single collection), `--repos` (comma-separated subset), `--module`,
or a collection name. **Scanner phase only:** clone and scan that scope. If both `--repo`
and `--repos` are given, prefer `--repo`. **Validator phase:** consumes the scanner hits
artifact — no separate `--repo`/`--repos` flags; scope is whatever repos appear in the hits.

---

## Orchestration Pipeline

Track progress with a checklist:

```
Orchestrator Progress:
- [ ] Phase 1 — Scanner (network-issues-scanner)
- [ ] Phase 2 — Validator (network-issues-validator)
- [ ] Phase 3 — Deliver final report
```

### Phase 1 — Scanner

Read and follow [network-issues-scanner/SKILL.md](../network-issues-scanner/SKILL.md)
in full. Execute its 7-step scan pipeline.

**Outputs required before Phase 2:**

- `network-issues-scanner-hits.md`
- `network-issues-scanner-hits.json`

If the scanner finds zero hits, skip to Phase 3 with an empty validated report.

### Phase 2 — Validator

Read and follow [network-issues-validator/SKILL.md](../network-issues-validator/SKILL.md)
in full. Pass the Phase 1 output files as input — **do not** re-apply scanner scope flags;
validate every hit row in the scanner hits artifact.

Execute all 5 validation steps. Process every hit — do not skip `candidate` rows.

**Outputs:**

- `network-issues-report.md`
- `network-issues-report.json`

### Phase 3 — Deliver final report

- Executive summary: modules scanned, hits, confirmed gaps, drop rate
- Confirmed gaps table from `network-issues-report.md`
- Notable drops (high-confidence only; brief reason)
- Artifact paths (all four output files)

To fix one gap: hand off to `network-issues-resolver`. Do not present raw scanner hits unless explicitly asked.

---

## Handoff contract

| Artifact | Producer | Consumer | Purpose |
|----------|----------|----------|---------|
| `network-issues-scanner-hits.md` | Scanner | Validator, User (optional) | Human-readable candidates |
| `network-issues-scanner-hits.json` | Scanner | Validator | Machine handoff |
| `network-issues-report.md` | Validator | User, Resolver | Final validated gaps |
| `network-issues-report.json` | Validator | User, Resolver | Structured confirmed + dropped |

---

## Critical rules

- **Preserve scope** — `--repo`, `--repos`, or `--module` controls the **scanner** phase only.
  The validator inherits scope from scanner hits; the resolver takes one issue from the
  validated report.
- **Reuse clones** — validator uses the same collection paths the scanner used.
- **Artifact naming** — targeted scans: suffix artifacts with scope (e.g. `network-issues-scanner-hits.cisco.iosxr.md`). Full-scope: default names.
