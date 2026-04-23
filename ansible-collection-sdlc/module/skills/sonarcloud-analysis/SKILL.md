---
name: sonarcloud-analysis
description: >-
  Fetch and analyse SonarCloud issues for a project or pull request.
  Use when asked to check, review, or analyse SonarCloud issues, code quality,
  security hotspots, or technical debt.
---

# SonarCloud Analysis Skill

Fetch and analyse issues from SonarCloud for either the entire project (technical debt overview) or a specific pull request (PR impact analysis).

## Purpose

This skill retrieves static analysis results from SonarCloud and presents them in an actionable format, grouped by category, severity, or file. Use it to:

- Review all unresolved issues in a project (technical debt audit)
- Check what issues a specific PR introduces
- Identify security hotspots requiring review
- Prioritise code quality improvements

## When to Invoke

TRIGGER when the user asks to:

- Check SonarCloud issues or results
- Review code quality, security hotspots, or technical debt
- Analyse issues for a specific PR
- Get a technical debt overview

DO NOT TRIGGER when:

- The user wants to fix issues (use a separate fix/implementation skill)
- The question is about code logic unrelated to static analysis

## Modes

### Project-wide Mode (default)

Analyses all unresolved issues in the project. Use for:

- Technical debt audits
- Planning refactoring work
- Understanding code quality trends

### PR-specific Mode

Analyses issues introduced by a specific pull request. Use for:

- PR reviews
- Validating that changes don't introduce new issues
- Understanding the quality impact of changes

## Dependencies

This skill uses helper skills to determine repository and PR context:

- `get-upstream-info` - Determines upstream repository and SonarCloud project key
- `get-pr-number` - Determines PR number for the current branch (in PR mode)

**Caching:** See caching guidance in `get-upstream-info`. This skill should cache upstream info at the start and reuse it throughout execution.

## Workflow

### 1. Determine Project Key

Use the `get-upstream-info` skill to determine the SonarCloud project key:

```
Invoke get-upstream-info skill to get:
- UPSTREAM_PATH (e.g., ansible-collections/amazon.aws)
- SONARCLOUD_KEY (e.g., ansible-collections_amazon.aws)
- UPSTREAM_ORG (e.g., ansible-collections)
- UPSTREAM_REPO (e.g., amazon.aws)
```

**Cache these values** for use throughout the skill execution.

**Verify the project exists on SonarCloud:**

```bash
curl -s "https://sonarcloud.io/api/components/show?component=$SONARCLOUD_KEY"
```

If the API returns an error (component not found), inform the user that SonarCloud analysis is not available for this project.

### 2. Determine Mode and Parameters

**Auto-detect mode from context:**

- If user mentions "PR", "pull request", or provides a PR number → PR-specific mode
- If current branch has an open PR and user asks to "check sonar" → PR-specific mode
- Otherwise → Project-wide mode

**For PR-specific mode, get PR number:**

- If user provided a number as argument, use it
- Otherwise, use the `get-pr-number` skill to detect PR for current branch:

  ```
  Invoke get-pr-number skill to get:
  - PR_NUMBER
  - PR_FOUND (boolean)
  - PR_STATE
  ```

- If `PR_FOUND` is false, inform user and ask if they want project-wide analysis instead

**Determine issue type filter (optional):**

Ask the user which types to analyse (or analyse all if not specified):

- **Security hotspots** - Security vulnerabilities and potential security issues
- **Reliability issues** - Bugs and potential runtime errors
- **Maintainability issues** - Code smells and technical debt
- **All issues** - Everything combined

### 3. Fetch Issues from SonarCloud

Retrieve issues from SonarCloud using the appropriate API endpoint.

**Use the cached values from step 1:**

- `$SONARCLOUD_KEY` - From get-upstream-info skill
- `$PR_NUMBER` - From get-pr-number skill (if in PR mode)

**For Security Hotspots (project-wide):**

```bash
curl -s "https://sonarcloud.io/api/hotspots/search?projectKey=$SONARCLOUD_KEY&status=TO_REVIEW&ps=500"
```

**For Security Hotspots (PR-specific):**

```bash
curl -s "https://sonarcloud.io/api/hotspots/search?projectKey=$SONARCLOUD_KEY&pullRequest=$PR_NUMBER&status=TO_REVIEW&ps=500"
```

