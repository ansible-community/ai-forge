---
name: issue-implement
description: Execute the implementation plan for any issue (bug/feature/enhancement). Applies code changes, adds comprehensive tests (unit + integration), ensures style consistency, validates RETURN blocks, and auto-installs dependencies. Use after /issue-plan, when ready to implement, or when asked to "implement", "apply fix", or "write the code".
---

# Issue Implement Skill

Execute the implementation plan for any issue type with comprehensive testing.

## Author

**Alina Buzachis (alinabuzachis)** - Ansible Cloud Content Team

## Purpose

Reads the implementation plan, applies code changes, adds mandatory unit and integration tests, verifies RETURN blocks, auto-installs dependencies, formats code, and validates the implementation works.

## Prerequisites

- Implementation plan from `/issue-plan` (in `.bug-fixes/plan-N.md`)
- Git repository with configured fork/upstream
- Access to modify code and tests

## CRITICAL: Collection Path

**ALWAYS ask user for collection path at the start:**

Before beginning implementation, ask user:

```
Which directory should I work in?
Please provide the full path to your collection git repository.

Example: /Users/username/projects/ansible_collections/amazon/aws
```

After receiving path, verify it's valid:

```bash
cd <user_provided_path>
[ -d ".git" ]  | | echo "❌ Not a git repository"
[ -f "galaxy.yml" ] && echo "✓ Ansible collection found"
```

**DO NOT ASSUME** any default path or directory structure - always ask user to provide the exact path.

## Critical Requirements

### 1. Auto-Dependency Management

**NEVER fail because a tool is missing.** Always:

- Create virtual environment if it doesn't exist
- Install required dependencies automatically
- Use `.venv/bin/<tool>` instead of global installs

### 2. Comprehensive Testing (MANDATORY)

**ALWAYS add both unit AND integration tests** for any code change:

- Unit tests: parameter validation, behavior, edge cases
- Integration tests: follow existing patterns, NO conditionals
- Read full test role structure before writing tests

### 3. Version Management

**Check stable branches, not main** to determine version_added:

- Find latest stable: `git branch -r | grep upstream/stable | sort -V | tail -1`
- Get version from stable: `git show upstream/stable-X:galaxy.yml`
- Use next minor: 11.2.0 → 11.3.0 (for features)

### 4. RETURN Block Validation

**Always verify RETURN block** when adding features:

- Check if new feature changes return values
- Update RETURN documentation if needed
- Verify examples are still accurate

### 5. Integration Test Best Practices

**Read full test role structure** before adding tests:

- `tasks/main.yml` - understand orchestration
- `tasks/common.yml` - understand helper tasks
- `defaults/main.yml` - understand available variables
- Read one similar test - understand patterns
- Use creative approaches instead of conditionals

## Implementation Workflow

### [1/13] Verify Collection Path and Load Plan

#### Step 1a: Ask user for collection path**

```
Which directory should I work in?
Please provide the full path to your collection git repository.

(This is the directory containing galaxy.yml and .git/)
```

#### Step 1b: Verify path and change directory**

```bash
cd <user_provided_path>
pwd  # Confirm working directory
```

#### Step 1c: Load implementation plan**

Read the implementation plan from `.bug-fixes/plan-N.md`:

- Extract files to modify
- Extract code changes needed
- Extract test strategy
- Identify if it's a bug fix or feature

### [2/13] Setup Dependencies

**Auto-install all required dependencies:**

```bash
# Create virtual environment if missing
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Install requirements
.venv/bin/pip install -q -r requirements.txt
.venv/bin/pip install -q -r test-requirements.txt

# Install test and formatting tools
.venv/bin/pip install -q pytest pytest-mock pytest-cov black isort flynt ruff tox
```

**Never proceed if dependencies fail to install.** Report the error to the user.

### [3/13] Determine version_added and check for breaking changes

#### CRITICAL: Check if the change is backward compatible**

#### Breaking Change Detection

A change is **BREAKING** if it:

- Removes a parameter or module
- Changes parameter behavior in an incompatible way
- Changes return value structure
- Requires users to modify existing playbooks
- Changes default behavior that breaks existing usage

**Examples:**

❌ **BREAKING:**

- Removing a parameter
- Changing parameter default from `false` to `true`
- Renaming a parameter without alias
- Changing return value structure
- Removing deprecated features before announced date

✅ **NOT BREAKING:**

- Adding a new optional parameter
- Adding a new module
- Adding a new return value
- Fixing a bug
- Adding deprecation warning

