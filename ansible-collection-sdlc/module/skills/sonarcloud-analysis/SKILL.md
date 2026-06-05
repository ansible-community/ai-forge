---
name: sonarcloud-analysis
description: >-
  Fetch and analyse SonarCloud issues for a project or pull request.
  Use when asked to check, review, or analyse SonarCloud issues, code quality,
  security hotspots, or technical debt.
user-invocable: true
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

See [references/issue-patterns.md](references/issue-patterns.md) for rule-specific fix guidance.

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

See [references/examples.md](references/examples.md) for detailed usage scenarios.
