# Ansible Community AI Forge

⚠️ This is a brand new repo, the structure and contents may change frequently as AI Tooling and standards evolve.

⚠️ As with all AI tools, careful human review is needed.

A repository of Lola modules for Ansible automation development following Red Hat Communities of Practice (CoP) automation good practices.

## What is This?

This repository provides AI assistant skills and commands for developing Ansible content that follows industry best practices.
Using the Lola package manager, you can install these modules to any AI coding assistant (Claude Code, Cursor, Gemini CLI, OpenCode, etc.)
and get expert guidance for creating, reviewing, and improving Ansible automation.

## Quick Start

```bash
# Install Lola package manager
pip install lola-ai

# Clone the repository
git clone https://github.com/ansible-community/ai-forge.git

# Install all modules to Claude Code
lola mod add ./ai-forge/ansible-collection-standards
lola mod add ./ai-forge/ansible-role
lola mod add ./ai-forge/ansible-collection-sdlc
lola install ansible-collection-standards -a claude-code
lola install ansible-role -a claude-code
lola install ansible-collection-sdlc -a claude-code

# Or install directly from GitHub
lola mod add https://github.com/ansible-community/ai-forge/ansible-collection-standards
lola mod add https://github.com/ansible-community/ai-forge/ansible-role
lola mod add https://github.com/ansible-community/ai-forge/ansible-collection-sdlc
lola install ansible-collection-standards -a claude-code
lola install ansible-role -a claude-code
lola install ansible-collection-sdlc -a claude-code

# Or install globally (available in all projects)
lola install ansible-collection-standards -a claude-code ~
lola install ansible-role -a claude-code ~
lola install ansible-collection-sdlc -a claude-code ~
```

## Modules

### ansible-collection-standards

Standards and guidelines compliance, scaffolding.

**Skills:**

- `ansible-zen` - Zen of Ansible principles and philosophical code review

**Commands:**

- `/ansible-cop-review` - Review code against Red Hat CoP practices
- `/ansible-scaffold-collection` - Create new collections
- `/ansible-collection-standards-inclusion-review` - Review collections for community inclusion

[Full documentation](./ansible-collection-standards/README.md)

### ansible-role

Role scaffolding tools.

**Commands:**

- `/ansible-scaffold-role` - Create new roles with interactive builder

[Full documentation](./ansible-role/README.md)

### ansible-collection-sdlc

Full lifecycle: commits, PRs, releases, tests.

**Skills:**

- `changelog-fragment` - Create and update changelog fragments
- `commit` - Conventional commits with FQCN scopes
- `create-branch` - Create feature branches following conventions
- `create-pr` - Create draft PRs with pre-flight checks and validation
- `implement-sonarcloud-fixes` - Implement fixes for SonarCloud issues
- `pr-review` - PR review against Ansible collection standards
- `release` - Guided collection release process
- `remove-deprecations` - Find and remove overdue deprecations
- `run-tests` - Run and write tests using ansible-test
- `sonarcloud-analysis` - Analyse SonarCloud issues and technical debt
- `next-release` - Calculate next patch/minor/major versions for version_added tags
- `current-release` - Fetch current release version (helper)
- `get-branch-changes` - Determine merge-base and changed files (helper)
- `get-pr-action-results` - Get GitHub Actions/GitLab CI results and analyze failures (helper)
- `get-pr-number` - Find PR number for branch (helper)
- `get-upstream-info` - Determine upstream repository info (helper)

[Full documentation](./ansible-collection-sdlc/README.md)

## What is Lola?

Lola is a universal AI package manager that allows you to write skills and commands once, then install them to any AI assistant. Think of it as DNF/YUM for AI tools.

## Contributing

We welcome contributions from the community. See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed instructions on:

- Setting up pre-commit hooks and linting
- Adding new skills or commands
- Making skills available via Lola

This project follows the [Red Hat Communities of Practice contributing guidelines](https://redhat-cop.github.io/contrib/).

### Reporting Issues

Open an issue on GitHub for bug reports, feature requests, or rule updates.

## License

GPL-3.0-or-later
