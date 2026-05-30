---
name: write-content
description: >-
  Write or improve Ansible content (playbooks, tasks, handlers, templates,
  variables, inventories, argument specs) following Red Hat CoP automation
  good practices. Use when writing new Ansible YAML content from a description,
  or improving existing content against best practices. Do NOT use for Python
  module development (use write-module), role/collection scaffolding (use
  ansible-scaffold-role / ansible-scaffold-collection), compliance auditing
  (use ansible-cop-review), or style review (use ansible-zen).
argument-hint: "[content-file-path or content-description]"
user-invocable: true
metadata:
  author: David Danielsson
  version: 1.0.0
---

# Skill: write-content

## Purpose

Write new Ansible YAML content or improve existing content following Red Hat CoP automation good practices and official Ansible documentation. This
is a hands-on writing assistant for individual pieces of content — tasks, handlers, playbooks, templates, variables, inventories, and argument specs.

## When to Invoke

TRIGGER when:

- A user asks to write, create, or generate a task, handler, playbook, template, variable definition, inventory structure, or argument spec
- A user asks to improve, fix, or update existing Ansible YAML content against best practices
- A user asks how to structure a specific piece of Ansible content correctly
- A user asks for help writing Jinja2 templates for Ansible
- A user asks about variable naming, placement, or precedence conventions
- A user asks to add proper tags, blocks, or error handling to existing content

DO NOT TRIGGER when:

- Writing Python modules (use `write-module` instead)
- Scaffolding an entire role (use `ansible-scaffold-role` instead)
- Scaffolding an entire collection (use `ansible-scaffold-collection` instead)
- Auditing code against CoP compliance rules (use `ansible-cop-review` instead)
- Reviewing code for Zen/philosophy alignment (use `ansible-zen` instead)
- Reviewing a PR (use `pr-review` instead)
- Running tests (use `run-tests` instead)

## Important

