---
name: severity-assessor
description: >-
  Categorizes an issue or PR and assigns severity (critical/major/minor/trivial)
  with configurable escalation rules. Generic helper for any Ansible collection.
user-invocable: false
allowed-tools:
  - Bash
---

# Severity Assessor Skill

Categorize a GitHub issue or pull request and assign a triage severity level.
Designed as a reusable helper that any Ansible collection triage workflow can
invoke with its own domain-specific escalation rules.

---

## Purpose

Accept an issue or PR (by URL or pre-fetched data), classify it into one of
five categories, assign a base severity from that category, apply universal
and caller-supplied escalation rules, and return a structured assessment.

The skill contains **no domain-specific knowledge** (no collection names,
no dependency chains, no platform details). All domain context is passed in
by the calling skill via escalation rules.

---

## When to Invoke

TRIGGER when:

- Another skill or workflow needs to assign severity to a GitHub issue or PR
- Batch-processing issues in scan/triage mode and need consistent categorization
- A triage workflow delegates the "assess severity" step

DO NOT TRIGGER when:

- The caller already has a final severity and only needs formatting
- The item is not an issue or PR (e.g. a discussion, wiki page, release)
- The user asks to triage — invoke the parent triage skill instead, which
  will delegate to this skill internally

---

## Inputs

The skill accepts the following inputs from the calling skill:

### Required (one of)

**Option A — GitHub/GitLab URL:**

A single issue or PR URL. The skill fetches details via `gh`:

```bash
# For issues
gh issue view <number> --repo <owner/repo> --json number,title,body,labels,assignees,author,state,createdAt,updatedAt

# For pull requests
gh pr view <number> --repo <owner/repo> --json number,title,body,labels,assignees,author,state,createdAt,updatedAt,files,statusCheckRollup
```

**Option B — Structured data:**

Pre-fetched data provided by the caller (e.g. from a batch scan). Minimum
required fields:

| Field | Type | Description |
|---|---|---|
| `title` | string | Issue or PR title |
| `labels` | string[] | Label names attached to the item |

Optional fields that improve accuracy:

| Field | Type | Description |
|---|---|---|
| `body` | string | Issue or PR body text |
| `url` | string | GitHub/GitLab URL |
| `number` | integer | Issue or PR number |
| `repo` | string | Repository in `owner/name` format |
| `files` | string[] | Changed file paths (PRs only) |
| `state` | string | `open`, `closed`, or `merged` |
| `author` | string | GitHub username of the author |

### Optional — Escalation rules

A list of caller-supplied escalation rules. Each rule has:

| Field | Type | Description |
|---|---|---|
| `name` | string | Short label for the escalator (used in output) |
| `condition` | string | Human-readable description of when this rule fires |
| `action` | string | `"critical"`, `"major"`, `"minor"`, or `"bump+1"` |
| `reason` | string | Justification text included in the assessment |

**Action values:**

- `"critical"` / `"major"` / `"minor"` — set severity to this level (only if higher than current)
- `"bump+1"` — raise severity by one level: trivial→minor, minor→major, major→critical

The calling skill decides **whether** each rule fires based on its own
domain knowledge (dependency chains, collection metadata, customer lists).
It passes only the rules that matched.

**Example — network collection triage caller:**

```yaml
escalationRules:
  - name: shared-dependency-cascade
    condition: "Bug in ansible.netcommon confirmed breaking downstream collections"
    action: "critical"
    reason: "Confirmed cascade — CI failing in downstream collections due to netcommon change"
  - name: shared-dependency-risk
    condition: "Bug is in ansible.netcommon but downstream impact not yet confirmed"
    action: "bump+1"
    reason: "Potential cascade risk — needs downstream CI verification before full escalation"
  - name: certified-collection
    condition: "Affected collection is Red Hat certified"
    action: "bump+1"
    reason: "Higher SLA for certified content"
```

**Example — cloud collection triage caller:**

```yaml
escalationRules:
  - name: provider-api-break
    condition: "Cloud provider API breaking change confirmed affecting collection"
    action: "critical"
    reason: "Provider API change breaks existing automation until collection is patched"
  - name: shared-dependency-cascade
    condition: "Bug in amazon.aws confirmed breaking community.aws or other downstream"
    action: "critical"
    reason: "Confirmed cascade — amazon.aws is a dependency of community.aws and other cloud collections"
  - name: shared-dependency-risk
    condition: "Bug is in amazon.aws but downstream impact not yet confirmed"
    action: "bump+1"
    reason: "Potential cascade risk — needs downstream CI verification"
  - name: validated-collection
    condition: "Affected collection is Ansible validated content"
    action: "bump+1"
    reason: "Validated content has support commitments"
```

