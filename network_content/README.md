# Network Content Module

A Lola module for network automation skills and workflows specific to Ansible network collections.
Contains community-facing skills for network device management, configuration, and validation.

## Installation

```bash
# Install Lola package manager
pip install lola-cli

# Register the module from GitHub
lola mod add https://github.com/ansible-community/ai-forge/network_content

# Or clone and register locally
git clone https://github.com/ansible-community/ai-forge.git
lola mod add ./ai-forge/network_content

# Install to Claude Code
lola install network_content -a claude-code

# Install to Cursor
lola install network_content -a cursor

# Install to other assistants
lola install network_content -a gemini-cli
lola install network_content -a opencode
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

This module is for **public, community-facing** network automation skills. Examples include:

- Network device configuration validation
- Network topology analysis helpers
- Platform-specific module development aids
- Network testing and troubleshooting workflows

Internal or business-specific network skills should be contributed to the private repository.

## Development

This module follows the Lola module structure:

```
network_content/
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