#### Version Calculation

```bash
# Find latest stable branch
STABLE_BRANCH=$(git branch -r | grep "upstream/stable-" | grep -v "patchback" | sort -V | tail -1 | tr -d ' ')

# Get version from stable branch
STABLE_VERSION=$(git show ${STABLE_BRANCH}:galaxy.yml | grep "^version:" | awk '{print $2}')
# Example: 11.2.0

MAJOR=$(echo $STABLE_VERSION | cut -d. -f1)
MINOR=$(echo $STABLE_VERSION | cut -d. -f2)

# For BREAKING changes: use next MAJOR version
if [[ "$IS_BREAKING" == "true" ]]; then
    NEXT_MAJOR=$((MAJOR + 1))
    VERSION_ADDED="${NEXT_MAJOR}.0.0"
    # Example: 11.2.0 → 12.0.0
else
    # For features: use next MINOR version
    NEXT_MINOR=$((MINOR + 1))
    VERSION_ADDED="${MAJOR}.${NEXT_MINOR}.0"
    # Example: 11.2.0 → 11.3.0
fi
```

**Use version_added:**

- **New features (not breaking):** Next minor (11.3.0)
- **Breaking changes:** Next major (12.0.0)
- **Bug fixes:** No version_added

**Changelog category:**

- **Breaking changes:** `breaking_changes`
- **New features:** `minor_changes`
- **Bug fixes:** `bugfixes`
- **Deprecations:** `deprecated_features`

### [4/13] Read Full Test Role Structure (before writing tests)

**For integration tests, read the complete structure:**

```bash
# Find the test target directory
TEST_DIR="tests/integration/targets/<module_name>/"

# Read these files to understand patterns:
1. ${TEST_DIR}/tasks/main.yml          # Test orchestration
2. ${TEST_DIR}/tasks/common.yml        # Helper tasks
3. ${TEST_DIR}/defaults/main.yml       # Available variables
4. ${TEST_DIR}/tasks/<similar_test>.yml # Existing test pattern
```

**Key patterns to look for:**

- How tests use `module_defaults`
- How tests use `common.yml` helpers (has_new_*, delete_*, etc.)
- What variables are available in defaults
- How similar features are tested

### [5/13] Apply Code Changes

Read affected files and apply changes:

```python
# Read all files mentioned in plan (in ONE message)
for file in plan.files_to_modify:
    read(file)

# Apply minimal changes with Edit tool
# For new parameters, include version_added
edit(file, old_code, new_code_with_version_added)
```

**For new parameters:**

```yaml
parameter_name:
  description: What this parameter does
  type: str
  version_added: "11.3.0"  # From step 3
```

### [6/13] Verify RETURN Block

**Always check the RETURN block when adding features:**

```python
# Read the RETURN section of the module
return_block = read_return_block(module_file)

# Ask yourself:
# 1. Does the new feature return new values?
# 2. Do existing return values change format?
# 3. Are examples in RETURN still accurate?

# If RETURN needs updates:
edit(module_file, old_return, new_return)
```

**Common cases:**

- New parameter that doesn't affect output → No RETURN changes
- New return value → Add to RETURN with examples
- Changed return format → Update RETURN documentation

### [7/13] Add Unit Tests (MANDATORY)

**Create unit tests following existing patterns:**

```python
# Determine test location
unit_test_dir = f"tests/unit/plugins/modules/{module_name}/"

# Check if directory exists
if not exists(unit_test_dir):
    # Look for parent structure
    unit_test_dir = f"tests/unit/plugins/modules/"

# Create test file
test_file = f"{unit_test_dir}/test_{feature_name}.py"

# Write comprehensive tests:
# 1. Test the new functionality works
# 2. Test parameter validation
# 3. Test edge cases
# 4. Test with mocks (don't call external APIs)
```

**Minimum test cases:**

- Happy path (feature works as expected)
- Parameter validation (required parameters, invalid values)
- Edge cases (None values, empty strings, etc.)
- Check mode behavior

**Example structure:**

```python
from unittest.mock import MagicMock, patch
import pytest
from ansible_collections.amazon.aws.plugins.modules import module_name

def test_feature_works():
    # Test normal operation
    pass

def test_parameter_validation():
    # Test required_by, invalid values
    pass

def test_edge_cases():
    # Test None, empty, boundary values
    pass

def test_check_mode():
    # Test check_mode doesn't make changes
    pass
```

