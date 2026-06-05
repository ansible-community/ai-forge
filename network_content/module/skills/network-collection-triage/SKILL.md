---
name: network-collection-triage
description: >-
  Triage bug reports, CI failures, and GitHub issues across Ansible network
  collections (cisco.ios, cisco.iosxr, cisco.nxos, arista.eos, junos,
  ansible.netcommon, ansible.utils). Two modes: scan mode for bulk weekly
  triage across all repos, and direct mode for deep triage of a single
  issue. Network-specific: uses cross-collection cascade detection for
  shared dependencies (netcommon, utils) and known network CI failure
  patterns. Outputs structured JSON and markdown. Use when asked to triage
  network issues, scan network issues, weekly triage, triage CI failure,
  or triage collection issue. Do not use for non-network collections or
  general Ansible questions.
triggers:
  - triage network issues
  - triage network
  - scan network issues
  - weekly triage
  - triage CI failure
  - triage collection issue
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
argument-hint: "[<github-issue-url>] [--scan]"
---

# Skill: network-collection-triage

## Purpose

Triage bug reports, CI failures, and GitHub issues across Ansible network
collections. Categorize items, check known network CI failure patterns,
assess severity with cross-collection cascade detection for shared
dependencies (`ansible.netcommon`, `ansible.utils`), and produce structured
JSON and markdown output suitable for downstream dashboards or reports.

### Why network-specific

This skill exists in `network_content` rather than `ansible-collection-sdlc`
because the triage logic depends on network-specific domain knowledge:

- **Cross-collection cascade detection** tied to the `ansible.netcommon` and
  `ansible.utils` dependency chain shared by all network collections
- **Known CI failure patterns** specific to network collection CI (Galaxy
  version lag for netcommon, persistent connection timeout leaks, etc.)
- **Scoped repo list** — queries a fixed set of network collection repositories
  under the `ansible-collections` GitHub org

A generic collection triage skill would not have this domain knowledge.

## When to Invoke

TRIGGER when:

- A user asks to triage network collection issues or CI failures
- A user asks to scan repos for unassigned bugs/PRs (scan mode)
- A user pastes a GitHub issue URL or CI failure link for a network collection
- A user asks for a weekly triage report
- A user says "triage network", "scan network issues", or "weekly triage"

DO NOT TRIGGER when:

- The issue is in a non-network collection (use generic triage instead)
- The user is asking general Ansible questions unrelated to triage
- The user wants to fix a bug (use a bugfix workflow instead)

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- Push access not required — this skill only reads GitHub data

---

## Mode Detection

This skill has TWO modes. Detect the mode from the user's trigger and
act accordingly. **Do NOT ask clarifying questions in scan mode.**

### Scan mode (no specific issue provided)

Any trigger that does NOT include a specific GitHub URL or issue number
runs scan mode. This includes: "triage network issues", "triage network",
"scan network issues", "weekly triage", "generate triage report".

**When scan mode is triggered: immediately run the full pipeline end-to-end
without asking the user for any input.** Do NOT stop to ask "What would you
like me to triage?" — the whole point of scan mode is zero-input bulk triage.

### Direct mode (specific issue provided)

A user pastes a GitHub issue URL, CI failure link, error log, or describes
a specific bug symptom. In this mode (and ONLY this mode), ask the user
for additional context if needed (collection, platform, Ansible version).

---

## Collections in Scope

| Collection | Platform | Connection |
|---|---|---|
| `ansible.netcommon` | Shared (connection plugins, base classes) | N/A |
| `ansible.utils` | Shared (utility filters, cli_parse) | N/A |
| `cisco.ios` | Cisco IOS / IOS-XE | network_cli |
| `cisco.iosxr` | Cisco IOS-XR | network_cli, netconf |
| `cisco.nxos` | Cisco NX-OS | network_cli, httpapi |
| `arista.eos` | Arista EOS | network_cli, httpapi |
| `junipernetworks.junos` | Juniper JunOS | network_cli, netconf |
| `cisco.asa` | Cisco ASA | network_cli |
| `vyos.vyos` | VyOS | network_cli |

**GitHub org**: `ansible-collections`

---

## Scan Mode Pipeline

**Execute all steps automatically without stopping for user input.**

### Step 1 — Fetch open issues and PRs across all repos

Use `gh` to query each repo in scope. Fetch open issues labelled `bug`
and open pull requests from the last 14 days (configurable).

**For bugs (issues):**

```bash
gh issue list --repo ansible-collections/cisco.ios --label bug --state open \
  --json number,title,url,labels,createdAt,author,assignees --limit 50
```

**For pull requests:**

