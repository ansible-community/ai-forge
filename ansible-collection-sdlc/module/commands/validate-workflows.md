---
description: Validate GitHub Actions workflows for security issues and best practices
argument-hint: "[--check-permissions] [--check-secrets] [--check-actions] [--check-sources] [--fix] [--all] [--score]"
---

Validate GitHub Actions workflow files for security issues, deprecated actions, untrusted action sources, unsafe secret usage, and permission misconfigurations.

Use the `validate-workflows` skill to:

1. Check workflows against approved action sources list
2. Detect deprecated or archived repositories
3. Validate SHA commit hash pinning on action references
4. Identify hardcoded secrets and credential exposure
5. Audit permissions configurations
6. Detect dangerous workflow patterns (pull_request_target with secrets, etc.)
7. Generate security scores for actions
8. Optionally auto-fix safe issues

## Arguments

- `--check-permissions` - Check only permission configurations
- `--check-secrets` - Check only for secret exposure issues
- `--check-actions` - Check only action reference security
- `--check-sources` - Check only action sources against approved list
- `--fix` - Automatically fix safe issues (with confirmation)
- `--all` - Validate all workflows in repository (not just changed)
- `--score` - Generate security scores for each action

## When to Use

- Before creating a PR that modifies workflows
- During security audits of CI/CD configurations
- When adding new GitHub Actions to workflows
- As part of pre-commit checks for workflow changes

## Configuration

The skill uses `approved-sources.yml` for security policies:

- **Load order** (first found wins):
  1. `.claude/approved-sources.yml` (project-specific)
  2. Skill directory default

- **Customize**: Copy skill's `approved-sources.yml` to `.claude/` and modify trusted sources, deprecated actions, and policies

## Example Output

```markdown
## 🔒 GitHub Actions Security Validation

### Summary
- 🚨 Critical: 1
- ❌ Errors: 3
- ⚠️ Warnings: 2
- ℹ️ Info: 1

### 🚨 CRITICAL

#### Hardcoded Secret
**File**: `.github/workflows/deploy.yml:23`
**Pattern**: AWS Access Key
**Fix**: Remove and use GitHub secrets

### ❌ ERRORS

#### Untrusted Action Source
**File**: `.github/workflows/ci.yml:15`
**Action**: `random-user/unknown-action@main`
**Issue**: Not in approved sources list
**Fix**: Review action code or use approved alternative

### Verdict
❌ FAILED - Fix 1 critical and 3 errors before merging
```

The skill will provide a structured report with severity levels, specific file locations, and actionable fixes.