- This skill focuses on YAML-based Ansible content, not Python files under `plugins/modules/`. If the user needs help with a Python module, redirect to the `write-module` skill.
- Always explain WHY a practice matters, not just WHAT to do. Users learn better when they understand the rationale.
- When improving, highlight what is already done well — not every review needs to find problems.
- For full project/role scaffolding, suggest `ansible-scaffold-collection` or `ansible-scaffold-role` and point the user there. This skill writes individual content pieces, not entire directory structures.
- When generating content that belongs inside a role, always prefix variables with the role name.
- Primary source: Red Hat CoP automation good practices (https://redhat-cop.github.io/automation-good-practices/). Secondary source: docs.ansible.com. For the full set of rules and examples, see [reference.md](reference.md).

## Modes

Determine the mode based on the user's invocation and `$ARGUMENTS`:

- If `$ARGUMENTS` is a path to an existing `.yml`, `.yaml`, or `.j2` file → **Mode 2: Improve**
- If `$ARGUMENTS` is a text description (no path separator or file does not exist) → **Mode 1: Write**
- If `$ARGUMENTS` is empty → ask the user whether they want to write new content or improve existing content
- If ambiguous → ask the user to clarify

---

### Mode 1: Write New Content

Generate best-practice-compliant Ansible content from a user description.

#### Step 1 — Determine Content Type

Identify what the user wants from their description:

| Content Type | Detection Signals | Primary Output |
|--------------|-------------------|----------------|
| Task / Task file | "task", "install", "configure", "ensure", action verbs | One or more YAML tasks |
| Handler | "handler", "restart", "reload", "notify" | Handler YAML block |
| Playbook | "playbook", "play", multiple hosts/roles | Full playbook YAML |
| Template (Jinja2) | "template", ".conf", ".cfg", config file names | `.j2` file content |
| Variable definitions | "variables", "defaults", "vars", "inventory vars" | YAML variable block |
| Inventory structure | "inventory", "hosts", "groups" | Inventory directory/file layout |
| Argument spec | "argument_specs", "meta/argument_specs", "validate role args" | `meta/argument_specs.yml` content |

If the type is unclear, ask the user.

#### Step 2 — Gather Context

Collect from the user (ask if not provided):

- **For tasks/handlers**: What action? Which service/package/resource? Target state? Role context (for variable naming)?
- **For playbooks**: Target hosts? What roles/tasks? Become needed? Tags?
- **For templates**: What application/service? Configuration parameters? File path on target?
- **For variables**: Role name (for prefixing)? Defaults vs vars? Platform-specific?
- **For inventory**: Environments? Group hierarchy? Static or dynamic?
- **For argument specs**: Role name? Which variables to validate?

If in a project directory, detect context automatically:

- Read `galaxy.yml` for namespace/collection info
- Read existing `defaults/main.yml` for variable naming patterns
- Read existing role structure to determine role name prefix

#### Step 3 — Generate Content

Apply the content-type-specific template from the **Content Templates** section below. All generated content must follow every applicable rule from the **Style Rules** section.

#### Step 4 — Post-Write Guidance

After generating content:

1. Suggest running `ansible-lint <file>` to validate
2. Suggest running `ansible-playbook --syntax-check <playbook>` for playbooks
3. Suggest using the `write-content-tests` skill to generate Molecule functional tests
4. If the content is part of a role and no `meta/argument_specs.yml` exists, suggest creating one
5. If the user needs a full role, suggest `ansible-scaffold-role` instead
6. If the user needs a full collection, suggest `ansible-scaffold-collection` instead

---

### Mode 2: Improve Existing Content

Audit existing Ansible YAML content against best practices and suggest improvements.

#### Step 1 — Discover Scope

- If `$ARGUMENTS` is a file path, improve that file
- If `$ARGUMENTS` is a directory, find all `.yml`, `.yaml`, and `.j2` files
- If no arguments, improve all Ansible content files in the current project

#### Step 2 — Read the Content

Read every file completely before forming any judgment. Determine the content type of each file (task file, handler, playbook, template, variable file, inventory, argument spec) from its path and structure.

#### Step 3 — Evaluate Against Checklist

Run through every category in the **Improvement Checklist** below. Collect findings per category. For the full detailed rules behind each check, consult [reference.md](reference.md).

#### Step 4 — Score

Rate overall compliance on a 1-10 scale:

- **9-10**: Exemplary — follows all practices, well-structured, clean style
- **7-8**: Good — follows most practices, minor issues only
- **5-6**: Acceptable — works but has notable gaps in naming, style, or structure
- **3-4**: Needs work — significant violations in multiple categories
- **1-2**: Non-compliant — fundamental structural or style issues

#### Step 5 — Top Recommendations

List the 3 most impactful changes that would improve compliance. Focus on changes that affect correctness, idempotency, or maintainability — not style preferences.

---

## Content Templates

### Task

```yaml
- name: Ensure nginx is installed
  ansible.builtin.dnf:
    name: "{{ webserver_packages }}"
    state: present
  become: true
  notify:
    - Restart nginx
  tags:
    - webserver
    - install
```

### Handler

```yaml
- name: Restart nginx
  ansible.builtin.systemd_service:
    name: "{{ webserver_service_name }}"
    state: restarted
  become: true
  listen:
    - Restart nginx
```

### Playbook

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: true
  gather_facts: true

  roles:
    - role: namespace.collection.webserver
      tags:
        - webserver
```

### Template (Jinja2)

```jinja2
{{ ansible_managed | comment }}

# Application configuration
server {
    listen {{ webserver_port | default(80) }};
    server_name {{ webserver_hostname }};

{% for location in webserver_locations %}
    location {{ location.path }} {
        proxy_pass {{ location.backend }};
    }
{% endfor %}
}
```

### Variable Definitions — defaults/main.yml

```yaml
---
# webserver - Web server configuration

# Packages to install.
webserver_packages:
  - nginx

# Service name for the web server.
webserver_service_name: nginx

# Whether the service should be enabled at boot.
webserver_service_enabled: true

# Port the web server listens on.
webserver_port: 80

# Variables without safe defaults (uncomment and set):
# webserver_ssl_certificate: /path/to/cert.pem
# webserver_ssl_key: /path/to/key.pem
```

### Variable Definitions — vars/main.yml

```yaml
---
# Internal constants - do not override
__webserver_config_path: /etc/nginx/nginx.conf
__webserver_config_owner: root
__webserver_config_group: root
__webserver_config_mode: "0644"
```

### Inventory Structure

```
inventory/
├── production/
│   ├── hosts.yml
│   ├── group_vars/
│   │   ├── all/
│   │   │   ├── vars.yml
│   │   │   └── vault.yml
│   │   └── webservers/
│   │       └── vars.yml
│   └── host_vars/
│       └── web01.example.com/
│           └── vars.yml
└── staging/
    ├── hosts.yml
    ├── group_vars/
    │   └── all/
    │       ├── vars.yml
    │       └── vault.yml
    └── host_vars/
```

### Argument Spec — meta/argument_specs.yml

```yaml
---
argument_specs:
  main:
    short_description: Configure web server
    description:
      - Install and configure a web server with reverse proxy support.
    options:
      webserver_packages:
        description:
          - List of packages to install for the web server.
        type: list
        elements: str
        default:
          - nginx
      webserver_service_name:
        description:
          - Name of the web server service.
        type: str
        default: nginx
      webserver_port:
        description:
          - Port the web server listens on.
        type: int
        default: 80
      webserver_ssl_certificate:
        description:
          - Path to the SSL certificate file.
          - Required when enabling HTTPS.
        type: path
```

---

## Style Rules

All generated and improved content must follow these rules. Each rule references the corresponding section in [reference.md](reference.md) for full detail.

1. Two-space indentation
2. `.yml` extension (not `.yaml`)
3. YAML style for module arguments (not `key=value` inline)
4. `true`/`false` (not `yes`/`no` or `True`/`False`)
5. FQCN for all modules (e.g., `ansible.builtin.copy`, not `copy`)
6. Name ALL tasks, plays, and blocks in imperative mood
7. Always specify `state` explicitly — never rely on module defaults
8. Double quotes for YAML strings, single quotes only inside Jinja2
9. Use `>-` for folded scalars (not `>`) — prevents trailing newline bugs
10. Break long `when:` conditions into lists — Ansible auto-ANDs list elements
11. Use `loop:` not deprecated `with_*` constructs
12. Prefer modules over `command`/`shell`; prefer `command` over `shell`
13. Use `failed_when:` with specific conditions, not `ignore_errors: true`
14. Use `delegate_to: localhost` not `local_action`
15. Set `verbosity:` on `ansible.builtin.debug` tasks
16. Use `block:` for error handling (`rescue`/`always`)
17. Prefix task names in sub-task files: `install | Install packages`
18. Role variable prefix: `<role_name>_variable`
19. Internal variable double-underscore prefix: `__<role_name>_variable`
20. `{{ ansible_managed | comment }}` at the top of all templates
21. `backup: true` on template/copy tasks that overwrite config files
22. `snake_case` for all file names, variable names, and role names
23. Line length under 120 characters (ansible-lint default)
24. Use `ansible_facts['os_family']` bracket notation (not `ansible_os_family`)

---

## Improvement Checklist

| Category | What to Check |
|----------|---------------|
| YAML Style | 2-space indent, `true`/`false` booleans, `.yml` extension, line length under 120, `>-` for folded scalars, double quotes for YAML strings |
| Naming | `snake_case` everywhere, imperative task/play/block names, sub-task file prefixes (`install \| ...`), role-prefixed variables, `__` prefix for internal vars |
| Module Usage | FQCN for all modules, `loop:` not `with_*`, YAML-style args not `key=value`, explicit `state`, prefer modules over `command`/`shell` |
| Task Structure | All tasks/plays/blocks named, `become` scoped correctly (play-level vs task-level), `notify:` wired to handlers, meaningful `tags:` present |
| Handlers | Role-prefixed names, uses `listen:` for decoupling, only for change-triggered actions, service handlers for restart/reload |
| Templates | `{{ ansible_managed \| comment }}` header present, `backup: true` on the task, no dynamic timestamps, proper Jinja2 quoting |
| Variables | Defaults in `defaults/main.yml`, constants in `vars/main.yml`, role-name prefix on all vars, `__` prefix for internals, dangerous defaults commented out |
| Playbook Structure | No mixed `roles:` + `tasks:` sections, logic in roles not playbooks, `gather_subset` specified when full facts not needed, `become` at correct level |
| Inventory | Structured directory layout, no variable definitions in hosts file, vault layering (`vars.yml` + `vault.yml`), groups named by function |
| Error Handling | `block`/`rescue`/`always` for error handling, `failed_when:` not `ignore_errors:`, `changed_when:` on `command`/`shell` tasks |
| Idempotency | `changed_when:` on `command`/`shell`, modules used where available, `state` explicit, no unnecessary changes on re-run |
| Argument Specs | `meta/argument_specs.yml` exists, matches `defaults/main.yml`, types and descriptions present, choices for constrained values |
| Tags | Named after roles or meaningful operations, no standalone destructive tags, documented in README |
| Platform Support | `include_vars` with `lookup('first_found')`, platform-specific var files (`RedHat.yml`, `Debian.yml`), `ansible_facts['...']` bracket notation |

---

## Output Format

### Write Mode

After generating content, output:

```
## Generated: <content type>

### Content
<the generated YAML or Jinja2 content>

### File Placement
`<suggested file path relative to role or project root>`

### Rules Applied
- <numbered list of key style rules applied from the Style Rules section>

### Next Steps
1. Run `ansible-lint <file>` to validate
2. <additional contextual suggestions>
```

### Improve Mode

```
## Content Review: <file path>

### Summary
<One-paragraph assessment: scope, quality, primary concerns.>

### Findings

#### Blockers (must fix)
- [CATEGORY] <file>:<line> — <description>

#### Warnings (should fix)
- [CATEGORY] <file>:<line> — <description>

#### Suggestions (optional improvements)
- [CATEGORY] <file>:<line> — <description>

### Checklist Status
| Category | Status | Notes |
|----------|--------|-------|
| YAML Style | PASS / FAIL / N/A | ... |
| Naming | PASS / FAIL / N/A | ... |
| Module Usage | PASS / FAIL / N/A | ... |
| Task Structure | PASS / FAIL / N/A | ... |
| Handlers | PASS / FAIL / N/A | ... |
| Templates | PASS / FAIL / N/A | ... |
| Variables | PASS / FAIL / N/A | ... |
| Playbook Structure | PASS / FAIL / N/A | ... |
| Inventory | PASS / FAIL / N/A | ... |
| Error Handling | PASS / FAIL / N/A | ... |
| Idempotency | PASS / FAIL / N/A | ... |
| Argument Specs | PASS / FAIL / N/A | ... |
| Tags | PASS / FAIL / N/A | ... |
| Platform Support | PASS / FAIL / N/A | ... |

### Score: X/10
<One sentence justification.>

### Top 3 Recommendations
1. ...
2. ...
3. ...
```

---

## Integration with Other Skills

| When | Skill |
|------|-------|
| Write functional tests (Molecule) for the content | `write-content-tests` |
| Writing a Python module, not YAML content | `write-module` |
| Scaffolding an entire role structure | `ansible-scaffold-role` |
| Scaffolding an entire collection | `ansible-scaffold-collection` |
| Full CoP compliance audit across a project | `ansible-cop-review` |
| Philosophical/style review | `ansible-zen` |
| Running tests after writing content | `run-tests` |
| Determining version for argument specs | `next-release` |
| Creating a changelog after content changes | `changelog-fragment` |
