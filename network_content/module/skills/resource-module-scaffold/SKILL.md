---
name: resource-module-scaffold
description: >-
  Scaffold a new Ansible network resource module from scratch. Generates all
  required files — module plugin, argspec, config class, facts class,
  rm_templates parser, __init__.py stubs, and facts.py registration — following
  the exact patterns used by production cisco.ios, cisco.iosxr, cisco.nxos, and
  arista.eos collections. Supports both simple (dict-based, e.g. hostname) and
  complex (list-based, e.g. vlans, interfaces) resource types. Does NOT generate
  integration tests — use molecule-scenario-generator for that. Use when asked to
  scaffold, create, or bootstrap a new resource module for any network collection.
triggers:
  - scaffold resource module
  - create resource module
  - new resource module
  - bootstrap module
  - rm scaffold
  - generate module skeleton
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
argument-hint: "<resource_name> [--collection <namespace.name>] [--type dict|list]"
---

# Skill: resource-module-scaffold

## Purpose

Generate all boilerplate files for a new Ansible network resource module,
following the exact structure and conventions used by production collections.
The skill produces working, importable code that passes `ansible-test sanity`
and provides a solid foundation for the developer to fill in resource-specific
logic (parsers, commands, argspec options).

### What this skill generates (9 files + 1 edit)

```
plugins/
  modules/<platform>_<resource>.py                                    # Main module entry point
  module_utils/network/<platform>/argspec/<resource>/<resource>.py    # Argument specification
  module_utils/network/<platform>/argspec/<resource>/__init__.py      # Package init
  module_utils/network/<platform>/config/<resource>/<resource>.py     # Config class (ResourceModule)
  module_utils/network/<platform>/config/<resource>/__init__.py       # Package init
  module_utils/network/<platform>/facts/<resource>/<resource>.py      # Facts class
  module_utils/network/<platform>/facts/<resource>/__init__.py        # Package init
  module_utils/network/<platform>/rm_templates/<resource>.py          # Parser templates
  module_utils/network/<platform>/facts/facts.py                      # EDIT: register new facts class

tests/
  unit/modules/network/<platform>/test_<platform>_<resource>.py       # Unit test scaffold
```

### What this skill does NOT generate

- Integration tests (use `molecule-scenario-generator` skill)
- DOCUMENTATION/EXAMPLES docstring content (developer fills in resource-specific examples)
- Complex parser regex (skill provides TODO-marked placeholders)
- Changelog fragments

## When to Invoke

TRIGGER when:
- User asks to scaffold/create/bootstrap a new resource module
- User says "new module for <resource>" in a network collection context
- User asks to add a resource module to cisco.ios, cisco.iosxr, cisco.nxos, arista.eos, or similar
- User references EPIC 2A/2B or the resource module scaffold ticket

DO NOT TRIGGER when:
- User asks about existing modules (use grep/read instead)
- User wants to fix/modify an existing module (use bugfix-workflow)
- User wants integration tests only (use molecule-scenario-generator)
- User wants a non-resource module (action plugin, filter, httpapi, etc.)

## Prerequisites

- Working directory must be inside a network collection (or collection path provided)
- The collection must follow the standard `plugins/module_utils/network/<platform>/` layout
- `ansible.netcommon` must be a dependency (provides `ResourceModule` and `NetworkTemplate` base classes)

## Input Specification

The skill needs the following information. Gather interactively if not provided:

### Required

| Parameter | Description | Example |
|---|---|---|
| `resource_name` | The resource being managed (snake_case) | `track` |
| `collection` | Namespace.name of the target collection | `cisco.ios` |

### Auto-detected (from collection)

| Parameter | How detected | Example |
|---|---|---|
| `platform` | Extracted from collection name | `ios` |
| `namespace` | Extracted from collection name | `cisco` |
| `collection_root` | Found by walking up to find `galaxy.yml` | `/path/to/cisco/ios` |

### Optional (with smart defaults)

| Parameter | Default | Description |
|---|---|---|
| `resource_type` | `dict` | `dict` for single-instance resources (hostname, logging_global), `list` for multi-instance (vlans, interfaces, acls) |
| `list_key` | None (required if type=list) | The unique key field for list resources (e.g. `vlan_id`, `name`, `afi`) |
| `config_attributes` | `[]` | List of config attributes with types. Skill generates TODO placeholders if empty |
| `show_command` | Auto-generated | The IOS show command for gathering facts (e.g. `show running-config \| section ^hostname`) |
| `version_added` | Current collection version | Ansible collection version for docs |
| `author` | Git user.name + GitHub handle | Module author for docs |

## Workflow

### Step 0 — Detect collection and validate

```
ACTION: Auto-detect or validate collection context
```

1. If inside a collection directory, detect from `galaxy.yml`:
   ```bash
   # Walk up from cwd to find galaxy.yml
   cat galaxy.yml | grep -E '^(namespace|name|version):'
   ```