**For Reliability Issues (project-wide):**

```bash
curl -s "https://sonarcloud.io/api/issues/search?componentKeys=$SONARCLOUD_KEY&types=BUG&resolved=false&ps=500"
```

**For Reliability Issues (PR-specific):**

```bash
curl -s "https://sonarcloud.io/api/issues/search?componentKeys=$SONARCLOUD_KEY&pullRequest=$PR_NUMBER&types=BUG&resolved=false&ps=500"
```

**For Maintainability Issues (project-wide):**

```bash
curl -s "https://sonarcloud.io/api/issues/search?componentKeys=$SONARCLOUD_KEY&types=CODE_SMELL&resolved=false&ps=500"
```

**For Maintainability Issues (PR-specific):**

```bash
curl -s "https://sonarcloud.io/api/issues/search?componentKeys=$SONARCLOUD_KEY&pullRequest=$PR_NUMBER&types=CODE_SMELL&resolved=false&ps=500"
```

**For All Issues (PR-specific):**

```bash
curl -s "https://sonarcloud.io/api/issues/search?componentKeys=$SONARCLOUD_KEY&pullRequest=$PR_NUMBER&resolved=false&ps=500"
```

**Parse the JSON response** to extract issue details:

- `key` - Issue identifier
- `component` - File path
- `severity` or `vulnerabilitySeverity` - Severity level
- `line` - Line number
- `message` - Issue description
- `rule` - Rule identifier (e.g., `python:S3776`)
- `type` - Issue type (BUG, VULNERABILITY, CODE_SMELL, SECURITY_HOTSPOT)
- For hotspots: `securityCategory` - Security category (e.g., `weak-cryptography`)

**Handle pagination for large result sets:**

The API returns `paging` information:

```json
{
  "paging": {
    "pageIndex": 1,
    "pageSize": 500,
    "total": 2626
  }
}
```

If `total > pageSize`, fetch additional pages:

```bash
# Page 2
curl -s "https://sonarcloud.io/api/issues/search?componentKeys=$SONARCLOUD_KEY&types=CODE_SMELL&resolved=false&ps=500&p=2"

# Page 3
curl -s "https://sonarcloud.io/api/issues/search?componentKeys=$SONARCLOUD_KEY&types=CODE_SMELL&resolved=false&ps=500&p=3"
```

**For project-wide analysis with many issues:**

- Consider showing summary statistics first (total count by type/severity)
- Ask user which subset to analyse in detail (e.g., "Show CRITICAL issues only")
- Avoid fetching thousands of issues unless necessary
- For large codebases (>500 issues), focus on high-priority items first

### 4. Group Issues

Group issues using the strategy appropriate for the issue type and mode:

**Security Hotspots - Group by `securityCategory`:**

- `weak-cryptography` - Cryptographic issues (often `random` module usage)
- `encrypt-data` - Data encryption issues (HTTP vs HTTPS)
- `dos` - Denial of Service vulnerabilities (regex backtracking)
- `permission` - Permission and access control issues
- `injection` - Injection vulnerabilities
- `auth` - Authentication issues
- `insecure-conf` - Insecure configuration
- `others` - Uncategorised security issues

**Reliability Issues - Group by `severity`:**

- `BLOCKER` - Must be fixed immediately
- `CRITICAL` - Critical bugs
- `MAJOR` - Major bugs
- `MINOR` - Minor bugs
- `INFO` - Informational

**Maintainability Issues - Group by `component` (file path):**

- This allows addressing all issues in a file together
- Within each file, sub-group by severity

**Mixed/All Issues - Group by `type` first, then by severity or category:**

- `SECURITY_HOTSPOT` → by category
- `BUG` → by severity
- `VULNERABILITY` → by severity
- `CODE_SMELL` → by file or severity

### 5. Present Summary

Display a summary table appropriate for the issue type and mode.

**Include mode context at the top:**

```
SonarCloud Analysis
===================
Project: $UPSTREAM_PATH (e.g., ansible-collections/amazon.aws)
Mode: <Project-wide | Pull Request #$PR_NUMBER>
Issue Types: <All | Security | Reliability | Maintainability>
Link: https://sonarcloud.io/project/<issues or pull_requests>?id=$SONARCLOUD_KEY<&pullRequest=$PR_NUMBER>
```

