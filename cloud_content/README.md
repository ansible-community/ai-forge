# Cloud Content Module

A Lola module for cloud automation skills and workflows specific to Ansible cloud collections.
Contains community-facing skills for cloud provider integrations, infrastructure management, and cloud-native workflows.

## Installation

```bash
# Install Lola package manager
pip install lola-cli

# Register the module from GitHub
lola mod add https://github.com/ansible-community/ai-forge/cloud_content

# Or clone and register locally
git clone https://github.com/ansible-community/ai-forge.git
lola mod add ./ai-forge/cloud_content

# Install to Claude Code
lola install cloud_content -a claude-code

# Install to Cursor
lola install cloud_content -a cursor

# Install to other assistants
lola install cloud_content -a gemini-cli
lola install cloud_content -a opencode
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

This module is for **public, community-facing** cloud automation skills. Examples include:

- Cloud resource provisioning helpers
- Infrastructure-as-code validation
- Cloud provider API interaction patterns
- Multi-cloud workflow development aids

Internal or business-specific cloud skills should be contributed to the private repository.

## Development

This module follows the Lola module structure:

```
cloud_content/
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