```bash
gh pr list --repo ansible-collections/cisco.ios --state open \
  --json number,title,url,labels,createdAt,author,isDraft,reviewDecision \
  --limit 50
```

Run these for every repo in the Collections in Scope table:

```
ansible-collections/ansible.netcommon
ansible-collections/ansible.utils
ansible-collections/cisco.ios
ansible-collections/cisco.iosxr
ansible-collections/cisco.nxos
ansible-collections/arista.eos
ansible-collections/junipernetworks.junos
ansible-collections/cisco.asa
ansible-collections/vyos.vyos
```

Combine all results into a single list for processing.

### Step 2 — Check CI status for each repo

For each repo, check the latest CI workflow run status:

```bash
gh run list --repo ansible-collections/cisco.ios --workflow tests.yml \
  --json status,conclusion,headBranch,createdAt --limit 5
```

Note any repos where the main branch CI is currently failing — this feeds
into cross-collection signal detection in Step 5.

### Step 3 — Categorize every item

Examine each issue/PR title, labels, and body to assign a category:

| Category | Base Severity | Rationale |
|---|---|---|
| Bug report | **Major** | User-facing issue, needs investigation |
| Downstream fix | **Major** | Upstream breakage actively affecting this collection |
| New feature PR | **Minor** | No urgency unless tied to release deadline |
| Test infrastructure | **Minor** | Strategic work enabling CI reliability |
| Chore / CI / Modernization | **Trivial** | No functional change, auto-merge candidate if CI green |

**Heuristics for categorization:**

- Label `bug` or title contains "fix", "broken", "error" → Bug report
- Title references another collection's PR/issue or "bump dependency" → Downstream fix
- Label `enhancement` or `feature` or title contains "add support" → New feature PR
- Title mentions "test", "molecule", "mock", "integration target" → Test infrastructure
- Title mentions "dependabot", "bump", "ci:", "chore:", "linting" → Chore

**Key distinction:** A Molecule/CISSHGO PR building mock-device test
scenarios is test INFRASTRUCTURE (Minor). A Dependabot bump or
pyproject.toml cleanup is a Chore (Trivial).

### Step 4 — Check for known CI failure patterns

Check whether any failing CI or reported issue matches a known pattern.
If a known pattern matches, note it in the triage output and use the
documented resolution rather than investigating from scratch.

**Pattern 1 — Galaxy version lag:**
Unit CI (`unit-galaxy` job) fails with an error already fixed in
`ansible.netcommon` or `ansible.utils` main but not yet released to Galaxy.
The `unit-galaxy` job installs the last Galaxy release, so fixes in main
don't reach it until a new release is cut.
*Resolution*: Cut a netcommon/utils release, or temporarily pin to git source.

**Pattern 2 — devel/milestone only failure:**
CI fails only on `devel` or `milestone` ansible-core versions due to an
API change or deprecation not yet adapted. Check ansible-core changelog.
*Resolution*: May be `needs_revision`; adapt to new API.

**Pattern 3 — Cross-PR dependency:**
PR passes CI independently but fails when merged due to an unmerged
dependency (e.g. a netcommon fix that this PR depends on).
*Resolution*: Merge dependencies in correct order.

**Pattern 4 — Persistent connection state leak:**
A test task sets connection options (e.g. `ansible_command_timeout`) via
`include_tasks vars:`. The persistent connection daemon caches the value
and does not reset it when the task scope ends, causing subsequent tasks
to fail with stale values.
*Resolution*: Add `ansible.builtin.meta: reset_connection` after the test.

### Step 5 — Apply severity escalators

Escalators can only raise severity, never lower it.

| Condition | Action |
|---|---|
| Bug in `ansible.netcommon` or `ansible.utils` | **Always Critical** — cascade risk |
| Data loss or security issue | **Critical** |
| Multiple collections failing with same root cause | **Critical** — cascade event |

### Step 6 — Detect cross-collection signals

If a bug or failing CI is in `ansible.netcommon` or `ansible.utils`:

- List all downstream collections importing the affected code
- Check if their CI is currently failing (from Step 2 data)
- If multiple collections failing → cascade event
- Priority action: fix in netcommon/utils → cut release → re-trigger downstream CI

Dependency chain:

```
ansible.netcommon ──→ cisco.ios, cisco.iosxr, cisco.nxos,
                      arista.eos, junipernetworks.junos,
                      cisco.asa, vyos.vyos
ansible.utils ────→ (same downstream consumers)
```

### Step 7 — Generate structured output

Save two files:

1. **`triage-report-YYYY-MM-DD.json`** — structured triage data (see JSON Output Schema)
2. **`triage-report-YYYY-MM-DD.md`** — human-readable markdown summary