**Example — community collection triage caller:**

```yaml
escalationRules:
  - name: high-download-collection
    condition: "Affected collection has >1M monthly Galaxy downloads"
    action: "bump+1"
    reason: "High community impact due to download volume"
  - name: included-in-ansible-package
    condition: "Collection is included in the ansible community package"
    action: "bump+1"
    reason: "Breakage affects all users who install the ansible meta-package"
```

**Note:** The calling skill is responsible for checking whether a shared-dependency
bug actually breaks downstream collections (e.g. by inspecting downstream CI
status). A bug in a shared collection does **not** automatically warrant Critical —
only confirmed downstream breakage does. Unconfirmed risk should use `bump+1` to
flag for investigation.

---

## Context Profiles

Pre-built and custom escalation contexts live in the `contexts/` directory.
Each file defines the collections in scope and the domain-specific escalation
rules for a collection type.

### Available profiles

| File | Domain | Collections |
|---|---|---|
| `contexts/network.yaml` | Network platform collections | netcommon, ios, iosxr, nxos, eos, ... |
| `contexts/cloud.yaml` | Cloud provider collections | amazon.aws, community.aws, google.cloud, ... |
| `contexts/community.yaml` | Community-maintained collections | community.general, community.crypto, ... |

### Creating a new profile

1. Copy `contexts/_template.yaml` to a new file (e.g. `contexts/security.yaml`)
2. Fill in `name`, `description`, and the `collections` list
3. Add escalation rules specific to your domain
4. The calling triage skill loads the appropriate context file and passes
   matched rules to the severity-assessor at invocation time

### How context files are used

The severity-assessor skill does **not** read context files directly. The
calling skill (e.g. a triage workflow) is responsible for:

1. Loading the relevant context file for the repositories being triaged
2. Evaluating each escalation rule's `condition` against the current issue
3. Passing only the **matched rules** to severity-assessor via the
   `escalationRules` input

This keeps the severity-assessor generic while giving each team a
versioned, reviewable place to maintain their escalation policy.

---

## Workflow

### Step 1 — Resolve input

If the caller provides a URL:

1. Parse the URL to extract `owner/repo` and issue/PR number
2. Detect whether it is an issue or PR from the URL path (`/issues/` vs `/pull/`)
3. Fetch details via `gh` (see commands in Inputs section above)
4. Extract `title`, `body`, `labels`, and other fields from the response

If the caller provides structured data, use it directly.

If both are provided, prefer structured data (it avoids an API call).

### Step 2 — Categorize

Examine the title, labels, and body to assign exactly one category.
Apply heuristics in priority order (first match wins):

| Priority | Heuristic | Category |
|---|---|---|
| 1 | Label `bug`, or title contains "fix", "broken", "error", "crash", "regression", "traceback" | **Bug report** |
| 2 | Title references another collection's PR/issue, or contains "bump dependency", "upstream" | **Downstream fix** |
| 3 | Label `enhancement` or `feature`, or title contains "add support", "new module", "new plugin" | **Feature** |
| 4 | Title contains "test", "molecule", "mock", "integration target", "test fixture" | **Test infrastructure** |
| 5 | Title contains "dependabot", "bump", "ci:", "chore:", "linting", "pre-commit", "renovate" | **Chore** |
| 6 | *(no match)* | **Bug report** (default — unclassified items get investigation) |

**Key distinction:** A PR building test fixtures, mock responses, or
integration test targets is **test infrastructure** (Minor). A Dependabot
bump, pyproject.toml cleanup, or CI config change is a **Chore** (Trivial).

### Step 3 — Assign base severity

Look up the category in this table:

| Category | Base Severity | Rationale |
|---|---|---|
| Bug report | **Major** | User-facing issue, needs investigation |
| Downstream fix | **Major** | Upstream breakage actively affecting this collection |
| Feature | **Minor** | No urgency unless tied to release deadline |
| Test infrastructure | **Minor** | Strategic work enabling CI reliability |
| Chore | **Trivial** | No functional change, auto-merge candidate if CI green |

Record this as `baseSeverity`.

### Step 4 — Apply escalators

Escalators can **only raise** severity, never lower it. The severity order
from lowest to highest is: `trivial` < `minor` < `major` < `critical`.

**Built-in universal escalators** (always applied):

| Condition | Action |
|---|---|
| Title or body indicates data loss (e.g. "data loss", "data corruption", "destroys", "wipes") | **Critical** |
| Title or body indicates security issue (e.g. "CVE", "vulnerability", "injection", "credential leak", label `security`) | **Critical** |

**Caller-supplied escalators:**

Apply each rule from the `escalationRules` input. For each:

1. The calling skill has already determined the rule matches — apply its action
2. If `action` is a severity level (`critical`, `major`, `minor`), set severity to that level only if it is higher than the current severity
3. If `action` is `"bump+1"`, raise the current severity by one level (cap at `critical`)
4. Record the escalator name and reason in the `escalatorsApplied` list

### Step 5 — Return structured result

Return the assessment as a structured object matching the
`severity-assessment.schema.json` schema (see Schema section below).

**Display format** for human-readable output:

```markdown
### Severity Assessment

**Category**: [category]
**Severity**: [severity] (base: [baseSeverity])
**Escalators applied**: [list or "None"]

**Justification**: [explanation of why this category and severity were assigned,
including which heuristics matched and which escalators fired]

**Source**: [url or "Provided by caller"]
```

---

## Output Schema

The structured output conforms to `schema/severity-assessment.schema.json`
in this skill directory. Key fields:

| Field | Type | Description |
|---|---|---|
| `category` | enum | `bug`, `downstream-fix`, `feature`, `test-infra`, `chore` |
| `severity` | enum | `critical`, `major`, `minor`, `trivial` — final severity after escalation |
| `baseSeverity` | enum | Severity before escalation (from category table) |
| `escalatorsApplied` | array | List of `{ name, reason }` for each escalator that fired |
| `justification` | string | Human-readable explanation of the assessment |
| `source` | object | `{ url, title, labels, number, repo }` — item that was assessed |

---

## Integration with Other Skills

This skill is designed to be invoked by any Ansible collection triage or
workflow skill. The calling skill owns domain knowledge (which collections
are shared dependencies, which are certified, what the dependency chains
look like). This skill owns the categorization logic and severity math.

**In a network collection triage skill:**

```
1. Gather issues via triager or gh CLI
2. For each issue:
   a. Determine if the issue is in a shared dependency (netcommon, utils, pylibssh)
   b. If yes, check downstream CI status to confirm or rule out cascade
   c. Invoke severity-assessor with structured data + matched escalation rules:
      - Confirmed downstream breakage → Critical
      - Unconfirmed shared-dependency risk → bump+1
      - Certified collection affected → bump+1
      - Multiple collections failing same root cause → Critical
3. Use returned severity to populate triage report
```

**In a cloud collection triage skill:**

```
1. Gather issues from amazon.aws, community.aws, google.cloud,
   azure.azcollection, etc.
2. For each issue:
   a. Check if it relates to a provider API/SDK change
   b. Determine if the affected collection is a shared dependency
      (e.g. amazon.aws is upstream of community.aws)
   c. Invoke severity-assessor with structured data + matched escalation rules:
      - Provider API breaking change confirmed → Critical
      - Shared dependency confirmed breaking downstream → Critical
      - Shared dependency risk unconfirmed → bump+1
      - Validated content affected → bump+1
3. Use returned severity for sprint prioritization
```

**In a community collection triage skill:**

```
1. Gather issues from community.general, community.crypto,
   community.docker, etc.
2. For each issue:
   a. Check collection download stats and inclusion in ansible package
   b. Invoke severity-assessor with structured data + matched escalation rules:
      - Collection included in ansible package → bump+1
      - High download volume (>1M/month) → bump+1
      - Breaking change in widely-used module → Critical
3. Use returned severity for maintainer review queue
```

**In a single-issue triage (direct mode):**

```
1. Receive GitHub issue URL from user
2. Invoke severity-assessor with the URL
3. Optionally pass domain escalation rules
4. Present the structured assessment to the user
```

---

## Error Handling

### `gh` CLI not available

```
Error: gh CLI is not installed or not in PATH.
Install it from: https://cli.github.com/
```

### `gh` not authenticated

```
Error: gh CLI is not authenticated.
Run 'gh auth login' to authenticate with GitHub.
```

### URL not resolvable

If `gh issue view` or `gh pr view` returns a 404:

```
Error: Could not fetch [URL]. The issue or PR may not exist,
or you may not have access to the repository.
```

### Ambiguous categorization

If multiple heuristics match, use the **first match** in priority order
(Step 2 table). Do not attempt to merge categories — each item gets
exactly one category.

### Missing required input

If neither a URL nor structured data with at least `title` and `labels`
is provided:

```
Error: severity-assessor requires either a GitHub/GitLab URL or
structured data with at least 'title' and 'labels' fields.
```

---

## Example Usage

### Example 1: Cloud collection — bug report with no escalation

**Input:**
```json
{
  "title": "ec2_instance module broken after Ansible 2.19 upgrade",
  "labels": ["bug"],
  "repo": "ansible-collections/amazon.aws"
}
```