2. Extract `namespace`, `name` (→ `platform`), `version`
3. Verify the standard layout exists:
   ```bash
   ls plugins/module_utils/network/<platform>/config/
   ls plugins/module_utils/network/<platform>/facts/
   ls plugins/module_utils/network/<platform>/rm_templates/
   ls plugins/module_utils/network/<platform>/argspec/
   ```
4. Verify `ansible.netcommon` is listed as a dependency in `galaxy.yml` or `requirements.yml`

If detection fails, ask the user for the collection path.

### Step 1 — Validate resource name and check for conflicts

```
ACTION: Ensure the resource doesn't already exist
```

1. Check that no existing module matches the name:
   ```bash
   ls plugins/modules/<platform>_<resource>.py 2>/dev/null
   ls plugins/module_utils/network/<platform>/config/<resource>/ 2>/dev/null
   ```
2. If files exist, STOP and report: "Module `<platform>_<resource>` already exists. Use edit/bugfix workflows instead."
3. Validate resource_name is valid Python identifier (snake_case, no hyphens)

### Step 2 — Determine resource complexity

```
ACTION: Choose dict vs list pattern based on resource type
```

**Dict-based (simple)** — Single-instance resource on the device. One config block, no key field needed.
- Examples: `hostname`, `logging_global`, `service`, `ntp_global`
- Config class uses `self.want` / `self.have` as dicts directly
- `generate_commands()` compares dicts
- Facts returns a single dict

**List-based (complex)** — Multiple instances identified by a key field.
- Examples: `vlans`, `interfaces`, `acls`, `static_routes`, `bgp_address_family`
- Config class indexes by key: `wantd = {entry[key]: entry for entry in conf_want}`
- `generate_commands()` iterates over keyed entries
- Facts returns a list of dicts
- Requires `list_key` parameter

### Step 3 — Generate files

Generate all files using the reference templates in `templates/` directory.
Read each template, substitute placeholders, and write to the collection.

#### Naming conventions (CRITICAL — follow exactly)

| Item | Convention | Example (resource=`track`) |
|---|---|---|
| Module file | `<platform>_<resource>.py` | `ios_track.py` |
| Module class | `<Resource>` (CamelCase) | `Track` |
| ArgSpec class | `<Resource>Args` | `TrackArgs` |
| Facts class | `<Resource>Facts` | `TrackFacts` |
| Template class | `<Resource>Template` | `TrackTemplate` |
| Resource string | `<resource>` (snake_case) | `track` |
| FQCN | `<namespace>.<name>.<platform>_<resource>` | `cisco.ios.ios_track` |

For multi-word resources (e.g., `bgp_global`):

| Item | Convention | Example |
|---|---|---|
| Class names | Each word capitalized, no separator | `Bgp_global` |
| Note | The underscore IS kept in class names | `Bgp_globalFacts`, NOT `BgpGlobalFacts` |

**IMPORTANT**: The class naming convention keeps underscores. Check existing modules in the collection
to confirm the exact pattern. For cisco.ios, it is `Bgp_global`, `L2_interfaces`, `Acl_interfaces`.

#### File generation order

Generate files in this order (dependencies first):

1. `__init__.py` stubs (3 files) — empty package markers
2. `rm_templates/<resource>.py` — parser definitions (no internal deps)
3. `argspec/<resource>/<resource>.py` — argument spec (no internal deps)
4. `facts/<resource>/<resource>.py` — facts class (imports argspec + rm_templates)
5. `config/<resource>/<resource>.py` — config class (imports facts + rm_templates)
6. `modules/<platform>_<resource>.py` — main module (imports argspec + config)
7. `facts/facts.py` — EDIT to add import + registration
8. `tests/unit/.../test_<platform>_<resource>.py` — unit test scaffold

### Step 4 — Register in facts.py

```
ACTION: Add import and registration to the master facts file
```

This is an EDIT, not a new file. The changes are:

1. **Add import** (alphabetically sorted with existing imports):
   ```python
   from ansible_collections.<namespace>.<name>.plugins.module_utils.network.<platform>.facts.<resource>.<resource> import (
       <Resource>Facts,
   )
   ```

2. **Add to FACT_RESOURCE_SUBSETS dict** (alphabetically sorted):
   ```python
   FACT_RESOURCE_SUBSETS = dict(
       ...
       <resource>=<Resource>Facts,
       ...
   )
   ```

3. **Add to FACT_SUBSETS list** (if the collection uses one — check first)

### Step 5 — Generate unit test scaffold

```
ACTION: Create a minimal but runnable unit test
```

Generate a unit test that:
- Imports the module
- Mocks `get_resource_connection` and the facts data method
- Has one idempotent test case (merged state, config matches)
- Has one change test case (merged state, config differs)
- Follows the exact test pattern used by existing tests in the collection

### Step 6 — Validation

```
ACTION: Verify all generated files are syntactically valid
```

1. **Python syntax check** on all generated `.py` files:
   ```bash
   python3 -c "import py_compile; py_compile.compile('<file>', doraise=True)"
   ```

