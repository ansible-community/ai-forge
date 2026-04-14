# Ansible Collection SDLC Module

A Lola module for the full software development lifecycle of Ansible collections: conventional commits, PR reviews, releases, and testing.
Streamlines day-to-day development workflows from code commit to production release.

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

- **commit** - Create conventional commits with FQCN scopes for Ansible collection content
- **pr-review** - Review PRs against project standards and the Ansible Collection Review Checklist
- **release** - Guide collection releases with automatic version detection from changelog fragments
- **run-tests** - Run and write sanity, unit, and integration tests using ansible-test
- **sonarcloud-analysis** - Fetch and analyse SonarCloud issues for projects or pull requests

#### Helper Skills

- **get-upstream-info** - Determine upstream repository information and service identifiers (used by other skills)
- **get-pr-number** - Determine pull request number for a branch (used by other skills)

### Commands

None currently defined.

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
    ├── skills/         # Skill folders with SKILL.md
    ├── commands/       # Slash command .md files
    ├── agents/         # Subagent .md files
    └── mcps.json       # MCP server configuration
```

## Dependencies

- **antsibull-changelog** (optional) - Used by the release skill for changelog generation
- **gh CLI** (optional) - Used by the release skill for creating GitHub releases and PRs, and by the sonarcloud-analysis skill for PR detection
- **ansible-test** - Used by the run-tests skill for running sanity, unit, and integration tests
- **curl** (optional) - Used by the sonarcloud-analysis skill for fetching static analysis results

## License

GPL-3.0-or-later
