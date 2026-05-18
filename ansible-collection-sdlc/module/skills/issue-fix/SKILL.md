---
name: issue-fix
description: Generic issue resolution workflow. Auto-detects bug vs feature, analyzes issue, creates plan, implements with tests, runs quality checks, and creates PR. Adapts workflow based on issue type (bug/feature/enhancement). Use for any GitHub issue.
imports:
  - issue-analyze
  - issue-plan
  - issue-implement
  - lint-fix
  - lint
  - pr-create
---

# Issue Fix Orchestrator

Complete end-to-end issue resolution workflow from GitHub issue to pull request. Auto-detects issue type and adapts approach.

## Author

**Alina Buzachis (alinabuzachis)** - Ansible Cloud Content Team

## Purpose

Generic issue handler that orchestrates the entire resolution process: analyze issue, plan implementation, code with tests, ensure quality, and create PR. Automatically adapts workflow based on whether it's a bug fix, feature request, or enhancement.

## When to Use

- Asked to fix/implement any GitHub issue
- Automated issue resolution workflows
- Complete implementation from start to finish
- When you're unsure if it's a bug or feature

## Usage

```bash
# Auto-detect issue type and handle appropriately
/issue-fix https://github.com/owner/repo/issues/123

# Or with just issue number (detects repo from context)
/issue-fix --issue 123

# Analyze only
/issue-fix --issue 123 --analyze-only

# Skip PR creation
/issue-fix --issue 123 --no-pr

# For Ansible collection (includes sanity)
/issue-fix --issue 123 --ansible

# Manual control (step through)
/issue-fix --issue 123 --interactive

# Force specific approach
/issue-fix --issue 123 --type=bug       # Minimal fix approach
/issue-fix --issue 123 --type=feature   # Feature implementation
```

## Git Branching Strategy

**CRITICAL**: All feature branches and bugfix branches MUST be created from `main` unless explicitly stated otherwise by the user.

### Default Behavior

- **Features**: Create branch from `main` (NOT from stable-X branches)
- **Bugfixes**: Create branch from `main` (NOT from stable-X branches)
- **Enhancements**: Create branch from `main` (NOT from stable-X branches)

### Exception Cases (ONLY if user explicitly states)

- User says: "fix this on stable-11" → create branch from stable-11
- User says: "backport to stable-X" → create branch from stable-X
- Otherwise: **ALWAYS use main**

### Why This Matters

- Features go to main first, then backported if needed
- Bugfixes go to main first, then cherry-picked to stable branches
- Creating from stable-X by mistake requires force-push to fix

### Verification Before Creating Branch

```bash
# ALWAYS check current branch before creating feature branch
git branch --show-current

# If not on main, switch to main first
git checkout main
git pull upstream main

# THEN create feature branch
git checkout -b feature-NNNN-description
```

## Auto-Detection Logic

The skill analyzes the issue and automatically determines the approach:

```
IF issue has label "bug" OR type is "Bug Report":
  → BUG FIX approach
    - Minimal, surgical changes
    - Focus on regression tests
    - Commit: "fix: ..."
    
ELSE IF issue has label "feature" OR type is "Feature Idea":
  → FEATURE IMPLEMENTATION approach
    - New functionality
    - Comprehensive test coverage
    - Commit: "feat: ..."
    
ELSE IF issue has label "enhancement":
  → ENHANCEMENT approach
    - Improve existing feature
    - Test enhancements
    - Commit: "enhance: ..."
    
ELSE:
  → ASK USER which approach to use
```

## Workflow Steps

### [1/7] Pull & Analyze Issue

```bash
/issue-analyze --issue 123
```

- Fetches issue from GitHub
- **Auto-detects issue type** from labels, title, body
- Validates it's actionable
- Extracts key information
- **Output**: Issue summary in `.bug-fixes/issue-123.md`

**Example Output**:

```
Issue #2755: Allow ec2_eip to assign specific IP from byoip pool
Type: FEATURE REQUEST 🆕
Actionability: HIGH ✅
Approach: Feature implementation

Auto-detected because:
  - Label: "feature"
  - Issue type: "Feature Idea"
  - Missing API parameter exposure

Proceed with implementation? [Y/n]:
```

### [2/7] Create Implementation Plan

```bash
/issue-plan
```

- Analyzes code to understand current implementation
- **Checks for breaking changes** (backward compatibility)
- Determines correct version_added (major for breaking, minor for features)
- Proposes changes (minimal for bugs, comprehensive for features)
- Plans test strategy based on issue type
- **Plans changelog fragment** (category and content)
- **Output**: Plan in `.bug-fixes/plan-123.md`