The JSON file is the primary output — it can be loaded by a separate
dashboard frontend or consumed by other tools. The markdown file is for
quick human review.

### Step 8 — Present results

Share both file links and a brief summary: total items, breakdown by
severity, any critical items or cross-collection signals that need
immediate attention.

---

## Direct Mode Steps

### Step 1 — Identify collection and component

Determine which collection, which module/plugin, and what connection type.
If a GitHub URL is provided, fetch the issue or PR details:

```bash
gh issue view <number> --repo ansible-collections/<collection> --json title,body,labels,comments
```

or:

```bash
gh pr view <number> --repo ansible-collections/<collection> --json title,body,labels,files,statusCheckRollup
```

### Step 2 — Check for known CI failure patterns

Check whether the failure matches a known pattern (see Step 4 in scan
mode). If a known pattern matches, document it and skip to resolution.

### Step 3 — Cross-collection dependency check

If the bug is in `ansible.netcommon` or `ansible.utils`, check the
dependency chain (same as scan mode Step 6).

### Step 4 — Apply severity escalators

Same table as scan mode Step 5.

### Step 5 — Produce triage report

Use the Output Format below.

---

## Output Format

Every triage produces this structured report:

```markdown
## Network Collection Triage Report

**Date**: [date]
**Mode**: [Scan / Direct]

### Issue
[GitHub issue URL or CI failure link]

### Collection: [e.g. cisco.ios]
### Component: [module name, plugin, or CI infrastructure]
### Ansible Version: [e.g. stable-2.19 / devel]
### Connection Type: [network_cli / netconf / httpapi]

### Category
[Downstream fix / New feature / Bug report / Chore-CI / Test improvement]

### Severity: [Critical / Major / Minor / Trivial]
[Justification, including any escalators applied]

### Known Pattern Match
[Matched pattern name, OR "No known pattern — new issue"]

### Cross-Collection Impact
[None / List of affected collections / Cascade event detected]

### Root Cause
[Technical explanation if identified]

### Recommended Resolution
[Specific action: cut release, fix in PR #N, add meta: reset_connection, etc.]
```

---

## JSON Output Schema

The JSON output file follows this structure. A separate dashboard frontend
can load this file to render a visual report.

```json
{
  "metadata": {
    "date": "2026-05-20",
    "mode": "scan",
    "period_days": 14,
    "collections_scanned": ["cisco.ios", "cisco.iosxr", "..."],
    "skill_version": "1.0"
  },
  "summary": {
    "total_items": 11,
    "by_type": { "pull_request": 8, "issue": 3 },
    "by_severity": { "critical": 1, "major": 3, "minor": 5, "trivial": 2 },
    "by_category": { "bug": 2, "downstream_fix": 3, "feature": 2, "test_infra": 2, "chore": 2 },
    "cross_collection_signals": 1
  },
  "items": [
    {
      "number": 1,
      "github_url": "https://github.com/ansible-collections/cisco.ios/pull/1325",
      "type": "pull_request",
      "title": "...",
      "collection": "cisco.ios",
      "component": "ios_vlans",
      "category": "downstream_fix",
      "severity": "major",
      "severity_justification": "...",
      "escalators_applied": [],
      "known_pattern_match": null,
      "cross_collection_impact": "none",
      "root_cause": "...",
      "recommended_action": "..."
    }
  ],
  "signals": [
    {
      "type": "cascade",
      "title": "netcommon breakage affecting 3 collections",
      "description": "...",
      "affected_collections": ["cisco.ios", "cisco.iosxr", "arista.eos"]
    }
  ],
  "priority_actions": [
    {
      "priority": "critical",
      "description": "Cut ansible.netcommon release to unblock downstream CI",
      "related_items": [1, 5]
    }
  ]
}
```

Generate JSON for scan mode always. For direct mode, output the single
item's triage report in markdown (using the Output Format above) unless
the user specifically asks for JSON.

---

## Error Handling

- **`gh` not authenticated**: Run `gh auth status`. If not logged in, inform
  user to run `gh auth login` and stop.
- **Rate limiting**: GitHub API has rate limits. If hitting limits during scan
  mode, space out requests or reduce the repo list to critical collections first
  (netcommon, utils, ios, iosxr, nxos, eos).
- **Empty results**: If no open bugs or PRs are found for a repo, skip it
  silently. If ALL repos return empty, report "No open items found across
  network collections" and confirm the time window.
- **Repo not found**: If `gh` returns a 404 for a repo, skip it and note
  the skip in the output. The repo may have been renamed or archived.
