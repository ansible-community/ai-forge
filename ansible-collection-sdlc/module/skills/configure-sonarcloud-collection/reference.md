# SonarCloud setup reference

Supplementary detail for `configure-sonarcloud-collection`. Read when validating locally or explaining admin steps.

## SonarCloud web UI

1. Sign in at https://sonarcloud.io with GitHub.
2. **Analyze new project** → select the collection repository.
3. Set the **project key** to match `sonar.projectKey` in `sonar-project.properties` (must match exactly).

Org admins create projects and manage tokens; coordinate through your team’s usual channels if the project does not exist or keys conflict.

## ansible-collections org token in CI

```yaml
env:
  SONAR_TOKEN: ${{ secrets.ANSIBLE_COLLECTIONS_ORG_SONAR_TOKEN_CICD_BOT }}
```

Secret is configured at **organization** level; repository workflows reference it by name.

## Run SonarScanner locally

Useful to validate `sonar-project.properties` and layout before relying on CI.

1. Install [SonarScanner CLI](https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/) and put `bin` on `PATH`.
2. Create a user token in SonarCloud (**My Account → Security**) and export:

```bash
export SONAR_TOKEN=<token>
```

3. From the **repository root** (where `sonar-project.properties` lives):

```bash
sonar-scanner -Dsonar.projectBaseDir=. -Dsonar.host.url=https://sonarcloud.io
```

4. Check the end of the log for errors. Results appear under the project on SonarCloud.

## Staged PRs

Common rollout:

1. **First PR:** `sonar-project.properties` + minimal Sonar workflow (scanner runs; coverage may be absent initially).
2. **Second PR:** tox/pytest/workflow changes so `coverage.xml` is produced at repo root + README/doc updates.

This matches workflows where unit jobs historically only produced HTML coverage reports.

## Example community reference

Concrete file-level examples appear in public collection PRs (e.g. amazon.aws SonarCloud onboarding). Use them as templates; adapt paths and Python versions to each collection.
