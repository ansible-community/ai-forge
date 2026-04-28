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

This module is for **public, community-facing** network automation skills.

### What is a Network Collection?

A **Network Collection** provides modules and plugins for managing network devices - routers, switches, firewalls, load balancers, and other network infrastructure.
These collections automate device configuration, state management, and operational tasks.

Examples: `cisco.ios`, `cisco.nxos`, `arista.eos`, `junipernetworks.junos`, `vyos.vyos`, `ansible.netcommon`

### What Makes Network Collections Different

Network collections have unique development patterns:

- **Connection**: Specialized plugins (`network_cli`, `netconf`, `httpapi`) instead of standard SSH
- **State handling**: Resource Modules with states: `merged`, `replaced`, `overridden`, `deleted`, `gathered`, `rendered`, `parsed`
- **Authentication**: Device credentials via `ansible_network_os`, `ansible_user`, `ansible_password`
- **Idempotency**: Parse running-config, compare to desired state, generate minimal config diff

### Planned Skills

| Skill | Description |
|-------|-------------|
| `resource-module-scaffold` | Generate Resource Module structure with argument spec, facts, and all state operations |
| `resource-module-parser` | Create parsers for extracting structured data from device CLI output |
| `network-facts-module` | Scaffold `*_facts` modules that populate `ansible_network_resources` |
| `netconf-module` | Generate NETCONF-based modules with proper XML/YANG handling |
| `httpapi-plugin` | Scaffold httpapi connection plugins for REST-based network devices |
| `network-config-diff` | Implement config comparison and minimal diff generation |
| `network-integration-tests` | Generate integration tests with device mocking patterns |

### Resource Module Pattern

Resource modules solve the "every vendor has different CLI syntax" problem:

```yaml
# Consistent interface across all platforms
- cisco.ios.ios_interfaces:
    config:
      - name: GigabitEthernet0/1
        enabled: true
    state: merged  # or replaced, overridden, deleted, gathered
```

The `resource-module-scaffold` skill would generate:

- Argument spec from a resource model
- `rm_builder` templates
- Config parsers for existing device output
- Each state operation implementation

### Example Use Cases

- Network device configuration validation
- Platform-specific module development
- Config backup and restore workflows
- Network topology analysis helpers
- Compliance checking against golden configs

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