**Output:**
```json
{
  "category": "bug",
  "severity": "major",
  "baseSeverity": "major",
  "escalatorsApplied": [],
  "justification": "Matched category 'bug' via label 'bug'. Base severity Major. No escalators applied.",
  "source": {
    "title": "ec2_instance module broken after Ansible 2.19 upgrade",
    "labels": ["bug"],
    "repo": "ansible-collections/amazon.aws"
  }
}
```

### Example 2: Community collection — security issue escalated to Critical

**Input:**
```json
{
  "title": "Credential leak in debug output when verbosity >= 3",
  "labels": ["bug", "security"],
  "repo": "ansible-collections/community.general",
  "body": "When running with -vvv, the module logs the API token in plain text..."
}
```

**Output:**
```json
{
  "category": "bug",
  "severity": "critical",
  "baseSeverity": "major",
  "escalatorsApplied": [
    {
      "name": "security-issue",
      "reason": "Title or labels indicate a security vulnerability (label: security, keyword: credential leak)"
    }
  ],
  "justification": "Matched category 'bug' via label 'bug'. Base severity Major. Escalated to Critical: security issue detected.",
  "source": {
    "title": "Credential leak in debug output when verbosity >= 3",
    "labels": ["bug", "security"],
    "repo": "ansible-collections/community.general"
  }
}
```

### Example 3: Network collection — chore with certified collection escalation

**Input:**
```json
{
  "title": "Bump netcommon dependency to 7.1.0",
  "labels": [],
  "repo": "ansible-collections/cisco.ios"
}
```

**Caller-supplied escalation rules:**
```json
[
  {
    "name": "certified-collection",
    "condition": "cisco.ios is Red Hat certified",
    "action": "bump+1",
    "reason": "Higher SLA for certified content"
  }
]
```

**Output:**
```json
{
  "category": "chore",
  "severity": "minor",
  "baseSeverity": "trivial",
  "escalatorsApplied": [
    {
      "name": "certified-collection",
      "reason": "Higher SLA for certified content"
    }
  ],
  "justification": "Matched category 'chore' via title keyword 'bump'. Base severity Trivial. Escalated to Minor: certified collection bump+1.",
  "source": {
    "title": "Bump netcommon dependency to 7.1.0",
    "labels": [],
    "repo": "ansible-collections/cisco.ios"
  }
}
```

### Example 4: Cloud collection — confirmed cascade escalation

**Input:**
```json
{
  "title": "boto3 session handling error causes all AWS modules to fail",
  "labels": ["bug"],
  "repo": "ansible-collections/amazon.aws",
  "body": "After upgrading boto3 to 1.35.0, all modules that create sessions raise TypeError..."
}
```

**Caller-supplied escalation rules:**
```json
[
  {
    "name": "shared-dependency-cascade",
    "condition": "Bug in amazon.aws confirmed breaking community.aws and community.docker",
    "action": "critical",
    "reason": "Confirmed cascade — CI failing in community.aws and amazon.cloud_trail due to session change"
  }
]
```

**Output:**
```json
{
  "category": "bug",
  "severity": "critical",
  "baseSeverity": "major",
  "escalatorsApplied": [
    {
      "name": "shared-dependency-cascade",
      "reason": "Confirmed cascade — CI failing in community.aws and amazon.cloud_trail due to session change"
    }
  ],
  "justification": "Matched category 'bug' via label 'bug'. Base severity Major. Escalated to Critical: confirmed downstream cascade.",
  "source": {
    "title": "boto3 session handling error causes all AWS modules to fail",
    "labels": ["bug"],
    "repo": "ansible-collections/amazon.aws"
  }
}
```

### Example 5: Community collection — feature in high-impact collection

**Input:**
```json
{
  "title": "Add support for podman pod resource limits",
  "labels": ["enhancement"],
  "repo": "ansible-collections/community.docker"
}
```

**Caller-supplied escalation rules:**
```json
[
  {
    "name": "included-in-ansible-package",
    "condition": "community.docker is included in the ansible community package",
    "action": "bump+1",
    "reason": "Breakage affects all users who install the ansible meta-package"
  }
]
```

**Output:**
```json
{
  "category": "feature",
  "severity": "major",
  "baseSeverity": "minor",
  "escalatorsApplied": [
    {
      "name": "included-in-ansible-package",
      "reason": "Breakage affects all users who install the ansible meta-package"
    }
  ],
  "justification": "Matched category 'feature' via label 'enhancement'. Base severity Minor. Escalated to Major: collection is part of ansible package bump+1.",
  "source": {
    "title": "Add support for podman pod resource limits",
    "labels": ["enhancement"],
    "repo": "ansible-collections/community.docker"
  }
}
```
