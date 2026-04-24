# Partner Engineering Module

A Lola module for partner engineering skills and workflows.
Contains community-facing skills for partner integrations, certified content development, and ecosystem collaboration.

## Installation

```bash
# Install Lola package manager
pip install lola-cli

# Register the module from GitHub
lola mod add https://github.com/ansible-community/ai-forge/partner_engineering

# Or clone and register locally
git clone https://github.com/ansible-community/ai-forge.git
lola mod add ./ai-forge/partner_engineering

# Install to Claude Code
lola install partner_engineering -a claude-code

# Install to Cursor
lola install partner_engineering -a cursor

# Install to other assistants
lola install partner_engineering -a gemini-cli
lola install partner_engineering -a opencode
```

## Components

### Skills

None currently defined.

### Commands

None currently defined.

### Agents

None currently defined.

### MCP Servers

None currently defined.

## Scope

This module is for **public, community-facing** partner engineering skills. Examples include:

- Partner collection certification workflows
- Integration testing helpers for partner modules
- Documentation generation for partner content
- Ecosystem compatibility validation

Internal or business-specific partner skills should be contributed to the private repository.

## Development

This module follows the Lola module structure:

```
partner_engineering/
├── README.md           # This file
└── module/             # Lola-importable content
    ├── AGENTS.md       # Module-level instructions
    ├── skills/         # Skill folders with SKILL.md
    ├── commands/       # Slash command .md files
    ├── agents/         # Subagent .md files
    └── mcps.json       # MCP server configuration
```

## Contributing

See [SKILL_GUIDELINES.md](../SKILL_GUIDELINES.md) for criteria on writing new skills.
See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution process.

## License

GPL-3.0-or-later
