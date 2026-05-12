# SonarCloud coverage reference

Public references for `configure-sonarcloud-coverage`.

## Example SonarCloud project (kubernetes.core)

- [Project overview (SonarCloud)](https://sonarcloud.io/project/overview?id=ansible-collections_kubernetes.core)

## Canonical templates in this module

- **`module/skills/sonarcloud-workflow-templates/README.md`** — index of **`sonarcloud.workflow_run.yml.template`** vs **`sonarcloud.workflow_call.yml.template`** (artifact **`coverage*`** vs single **`coverage`**, **`dawidd6/action-download-artifact`** vs **`actions/download-artifact`**, permissions).

## Example merged PR (coverage + workflow_run)

- [ansible-collections/amazon.aws#2871](https://github.com/ansible-collections/amazon.aws/pull/2871) —
  describes adding a **coverage** job to **`all_green`**, uploading **`coverage*`** artifacts, and a **Sonar**
  workflow triggered by **`workflow_run`** that downloads artifacts and passes
  **`sonar.python.coverage.reportPaths`**.
- Reference workflows in that repository:
  [all_green_check.yml](https://github.com/ansible-collections/amazon.aws/blob/main/.github/workflows/all_green_check.yml),
  [sonarcloud.yml](https://github.com/ansible-collections/amazon.aws/blob/main/.github/workflows/sonarcloud.yml).

## Documentation

- [SonarQube Cloud — CI-based analysis](https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/ci-based-analysis)
- [Analysis parameters](https://docs.sonarqube.org/latest/analysis/analysis-parameters/) (includes Python coverage paths)
- [workflow_run event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_run)
- [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)

## ansible-test coverage CLI

From collection root, after `ansible-test units --coverage`:

- `ansible-test coverage combine …`
- `ansible-test coverage xml …`

XML output is typically under `tests/output/reports/`; confirm with `ansible-test coverage xml -e` if needed.
