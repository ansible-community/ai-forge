---
name: network-issues-resolver
description: >-
  Reproduce and fix a single confirmed parser, rm_template, or documentation (EXAMPLES)
  gap from network-issues-validator output. Acts as a senior Ansible network automation
  engineer: prepares collection branch, writes corrective reproduction playbooks,
  implements the fix with changelog and tests, validates unit + sanity via tox in
  the user venv, and simulates integration via playbook. Supports --skip-device for
  code-only fixes and --dry-run for local preview without git branch/commit/push/PR.
  Optionally opens an upstream draft PR. Resolves exactly one issue per invocation.
triggers:
  - resolve network issue
  - fix parser gap
  - reproduce and fix
  - fix rm_template bug
  - network issues resolver
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
argument-hint: "[network-issues-report.md] [--issue N] [--skip-device] [--dry-run]"
---

# Skill: network-issues-resolver

## Flags

| Flag | Effect |
|------|--------|
| `--issue N` | 1-based index into confirmed gaps (skip interactive pick when valid) |
| `--skip-device` | Code-only path: skip device playbook steps 3–4, 6, 10–11; unit + sanity are primary proof. Aliases: “code-only”, “no lab”, “offline” |
| `--dry-run` | **Local changes allowed**; **no** git branch, commit, push, or PR. Preview on disk via `git status` / `git diff` |

Both flags may be combined (`--skip-device --dry-run`).

**`--dry-run` is not read-only.** Unlike some other skills’ dry-run modes, this flag
**writes local files** (collection fix, changelog, tests, and playbooks when not
skipping device). Always tell the user up front and at the end that the working
tree was modified.

Device alternatives and skip rules:
[reference/device-alternatives.md](reference/device-alternatives.md).

## Entry gates

Do not proceed until the user provides. Ensure you demand the following, and not assume any of them are present:

| Gate | Input | Default | `--skip-device` | `--dry-run` |
|------|-------|---------|----------------|-------------|
| Validated report | `network-issues-report.md` / `.json` | Required | Required | Required |
| **Single issue** | Exactly one row from **Confirmed gaps** | Required | Required | Required |
| **Playbook directory** | Absolute path for reproduction playbooks | Required | **Not required** | Same as device mode |
| **Collection path** | Absolute path to collection clone | Required | Required | Required |
| **Python venv** | Path to venv (before playbook or tox) | Required | Required (tox) | Same as device mode |

If playbook directory is missing and not `--skip-device`: ask the user; suggest
`mkdir -p ~/network-playbooks`, or offer `--skip-device`.

Present confirmed gaps and ask the user to pick **one** issue (unless `--issue N`).
Zero confirmed gaps → stop.

**No collection-scope flags.** Scope is the single confirmed gap row from the validated
report (`Repo`, `Module`, `Parameter`, `File:Line`, `Pattern`). Use `repos.yaml` only to
resolve path templates for that issue's `Repo` entry — not to select which collections to scan.

## Modes

### Default (lab)

Full pipeline including device repro (steps 3–4, 6) and integration sim (10–11).

### `--skip-device` (code-only)

See [device-alternatives.md](reference/device-alternatives.md). Mark steps 3–4, 6,
10–11 as N/A. Primary mock = unit fixtures; optional `rendered`/`parsed` notes there.

### `--dry-run` (local preview)

Write local files (honor `--skip-device`); skip step 1 branch creation and
step 12. Announce at start and end that local files were modified. Deliver:
`git status`/`git diff`, suggested branch name, would-run step-12 commands.
Ask: keep / discard / continue without `--dry-run`.

## Resolution pipeline

