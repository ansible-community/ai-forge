---
name: issue-plan
description: Create a detailed implementation plan for any issue (bug/feature/enhancement). Analyzes code, identifies approach, proposes changes, and outlines test strategy. Use after /issue-analyze, when asked to "plan implementation", "create plan", or before implementing changes.
---

# Issue Plan Skill

Analyze code and create a detailed implementation plan for any issue type.

## Author

**Alina Buzachis (alinabuzachis)** - Ansible Cloud Content Team

## Purpose

Reads relevant code, identifies root cause, proposes a minimal and self-contained fix, and creates a step-by-step implementation plan with test strategy.

## When to Use This Skill

- After `/bug-pull` analyzes an issue
- Before implementing a fix
- To understand root cause
- To get team alignment on approach
- Part of bug-fix workflow

## Prerequisites

**Required:**

- Issue summary from `/issue-analyze` (in `.bug-fixes/issue-N.md`)
- Access to codebase (local clone)
- Git repository

**Optional (Enhanced Features):**

- **GitHub MCP server** (see `GITHUB_MCP_SETUP.md`)
  - Access code from GitHub for comparison
  - Check commit history for context
  - Compare branches to find existing fixes
  - Falls back to local git if not available

## Usage Examples

```bash
# Plan with full GitHub URL (recommended - copy/paste from browser)
/issue-plan https://github.com/ansible-collections/amazon.aws/issues/2755

# Create plan from last analyzed issue
/issue-plan

# Create plan for specific issue (detects repo from current directory)
/issue-plan --issue 2755

# Show plan without saving
/issue-plan https://github.com/owner/repo/issues/123 --dry-run
```

**Tip:** Using full URLs is recommended - just copy/paste from your browser!

## Expected Behavior

When this skill is invoked:

1. **Load issue summary**

   ```bash
   # Find latest issue summary
   LATEST_ISSUE=$(ls -t .bug-fixes/issue-*.md 2>/dev/null | head -1)
   
   if [ -z "$LATEST_ISSUE" ]; then
       echo "Error: No issue summary found"
       echo "Run /bug-pull --issue N first"
       exit 1
   fi
   
   ISSUE_NUMBER=$(basename "$LATEST_ISSUE" .md | sed 's/issue-//')
   echo "Planning fix for issue #$ISSUE_NUMBER"
   ```

2. **Read issue summary** (batch file operations)

   ```bash
   # Read the issue summary created by bug-pull
   ISSUE_SUMMARY=$(cat ".bug-fixes/issue-$ISSUE_NUMBER.md")
   
   # Extract affected files list
   AFFECTED_FILES=$(grep "Affects:" "$LATEST_ISSUE" | sed 's/.*Affects: //')
   ```

3. **Identify and read relevant code** (batch in ONE message)

   **CRITICAL**: Read all relevant files in parallel to minimize prompts:

   ```bash
   # Find affected files mentioned in issue
   # Read them ALL in one message with multiple Read tool calls
   ```

   Example files to read:
   - Primary affected file (from issue)
   - Related test files
   - Module utils/dependencies
   - Related documentation

4. **Analyze root cause**

   Based on error message and code:

   ```python
   # Example: KeyError analysis
   
   # Issue says: KeyError: 'optional_param'
   # Code shows:
   def my_function(params):
       value = params['optional_param']  # ← BUG: assumes key exists
       ...
   
   # Root cause: Code doesn't handle missing optional parameter
   # Should use: params.get('optional_param', default_value)
   ```

   **Analysis steps:**
   - Locate exact line causing error
   - Understand why error occurs
   - Check if it's a logic error, missing validation, or edge case
   - Identify assumptions in code that are violated

5. **Check for similar fixes** (optional, GitHub MCP only)

   If GitHub MCP is available, search for similar issues/fixes:

   **Method A: GitHub MCP (Enhanced)**

   ```python
   # Search for similar issues
   similar_issues = github_search_issues(
       repo=REPO,
       query=f"is:closed {affected_file} {error_keyword}"
   )
   
   # Find related PRs
   related_prs = github_search_issues(
       repo=REPO,
       query=f"is:pr is:merged {affected_file}",
       sort="updated",
       order="desc"
   )
   
   # Check commit history for affected file
   file_history = github_list_commits(
       repo=REPO,
       path=affected_file,
       per_page=10
   )
   
   # Benefits:
   # - See how similar issues were fixed
   # - Avoid duplicating work
   # - Learn from past solutions
   # - Identify patterns in fixes
   ```

   **Method B: Local git (Fallback)**

   ```bash
   # Check recent changes to affected file
   git log --oneline -10 -- plugins/modules/xyz.py
   
   # Search for similar fix keywords
   git log --grep="KeyError" --grep="optional" --all
   ```

   **Use findings to inform approach:**
   - If similar fix exists: Follow established pattern
   - If related PR merged: Check if it partially addresses this
   - If pattern emerges: Apply consistent solution

