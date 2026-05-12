# Ansible Collection SDLC Module

A Lola module for the full software development lifecycle of Ansible collections: conventional commits, changelog
fragments, PR reviews, releases, and testing.  Streamlines day-to-day development workflows from code commit to
production release.

## Installation

```bash
# Install Lola package manager
pip install lola-cli

# Register the module from GitHub
lola mod add https://github.com/ansible-community/ai-forge/ansible-collection-sdlc

# Or clone and register locally
git clone https://github.com/ansible-community/ai-forge.git
lola mod add ./ai-forge/ansible-collection-sdlc

# Install to Claude Code
lola install ansible-collection-sdlc -a claude-code

# Install to Cursor
lola install ansible-collection-sdlc -a cursor

# Install to other assistants
lola install ansible-collection-sdlc -a gemini-cli
lola install ansible-collection-sdlc -a opencode
```

## Components

### Skills

- **changelog-fragment** - Create or update changelog fragments for documenting changes with automatic change analysis
- **commit** - Create conventional commits with FQCN scopes for Ansible collection content
- **configure-sonarcloud-collection** - Add SonarCloud configuration: `sonar-project.properties`, CI
  workflow, coverage.xml, contributor docs, and assistant-safe fork/secret guidance (see skill Security
  section)
- **configure-sonarcloud-coverage** - Second-phase SonarCloud coverage: XML reports in CI,
  `workflow_run`/artifacts, aggregator gates, README badges (see companion to configure-sonarcloud-collection)
- **sonarcloud-workflow-templates** - Canonical `sonar-project.properties` and Sonar workflow YAML under
  `module/skills/sonarcloud-workflow-templates/` for **ansible-collections** org parity (see that folder’s
  `README.md` for `workflow_run` vs reusable `workflow_call` and artifact naming)
- **create-branch** - Create feature branches following project conventions with proper fork workflow setup
- **create-pr** - Create draft pull requests with pre-flight checks, changelog validation, and automated formatting
- **implement-sonarcloud-fixes** - Implement fixes for SonarCloud issues with testing and PR creation
- **pr-review** - Review PRs against project standards and the Ansible Collection Review Checklist
- **release** - Guide collection releases with automatic version detection from changelog fragments
- **remove-deprecations** - Find and remediate overdue deprecation warnings with guided removal workflow
- **run-tests** - Run and write sanity, unit, and integration tests using ansible-test
- **sonarcloud-analysis** - Fetch and analyse SonarCloud issues for projects or pull requests
- **next-release** - Calculate next patch/minor/major release versions for version_added tags following SemVer

#### Helper Skills

- **current-release** - Fetch current release version from git tags/branches or galaxy.yml (used by other skills)
- **get-branch-changes** - Determine merge-base and changed files for current branch, avoiding unrelated changes when behind target (used by other skills)
- **get-pr-action-results** - Get GitHub Actions/GitLab CI results for PRs and branches, analyze failures, and suggest fixes (used by other skills)
- **get-pr-number** - Determine pull request number for a branch (used by other skills)
- **get-upstream-info** - Determine upstream repository information and service identifiers (used by other skills)

### Commands

- **/check-pr-actions** - Check GitHub Actions/GitLab CI status and analyze failures
- **/check-pr-sonarcloud** - Check SonarCloud analysis results for the current pull request

### Agents

None currently defined.

### MCP Servers

None currently defined.

## Development

This module follows the Lola module structure:

```
ansible-collection-sdlc/
├── README.md           # This file
└── module/             # Lola-importable content
    ├── AGENTS.md       # Module-level instructions
    ├── skills/         # Skill folders with SKILL.md (includes sonarcloud-workflow-templates/ for canonical CI YAML)
    ├── commands/       # Slash command .md files
    ├── agents/         # Subagent .md files
    └── mcps.json       # MCP server configuration
```

## Dependencies

- **antsibull-changelog** (optional) - Used for changelog generation
- **gh CLI** (optional) - Used for GitHub/GitLab operations (PRs, releases, upstream detection)
- **ansible-test** - Used for running sanity, unit, and integration tests
- **curl** (optional) - Used for fetching SonarCloud analysis results

## License

GPL-3.0-or-later