```
- [ ] Gates satisfied
- [ ] 1 — Prepare collection branch   (skip branch under --dry-run)
- [ ] 2 — Study issue; read sibling playbooks in playbook dir (if any)
- [ ] 3 — Write repro playbook (one file; iterate in place)   [--skip-device: N/A]
- [ ] 4 — Run playbook; confirm broken behavior               [--skip-device: N/A]
- [ ] 5 — Implement fix in collection
- [ ] 6 — Corrective repro playbook + re-run (gate before unit tests)  [--skip-device: N/A]
- [ ] 7 — Changelog fragment
- [ ] 8 — Update unit cases → run unit + sanity tox
- [ ] 9 — Update integration cases (source only; not runnable via tox)
- [ ] 10 — Integration sim playbook in playbook dir + run on device  [--skip-device: N/A]
- [ ] 11 — Ask user about reverting device changes                   [--skip-device: N/A]
- [ ] 12 — Ask user about upstream **draft** PR   (skip under --dry-run; show would-run cmds)
```

All operational detail: [reference/resolution-details.md](reference/resolution-details.md).

Pattern/fix context: [network-issues-knowledge/patterns.md](../network-issues-knowledge/patterns.md).

**Pattern 11 (stale EXAMPLES):** reproduce the faulty task vars from `EXAMPLES` in
`plugins/modules/<prefix><module>.py` (step 3–4), update `EXAMPLES` to match argspec
(step 5), re-run playbook with the corrected example (step 6). Under `--skip-device`,
skip device repro; prove with sanity + corrected example analysis / unit if present.
Sanity tox validates module documentation; unit/integration case updates only if the
stale example also appears in tests.

## Critical rules

- One issue only; sync fresh `main` from **upstream** before branching (when not `--dry-run`)
- **`--dry-run`:** local file edits OK; **never** create a branch, commit, push, or open a PR; always state that local files were modified
- **`--skip-device`:** do not invent device runs; use unit fixtures as primary mock ([device-alternatives.md](reference/device-alternatives.md))
- **Fork workflow:** `git push origin` → PR base **upstream** / head **fork:branch** (step 12 only; not under `--dry-run`)
- One repro playbook path — update in place through steps 3–6; never `repro_v2` copies (when not skipping device)
- **Corrective repro:** playbook must auto-undo device changes before unit tests (step 6; when not skipping device)
- **Integration sim:** after integration case edits, mirror full flow in playbook dir (step 10; when not skipping device)
- Same venv for playbook runs and tox
- **Tests:** read existing cases first; update in place; one scenario per case
- **End with steps 11–12** in default mode; under `--skip-device` end with step 12 only; under `--dry-run` end with local preview (no step 12 execution)
- **Capture before/after snippets** at steps 4 and 6 (device) or from unit evidence (`--skip-device`) for the PR body

## Deliverables

Items marked **[device]** are N/A under `--skip-device`. Item 8 applies only under `--dry-run`.

1. Issue, branch (or “current branch — dry-run”), collection path
2. **[device]** Corrective repro playbook + before/after summary; else unit evidence
3. **[device]** Integration sim playbook path + run summary (step 10)
4. Files changed (fix, changelog, unit + integration cases)
5. Unit + sanity tox results
6. Integration cases updated (not run via tox locally)
7. **[device]** Device cleanup prompt if corrective/sim did not fully restore state
8. `--dry-run` only: local preview banner, `git status`/`git diff`, discard/keep/continue, would-run step-12 commands

Do not commit, push, or open a PR unless user requests it in step 12. Use `--draft` unless user asks for ready-for-review.

## Resources

| File | Content |
|------|---------|
| [reference/resolution-details.md](reference/resolution-details.md) | Branch, playbooks, changelog, tests, tox, sim, cleanup |
| [reference/device-alternatives.md](reference/device-alternatives.md) | `--skip-device`, mocks, code-only evidence |
| [reference/upstream-pr.md](reference/upstream-pr.md) | Draft PR template, snippets, fork remotes, unit-only evidence |
| [../network-issues-knowledge/patterns.md](../network-issues-knowledge/patterns.md) | Gap patterns and fixes |
| [../network-issues-scanner/config/repos.yaml](../network-issues-scanner/config/repos.yaml) | Path templates — look up `platform` / `module_prefix` for the issue's `Repo` |
