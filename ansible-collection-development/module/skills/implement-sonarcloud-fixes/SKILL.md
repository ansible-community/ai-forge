---
name: implement-sonarcloud-fixes
description: >-
  Implement fixes for SonarCloud issues identified by the sonarcloud-analysis skill.
  Creates feature branches, applies code changes, runs tests, and creates pull requests.
  Use after reviewing SonarCloud analysis results.
---

# Skill: implement-sonarcloud-fixes

## Purpose

Implement fixes for SonarCloud issues that have been identified and analyzed.
This skill complements the `sonarcloud-analysis` skill by taking the analysis results and implementing the suggested fixes.

## When to Invoke

TRIGGER when:

- User asks to fix SonarCloud issues that were previously analyzed
- User wants to implement suggested fixes from SonarCloud analysis
- After reviewing SonarCloud analysis and deciding to address specific issues
- User asks "implement the sonarcloud fixes" or "fix these issues"

DO NOT TRIGGER when:

- User wants to view/analyze SonarCloud issues (use `sonarcloud-analysis` skill first)
- User hasn't reviewed the analysis yet
- No specific issues have been identified to fix

## Inputs

- `issues` (required): Issues to fix, typically from prior `sonarcloud-analysis` output
- `category` (optional): Focus on specific category (e.g., weak-cryptography, S3776)

## Prerequisites

- The `sonarcloud-analysis` skill should be run first to identify and analyze issues
- User should have reviewed the analysis and decided which issues to address

## Workflow

### Step 1 — Confirm issues to fix

If not already clear from context, review with the user which issues to fix.

Present options based on the analysis:

- "Fix all suggested issues in category X"
- "Fix specific issues" (then list which ones)
- "Fix all high-priority issues"

Use `AskUserQuestion` to confirm the scope of work.

### Step 2 — Create feature branch

Use the `create-branch` skill to create a new feature branch.

Suggested branch naming based on issue type:

- Security: `security/<category>` (e.g., `security/weak-cryptography`)
- Reliability: `reliability/<category>` (e.g., `reliability/duplicate-branches`)
- Maintainability: `maintainability/<module-name>` (e.g., `maintainability/ec2_instance`)

If fixing mixed types, use: `sonarcloud/<description>` (e.g., `sonarcloud/critical-issues`)

### Step 3 — Apply fixes

For each issue to be fixed:

**a) Read the affected file** with context around the issue location.

**b) Apply the fix** using the Edit tool:

- Implement the suggested code change
- Add explanatory comments where helpful
- Follow project coding standards
- Ensure the fix doesn't introduce new issues

**c) Document the change:**

- Note which SonarCloud issue key this addresses
- Explain the rationale if not obvious
- Reference the rule documentation if needed

### Step 4 — Add unit tests and verify changes

**For refactoring changes (especially cognitive complexity fixes):**

When extracting complex logic into helper functions, write unit tests for the new functions:

- New helper functions are ideal candidates for unit testing
- They're typically smaller and more focused than the original code
- Unit tests document the expected behavior
- Tests prevent regression when the code is modified later
- Place tests in `tests/unit/plugins/module_utils/` or `tests/unit/plugins/modules/`

**Run all tests:**

Use the `run-tests` skill to verify the changes:

- Run sanity tests on changed files
- Run unit tests (including newly added tests)
- Run integration tests if behavior changed

**If tests fail:**

- Analyze the failure
- Adjust the fix if needed
- Re-run tests
- If fix causes unavoidable test changes, update tests appropriately

### Step 5 — Commit changes

Use the `commit` skill to create a conventional commit.

Suggested format based on issue type:

**For security fixes:**

```
fix(security): address <category> issues

- <file>:<line> - <brief description>
- <file>:<line> - <brief description>

Addresses <count> security issue(s) identified by SonarCloud.
Rule: <ruleKey> - <rule description>

SonarCloud issue keys: <key1>, <key2>
```

**For reliability fixes:**

```
fix: address <severity> reliability issues

- <file>:<line> - <brief description>

Fixes <count> bug(s) identified by SonarCloud.
Rule: <ruleKey> - <rule description>

SonarCloud issue keys: <key1>
```

**For maintainability improvements:**

```
refactor: improve code quality in <module>

- <file>:<line> - <brief description>

Addresses <count> code smell(s) identified by SonarCloud.
Rule: <ruleKey> - <rule description>

SonarCloud issue keys: <key1>, <key2>
```

### Step 6 — Create changelog fragment

Use the `changelog-fragment` skill to document the changes.

Fragment type based on issue category:

- Security hotspots → `trivial` (or `security_fixes` if actual vulnerability)
- Reliability issues → `bugfixes`
- Maintainability issues → `trivial`

Example fragment content:

```yaml
bugfixes:
  - >-
    Fixed reliability issues identified by SonarCloud static analysis
    (https://github.com/ORG/REPO/pull/XXXX).
```

or

```yaml
trivial:
  - >-
    Improved code quality by addressing maintainability issues in module_name
    (https://github.com/ORG/REPO/pull/XXXX).
```

### Step 7 — Create pull request (optional)

Use `AskUserQuestion` to ask if user wants to create a PR:

Options:

- "Create PR now"
- "Make more fixes first"
- "Done (I'll create PR manually)"

If creating PR, use the `create-pr` skill with:

- Title based on issue type:
  - Security: "Fix security `<category>` issues"
  - Reliability: "Fix `<severity>` reliability issues"
  - Maintainability: "Improve code quality in `<module>`"
- Body should include:
  - Summary of what was fixed
  - Links to SonarCloud issue details
  - SonarCloud issue keys
  - Link to SonarCloud project

## Fix Strategies by Common Patterns

These strategies align with the guidance provided by `sonarcloud-analysis`:

### Weak Cryptography (python:S2245)

- Check if cryptographic randomness is actually needed
- If yes: use `secrets` module instead of `random`
- If for hashing: use `usedforsecurity=False` parameter
- If not security-sensitive: mark as SAFE (don't fix)

Example fix:

```python
# Before
import random
token = ''.join(random.choice(string.ascii_letters) for _ in range(16))

# After
import secrets
token = secrets.token_hex(8)  # generates 16 character hex string
```

### HTTP URLs (encrypt-data)

- Check if HTTP is required (e.g., AWS metadata at http://169.254.169.254)
- If required: mark as SAFE (don't fix)
- Otherwise: change to HTTPS

### Cognitive Complexity (python:S3776)

- Extract nested logic into helper functions
- Simplify conditional statements
- Prioritize extracting logic that can be unit tested

Example fix:

```python
# Before
def complex_function(params):
    if condition1:
        if condition2:
            if condition3:
                # deeply nested logic
                pass

# After
def complex_function(params):
    if not condition1:
        return
    if not condition2:
        return
    _handle_condition3(params)

def _handle_condition3(params):
    if condition3:
        # extracted logic
        pass
```

### Duplicate Strings (python:S1192)

- Extract into named constants
- Use descriptive names
- Group related constants

Example fix:

```python
# Before
module.fail_json(msg="Invalid parameter value")
# ... later ...
module.fail_json(msg="Invalid parameter value")

# After
INVALID_PARAM_MSG = "Invalid parameter value"
module.fail_json(msg=INVALID_PARAM_MSG)
# ... later ...
module.fail_json(msg=INVALID_PARAM_MSG)
```

### Generic Exceptions (python:S112)

- Replace with specific exception types
- Create custom exception classes for domain-specific errors

Example fix:

```python
# Before
raise Exception("Connection failed")

# After
raise ConnectionError("Connection failed")
```

### Duplicate Branches (python:S1862)

- Refactor to eliminate duplication
- Verify logic is correct

Example fix:

```python
# Before
if mode == 'A':
    result = process_data(data)
elif mode == 'B':
    result = process_data(data)  # Duplicate!

# After
if mode in ('A', 'B'):
    result = process_data(data)
```

## Important Notes

### Testing Requirements

- All fixes MUST pass tests before committing
- Unit tests may need updates if behavior changes
- Integration tests verify end-to-end functionality
- Add new tests for previously untested code paths

### Review Considerations

- Each PR should focus on one category/type of issues
- Include rationale for each fix in commit message
- Reference SonarCloud issue keys for traceability
- Link to SonarCloud rule documentation

### Issue Resolution

SonarCloud issues resolve automatically when:

- Fixes are merged to the main branch
- SonarCloud re-analyzes the code
- The issue is no longer detected

For false positives, mark them in SonarCloud UI (not via this skill).

### Batch Fixes

When fixing multiple related issues:

- Group by file or rule type
- Apply all fixes in one branch
- Test together to ensure no interactions
- Create one focused PR

### When Not to Fix

Don't fix issues that are:

- False positives (legitimate patterns flagged incorrectly)
- Required by external constraints (e.g., HTTP to AWS metadata)
- Intentional technical debt (documented and accepted)

## Integration with Other Skills

- **sonarcloud-analysis**: MUST be run first to identify and analyze issues
- **create-branch**: Used to create feature branch for fixes
- **run-tests**: Used to verify fixes don't break functionality
- **commit**: Used to create conventional commits
- **changelog-fragment**: Used to document changes
- **create-pr**: Used to create pull request for review

## Example Output

### Example: Implementing weak cryptography fixes

```
User: "Implement the fixes for weak cryptography issues"

Step 1: Confirm scope
You want to fix 2 weak-cryptography issues:
  - plugins/module_utils/aws_ssm.py:45 - Use secrets module for token generation
  - plugins/modules/core.py:123 - Use secrets module for random IDs

Proceed?
> Yes

Step 2: Create branch
Creating branch: security/weak-cryptography
Branch created from origin/main

Step 3: Apply fixes

Fixing plugins/module_utils/aws_ssm.py:45...
Changed:
  - import random
  + import secrets
  - token = ''.join(random.choice(string.ascii_letters) for _ in range(16))
  + token = secrets.token_hex(8)

Fixing plugins/modules/core.py:123...
Changed:
  - request_id = str(random.randint(100000, 999999))
  + request_id = secrets.token_hex(3)

Step 4: Run tests
Running sanity tests... PASSED
Running unit tests... PASSED

Step 5: Commit
Created commit: fix(security): address weak-cryptography issues

Step 6: Create changelog fragment
Created: changelogs/fragments/123-security-fixes.yml

Step 7: Create PR?
> Create PR now

Created PR #456: Fix security weak-cryptography issues
https://github.com/ansible-collections/amazon.aws/pull/456

SonarCloud will re-analyze when this PR is merged.
```