**Bug approach**:

```
Plan: Fix KeyError by adding .get() with default
Risk: LOW
Scope: 2 line change
Tests: 1 regression test
Breaking: NO
version_added: N/A (bug fix)
Changelog: bugfixes
```

**Feature approach**:

```
Plan: Add 'address' parameter to ec2_eip module
Risk: MEDIUM
Scope: 
  - Module parameter addition (15 lines)
  - API call modification (5 lines)
  - Documentation update (10 lines)
Tests: 
  - 2 unit tests (parameter validation)
  - 1 integration test (specific IP assignment)
Breaking: NO (optional parameter, backward compatible)
version_added: "11.3.0" (next minor from stable-11)
Changelog: minor_changes (new feature)
Fragment: 2755-ec2_eip-address-parameter.yml
```

### [3/7] Implement Changes

```bash
/issue-implement
```

- Auto-installs dependencies (pytest, black, isort, etc.)
- Detects breaking changes and calculates version_added
- Applies code changes based on plan
- Validates RETURN block
- **Adds MANDATORY unit tests** (minimum 3 test cases - NO EXCEPTIONS)
- **Adds MANDATORY integration tests** (when applicable - NO SKIPPING)
- Formats code automatically
- **Creates changelog fragment** (MANDATORY)
- Validates implementation

**CRITICAL TESTING REQUIREMENTS**:

Testing is **MANDATORY**, not optional. Every implementation MUST include tests:

1. **Unit Tests Required** (ALWAYS):
   - Minimum 3 test cases
   - Test parameter acceptance
   - Test parameter conversion (e.g., snake_case → CamelCase)
   - Test parameter passing to boto3/underlying API
   - File location: `tests/unit/plugins/modules/test_<module>.py`

2. **Integration Tests** (when applicable):
   - Test actual AWS API interaction
   - Test idempotency (run twice, second run unchanged)
   - Test check mode
   - File location: `tests/integration/targets/<module>/tasks/main.yml`

3. **For New Module Parameters** (Ansible collections):
   - MUST verify parameter is passed to boto3 correctly
   - MUST test both valid choices/values
   - MUST test default value behavior
   - Example reference: Look at existing parameters in the same module

**How to Find Test Patterns**:

```bash
# Find existing unit tests for the module
ls tests/unit/plugins/modules/test_<module>.py

# Read existing tests to understand patterns
# Look for recent parameter additions in git history
git log --all --oneline -- tests/unit/plugins/modules/test_<module>.py

# Find a similar parameter's implementation
git log --all --grep="add.*parameter" --oneline
git show <commit-hash>
```

**Output varies by type**:

```
BUG FIX (minimum 3 files changed):
✅ Fix implemented
- plugins/modules/xyz.py (+2, -2)
- tests/unit/plugins/modules/test_xyz.py (+15, -0)  ← MANDATORY
- changelogs/fragments/123-xyz-fix-keyerror.yml (+2, -0)

FEATURE (minimum 4 files changed):
✅ Feature implemented
- plugins/modules/ec2_eip.py (+25, -5)
- plugins/modules/ec2_eip.py (docstring) (+10, -0)
- tests/unit/plugins/modules/test_ec2_eip.py (+45, -0)  ← MANDATORY
- tests/integration/targets/ec2_eip/tasks/main.yml (+30, -0)  ← MANDATORY (when applicable)
- changelogs/fragments/2755-ec2_eip-address-parameter.yml (+2, -0)
```

**Verification Checklist Before Committing**:

- [ ] Module code changed
- [ ] Unit tests added (minimum 3 test cases)
- [ ] Integration tests added (if applicable)
- [ ] Tests verify parameter passing to boto3
- [ ] Changelog fragment created
- [ ] All tests pass locally
- [ ] Lint checks pass

**Note:** Step [3/7] Implement Changes actually runs 11 internal steps:

- Setup deps, check breaking changes, apply code, verify RETURN,
  **add unit tests** (MANDATORY), **add integration tests** (MANDATORY when applicable), format, create changelog, validate

### [4/7] Auto-Fix Style

```bash
/lint-fix
```

- Already done in /issue-implement step
- This step can be skipped as formatting is now automatic

### [5/7] Quality Checks (Parallel)

```bash
# Run in parallel
/lint &
/sanity --mode=smart &  # Only if --ansible flag
wait
```

### [6/7] Commit Changes

**Commit message adapts to issue type**:

```bash
# Bug fix:
git commit -m "fix: resolve KeyError in xyz module

Handle missing parameter by using .get() with default value.

Fixes #123

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Feature:
git commit -m "feat: add support for specific IP assignment in ec2_eip

Allow users to assign specific public IPs from BYOIP pools by
adding 'address' parameter. AWS EC2 API already supports this.

Closes #2755

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Enhancement:
git commit -m "enhance: improve error handling in xyz module

Add detailed error messages and validation.

Closes #456

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### [7/7] Create Pull Request

```bash
/pr-create --title "<commit-type> #123: <issue title>"
```

**PR title/body adapts**:

- **Bug**: "Fix #123: ..." - emphasizes the fix
- **Feature**: "Add support for specific IP assignment (#2755)" - describes capability
- **Enhancement**: "Improve error handling (#456)" - describes improvement

## Complete Output Example (Feature)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue Resolution Workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: #2755
Repository: ansible-collections/amazon.aws

[1/7] Analyzing issue...
      Running: /issue-analyze --issue 2755

      ✅ Issue analyzed
      Title: Allow ec2_eip to assign specific IP from byoip pool
      Type: FEATURE REQUEST 🆕
      Actionability: HIGH
      
      Auto-detected approach: Feature implementation
      Reason: Issue labeled as "feature" and describes missing API parameter

      Proceed with implementation? [Y/n]: y

[2/7] Creating implementation plan...
      Running: /issue-plan

      ✅ Plan created
      Approach: Add 'address' parameter to module
      Risk: MEDIUM
      Scope: 
        - Module: +25 lines (parameter, validation, API call)
        - Tests: +75 lines (unit + integration)
        - Docs: +10 lines (parameter documentation)

      Review plan? [Y/n]: n

[3/7] Implementing feature...
      Running: /issue-implement

      ✅ Feature implemented
      - plugins/modules/ec2_eip.py (+25, -5)
      - tests/unit/plugins/modules/test_ec2_eip.py (+45, -0)
      - tests/integration/targets/ec2_eip/tasks/main.yml (+30, -0)

[4/7] Auto-fixing style...
      Running: /lint-fix

      ✅ Style fixed
      - black: 3 files reformatted
      - isort: imports sorted

[5/7] Running quality checks...
      Running: /lint (parallel)
      Running: /sanity --mode=smart (parallel)

      ✅ lint: All checks passed (2.3s)
      ✅ sanity: All tests passed (18.7s)

[6/7] Committing changes...

      ✅ Committed: b4c7d9e
      Message: feat: add support for specific IP assignment in ec2_eip
      ✅ Pushed to origin/feature-2755-eip-specific-ip

[7/7] Creating pull request...
      Running: /pr-create

      ✅ PR created: https://github.com/ansible-collections/amazon.aws/pull/2800

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue resolution complete! 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
  Issue: #2755 (feature)
  Implementation: Add 'address' parameter for specific IP assignment
  Files: 3 modified
  Tests: 4 tests added (2 unit, 2 integration)
  PR: https://github.com/ansible-collections/amazon.aws/pull/2800

Next steps:
  1. Monitor PR: gh pr view 2800
  2. Wait for CI checks
  3. Address review feedback if needed

Total time: 62.4 seconds
```

## Flags & Options

| Flag | Description |
|------|-------------|
| `--issue N` or URL | GitHub issue number or full URL (required) |
| `--type bug\|feature\|enhance` | Force specific approach (overrides auto-detect) |
| `--analyze-only` | Stop after analysis |
| `--no-pr` | Skip PR creation |
| `--ansible` | Run Ansible sanity tests |
| `--interactive` | Pause for confirmation at each step |
| `--auto` | No prompts (use for automation) |
| `--dry-run` | Show what would happen |

## Issue Type Comparison

| Aspect | Bug Fix | Feature | Enhancement |
|--------|---------|---------|-------------|
| **Scope** | Minimal | New functionality | Improve existing |
| **Testing** | Regression test | Comprehensive | Enhanced coverage |
| **Docs** | Usually none | Required | Update existing |
| **Commit** | `fix:` | `feat:` | `enhance:` |
| **Risk** | Low | Medium-High | Low-Medium |
| **Review** | Quick | Thorough | Moderate |

## Gray Areas

Some issues blur the line between bug and feature:

**Example**: "Module doesn't support AWS API parameter X"

- **Bug perspective**: Incomplete API coverage
- **Feature perspective**: Missing capability

**How we handle it**:

1. Check labels first
2. Look for keywords ("should work but doesn't" = bug)
3. If unclear, ask user or default to feature approach (safer)

## Error Handling

