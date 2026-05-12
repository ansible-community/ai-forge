# SonarCloud workflow templates (ansible-collections org)

These files are **canonical copies** for Ansible collections under the **ansible-collections** GitHub org.

| File | Role |
| ---- | ---- |
| [sonar-project.properties.template](sonar-project.properties.template) | Per-repo Sonar keys, paths, Python version |
| [sonarcloud.workflow_run.yml.template](sonarcloud.workflow_run.yml.template) | Sonar after **`workflow_run`** on workflow **`all_green`** completes |
| [sonarcloud.workflow_call.yml.template](sonarcloud.workflow_call.yml.template) | Reusable Sonar job; caller runs on **`pull_request`** / **`push`** |

**Do not edit structure, action SHAs, job names, or secret names** in the workflow YAML when applying
them to a collection unless **GitHub / Sonar org maintainers** approve a coordinated change across repos.

## Choosing `workflow_run` vs `workflow_call`

| | [workflow_run](sonarcloud.workflow_run.yml.template) | [workflow_call](sonarcloud.workflow_call.yml.template) |
| - | - | - |
| **Trigger** | Separate workflow runs when **`all_green`** finishes | Invoked from caller with `uses: ./.github/workflows/sonarcloud.yml` |
| **Checkout** | `ref: ${{ github.event.workflow_run.head_sha }}` | PR head SHA or `github.sha` from caller event |
| **Coverage download** | [dawidd6/action-download-artifact](https://github.com/dawidd6/action-download-artifact) with **`pattern: coverage*`** across the triggering run | [actions/download-artifact@v4](https://github.com/actions/download-artifact) with **`name: coverage`** (one artifact) |
| **Extra permissions** | `actions: read` (cross-workflow artifact read) | Not required for that download pattern |
| **PR metadata** | Shell + **`gh`** when `workflow_run.event == pull_request` | Native `github.event.pull_request.*` on PR callers |
| **Secrets** | Repo/org secret in job `env` | Caller passes `secrets: inherit` (or maps `ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT` into the called workflow) |

Use **`workflow_call`** when org policy avoids **`workflow_run`** + **`head_sha`** checkout (e.g. Sonar security hotspot / quality gate). Otherwise **`workflow_run`** matches the common **amazon.aws**-style aggregator pattern.

## What to copy where

| Template | Destination | Allowed edits |
| -------- | ----------- | ------------- |
| [sonar-project.properties.template](sonar-project.properties.template) | Repo root `sonar-project.properties` | Replace every `__PLACEHOLDER__` per table in that file. Paths (`sonar.tests`, `sonar.exclusions`) may be tuned for tree layout **only** if SonarCloud project settings agree. |
| [sonarcloud.workflow_run.yml.template](sonarcloud.workflow_run.yml.template) | `.github/workflows/sonarcloud.yml` | **None** in YAML structure or pins. Optional: uncomment the `if:` guard on the **`finalize`** job if your org requires same-repo-only finalize (see comments in file). Upstream **`all_green`** must upload artifacts matching **`coverage*`** (e.g. `coverage.xml`, `coverage-unit.xml`). |
| [sonarcloud.workflow_call.yml.template](sonarcloud.workflow_call.yml.template) | `.github/workflows/sonarcloud.yml` (alternative) | **None** in YAML structure or pins. Caller must upload **one** artifact whose **`name:`** is exactly **`coverage`** (see header comment in template); then add a job with `uses: ./.github/workflows/sonarcloud.yml` and `secrets: inherit` after the coverage upload step. |

## Aggregator workflow name (`workflow_run` template)

The **`workflow_run`** template listens for a workflow whose **`name:`** field is exactly **`all_green`**.
Your aggregator file (often `all_green_check.yaml`) must set:

```yaml
name: all_green
```

The **`workflows:`** list in `sonarcloud.yml` uses that **display name**, not the YAML filename.

## Org secret (lookup)

For **ansible-collections** repositories, workflows should reference:

```yaml
secrets.ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT
```

CI is expected to work **without** renaming that secret. Other orgs must replace the secret name in a
**single coordinated** change approved by their admins (do not fork the template with a different
secret name per repo unless required).

## Related skills

- **`configure-sonarcloud-collection`** — when to use templates, `sonar-project.properties`, first-phase docs.
- **`configure-sonarcloud-coverage`** — `all_green`, coverage jobs, `workflow_call` vs `workflow_run`, badges.