### [8/13] Add Integration Tests (MANDATORY, NO CONDITIONALS)

**Integration tests MUST run in CI without special resources.**

#### Step 1: Read existing tests**

```bash
# Read the full test structure
cat tests/integration/targets/<module>/tasks/main.yml
cat tests/integration/targets/<module>/tasks/common.yml
cat tests/integration/targets/<module>/defaults/main.yml
cat tests/integration/targets/<module>/tasks/<similar_feature>.yml
```

#### Step 2: Check if you can integrate into existing tests**

**IMPORTANT:** Before creating new tests, check if you can integrate your new parameters into existing tests that already have the required resources set up.

**Prefer integration over duplication:**

```yaml
# ✅ BEST - Add parameters to existing test
- name: Enable DNSSEC for Route53 public zone  # Existing test
  amazon.aws.route53_zone:
    zone: "{{ resource_prefix }}.public"
    state: present
    dnssec: true
    wait: true              # ← NEW parameter added
    wait_timeout: 600       # ← NEW parameter added
  register: _hosted_zone_dnssec

# ✅ Resources already created by this test target:
# - KMS key
# - Key Signing Key
# - Route53 hosted zone
# ✅ Cleanup already handled in always block
```

**Only create new tests if:**

- No existing test covers the same resource/operation
- Your feature requires a completely different test setup
- Adding to existing tests would make them overly complex

#### Step 3: Find creative testing approach (if creating new tests)**

Instead of:

```yaml
# ❌ BAD - conditional test that won't run in CI
- name: Test feature
  when: special_resource_available
  block:
    - name: Use special resource
      module:
        special_param: "{{ special_resource }}"
```

Do this:

```yaml
# ✅ GOOD - creative approach that runs in CI
- name: Create resource for testing
  module:
    state: present
  register: created_resource

- name: Test feature using created resource
  module:
    special_param: "{{ created_resource.value }}"
  
- name: Cleanup
  module:
    state: absent
```

**Example from ec2_eip:**

```yaml
# Instead of requiring BYOIP pool (conditional):
# 1. Allocate IP from amazon pool (always available)
# 2. Release it
# 3. Re-allocate that same IP with address parameter
# 4. Verify it's the same IP
```

#### Step 4: Reuse existing resources when possible**

Look for related test targets that already set up the resources you need:

#### Example: Testing DNSSEC wait functionality**

```yaml
# ❌ BAD - Creating duplicate resources
# In route53_zone tests:
- name: Create KMS key
- name: Create Key Signing Key
- name: Activate KSK
- name: Test DNSSEC with wait

# ✅ GOOD - Reuse existing resources
# In route53_key_signing_key tests (already creates KMS + KSK):
- name: Enable DNSSEC with wait  # Just add wait params to existing test
  amazon.aws.route53_zone:
    wait: true
    wait_timeout: 600
```

#### Critical: Always ensure cleanup**

- If you create new resources, add cleanup to the `always` block
- If you integrate into existing tests, verify cleanup is already handled
- Cleanup should handle failures gracefully (`ignore_errors: true`)

#### Step 5: Follow existing patterns**

Use the same structure as existing tests:

- Use `common.yml` helpers (has_new_*, has_no_new_*, delete_*)
- Use variables from `defaults/main.yml`
- Follow `check_mode` → actual → idempotence pattern
- Include cleanup in `always` block

#### Step 6: Write integration test (if creating new tests)**

```yaml
- name: Test new feature - check_mode
  module_name:
    new_parameter: value
  register: result
  check_mode: true

- ansible.builtin.assert:
    that:
      - result is changed

- name: Ensure no changes in check mode
  ansible.builtin.include_tasks: tasks/common.yml
  vars:
    has_no_new_resource: true

- name: Test new feature
  module_name:
    new_parameter: value
  register: result

- ansible.builtin.assert:
    that:
      - result is changed
      - result.expected_value is defined

- name: Ensure resource was created
  ansible.builtin.include_tasks: tasks/common.yml
  vars:
    has_new_resource: true

- name: Test idempotence
  module_name:
    new_parameter: value
  register: result

- ansible.builtin.assert:
    that:
      - result is not changed
```

### [9/13] Format Code

**Auto-format all changed files:**

```bash
# Install formatters if needed (already done in step 2)
# Format Python files
.venv/bin/black <changed_files>
.venv/bin/isort <changed_files>

# Check if formatters made changes
git diff <changed_files>

# If changes, stage them
git add <changed_files>
```