### Recoverable Errors

- **Quality checks fail**: Offer retry after manual fix
- **Tests fail**: Show test output, allow fixing
- **PR exists**: Update existing PR
- **Unsure about type**: Ask user to confirm

### Non-Recoverable Errors

- **Issue not found**: Check issue number
- **No actionable issue**: Issue needs more info
- **Merge conflicts**: Resolve manually

## Integration Points

This orchestrator imports:

- `/issue-analyze` - Fetch and analyze issue (enhanced with type detection)
- `/issue-plan` - Create implementation plan (adapts to issue type)
- `/issue-implement` - Apply changes + tests (scales scope based on type)
- `/lint-fix` - Auto-fix formatting
- `/lint` - Run linters
- `/sanity` - Run sanity (Ansible only)
- `/pr-create` - Create pull request (adapts title/body)

## Ansible Detection

Auto-detects if it's an Ansible collection:

```bash
if [ -f "galaxy.yml" ]; then
    echo "Ansible collection detected"
    RUN_SANITY=true
fi
```

## Ansible Module Parameter Implementation Checklist

When adding a new parameter to an Ansible module, follow this complete checklist:

### 1. Module Code Changes

- [ ] Add parameter to DOCUMENTATION block with:
  - `description:` - what the parameter does
  - `type:` - str, int, bool, list, dict, etc.
  - `choices:` - valid values (if applicable)
  - `default:` - default value (if applicable)
  - `version_added:` - when parameter was added
  - Use proper Ansible markup: `V()` for values, `O()` for options
- [ ] Add parameter to argument spec in `main()` function:

  ```python
  argument_spec=dict(
      ...
      network_type=dict(type="str", choices=["IPV4", "DUAL"], default="IPV4"),
  )
  ```

- [ ] Verify parameter is passed to boto3/API:
  - Check if automatic (e.g., via `format_rds_client_method_parameters`)
  - Or add manual parameter passing code

### 2. Unit Tests (MANDATORY)

Add to `tests/unit/plugins/modules/test_<module>.py`:

- [ ] Test 1: Parameter acceptance

  ```python
  def test_network_type_parameter():
      """Test network_type parameter is accepted by module"""
  ```

- [ ] Test 2: Parameter conversion

  ```python
  def test_network_type_conversion():
      """Test network_type converts to NetworkType for boto3"""
  ```

- [ ] Test 3: Parameter in create call

  ```python
  def test_create_with_network_type():
      """Test network_type passed to create_db_instance"""
  ```

- [ ] Test 4: Parameter in modify call (if applicable)

  ```python
  def test_modify_with_network_type():
      """Test network_type passed to modify_db_instance"""
  ```

- [ ] Test 5: Default value

  ```python
  def test_network_type_default():
      """Test default value when not specified"""
  ```

- [ ] Test 6: All valid choices

  ```python
  @pytest.mark.parametrize("network_type", ["IPV4", "DUAL"])
  def test_network_type_choices(network_type):
  ```

### 3. Integration Tests (when applicable)

Add to `tests/integration/targets/<module>/tasks/main.yml`:

- [ ] Test parameter with valid value
- [ ] Test idempotency (run twice, second unchanged)
- [ ] Test check mode

### 4. Changelog Fragment (MANDATORY)

Create `changelogs/fragments/<issue>-<module>-<parameter>.yml`:

```yaml
minor_changes:
  - <module> - add support for ``parameter_name`` parameter (https://github.com/ansible-collections/amazon.aws/issues/<issue>).
```

### 5. Verification Before Commit

```bash
# Run unit tests
pytest tests/unit/plugins/modules/test_<module>.py -v

# Run integration tests (if added)
ansible-test integration <module> --docker

# Run linters
tox -e black-lint,flake8-lint,pylint-lint

# Verify files changed (should be 3+)
git status
```

**Expected file count**:

- Bug fix: 3 files (module, unit test, changelog)
- Feature: 4+ files (module, unit test, integration test, changelog)

## Implementation Notes

- **CRITICAL**: All branches created from `main` unless user explicitly states otherwise
- **CRITICAL**: Unit tests are MANDATORY, not optional
- **CRITICAL**: Must verify parameter passing to boto3/underlying API
- Auto-detect issue type from labels, keywords, and structure
- Adapt commit message format (fix:/feat:/enhance:)
- Scale test coverage based on issue type
- Provide clear progress indicators
- Handle gray areas gracefully
- Works with any GitHub repository
- Supports both Ansible and generic Python projects
- Backward compatible with `/bug-fix` (treat all as bugs)