6. **Propose minimal fix**

   **Principle**: Self-contained, minimal changes

   ```python
   # ❌ BAD: Over-engineering
   def my_function(params):
       # Adding complex parameter validation framework
       validator = ParameterValidator(params)
       validator.validate_schema(COMPLEX_SCHEMA)
       value = validator.get_validated('optional_param')
   
   # ✅ GOOD: Minimal, self-contained fix
   def my_function(params):
       value = params.get('optional_param', None)  # One line change
       if value is None:
           # Handle missing parameter case
           ...
   ```

   **Fix criteria:**
   - Minimal code changes
   - Self-contained (doesn't require refactoring)
   - Preserves existing API/behavior
   - Follows project code style
   - Adds defensive checks if needed

7. **Check for breaking changes and determine version_added**

   **CRITICAL: Determine if the change is backward compatible**

   **Breaking change detection:**

   A change is **BREAKING** if it:
   - ❌ Removes a parameter or module
   - ❌ Changes parameter behavior in an incompatible way
   - ❌ Changes return value structure
   - ❌ Changes default values that break existing playbooks
   - ❌ Removes deprecated features

   A change is **NOT BREAKING** if it:
   - ✅ Adds a new optional parameter
   - ✅ Adds a new module
   - ✅ Adds a new return value
   - ✅ Fixes a bug
   - ✅ Adds deprecation warning

   **Version calculation:**

   ```bash
   # Find latest stable branch
   STABLE=$(git branch -r | grep "upstream/stable-" | grep -v patchback | sort -V | tail -1)
   
   # Get version from stable branch
   STABLE_VERSION=$(git show ${STABLE}:galaxy.yml | grep "^version:" | awk '{print $2}')
   # Example output: 11.2.0
   
   # If BREAKING change:
   #   Next MAJOR: 11.2.0 → 12.0.0
   # If feature (not breaking):
   #   Next MINOR: 11.2.0 → 11.3.0
   # If bug fix:
   #   No version_added
   ```

   **Changelog category:**
   - Breaking change: `breaking_changes`
   - New feature: `minor_changes`
   - Bug fix: `bugfixes`
   - Deprecation: `deprecated_features`

   **Include in plan:**
   - Breaking change check: YES/NO
   - version_added: "11.3.0" (or 12.0.0 if breaking)
   - Changelog category: minor_changes (or breaking_changes)
   - Changelog fragment: `<issue>-<module>-<feature>.yml`

8. **Identify files to modify**

   ```markdown
   Files to modify:
   1. plugins/modules/xyz.py (primary fix)
      - Line 45: Add parameter with version_added: "11.3.0"
      - Line 52: Add None check
      - Verify RETURN block (check if return values change)
   
   2. tests/unit/plugins/modules/xyz/test_new_feature.py (NEW)
      - Add test_parameter_works()
      - Add test_parameter_validation()
      - Add test_edge_cases()
      - Add test_check_mode()
   
   3. tests/integration/targets/xyz/tasks/new_feature.yml (NEW)
      - Add integration test (NO conditionals!)
      - Follow existing pattern from tasks/main.yml
      - Use common.yml helpers
   
   Files to read but NOT modify:
   - plugins/module_utils/common.py (understand dependencies)
   - docs/xyz.md (verify parameter documentation)
   - tests/integration/targets/xyz/tasks/main.yml (test orchestration)
   - tests/integration/targets/xyz/tasks/common.yml (helper tasks)
   - tests/integration/targets/xyz/defaults/main.yml (variables)
   ```

9. **Plan test strategy** (MANDATORY - both unit AND integration)

   **CRITICAL**: Every code change MUST include both unit and integration tests.

   **Unit tests** (always required):

   ```python
   # Minimum 3 test cases:
   # 1. Test the bug scenario / happy path
   def test_missing_optional_param():
       """Test module handles missing optional_param"""
       params = {'required': 'value'}  # No optional_param
       result = my_function(params)
       assert result['changed'] == False
       assert 'error' not in result
   
   # 2. Test parameter validation
   def test_parameter_validation():
       """Test that address requires public_ipv4_pool"""
       # Test that required_by is enforced
       pass
   
   # 3. Test edge cases
   def test_none_optional_param():
       """Test module handles None optional_param"""
       params = {'required': 'value', 'optional_param': None}
       result = my_function(params)
       # Should not crash
   
   # 4. Test check_mode (if applicable)
   def test_check_mode():
       """Test that check_mode doesn't make changes"""
       pass
   ```

   **Test file location:**
   - Check `tests/unit/plugins/modules/<module>/` first
   - Follow existing test structure
   - Create `test_<feature>.py` in appropriate location

   **Integration tests** (MANDATORY - must run in CI):

   **CRITICAL**: Integration tests MUST NOT use conditionals (`when:` statements).
   Find creative ways to test without requiring special resources.

   **Before writing integration tests:**
   1. Read full test role structure:
      - `tests/integration/targets/<module>/tasks/main.yml`
      - `tests/integration/targets/<module>/tasks/common.yml`
      - `tests/integration/targets/<module>/defaults/main.yml`
      - Read one similar test file for patterns

   2. Identify creative testing approach:

   **❌ BAD - Conditional test (won't run in CI):**

   ```yaml
   - name: Test with BYOIP pool
     when: byoip_pool_available  # Won't run in CI!
     ec2_eip:
       public_ipv4_pool: "{{ byoip_pool }}"
       address: "{{ specific_ip }}"
   ```

   **✅ GOOD - Creative approach (runs in CI):**

   ```yaml
   # Use resource that's always available
   - name: Allocate from amazon pool
     ec2_eip:
       public_ipv4_pool: amazon  # Always available
     register: eip_result
   
   - name: Save IP for reuse
     set_fact:
       test_ip: "{{ eip_result.public_ip }}"
   
   - name: Release IP
     ec2_eip:
       state: absent
       public_ip: "{{ test_ip }}"
   
   - name: Re-allocate with address parameter
     ec2_eip:
       public_ipv4_pool: amazon
       address: "{{ test_ip }}"  # Test specific IP!
     register: specific_result
   
   - assert:
       that:
         - specific_result.public_ip == test_ip
   ```

   **Integration test pattern:**

   ```yaml
   # Follow this structure:
   - name: <feature> - check_mode
     <module>:
       <params>
     register: result
     check_mode: true
   
   - assert:
       that: result is changed
   
   - name: Verify no changes in check mode
     include_tasks: tasks/common.yml
     vars:
       has_no_new_resource: true
   
   - name: <feature> - actual
     <module>:
       <params>
     register: result
   
   - assert:
       that:
         - result is changed
         - result.expected_value == expected
   
   - name: Verify resource created
     include_tasks: tasks/common.yml
     vars:
       has_new_resource: true
   
   - name: <feature> - idempotence
     <module>:
       <params>
     register: result
   
   - assert:
       that: result is not changed
   ```

   **Plan must specify:**
   - Where integration test goes (which tasks file)
   - How to test without special resources
   - What common.yml helpers to use
   - What variables from defaults/main.yml to use

10. **Match code style**

   Analyze existing code style:

   ```python
   # Observed patterns in codebase:
   # - Type hints: Yes, using typing module
   # - Docstrings: Google style
   # - Line length: 100 chars (from .editorconfig)
   # - Quotes: Double quotes
   # - Error handling: Raise AnsibleError
   
   # Plan must match these conventions
   ```

1. **Generate implementation plan**

   Create step-by-step plan:

   ```markdown
   # Bug Fix Plan: Issue #123
   
   ## Issue Summary
   Module xyz fails with KeyError when optional_param is not provided
   
   ## Root Cause
   File: plugins/modules/xyz.py, line 45
   Code assumes `optional_param` always exists in params dict
   ```python
   value = params['optional_param']  # Crashes if key missing
   ```

## Proposed Fix

### Minimal Changes (2 lines)

   **File: plugins/modules/xyz.py**

   ```python
   # Line 45 (before)
   value = params['optional_param']
   
   # Line 45 (after)
   value = params.get('optional_param', None)
   
   # Add check at line 46
   if value is not None:
       # existing logic
   ```

### Why this fix works

- Uses .get() with default value (Python best practice)
- Preserves existing behavior when param is provided
- Gracefully handles missing param case
- Minimal, self-contained change

## Code Style Requirements

- Type hints: Add `Optional[str]` for value
- Docstring: Update to document optional_param behavior
- Match existing: Double quotes, 100 char lines

## Test Plan

### Unit Tests (new file: tests/unit/test_xyz_missing_param.py)

   ```python
   def test_missing_optional_param():
       """Ensure module works without optional_param"""
       # Test code here
   
   def test_none_optional_param():
       """Ensure module handles None optional_param"""
       # Test code here
   
   def test_with_optional_param():
       """Ensure original behavior preserved"""
       # Test code here
   ```

### Integration Tests (if applicable)

- Add test case in tests/integration/targets/xyz/tasks/main.yml
- Test real scenario without optional_param

## Implementation Steps

   1. **Read code** (batch operation)
      - plugins/modules/xyz.py
      - plugins/module_utils/common.py (dependencies)
      - tests/unit/test_xyz.py (existing tests)

   2. **Implement fix**
      - Modify plugins/modules/xyz.py (2 lines)
      - Add type hint: `Optional[str]`
      - Update docstring

   3. **Add tests**
      - Create tests/unit/test_xyz_missing_param.py
      - Add 3 unit test cases
      - Add integration test if needed

   4. **Verify**
      - Run: pytest tests/unit/test_xyz_missing_param.py
      - Run: /lint-fix && /lint
      - Run: /sanity --mode=smart

   5. **Commit**
      - Message: "fix: handle missing optional_param in xyz module"
      - Reference: "Fixes #123"

## Risk Assessment

- **Low risk**: Minimal change, backward compatible
- **No API changes**: Existing behavior preserved
- **Test coverage**: Unit + integration tests added

## Success Criteria

- ✅ Module doesn't crash when optional_param missing
- ✅ Original behavior preserved when param provided
- ✅ All existing tests still pass
- ✅ New tests cover edge cases
- ✅ Lint and sanity checks pass

   ```

12. **Save plan**
    ```bash
    cat > .bug-fixes/plan-$ISSUE_NUMBER.md <<EOF
    [Generated plan]
    EOF
    
    echo "✅ Implementation plan saved: .bug-fixes/plan-$ISSUE_NUMBER.md"
    ```

13. **Report and confirm**
    ```
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Implementation Plan: Issue #123
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    Root Cause: Missing optional parameter handling in xyz.py:45
    
    Fix Approach: Add .get() with default value (2 line change)
    
    Files to modify:
      - plugins/modules/xyz.py (fix)
      - tests/unit/test_xyz_missing_param.py (new tests)
    
    Risk: LOW (minimal, backward compatible)
    
    Plan saved: .bug-fixes/plan-123.md
    
    Proceed with implementation? [Y/n]
    
    Next steps:
      1. Review plan: cat .bug-fixes/plan-123.md
      2. Implement: /bug-implement
      3. Or full workflow: /bug-fix --issue 123
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ```

## Planning Principles

### Minimal Changes
- Change only what's necessary
- Avoid refactoring existing code
- Preserve API compatibility
- One logical change per fix

### Self-Contained
- Fix should work within existing architecture
- No framework additions
- No new dependencies
- Use existing patterns

### Code Style Match
- Observe existing conventions
- Match type hint usage
- Match docstring style
- Follow line length limits
- Use same quote style

### Test Coverage
- Unit tests: Always required
- Integration tests: When applicable
- Test the bug scenario
- Test the fix
- Test edge cases

## Integration Points

This skill is imported by:
- `/bug-fix` - Bug fix orchestrator
- Can be used standalone for planning

## Troubleshooting

### "No issue summary found"
```bash
/bug-pull --issue 123  # Create summary first
```

### "Can't identify root cause"

```bash
# With GitHub MCP (check similar issues/PRs first):
similar = github_search_issues(repo=REPO, query="is:closed similar error")

# Then ask for more information:
github_add_issue_comment(
    owner=OWNER, 
    repo=REPO_NAME, 
    number=123, 
    body="Need more details on reproduction"
)

# Fallback with gh CLI:
gh issue comment 123 --body "Need more details on reproduction"
```

### "Fix too complex"

```bash
# With GitHub MCP:
github_create_issue(
    owner=OWNER,
    repo=REPO_NAME,
    title="Subtask 1: ...",
    body="Part of #123"
)

# Fallback with gh CLI:
gh issue create --title "Subtask 1: ..." --body "Part of #123"
```

## Implementation Notes

**Core Workflow:**

- Load issue summary from `.bug-fixes/issue-N.md`
- Read all relevant files in batch (one message, multiple Read calls)
- Analyze code to find root cause
- Propose minimal, self-contained fix
- Match existing code style
- Plan comprehensive test coverage (unit + integration)
- Check for breaking changes and calculate version_added
- Plan changelog fragment creation
- Save plan for issue-implement to execute
- Provide clear risk assessment
- Works with any codebase/language

**GitHub MCP Enhancements (Optional):**

- Search for similar closed issues/PRs before planning
- Check commit history for affected files
- Compare branches to find existing partial fixes
- Access code from GitHub for remote analysis
- Falls back to local git if MCP not available

**Integration:**

- Used by `/issue-fix` and `/bug-fix` orchestrators
- Produces plan consumed by `/issue-implement`
- Works standalone for planning without implementation