### [10/13] Create Changelog Fragment (MANDATORY)

**Every code change MUST have a changelog fragment.**

#### Determine Changelog Category

Based on antsibull-changelog categories:

- `breaking_changes` - Backward incompatible changes
- `major_changes` - Major new features
- `minor_changes` - Minor new features (most common)
- `deprecated_features` - Feature deprecations
- `removed_features` - Feature removals
- `security_fixes` - Security-related fixes
- `bugfixes` - Bug fixes
- `known_issues` - Known issues

**Common categories:**

- New parameter/feature: `minor_changes`
- Bug fix: `bugfixes`
- Breaking change: `breaking_changes`
- Deprecation: `deprecated_features`

#### Create Fragment File

**Naming convention:** `<issue_number>-<short_description>.yml`

**Example:** `2755-ec2_eip-address-parameter.yml`

**Format:**

```yaml
<category>:
  - <module_name> - <description>. (<link_to_issue_or_pr>)
```

**Examples:**

**For new feature (minor_changes):**

```yaml
minor_changes:
  - ec2_eip - added ``address`` parameter to allow allocating a specific IP address from a BYOIP pool (https://github.com/ansible-collections/amazon.aws/issues/2755).
```

**For bug fix (bugfixes):**

```yaml
bugfixes:
  - ec2_instance - fixed KeyError when optional_param is missing (https://github.com/ansible-collections/amazon.aws/issues/123).
```

**For breaking change (breaking_changes):**

```yaml
breaking_changes:
  - ec2_instance - removed deprecated ``instance_id`` parameter, use ``instance_ids`` instead (https://github.com/ansible-collections/amazon.aws/issues/456).
```

**For deprecation (deprecated_features):**

```yaml
deprecated_features:
  - ec2_instance - the ``instance_id`` parameter has been deprecated and will be removed in version 13.0.0. Use ``instance_ids`` instead (https://github.com/ansible-collections/amazon.aws/issues/789).
```

#### Create the Fragment

```bash
# Determine issue number from plan
ISSUE_NUMBER="<from plan or git branch>"

# Determine category
if [[ "$IS_BREAKING" == "true" ]]; then
    CATEGORY="breaking_changes"
elif [[ "$IS_BUG_FIX" == "true" ]]; then
    CATEGORY="bugfixes"
else
    CATEGORY="minor_changes"
fi

# Create fragment file
FRAGMENT_FILE="changelogs/fragments/${ISSUE_NUMBER}-<short-description>.yml"

cat > "$FRAGMENT_FILE" <<EOF
${CATEGORY}:
  - <module_name> - <description>. (<issue_link>)
EOF
```

**Fragment content guidelines:**

- Use backticks around parameter names: \`\`address\`\`
- Be concise but descriptive
- Include link to issue or PR
- Explain user benefit, not technical details

### [11/13] Validate Implementation

**Run syntax checks and unit tests:**

```bash
# Python syntax validation
for file in <changed_files>; do
    python3 -m py_compile $file
done

# Run unit tests
.venv/bin/pytest tests/unit/<relevant_tests>/ -v

# Note: Integration tests run in CI after PR creation
```

**Checklist before completing:**

- [ ] Breaking change check performed
- [ ] Code changes applied
- [ ] version_added set correctly (major for breaking, minor for features)
- [ ] RETURN block verified/updated
- [ ] Documentation example added
- [ ] Unit tests added (minimum 3 test cases)
- [ ] Integration tests added (NO conditionals)
- [ ] Integration tests follow existing patterns
- [ ] Code formatted (black, isort)
- [ ] Changelog fragment created (MANDATORY)
- [ ] Syntax validation passed
- [ ] Unit tests run locally

### [12/13] Report Ready for Git Operations

#### Implementation is complete - now ready for manual git operations**

Report to the user that the implementation is complete and provide clear instructions for creating a branch and committing. **DO NOT execute git commands automatically** - the user should run them manually.

**Output to user:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ready for Git Operations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Files modified:
  M  plugins/modules/route53_zone.py
  A  tests/unit/plugins/modules/test_route53_zone_wait.py
  A  changelogs/fragments/2981-route53_zone-wait-dnssec.yml

Next steps (run manually):

1. Create feature branch from main (synced with upstream):
   git checkout main
   git pull upstream main
   git push origin main  # (optional) sync your fork's main
   git checkout -b feature-<issue>-<description>

2. Stage and commit changes:
   git add plugins/modules/route53_zone.py \
           tests/unit/plugins/modules/test_route53_zone_wait.py \
           changelogs/fragments/2981-route53_zone-wait-dnssec.yml
   
   git commit -m "feat: add waiter support for Route53 DNSSEC operations

   Add wait and wait_timeout parameters to route53_zone module.
   
   Closes #2981
   
   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

3. Push to YOUR FORK and create PR:
   git push origin feature-<issue>-<description>
   gh pr create --title "..." --body "..."

Note: Branch is created from main (synced with upstream) but pushed to 
your fork (origin). PR will be from your fork to upstream.
```

