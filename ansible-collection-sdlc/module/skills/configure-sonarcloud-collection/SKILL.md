---
name: configure-sonarcloud-collection
description: >-
  Adds SonarCloud (SonarQube Cloud) static analysis to an Ansible collection repo:
  sonar-project.properties, GitHub Actions scanner workflow, XML coverage for Sonar,
  and contributor-facing docs. Use when onboarding SonarCloud, wiring CI secrets,
  producing coverage.xml, or mirroring ansible-collections setups like amazon.aws.
---

# Configure SonarCloud for an Ansible Collection

Guide repository changes so SonarCloud can analyze Python/plugins/tests and display coverage. Complements `sonarcloud-analysis` (read findings) and `implement-sonarcloud-fixes` (fix findings)—run those **after** the project exists on SonarCloud and CI uploads analysis.

## Purpose

Produce consistent, reviewable setup across collections:

- Root `sonar-project.properties` aligned with org project key and layout
- A workflow that runs the SonarScanner with the org token
- `coverage.xml` at the repository root for `sonar.python.coverage.reportPaths`
- Documentation (README section or dedicated doc) for Sonar/coverage expectations

## When to Invoke

TRIGGER when the user asks to:

- Add, enable, or configure SonarCloud / SonarQube Cloud for a collection
- Create `sonar-project.properties` or Sonar CI workflow from scratch
- Wire pytest/tox output to Sonar coverage
- Document Sonar or coverage thresholds for contributors

DO NOT TRIGGER when:

- The user only wants to **view** Sonar issues on an already-configured project (use `sonarcloud-analysis`)
- The user only wants to **fix** existing Sonar findings (use `implement-sonarcloud-fixes`)

## Prerequisites (human / org)

Before CI can succeed end-to-end:

1. **SonarCloud project** exists and is linked to the GitHub repo (Analyze new project → pick repo). Project key on SonarCloud **must match** `sonar.projectKey` in `sonar-project.properties`.
2. **Org-level secret** available to workflows: for `ansible-collections`, GitHub Actions use  
   `SONAR_TOKEN: ${{ secrets.ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT }}`  
   (Fork PRs do not receive org/repo secrets—see below.)
3. **Coordinate access** with collection/Sonar org admins if the project is missing or mis-keyed (internal Ansible channels/sponsor as applicable).

Use `get-upstream-info` to derive `UPSTREAM_ORG`, repo name, and the SonarCloud-style project key (typically `ORG_COLLECTIONNAME` with dots in the collection name replaced—e.g. `ansible-collections/amazon.aws` → `ansible-collections_amazon.aws`).

## Fork and secret limitation

GitHub **does not** expose secrets to workflows triggered by pull requests **from forks**. Plan accordingly:

- Sonar jobs that need `SONAR_TOKEN` should run on **push** to default branch and on PRs **from the same repository** (internal contributors), not from forks—or accept that fork PRs skip Sonar until merge.

Document this in the workflow comments or contributor docs.

## Workflow for the agent

### 1. Inventory the repo

- Read `galaxy.yml` for collection name (namespace.name).
- Locate existing test workflows: `.github/workflows/tests.yml`, `units.yml`, `ansible-test`-based jobs, or `tox`.
- Confirm whether unit tests already emit XML coverage; many collections only emit HTML via tox/pytest.

### 2. Add `sonar-project.properties` at the repository root

Tune paths to match the tree (`plugins/`, `tests/unit`, `tests/integration`). Minimum pattern for collections (adjust names):

```properties
# SonarCloud project configuration for <collection.name>
# Complete documentation: https://docs.sonarqube.org/latest/analysis/analysis-parameters/

sonar.projectKey=<ORG>_<collection.name with dots as needed>
sonar.organization=<sonarcloud org slug, e.g. ansible-collections>
sonar.sources=.
sonar.projectName=<collection.name>

sonar.python.coverage.reportPaths=coverage.xml

sonar.tests=tests/unit,tests/integration
sonar.python.version=<match CI primary Python, e.g. 3.13>
sonar.newCode.referenceBranch=main

sonar.exclusions=tests/**,.tox/**
```

**Consistency rule:** `sonar.projectKey` must equal the SonarCloud project key exactly.

### 3. Add a SonarCloud GitHub Actions workflow

- Typical filename: `.github/workflows/sonarcloud.yml` or `sonar_checks.yml` (match sibling repos if an org convention exists).
- Job must checkout the repo, optionally **produce `coverage.xml`** (step 4), then run SonarScanner (official SonarCloud GitHub Action or `sonar-scanner` CLI) with:

```yaml
env:
  SONAR_TOKEN: ${{ secrets.ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT }}
```

Use the **same default branch** name in `sonar.newCode.referenceBranch` as in GitHub (`main` vs `devel`).

Reference implementations: search sibling collections or community examples (e.g. amazon.aws Sonar onboarding PRs) for matrix/checkout patterns.

### 4. Ensure `coverage.xml` exists at repo root before Sonar runs

`sonar-project.properties` expects **`coverage.xml` at the repository root** unless paths are changed.

**Option A — Workflow job:** Run unit tests with XML report directly, e.g. pytest with `--cov-report xml:coverage.xml` at repo root, then run Sonar in the same workflow (or upload artifact between jobs).

**Option B — tox:** Add `--cov-report xml:coverage.xml` (or equivalent) to the relevant tox env; copy or configure output so the final file is **`coverage.xml` at repo root** before the Sonar step.

Until XML coverage is produced, SonarCloud still reports issues and duplication, but **coverage stays empty** in the UI.

### 5. Integrate with existing test workflows

Update the primary unit-test workflow (may be named `tests.yml`, `units.yml`, etc.) so CI reliably generates coverage used by Sonar **without** duplicating unnecessary work—often a **second focused PR** after the minimal Sonar workflow merges (matches common staged rollout).

### 6. Documentation

Add either:

- A **README** section covering SonarCloud, coverage expectation (~80% codebase target where policy applies), and fork secret behavior, or  
- A dedicated **`sonarcloud.md`** (or similar) linked from the README.

### 7. Validate locally (optional but recommended)

See [reference.md](reference.md) for SonarScanner CLI install, `SONAR_TOKEN`, and `sonar-scanner` invocation from repo root to catch misconfiguration before CI.

## Quality expectations

Where org policy applies, collections should **aim for ~80%** coverage across the codebase; Sonar setup makes coverage visible—raising coverage is separate work.

## Integration with other skills

| Phase | Skill |
|------|--------|
| Derive org/repo/Sonar key | `get-upstream-info` |
| After CI uploads analysis | `sonarcloud-analysis` |
| Fix findings | `implement-sonarcloud-fixes` |

## Checklist (copy for PR description)

```
- [ ] sonar-project.properties at repo root; projectKey matches SonarCloud UI
- [ ] Sonar workflow uses org SONAR_TOKEN secret (and triggers documented for forks)
- [ ] coverage.xml produced at repo root before Sonar step (or staged follow-up PR)
- [ ] Test workflow updated if needed for XML coverage
- [ ] README or sonarcloud.md explains Sonar + coverage for contributors
```
