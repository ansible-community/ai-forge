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

# Install this repository's marketplace
lola market add ansible-content https://raw.githubusercontent.com/ansible-community/ai-forge/main/lola-market.yml

### alternatively, you can install from a local file:
### lola market add ansible-content ./lola-market.yml

## Clone the repository
git clone https://github.com/ansible-community/ai-forge.git

## Install all modules to Claude Code
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

### Declarative Module Management

To manage the modules recommended for your project declaratively:

1. Install `lola` and this repository's marketplace, as described in the quickstart section.
2. Create a `.lola-req` file in your project. For example:

    ```
    # .lola-req - AI context modules for this project

    # Modules from https://raw.githubusercontent.com/ansible-community/ai-forge/main/lola-market.yml
    @ansible-content/ai-forge/ansible-collection-sdlc
    @ansible-content/ai-forge/ansible-collection-standards
    ```

3. Install the modules if needed, `lola sync`

## Modules

### ansible-collection-standards

Standards and guidelines compliance, scaffolding. Includes the `ansible-zen` skill and commands for CoP review, collection scaffolding, and inclusion review.

[Full documentation](./ansible-collection-standards/README.md)

### ansible-role

Role scaffolding tools with interactive builders for creating CoP-compliant roles.

[Full documentation](./ansible-role/README.md)

### ansible-collection-sdlc

Full lifecycle: commits, PRs, releases, tests. Includes skills for changelog fragments, conventional commits, PR reviews, releases, testing, and SonarCloud integration.

[Full documentation](./ansible-collection-sdlc/README.md)

### All Skills

See **[SKILLS.md](./SKILLS.md)** for the complete auto-generated index of all available skills.

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