**Important reminders for the user:**

**Branch Naming Convention:**

- Features: `feature-<issue>-<description>`
- Bug fixes: `fix-<issue>-<description>`
- Enhancements: `enhance-<issue>-<description>`

**Git Branching Strategy (CRITICAL):**

- ✅ **Default:** Create ALL branches from `main` (features, bugfixes, enhancements)
- ❌ **Exception:** Only branch from `stable-X` if user explicitly states:
  - "fix this on stable-11"
  - "backport to stable-X"
  - Otherwise: **ALWAYS use main**

**Commit Message Format:**

- Features: `feat: <description>`
- Bug fixes: `fix: <description>`
- Breaking changes: `feat!:` or `fix!:`
- Always include: `Closes #<issue>` and `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`

### [13/13] Summary

**Provide final summary without executing any git commands:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Implementation Complete! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
  Issue: #2981
  Type: Feature (minor_changes)
  Files changed: 3
  - plugins/modules/route53_zone.py (+53 lines)
  - tests/unit/plugins/modules/test_route53_zone_wait.py (+115 lines, new)
  - changelogs/fragments/2981-route53_zone-wait-dnssec.yml (+3 lines, new)
  
  version_added: "11.4.0"
  Breaking changes: None
  
All implementation steps complete. Ready for manual git operations.
```

## Output Format

Provide clear progress updates:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Implementation: Issue #NNNN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/13] Loaded implementation plan
      Plan: Add parameter X to module Y
      Type: Feature

[2/13] Setup dependencies
      ✓ Created .venv
      ✓ Installed requirements
      ✓ Installed test tools

[3/13] Determined version_added
      Breaking change check: No
      Stable branch: upstream/stable-11
      Stable version: 11.2.0
      version_added: "11.3.0"
      Changelog category: minor_changes

[4/13] Read test role structure
      ✓ Read tasks/main.yml
      ✓ Read tasks/common.yml
      ✓ Read defaults/main.yml
      ✓ Identified pattern from similar test

[5/13] Applied code changes
      Modified: plugins/modules/module_y.py (+25, -5)
      - Added parameter_x with version_added: "11.3.0"
      - Updated function to use parameter_x

[6/13] Verified RETURN block
      ✓ No changes needed (parameter is input-only)

[7/13] Added unit tests
      Created: tests/unit/plugins/modules/module_y/test_parameter_x.py
      - 4 test cases added
      ✓ All tests pass

[8/13] Added integration tests
      Modified: tests/integration/targets/module_y/tasks/feature_x.yml
      - Test uses creative approach (no conditionals)
      - Follows existing patterns
      - Uses common.yml helpers

[9/13] Formatted code
      ✓ black: 2 files reformatted
      ✓ isort: imports sorted

[10/13] Created changelog fragment
      File: changelogs/fragments/NNNN-module_y-parameter_x.yml
      Category: minor_changes
      ✓ Fragment created

[11/13] Validation
      ✓ Syntax check passed
      ✓ Unit tests passed (4/4)
      ✓ Changelog fragment valid

[12/13] Ready for Git Operations
      ✓ Implementation complete
      ✓ Files ready to commit (3 modified)

[13/13] Summary
      Issue: #NNNN (feature)
      Files: 3 changed (+171, -6)
      version_added: "11.3.0"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Implementation Complete! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
  Issue: #NNNN (feature)
  Files changed: 3
  - plugins/modules/module_y.py (+25, -5)
  - tests/unit/plugins/modules/test_module_y.py (+110 lines, new)
  - changelogs/fragments/NNNN-module-y-parameter.yml (+3 lines, new)
  
  version_added: "11.3.0"
  Breaking changes: None

Next steps (run manually):

1. Create feature branch:
   git checkout main
   git pull upstream main
   git checkout -b feature-NNNN-module-y-parameter

2. Commit changes:
   git add plugins/modules/module_y.py \
           tests/unit/plugins/modules/test_module_y.py \
           changelogs/fragments/NNNN-module-y-parameter.yml
   
   git commit -m "feat: add parameter_x to module_y
   
   <description>
   
   Closes #NNNN
   
   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

3. Push and create PR:
   git push origin feature-NNNN-module-y-parameter
   gh pr create --title "feat: add parameter_x to module_y" --body "..."
```

