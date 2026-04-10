# Awesome Ansible AI [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of AI tooling for Ansible automation development across the Ansible ecosystem

Discover AI-powered tools, skills, agents, and resources that enhance Ansible development workflows including code review, scaffolding, testing, and automation.

## Contents

- [Getting Started](#getting-started)
- [Agent Context Files](#agent-context-files)
  - [Core Ansible Repositories](#core-ansible-repositories)
  - [Collections with Agent Context](#collections-with-agent-context)
- [Skills](#skills)
  - [Skills Marketplaces](#skills-marketplaces)
  - [Code Review and Quality](#code-review-and-quality)
  - [Scaffolding and Generation](#scaffolding-and-generation)
  - [Commit and Changelog Management](#commit-and-changelog-management)
  - [Development Workflow](#development-workflow)
- [Commands](#commands)
- [MCP Servers](#mcp-servers)
- [Collections](#collections)
  - [AI Infrastructure Management](#ai-infrastructure-management)
  - [Collections with AI Development Tools](#collections-with-ai-development-tools)
- [Lola Modules](#lola-modules)
- [Package Managers](#package-managers)
- [Tools and Utilities](#tools-and-utilities)
  - [Development Tools](#development-tools)
  - [Management and Strategy Tools](#management-and-strategy-tools)
- [Resources](#resources)
  - [Documentation](#documentation)
  - [GitHub Search Queries](#github-search-queries)
  - [Community](#community)
- [Contributing](#contributing)

## Getting Started

AI tooling for Ansible helps developers write better automation code faster through intelligent assistance.
These tools provide code review against best practices, automated scaffolding of collections and roles,
commit message formatting, and context-aware development assistance.

### Quick Start Paths

**I want to review my Ansible code against best practices:**

- Use the **ansible-cop-review** skill for automated review against Red Hat Communities of Practice (CoP) guidelines

**I want to scaffold a new collection or role:**

- Use **ansible-scaffold-collection** or **ansible-scaffold-role** skills for interactive generation with CI/CD pipelines

**I want to give my AI assistant context about my Ansible repository:**

- Add an **AGENTS.md** or **CLAUDE.md** file to your repository root with project-specific guidelines and context

**I want to use multiple AI skills across different assistants:**

- Install **Lola** package manager (`pip install lola-cli`) and add the **ai-forge** modules for cross-platform skills

**I want AI-powered playbook generation in VS Code:**

- Install **Ansible Lightspeed** (IBM watsonx Code Assistant) for AI-powered content recommendations

### Key Concepts

- **AGENTS.md / CLAUDE.md** - Context files that provide AI assistants with project-specific information, coding standards, and workflow guidance
- **Skills** - Reusable AI capabilities defined in SKILL.md files that can be invoked across different AI assistants
- **MCP Servers** - Model Context Protocol servers that provide Ansible-specific operations and context to AI tools
- **Lola** - Universal package manager for distributing AI skills across multiple platforms (Claude Code, Cursor, Gemini CLI, etc.)

## Agent Context Files

Repositories containing AGENTS.md or CLAUDE.md files that provide AI assistants with project context, coding standards, and contribution workflows.

### Core Ansible Repositories

- [ansible/ansible](https://github.com/ansible/ansible) - Main Ansible repository with AGENTS.md and CLAUDE.md providing comprehensive guidance on PR review,
  testing workflows, contribution guidelines, and development best practices.
- [ansible/ansible-creator](https://github.com/ansible/ansible-creator) - Ansible content scaffolding tool with AGENTS.md for project interaction and development workflows.
- [ansible/vscode-ansible](https://github.com/ansible/vscode-ansible) - VS Code extension for Ansible with CLAUDE.md providing context for extension development.
- [ansible/metrics-service](https://github.com/ansible/metrics-service) - Metrics collection service with AGENTS.md and CLAUDE.md files providing AI assistant guidance.
- [ansible/ansible-backstage-plugins](https://github.com/ansible/ansible-backstage-plugins) - Backstage plugins for Ansible with CLAUDE.md for development context.
- [TerryHowe/ansible-modules-hashivault](https://github.com/TerryHowe/ansible-modules-hashivault) - Ansible modules for HashiCorp Vault interaction with AGENTS.md providing development guidance.

### Collections with Agent Context

- [ansible-collections/community.beszel](https://github.com/ansible-collections/community.beszel) - Beszel monitoring automation with .claude/skills for conventional commits and changelog management (23⭐).
- [ansible-collections/community.clickhouse](https://github.com/ansible-collections/community.clickhouse) - ClickHouse database collection with .agents/skills for PR review and collection development.
- [ansible-collections/community.mysql](https://github.com/ansible-collections/community.mysql) - MySQL collection with .agents/skills for commit formatting and PR review workflows.
- [ansible-collections/community.postgresql](https://github.com/ansible-collections/community.postgresql) - PostgreSQL collection with .agents/skills for commit, release management, and PR review.

## Skills

### Skills Marketplaces

Collections of multiple skills distributed as packages for reuse across projects:

- [leogallego/claude-ansible-skills](https://github.com/leogallego/claude-ansible-skills) - Marketplace of 5 reusable Claude Code skills for Ansible development:
  ansible-cop-review (CoP compliance), ansible-scaffold-role (role generation), ansible-scaffold-collection (collection generation),
  ansible-scaffold-ee (execution environment), and ansible-zen (philosophical code review).
  Distributed as Claude Code plugins with marketplace.json.

- [ansible-community/ai-forge](https://github.com/ansible-community/ai-forge) - Lola-based module marketplace providing cross-platform AI skills for Ansible collections and roles.
  Includes modules for collection development (ansible-collection) and role scaffolding (ansible-role) with skills following Red Hat CoP automation good practices.

- [sigridjineth/hello-ansible-skills](https://github.com/sigridjineth/hello-ansible-skills) - Multiple Claude Code skills for Ansible automation including ansible-playbook (playbook development),
  ansible-debug (troubleshooting), ansible-convert (shell script to playbook conversion), and ansible-interactive (interactive workflow assistance).

- [jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) - Extensive marketplace with 340 plugins and 1367 agent skills for Claude Code
  including production orchestration patterns and CCPI package manager with interactive tutorials.

- [mOdrA40/claude-codex-skills-directory](https://github.com/mOdrA40/claude-codex-skills-directory) - Contains ansible-mastery-skill focusing on Ansible as automation/operations contract
  with readable roles, predictable inventories, explicit change boundaries, and optimization for safe execution and auditability.

### Code Review and Quality

- **ansible-cop-review** - Comprehensive review of Ansible code against Red Hat Communities of Practice automation good practices.
  Features severity classification (ERROR/WARNING/INFO), diff-aware mode for reviewing only changed files, category filtering for specific rule types,
  ansible-lint integration for cross-referencing, parallel review with subagents for large projects, and auto-fix offer for common issues.
  - Available in: [leogallego/claude-ansible-skills](https://github.com/leogallego/claude-ansible-skills), [ansible-community/ai-forge](https://github.com/ansible-community/ai-forge)

- **ansible-zen** - Display the 20 Zen of Ansible principles and review code for simplicity, readability, and clarity.
  Provides a Zen Score (1-10 rating) and philosophical guidance complementing strict rule compliance with style and maintainability feedback.
  - Available in: [leogallego/claude-ansible-skills](https://github.com/leogallego/claude-ansible-skills), [ansible-community/ai-forge](https://github.com/ansible-community/ai-forge)

- **PR Review Skills** - Automated pull request review workflows including code quality checks, testing verification, and collection-specific guidelines.
  - Available in: [ansible-collections/community.clickhouse](https://github.com/ansible-collections/community.clickhouse),
    [ansible-collections/community.mysql](https://github.com/ansible-collections/community.mysql),
    [ansible-collections/community.postgresql](https://github.com/ansible-collections/community.postgresql)

### Scaffolding and Generation

- **ansible-scaffold-role** - Interactive role creation workflow with intelligent variable builder (asks what the role manages),
  task componentization (install.yml, configure.yml, service.yml), smart handler generation,
  and ansible-creator integration with fallback to manual generation.
  - Available in: [leogallego/claude-ansible-skills](https://github.com/leogallego/claude-ansible-skills), [ansible-community/ai-forge](https://github.com/ansible-community/ai-forge)

- **ansible-scaffold-collection** - Collection scaffolding with plugin generation (modules, filters, lookup plugins, action plugins),
  CI/CD pipeline generation (GitHub Actions, GitLab CI), antsibull-changelog setup,
  and automatic delegation to ansible-scaffold-role for included roles.
  - Available in: [leogallego/claude-ansible-skills](https://github.com/leogallego/claude-ansible-skills), [ansible-community/ai-forge](https://github.com/ansible-community/ai-forge)

- **ansible-scaffold-ee** - Execution environment creation with dependency introspection from project files (requirements.yml, requirements.txt, bindep.txt),
  external dependency handling, and CI/CD pipeline generation for container building.
  - Available in: [leogallego/claude-ansible-skills](https://github.com/leogallego/claude-ansible-skills)

- **ansible-collection-inclusion-review** - Systematic review workflow for Ansible collection community inclusion using official checklist-based validation against Ansible collection requirements.
  - Available in: [ansible-community/ai-forge](https://github.com/ansible-community/ai-forge)

### Commit and Changelog Management

- **commit** - Conventional commit message formatting following FQCN (Fully Qualified Collection Name) scopes and semantic commit standards for Ansible collections.
  - Available in: [ansible-collections/community.beszel](https://github.com/ansible-collections/community.beszel),
    [ansible-collections/community.mysql](https://github.com/ansible-collections/community.mysql),
    [ansible-collections/community.postgresql](https://github.com/ansible-collections/community.postgresql)

- **changelog** - Automated changelog generation and fragment management, categorizing commits into proper changelog sections (breaking changes, features, bug fixes, etc.).
  - Available in: [ansible-collections/community.beszel](https://github.com/ansible-collections/community.beszel)

- **release** - Release management workflows including version bumping, changelog finalization, and release preparation.
  - Available in: [ansible-collections/community.postgresql](https://github.com/ansible-collections/community.postgresql)

### Development Workflow

- **Molecule Testing Skills** - Integration with Molecule testing framework for automated testing workflows and test scenario generation.
  - Available in: [ansible-collections/community.beszel](https://github.com/ansible-collections/community.beszel)

## Commands

Slash commands available for specific AI-assisted workflows:

- **/ansible-cop-review** - Review code against Red Hat CoP automation good practices with severity levels and auto-fix suggestions
- **/ansible-scaffold-role** - Interactively create a new Ansible role with best practices
- **/ansible-scaffold-collection** - Interactively create a new Ansible collection with plugin scaffolding and CI/CD
- **/ansible-scaffold-ee** - Create an Ansible execution environment with dependency management
- **/ansible-collection-inclusion-review** - Review collection against community inclusion requirements
- **/ansible-zen** - Display Zen of Ansible principles and review code for simplicity

## MCP Servers

Model Context Protocol servers providing Ansible-specific operations and context to AI assistants:

- [ansible/aap-mcp-server](https://github.com/ansible/aap-mcp-server) - Official MCP server for Red Hat Ansible Automation Platform (AAP) providing AAP-specific context, operations, and resources.
  Technology preview in AAP 2.6.4 with dual-layer security (server-level + user-level RBAC) (22⭐).

- [ansible/ansible-mcp-tools](https://github.com/ansible/ansible-mcp-tools) - General-purpose MCP tools for Ansible providing core Ansible operations and context.

- [ansible-collections/ansible.mcp](https://github.com/ansible-collections/ansible.mcp) - Ansible collection containing Model Context Protocol plugins for integration with various AI assistants (3⭐).

- [ansible-community/ara MCP](https://github.com/ansible-community/ara) - ARA (Ansible Records Ansible) with MCP server integration at `contrib/mcp/`
  for playbook run analysis, troubleshooting, and historical data querying (2007⭐).

- [redhat-cop/ansible.mcp_builder](https://github.com/redhat-cop/ansible.mcp_builder) - Ansible collection that facilitates installing MCP servers in Execution Environments (EEs)
  for enhanced AI assistant integration.

- [bsahane/mcp-ansible](https://github.com/bsahane/mcp-ansible) - Advanced Python-based MCP server exposing Ansible utilities for inventories, playbooks, roles, and project workflows.

- [sibilleb/AAP-Enterprise-MCP-Server](https://github.com/sibilleb/AAP-Enterprise-MCP-Server) - Comprehensive MCP server suite for Ansible Automation Platform (AAP) and Event-Driven Ansible (EDA)
  with ansible-lint code quality integration and access to Red Hat's official documentation with secure domain validation.

- [a37ai/ansible-tower-mcp](https://github.com/a37ai/ansible-tower-mcp) - MCP server enabling LLMs to interact with Ansible Tower for infrastructure automation.

- [washyu/ansible-mcp-server](https://github.com/washyu/ansible-mcp-server) - Enables AI assistants to manage infrastructure using both Ansible and Terraform through unified MCP interface.

- [mancubus77/mcp-server-aap](https://github.com/mancubus77/mcp-server-aap) - Example MCP server implementation for working with Ansible Automation Platform.

- [tarnover/mcp-sysoperator](https://github.com/tarnover/mcp-sysoperator) - MCP server for Ansible, Terraform, LocalStack, and other Infrastructure as Code tools
  enabling AI-driven infrastructure creation and iteration.

- [bjeans/homelab-mcp](https://github.com/bjeans/homelab-mcp) - MCP servers for managing homelab infrastructure through Claude Desktop.
  Monitors Docker/Podman containers, Ollama AI models, Pi-hole DNS, Unifi networks, and Ansible inventory
  with security checks, templates, and automated pre-push validation.

## Collections

### AI Infrastructure Management

Ansible collections for managing AI/ML infrastructure and platforms:

- [ansible-collections/infra.ai](https://github.com/ansible-collections/infra.ai) - Validated Content for automating Red Hat Enterprise Linux AI (RHEL AI) infrastructure deployment and management.

- [ansible-collections/redhat.ai](https://github.com/ansible-collections/redhat.ai) - Collection for managing Red Hat AI products and services.

- [ansible-collections/amazon.ai](https://github.com/ansible-collections/amazon.ai) - Red Hat Ansible Certified Collection for Amazon AI/ML resources.
  Includes modules for Amazon Bedrock (foundation models, AI/ML applications), Amazon DevOps Guru (operational monitoring, insights, notification channels).
  Deploy and validate AI agents automatically, invoke foundation models programmatically, configure and audit operational monitoring at scale,
  and generate compliance-ready reports with idempotent automation. Entitled to support through Ansible Automation Platform (AAP).

### Collections with AI Development Tools

Collections that include AI-powered development tools and skills:

- [ansible-collections/community.beszel](https://github.com/ansible-collections/community.beszel) - Beszel monitoring automation with comprehensive .claude/skills
  including conventional commits (FQCN scopes), changelog management, and Molecule testing workflows (23⭐).

- [ansible-collections/community.clickhouse](https://github.com/ansible-collections/community.clickhouse) - ClickHouse database collection with .agents/skills for PR review and development patterns.

- [ansible-collections/community.mysql](https://github.com/ansible-collections/community.mysql) - MySQL collection with .agents/skills for commit formatting and PR review workflows.

- [ansible-collections/community.postgresql](https://github.com/ansible-collections/community.postgresql) - PostgreSQL collection with .agents/skills for commit, release management, and PR review workflows.

- [arillso/ansible.agent](https://github.com/arillso/ansible.agent) - Ansible collection for deploying infrastructure agents including Grafana Alloy, Tailscale VPN, and cloud monitoring.
  Supports Linux and Windows environments.

## Lola Modules

Lola-compatible modules for cross-platform AI skill distribution:

- [ansible-community/ai-forge](https://github.com/ansible-community/ai-forge) - Lola modules for Ansible automation development following Red Hat CoP practices:
  - **ansible-collection module** - Collection development tools including ansible-cop-review, ansible-scaffold-collection, ansible-collection-inclusion-review, and ansible-zen skills
  - **ansible-role module** - Role scaffolding tools including ansible-scaffold-role skill
  - Install with: `lola mod add github.com/ansible-community/ai-forge/ansible-collection` or `lola mod add github.com/ansible-community/ai-forge/ansible-role`

## Package Managers

Distribution mechanisms for AI skills and capabilities:

- **[Lola](https://github.com/RedHatProductSecurity/lola)** - Universal AI package manager for skills, commands, and agents.
  Write skills once and deploy to any AI assistant including Claude Code, Cursor, Gemini CLI, OpenCode, and more.
  Follows a modular structure with skills/, commands/, agents/, and mcps.json in each module.
  - Install: `pip install lola-cli`
  - Use: `lola mod add <module-url>` to add modules, `lola install` to activate

- **Claude Code Plugins** - Plugin system for Claude Code with marketplace.json distribution format.
  Example: [leogallego/claude-ansible-skills](https://github.com/leogallego/claude-ansible-skills) with `.claude-plugin/marketplace.json` for skill discovery and installation.

- **[Skills.sh](https://skills.sh/)** - Portable skill format specification for creating AI skills that work across multiple AI assistants and platforms.

## Tools and Utilities

### Development Tools

- [ansible/ai-helpers](https://github.com/ansible/ai-helpers) - Collection of experimental and official AI skills including aap-develop, pr-review, cve-audit,
  and sdp-proposal-reviews for Ansible development workflows.

- [ansible/platform-services-utilities](https://github.com/ansible/platform-services-utilities) - Extensive .claude/skills directory with DVT (design verification testing),
  tag management, backport automation, PR triage, CVE evaluation, and platform services workflows.

- [ansible/ansible-dev-tools](https://github.com/ansible/ansible-dev-tools) - Ansible automation developer tools suite included in AAP 2.4+ for creating, testing, and deploying collections.
  Provides standard development environments with VS Code, Ansible Lightspeed integration, and comprehensive documentation.

- [ansible/ansible-ai-connect-service](https://github.com/ansible/ansible-ai-connect-service) - Backend service for AI-powered Ansible assistance.
  Official Red Hat/Ansible project providing the API layer for Ansible Lightspeed and other AI integrations.

- [IBM/watsonx-code-assistant-for-ansible](https://github.com/IBM/watsonx-code-assistant-for-ansible) - IBM watsonx Code Assistant (Ansible Lightspeed)
  providing generative AI-powered content recommendations for Ansible playbook creation.
  Includes sample end-to-end demos, best prompting practices, model customization guidelines.
  Available as SaaS or on-premise deployment with VS Code extension integration.

- [rh-ai-quickstart/ansible-log-analysis](https://github.com/rh-ai-quickstart/ansible-log-analysis) - AI agent for AAP clusters that detects Ansible log errors,
  suggests step-by-step fixes using cluster-wide logs, and routes issues to appropriate experts. Part of Red Hat AI Quickstart initiative.

### Management and Strategy Tools

- [ansible/ansible-pm-ai](https://github.com/ansible/ansible-pm-ai) - PM-focused AI skills including decision pipeline, analytics context, Google Docs integration,
  Jira operations, and Ansible good practices for product management workflows.

- [ansible/ansible-mgr-ai](https://github.com/ansible/ansible-mgr-ai) - Engineering manager marketplace with skill quality evaluation and team management workflows.

- [ansible/ai-persona-card-catalog](https://github.com/ansible/ai-persona-card-catalog) - Persona cards for different AI assistant use cases
  including data analyst, code reviewer, and specialized automation personas.

## Resources

### Documentation

- [Ansible Forum: AI in the Community](https://forum.ansible.com/t/ai-in-the-community/45575) - Community discussion on AI tooling ecosystem,
  organization strategies, and collaboration on AI-powered Ansible development
- [Red Hat CoP Automation Good Practices](https://github.com/redhat-cop/automation-good-practices) - Guidelines and best practices referenced by ansible-cop-review
  and other review skills
- [Ansible Lightspeed Documentation](https://docs.redhat.com/en/documentation/red_hat_ansible_lightspeed_with_ibm_watsonx_code_assistant/) - Official documentation
  for Red Hat Ansible Lightspeed with IBM watsonx Code Assistant
- [Ansible Development Tools - AAP 2.4+](https://access.redhat.com/articles/7058551) - Documentation for Ansible development tools including Lightspeed integration
- [Lola Package Manager](https://github.com/RedHatProductSecurity/lola) - Documentation and guides for using Lola to distribute AI skills
- [Skills.sh Documentation](https://skills.sh/) - Specification for portable AI skill format
- [Model Context Protocol](https://modelcontextprotocol.io/) - Official MCP documentation for building AI assistant integrations
- [AGENTS.md Standard](https://tessl.io/blog/the-rise-of-agents-md-an-open-standard-and-single-source-of-truth-for-ai-coding-agents/) - Open standard for AI coding agent configuration files
- [Google Gemini CLI](https://github.com/google-gemini/gemini-cli) - Open-source AI agent for terminal access to Google Gemini with MCP support for custom integrations including Ansible workflows

### GitHub Search Queries

Discover more AI tools in the Ansible ecosystem using these GitHub searches:

**Using GitHub CLI (`gh`):**

```bash
# Find all AGENTS.md files
gh search code --owner=ansible --owner=ansible-community --owner=ansible-collections "filename:AGENTS.md"

# Find all CLAUDE.md files
gh search code --owner=ansible --owner=ansible-community --owner=ansible-collections "filename:CLAUDE.md"

# Find all SKILL.md files (individual skills)
gh search code --owner=ansible --owner=ansible-community --owner=ansible-collections "filename:SKILL.md"

# Find all GEMINI.md files
gh search code --owner=ansible --owner=ansible-community --owner=ansible-collections "filename:GEMINI.md"

# Find .claude directories
gh search code --owner=ansible --owner=ansible-community --owner=ansible-collections "path:.claude"

# Find .agents directories
gh search code --owner=ansible --owner=ansible-community --owner=ansible-collections "path:.agents"

# Find .gemini directories
gh search code --owner=ansible --owner=ansible-community --owner=ansible-collections "path:.gemini"

# Find MCP server configurations
gh search code --owner=ansible --owner=ansible-community --owner=ansible-collections "filename:mcps.json"

# Find MCP-related repositories
gh search code --owner=ansible --owner=ansible-community --owner=ansible-collections "mcp_servers OR mcpServers"
```

**Using GitHub Web Search:**

- AGENTS.md files: `org:ansible filename:AGENTS.md` or `org:ansible-community filename:AGENTS.md` or `org:ansible-collections filename:AGENTS.md`
- CLAUDE.md files: `org:ansible filename:CLAUDE.md` or `org:ansible-community filename:CLAUDE.md` or `org:ansible-collections filename:CLAUDE.md`
- SKILL.md files: `org:ansible filename:SKILL.md` or `org:ansible-community filename:SKILL.md` or `org:ansible-collections filename:SKILL.md`
- Combined search: `(org:ansible OR org:ansible-community OR org:ansible-collections) (filename:AGENTS.md OR filename:CLAUDE.md OR filename:SKILL.md)`

### Community

- [Ansible Forum](https://forum.ansible.com/) - Community discussions, announcements, and collaboration
- [Ansible Community Matrix](https://matrix.to/#/#ansible-community:ansible.im) - Real-time chat for Ansible community
- [Ansible Galaxy](https://galaxy.ansible.com/) - Discover and share Ansible content
- [Ansible GitHub Discussions](https://github.com/ansible/ansible/discussions) - GitHub-based community discussions

## Contributing

Contributions are welcome! To add a new tool to this list:

### Inclusion Criteria

**Must have:**

- Public repository in `ansible`, `ansible-community`, or `ansible-collections` GitHub organizations
- Clear AI/LLM-related functionality (skills, agents, MCP servers, AI context files, etc.)
- Documentation explaining what the tool does (README, SKILL.md, or AGENTS.md)

**Should have:**

- Active maintenance (updated within the last 12 months, or explicitly marked as stable/mature)
- Meaningful description beyond generic "AI tools"
- Examples or usage documentation

**Nice to have:**

- Community validation (GitHub stars, multiple contributors)
- Integration with popular AI assistants (Claude Code, Cursor, Copilot, etc.)
- Following established standards (AGENTS.md, SKILL.md, Lola modules, MCP)

### Submission Guidelines

1. Fork this repository
2. Add your tool in the appropriate category with format: `[Name](URL) - Description with key features`
3. Include star count (⭐) if the repository has 10+ stars
4. For skills available in multiple locations, use format: `Available in: [repo1](url1), [repo2](url2)`
5. Ensure descriptions are action-oriented (what the tool does, not what it is)
6. Verify all links work and point to public repositories
7. Submit a pull request with a clear description

### Style Guide

- Use present tense: "Provides X" not "Provided X"
- Be specific: "Review Ansible code against CoP practices" not "Code review tool"
- Include key features: "with severity classification, auto-fix, and ansible-lint integration"
- Keep descriptions concise (1-3 sentences maximum)

---

**Maintained by the Ansible community** | **Not affiliated with Red Hat or Ansible, Inc.** | **[Contribute](#contributing)**
