# Ansible Collection Development

Module provides skills for Ansible collection development workflows: conventional commits, PR review, releases, and testing.

## When to Use

- **commit skill**: Use the `commit` skill when you want to create a conventional commit
  with FQCN scopes for Ansible collection content.
  Invoke when the user asks to "commit", "create a commit", or "git commit".

- **pr-review skill**: Use the `pr-review` skill to review pull requests and code changes
  against project standards and the Ansible Collection Review Checklist.
  Invoke when asked to review a PR, patch, diff, or set of code changes.

- **release skill**: Use the `release` skill to guide the release of an Ansible collection.
  Automatically determines the next version from changelog fragments
  and outputs step-by-step instructions.
  Invoke when asked to release, publish, or tag a new collection version.

- **run-tests skill**: Use the `run-tests` skill to run or write sanity, unit, and integration tests using `ansible-test`. Invoke when asked to run, check, or write tests for a module or utility.

- **sonarcloud-analysis skill**: Use the `sonarcloud-analysis` skill to fetch and analyse SonarCloud issues and technical debt for Ansible collections.
  Invoke when asked to check, review, or analyse SonarCloud results, code smells, security hotspots, or static analysis findings.

### Utility Skills

- **get-pr-number skill**: Helper skill that determines the pull request number for a branch. Used internally by other skills.

- **get-upstream-info skill**: Helper skill that determines upstream repository information and service identifiers (GitHub/GitLab). Used internally by other skills.

## Configuration

**Optional Dependencies:**

- `antsibull-changelog` - Used by the release skill for changelog generation
- `gh` CLI - Used by the release skill for creating GitHub releases and PRs, and by the sonarcloud-analysis skill for PR detection
- `ansible-test` - Used by the run-tests skill
- `curl` - Used by the sonarcloud-analysis skill for fetching static analysis results

**Required Context:**

- The collection must reside at `ansible_collections/<namespace>/<name>/` (relative to a directory on `ANSIBLE_COLLECTIONS_PATHS`) for imports to resolve correctly
- Collection identity (namespace, name, version) is read from `galaxy.yml`

## Notes

- All skills follow Ansible collection conventions and best practices
- The commit skill uses Conventional Commits 1.0.0 standard
- The release skill includes human confirmation gates at critical steps
- The pr-review skill produces structured reports with blockers/warnings/suggestions and a verdict
