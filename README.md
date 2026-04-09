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
pip install lola-cli

# Clone the repository
git clone https://github.com/ansible-community/ai-forge.git

# Install all modules to Claude Code
lola mod add ./ai-forge/ansible-collection
lola mod add ./ai-forge/ansible-role
lola mod add ./ai-forge/ansible-collection-development
lola install ansible-collection -a claude-code
lola install ansible-role -a claude-code
lola install ansible-collection-development -a claude-code

# Or install directly from GitHub
lola mod add https://github.com/ansible-community/ai-forge/ansible-collection
lola mod add https://github.com/ansible-community/ai-forge/ansible-role
lola mod add https://github.com/ansible-community/ai-forge/ansible-collection-development
lola install ansible-collection -a claude-code
lola install ansible-role -a claude-code
lola install ansible-collection-development -a claude-code
```

## Modules

### ansible-collection

Collection development, review, and scaffolding tools.

**Skills:**

- `ansible-zen` - Zen of Ansible principles and philosophical code review

**Commands:**

- `/ansible-cop-review` - Review code against Red Hat CoP practices
- `/ansible-scaffold-collection` - Create new collections
- `/ansible-collection-inclusion-review` - Review collections for community inclusion

[Full documentation](./ansible-collection/README.md)

### ansible-role

Role scaffolding tools.

**Commands:**

- `/ansible-scaffold-role` - Create new roles with interactive builder

[Full documentation](./ansible-role/README.md)

### ansible-collection-development

Collection development workflow tools.

**Skills:**

- `commit` - Conventional commits with FQCN scopes
- `pr-review` - PR review against Ansible collection standards
- `release` - Guided collection release process
- `run-tests` - Run and write tests using ansible-test

[Full documentation](./ansible-collection-development/README.md)

## What is Lola?

Lola is a universal AI package manager that allows you to write skills and commands once, then install them to any AI assistant. Think of it as DNF/YUM for AI tools.

## Contributing

We welcome contributions from the community. This project follows the [Red Hat Communities of Practice contributing guidelines](https://redhat-cop.github.io/contrib/).

### Adding New Skills or Commands

1. Fork the repository
2. Add your skill/command to the appropriate module following the Lola structure
3. Update the module's README.md and AGENTS.md
4. Open a pull request

### Reporting Issues

Open an issue on GitHub for bug reports, feature requests, or rule updates.

## License

GPL-3.0-or-later