**Security Hotspots Summary:**

```
Security Hotspots (TO_REVIEW only)
===================================

Category           | Count | Severity       | Files Affected
-------------------|-------|----------------|------------------
weak-cryptography  |   2   | MEDIUM (2)     | aws_ssm.py, terminalmanager.py
encrypt-data       |   5   | LOW (5)        | transformations.py, ec2_metadata_facts.py
dos                |   1   | HIGH (1)       | regex_utils.py
```

**Reliability Issues Summary:**

```
Reliability Issues (Unresolved)
================================

Severity    | Count | Common Rules                      | Files Affected
------------|-------|-----------------------------------|---------------
BLOCKER     |   1   | python:S1862                      | module1.py
CRITICAL    |   2   | python:S3776                      | module2.py, module3.py
MAJOR       |   15  | python:S112, python:S1135         | various
```

**Maintainability Issues Summary:**

```
Maintainability Issues (Unresolved)
====================================

File                                    | Total | CRIT | MAJOR | MINOR | Common Rules
----------------------------------------|-------|------|-------|-------|------------------
plugins/modules/ec2_instance.py         |   12  |   2  |   8   |   2   | S3776, S1192
plugins/module_utils/botocore.py        |   8   |   1  |   5   |   2   | S1066, S1192
```

### 6. Detailed Issue Analysis

For each group (or the top priority groups), provide detailed analysis:

**a) List each issue with context:**

```
File: plugins/modules/ec2_instance.py:234
Rule: python:S3776 (Cognitive Complexity)
Severity: CRITICAL
Message: Refactor this function to reduce its Cognitive Complexity from 45 to the 15 allowed.

Context: The `ensure_present()` function has deeply nested conditionals and loops
that make it difficult to understand and maintain.
```

**b) Read the affected code:**
Use the Read tool to show the relevant lines with context.

**c) Explain the issue:**

- What is the rule checking for?
- Why is this a problem?
- What are the potential impacts (security, reliability, maintainability)?

**d) Suggest fixes:**

- Specific, actionable recommendations
- Example code where applicable
- Note if this appears to be a false positive

**e) Link to rule documentation:**

```
Rule details: https://rules.sonarsource.com/python/RSPEC-<number>
```

### 7. Prioritisation and Recommendations

**Prioritise issues by:**

1. **BLOCKER/CRITICAL severity** - Address immediately
2. **Security hotspots** - Review and address based on risk
3. **High-severity bugs** - Address in next iteration
4. **Maintainability issues** - Plan for incremental improvement

**Provide actionable recommendations:**

- "Fix the 2 BLOCKER issues before merging this PR"
- "Review the 5 weak-cryptography hotspots - 3 appear to be false positives (UUID generation)"
- "Consider refactoring ec2_instance.py to address the 8 MAJOR complexity issues"
- "The 15 code smell issues are low priority and can be addressed incrementally"

### 8. Next Steps

**For PR-specific analysis:**

- If issues are found: "These issues were introduced in this PR. Would you like to fix them before merging?"
- If no issues: "No new issues introduced by this PR ✓"

**For project-wide analysis:**

- Ask if the user wants to focus on a specific category
- Suggest creating issues/tickets for tracking
- Recommend periodic reviews to track progress

## Error Handling

Error handling is primarily delegated to dependent skills:

- **get-upstream-info**: Handles gh CLI availability, authentication, and repository detection
- **get-pr-number**: Handles PR detection, protected branches, and branch existence

**Skill-specific errors:**

- **SonarCloud project not found**: Detected in step 1, user informed gracefully that SonarCloud analysis is not available for this project
- **API rate limiting**: Documented in Important Notes section; recommend spacing out requests
- **Pagination needed**: Handled via interactive filtering in step 4 (show summary, ask user which subset to analyse)
- **Invalid PR number**: Delegated to get-pr-number skill which validates PR exists
- **Network/API failures**: curl errors should be caught and reported; recommend retrying or checking SonarCloud status

## Common Issue Patterns and Guidance

### Weak Cryptography (python:S2245)

**Pattern:** Using `random` module for security-sensitive operations

**Fix:**