## Error Handling

### Dependency Installation Fails

```
❌ Failed to install dependencies

Error: pip install failed with:
<error message>

Action required:
  1. Check internet connection
  2. Verify requirements.txt exists
  3. Try manual install: .venv/bin/pip install -r requirements.txt
```

### No Existing Tests Found

```
⚠️  No existing tests found for module_y

Creating new test structure:
  - tests/unit/plugins/modules/module_y/__init__.py
  - tests/unit/plugins/modules/module_y/test_parameter_x.py

Note: Follow Ansible collection test patterns
```

### Version Detection Fails

```
⚠️  Could not determine version from stable branch

Using fallback:
  - Checked main branch: 12.0.0-dev0
  - Using: version_added: "12.0.0"

⚠️  Warning: This may be incorrect. Please verify the version manually.
```

## Common Pitfalls

### ❌ DON'T

- Skip tests ("I'll add them later")
- Use conditional integration tests (`when: resource_available`)
- Use global tool installations (might not exist)
- Guess version_added from main branch
- Skip RETURN block validation
- Only read one test file (miss patterns)

### ✅ DO

- Always add comprehensive tests (unit + integration)
- Find creative ways to test without special resources
- Auto-install dependencies in virtual environment
- Check version_added from latest stable branch
- Verify RETURN block for any feature change
- Read full test role structure before writing tests

## Integration with Other Skills

This skill is used by:

- `/issue-fix` - Complete issue resolution workflow
- Can be called standalone after `/issue-plan`

This skill uses:

- Implementation plan from `/issue-plan`
- Repository configuration from `~/.claude/skills/issue-fix.conf`

## Examples

**Usage:**

```bash
# With full GitHub URL (recommended - copy/paste from browser)
/issue-implement https://github.com/ansible-collections/amazon.aws/issues/2755

# After /issue-plan (uses last plan)
/issue-implement

# With issue number (detects repo from current directory)
/issue-implement --issue 2755
```

**Tip:** Using full URLs is recommended - just copy/paste from your browser!

### Example 1: Add New Parameter to Module

```bash
# Plan already created by /issue-plan
/issue-implement

# Output:
# [1/13] Loaded plan: Add 'address' parameter to ec2_eip
# [2/13] Dependencies installed
# [3/13] version_added: "11.3.0"
# [4/13] Read test structure (4 files)
# [5/13] Code changes applied (+25, -5)
# [6/13] RETURN verified (no changes)
# [7/13] Unit tests added (4 tests, 110 lines)
# [8/13] Integration tests added (75 lines, no conditionals)
# [9/13] Code formatted
# [10/13] Changelog fragment created
# [11/13] Validation passed
# [12/13] Feature branch created: feature-2755-ec2-eip-address
# [13/13] Changes committed: a1b2c3d
# ✓ Implementation complete!
```

### Example 2: Fix Bug in Module

```bash
/issue-implement --issue 123

# Output:
# [1/13] Loaded plan: Fix KeyError in xyz module
# [2/13] Dependencies installed
# [3/13] version_added: N/A (bug fix)
# [4/13] Read test structure
# [5/13] Code changes applied (+2, -2)
# [6/13] RETURN verified (no changes)
# [7/13] Unit tests added (1 regression test)
# [8/13] Integration tests added (1 regression test)
# [9/13] Code formatted
# [10/13] Changelog fragment created
# [11/13] Validation passed
# [12/13] Bugfix branch created: fix-123-xyz-keyerror
# [13/13] Changes committed: b2c3d4e
# ✓ Bug fix complete!
```

## Testing This Skill

To verify this skill works correctly, test with:

1. A simple parameter addition (like ec2_eip address parameter)
2. A bug fix (minimal change with regression test)
3. A complex feature (new functionality with multiple tests)

Expected behavior:

- Dependencies auto-installed
- Correct version_added detected
- Both unit and integration tests created
- Integration tests have no conditionals
- RETURN block validated
- Code formatted automatically

---

**Last Updated:** Based on issue #2755 implementation (2026-04-02)