2. **Import chain verification** — ensure all cross-references resolve:
   ```bash
   # From collection root
   python3 -c "
   import sys
   sys.path.insert(0, '.')
   # This will fail if imports are broken
   from plugins.module_utils.network.<platform>.rm_templates.<resource> import <Resource>Template
   "
   ```
   Note: Full import verification requires ansible and netcommon installed.
   If not available, do syntax-only checks.

3. **File inventory check** — confirm all expected files exist:
   ```bash
   expected_files=(
     "plugins/modules/<platform>_<resource>.py"
     "plugins/module_utils/network/<platform>/argspec/<resource>/__init__.py"
     "plugins/module_utils/network/<platform>/argspec/<resource>/<resource>.py"
     "plugins/module_utils/network/<platform>/config/<resource>/__init__.py"
     "plugins/module_utils/network/<platform>/config/<resource>/<resource>.py"
     "plugins/module_utils/network/<platform>/facts/<resource>/__init__.py"
     "plugins/module_utils/network/<platform>/facts/<resource>/<resource>.py"
     "plugins/module_utils/network/<platform>/rm_templates/<resource>.py"
     "tests/unit/modules/network/<platform>/test_<platform>_<resource>.py"
   )
   for f in "${expected_files[@]}"; do
     [ -f "$f" ] && echo "OK: $f" || echo "MISSING: $f"
   done
   ```

4. **Facts registration check**:
   ```bash
   grep -n "<Resource>Facts" plugins/module_utils/network/<platform>/facts/facts.py
   grep -n "<resource>=" plugins/module_utils/network/<platform>/facts/facts.py
   ```

### Step 7 — Summary and next steps

```
ACTION: Report what was generated and what the developer needs to do next
```

Print a summary:
```
Generated files for <namespace>.<name>.<platform>_<resource>:

  Created:
    plugins/modules/<platform>_<resource>.py
    plugins/module_utils/network/<platform>/argspec/<resource>/<resource>.py
    plugins/module_utils/network/<platform>/config/<resource>/<resource>.py
    plugins/module_utils/network/<platform>/facts/<resource>/<resource>.py
    plugins/module_utils/network/<platform>/rm_templates/<resource>.py
    plugins/module_utils/network/<platform>/argspec/<resource>/__init__.py
    plugins/module_utils/network/<platform>/config/<resource>/__init__.py
    plugins/module_utils/network/<platform>/facts/<resource>/__init__.py
    tests/unit/modules/network/<platform>/test_<platform>_<resource>.py

  Modified:
    plugins/module_utils/network/<platform>/facts/facts.py  (added import + registration)

  Developer TODO:
    1. Fill in DOCUMENTATION and EXAMPLES in the module file
    2. Define config attributes in argspec (replace TODO placeholders)
    3. Write parser regex patterns in rm_templates (replace TODO placeholders)
    4. Update the show command in facts class for your resource
    5. Implement resource-specific compare/generate logic in config class if needed
    6. Add unit test cases for each state (merged, replaced, deleted, etc.)
    7. Run: ansible-test sanity --docker -v plugins/modules/<platform>_<resource>.py
    8. Generate integration tests with molecule-scenario-generator skill
```

## Reference Templates

The `templates/` directory contains reference implementations for each file type.
These are based on real production modules in cisco.ios (ios_hostname for dict-type,
ios_vlans for list-type) and should be used as the basis for generation.

Read the appropriate template file before generating each file:
- `templates/module.py.reference` — main module entry point
- `templates/argspec.py.reference` — argument specification
- `templates/config_dict.py.reference` — config class for dict-based resources
- `templates/config_list.py.reference` — config class for list-based resources
- `templates/facts.py.reference` — facts gathering class
- `templates/rm_templates.py.reference` — parser template definitions
- `templates/unit_test.py.reference` — unit test scaffold

## Error Handling

| Error | Action |
|---|---|
| Not inside a collection | Ask user for collection path |
| Module already exists | STOP — suggest edit/bugfix workflow |
| Invalid resource name | Reject and explain naming rules |
| Missing `ansible.netcommon` dep | Warn — generated code requires netcommon base classes |
| facts.py has unexpected format | Show the import and registration lines to add manually |
| Syntax check fails | Fix the generated file and re-validate |

## Cross-collection Compatibility

This skill works across network collections with minor platform differences:

| Collection | Platform | Import path prefix |
|---|---|---|
| `cisco.ios` | `ios` | `ansible_collections.cisco.ios` |
| `cisco.iosxr` | `iosxr` | `ansible_collections.cisco.iosxr` |
| `cisco.nxos` | `nxos` | `ansible_collections.cisco.nxos` |
| `arista.eos` | `eos` | `ansible_collections.arista.eos` |
| `junipernetworks.junos` | `junos` | `ansible_collections.junipernetworks.junos` |

The file structure, base classes, and patterns are identical across all of these.
Only the platform name in paths and class prefixes changes.