- If cryptographic randomness is needed: Use `secrets` module
- If randomness is for hashing but not cryptographic purposes: Add `usedforsecurity=False` parameter (SonarCloud recognises this)
- If not security-sensitive (e.g., generating unique IDs): Mark as SAFE with justification

**Example with usedforsecurity=False:**

```python
# For MD5 hash used for non-cryptographic purposes (e.g., checksums, cache keys)
hashlib.md5(data, usedforsecurity=False).hexdigest()
```

This parameter explicitly indicates to both Python and SonarCloud that the hash is not being used for security purposes.

### HTTP URLs (encrypt-data)

**Pattern:** Using HTTP instead of HTTPS

**Fix:**

- If HTTP is required (e.g., AWS metadata endpoint `http://169.254.169.254`): Mark as SAFE
- Otherwise: Change to HTTPS

### Cognitive Complexity (python:S3776)

**Pattern:** Functions with deeply nested logic

**Fix:**

- Extract nested logic into helper functions
- Simplify conditional statements
- Prioritise extracting logic that can be unit tested

### Duplicate Strings (python:S1192)

**Pattern:** Magic strings repeated multiple times

**Fix:**

- Extract into named constants
- Use descriptive constant names
- Group related constants

### Generic Exceptions (python:S112)

**Pattern:** Raising or catching generic `Exception`

**Fix:**

- Use specific exception types
- Create custom exception classes for domain-specific errors

### Duplicate Branches (python:S1862)

**Pattern:** Identical code in different conditional branches

**Fix:**

- Refactor to eliminate duplication
- Verify whether different conditions should have different logic

## Important Notes

### API Limitations

- Maximum page size: 500 issues per request
- If more than 500 issues exist, the API returns partial results
- Use pagination (`&p=2`, `&p=3`) if needed
- No authentication required for public projects

### False Positives

- Static analysis may flag legitimate patterns as issues
- Use domain knowledge to identify false positives
- Document why something is safe when it appears problematic

### Project Configuration

- Some projects may have custom quality gates or rule configurations
- SonarCloud analysis depends on the project's sonar-project.properties
- Coverage and duplication metrics are also available via the API

### Rate Limiting

- SonarCloud API has rate limits for unauthenticated requests
- Space out requests if analysing multiple issue types
- Consider caching results for repeated analyses

## Example Usage

### Example 1: PR Review

```
User: "Check sonar for this PR"

Skill:
1. Detects current branch: feature/add-caching
2. Finds PR #1234 for this branch
3. Fetches issues for PR #1234
4. Finds 3 new CODE_SMELL issues
5. Analyses each issue and suggests fixes
6. Reports: "3 new maintainability issues introduced. All are MINOR severity."
```

### Example 2: Technical Debt Audit

```
User: "Show me all security hotspots"

Skill:
1. Detects project key from git remote
2. Fetches all TO_REVIEW security hotspots
3. Groups by category (2 weak-cryptography, 5 encrypt-data, 1 dos)
4. Analyses each category
5. Identifies 3 false positives (AWS metadata HTTP calls)
6. Recommends addressing 2 weak-cryptography issues and 1 DOS issue
```

### Example 3: Comprehensive Analysis

```
User: "What's our SonarCloud status?"

Skill:
1. Fetches all issue types (security, reliability, maintainability)
2. Presents summary: 8 hotspots, 18 bugs, 156 code smells
3. Prioritises: 2 CRITICAL bugs, 8 MAJOR bugs
4. Recommends: "Focus on the 2 CRITICAL bugs first, then review security hotspots"
```

### Example 4: Large Codebase with Pagination

```
User: "Analyse SonarCloud issues for ansible-collections/amazon.aws"

Skill:
1. Determines project key: ansible-collections_amazon.aws
2. Fetches total counts:
   - 8 security hotspots
   - 5 bugs
   - 2,621 code smells
   Total: 2,626 issues
3. Recognises this exceeds 500 (page size limit)
4. Shows summary statistics and asks:
   "This project has 2,626 unresolved issues. Would you like to:
    - Analyse security hotspots (8 items)
    - Analyse bugs (5 items)
    - Analyse CRITICAL/BLOCKER code smells only
    - Analyse code smells by severity"
5. User selects "Analyse bugs"
6. Fetches and analyses all 5 bugs (no pagination needed)
7. Provides detailed analysis with fix suggestions
```
