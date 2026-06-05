---
name: validate-workflows
description: >-
  Validate GitHub Actions workflows for security issues and best practices.
  Checks action sources against approved lists, detects deprecated/archived
  repositories, validates SHA pinning, identifies secret exposure, and audits
  permissions. Use when reviewing workflows before PRs or during security audits.
argument-hint: "[--check-permissions] [--check-secrets] [--check-actions] [--check-sources] [--fix] [--all]"
user-invocable: true
---

# Skill: validate-workflows

## Purpose

Validate GitHub Actions workflow files for security issues, deprecated actions, untrusted action sources, unsafe secret usage, and permission misconfigurations.

## When to Invoke

TRIGGER when:

- User asks to "validate workflows", "check workflows", "security review workflows"
- Before creating a PR that modifies `.github/workflows/` files
- During security audits of GitHub Actions configurations
- When asked to "check if actions are approved/trusted"
- When reviewing PR changes to workflow files

DO NOT TRIGGER when:

- User wants to run/execute workflows (that's a CI/CD operation)
- Question is about workflow syntax without security concerns
- Just viewing workflow files without validation

## Security Issues Detected

GitHub Actions workflows can contain security vulnerabilities:

- Missing or overly permissive `permissions:` blocks
- Hardcoded secrets in workflow files
- Secrets passed to untrusted third-party actions
- Using deprecated, archived, or unmaintained actions
- Actions from unapproved or unknown sources
- Unsafe secret usage patterns (echoing to logs)
- Mutable action references (branches instead of SHAs)
- Missing or improper SHA commit hash pinning

This skill performs comprehensive security validation and provides actionable fixes.

## When to Use

- Before creating a pull request that modifies workflows
- During security audits of workflow configurations
- When reviewing PR changes to `.github/workflows/`
- As part of CI/CD security checks

## What It Validates

### 1. Permissions Security

- ❌ Missing `permissions:` block (defaults to write-all)
- ❌ `permissions: write-all` usage
- ⚠️ Overly broad permissions for workflow needs
- ℹ️ Recommends least-privilege permissions

### 2. Secrets Exposure

- 🚨 Hardcoded secrets/API keys in workflows (AWS keys, GitHub tokens, SSH keys)
- ❌ Secrets echoed to logs (`echo ${{ secrets.TOKEN }}`)
- ❌ Secrets in URLs (logged by proxies)
- ⚠️ Secrets passed to untrusted third-party actions
- ⚠️ Using `pull_request_target` with secrets (dangerous)

### 3. Action Source Security

- ❌ Actions from deprecated or archived repositories
- ❌ Actions from unapproved sources (not in trusted list)
- ⚠️ Actions from personal repositories (not org-owned)
- ⚠️ Actions from unknown third-party sources
- ℹ️ Validates against configurable approved sources list

### 4. Action Reference Security

- ❌ Using mutable refs (`@main`, `@master`, `@develop`)
- ❌ Missing SHA pinning on third-party actions
- ⚠️ Using deprecated action versions
- ℹ️ Recommends pinning to commit SHAs with version comments

## Usage

```bash
# Validate workflows in current branch (all checks)
/validate-workflows

# Check specific concerns
/validate-workflows --check-permissions
/validate-workflows --check-secrets
/validate-workflows --check-actions
/validate-workflows --check-sources

# All checks with auto-fix suggestions
/validate-workflows --fix

# Validate all workflows in repository (not just changed)
/validate-workflows --all
```

## Workflow Overview

The skill performs these validation steps in sequence. For detailed bash implementation, see [reference.md](./reference.md).

### Step 1: Discover Workflow Files

Find all workflow files to validate (changed in current branch or all workflows with `--all` flag).

### Step 2: Check Permissions

Validate that workflows have explicit `permissions:` blocks with least-privilege access.

### Step 3: Check Secrets Exposure

Scan for hardcoded secrets, secrets in echo statements, secrets in URLs, and secrets passed to untrusted actions.

### Step 4: Check Action Sources

Validate action sources against approved lists, check for deprecated/archived repositories, detect personal vs org actions.

### Step 5: Check Action References

Validate SHA pinning, detect mutable refs, check for deprecated action versions.

### Step 6: Generate Report

Create a structured security validation report with findings categorized by severity.

### Step 7: Apply Fixes (if --fix)

When `--fix` flag is provided, automatically apply safe fixes with confirmation.

## Report Format

```markdown
## 🔒 GitHub Actions Security Validation

### Summary
- 🚨 Critical: 1
- ❌ Errors: 3
- ⚠️ Warnings: 4
- ℹ️ Info: 2

### 🚨 CRITICAL FINDINGS

#### Hardcoded AWS Credentials
**File**: `.github/workflows/deploy.yml:23`
**Impact**: AWS access key exposed in workflow file
**Fix**: Remove hardcoded credentials, use GitHub secrets
**Action**: Rotate the exposed AWS key immediately

### ❌ ERRORS

#### Missing Permissions Block
**File**: `.github/workflows/ci.yml`
**Issue**: Workflow uses secrets but has no permissions block
**Impact**: GitHub token has write-all access by default
**Fix**:
\`\`\`yaml
permissions:
  contents: read
\`\`\`

### ⚠️ WARNINGS

#### Mutable Action Reference
**File**: `.github/workflows/ci.yml:15`
**Action**: `actions/cache@main`
**Issue**: Using mutable branch reference
**Fix**: Pin to SHA or stable tag

### Verdict
❌ FAILED - Fix 1 critical and 3 errors before merging
```

## Configuration

### Approved Sources Configuration

The skill uses `approved-sources.yml` to define trusted action sources, deprecated repositories, and security policies.

**Load Order** (first found is used):

1. `.claude/approved-sources.yml` (project-specific overrides)
2. `${SKILL_DIR}/approved-sources.yml` (skill defaults)

**Customize for your project**: Copy the default `approved-sources.yml` to `.claude/` and modify.

**Key Configuration Sections**:

```yaml
# Add your organization to trusted owners
trusted_owners:
  - actions
  - github
  - your-org-name  # <-- Add your org here

# Add specific trusted repositories
trusted_repos:
  - your-org/internal-action
  - community-user/vetted-action

# Mark deprecated actions
deprecated_repos:
  - old-org/archived-action@v1  # Use new-org/replacement instead

# SHA pinning policy
sha_pinning:
  required: true  # Require SHA pinning
  allow_version_tags_from_trusted: true  # Allow v1, v2 from trusted owners
  forbid_mutable_refs: true  # Block @main, @master

# Permissions policy
permissions:
  require_explicit: true  # Must have permissions: block
  forbid_write_all: true  # Block permissions: write-all
  max_default_scope: "read"  # Maximum default permission
```

See the included `approved-sources.yml` for complete configuration options.

## Examples

### Example 1: PR Review

```bash
# In a feature branch that modifies workflows
/validate-workflows

# Output:
# ⚠️ Found 2 security issues in changed workflows
# [detailed findings...]
```

### Example 2: Full Audit

```bash
# Audit all workflows
/validate-workflows --all

# Output:
# ## Workflow Security Audit
# Scanned: 5 workflow files
# Issues: 1 critical, 3 errors, 7 warnings
```

### Example 3: Check Action Sources

```bash
# Validate action sources against approved list
/validate-workflows --check-sources

# Output:
# Checking action sources...
# ✅ actions/checkout@v4 - Trusted owner
# ✅ docker/build-push-action@v5 - Trusted owner
# ⚠️ some-user/custom-action@main - NOT in approved sources
#    Repository: User account (not organization)
#    Status: Public, not archived
#    Action: Review code before use or add to trusted list
```

### Example 4: Fix Issues

```bash
# Auto-fix safe issues
/validate-workflows --fix

# Output:
# Applied 5 fixes:
# ✅ Added permissions to ci.yml
# ✅ Pinned actions/cache to SHA
# ✅ Updated checkout v2 → v4
# ⚠️ Commented out secret echo (review needed)
# ℹ️ 1 issue requires manual fix
```

## Integration with Other Skills

### With /create-pr

Add workflow validation to PR creation:

```bash
# Before creating PR
/validate-workflows
# If passed, then
/create-pr
```

### With /security-review

Include workflow security in security reviews (workflow validation would be part of the security review process).

## Dependencies

**Required**:

- `git` - For finding changed files and branch operations
- `yq` (v4+) - For parsing YAML workflows and configuration files

**Strongly Recommended**:

- `gh` CLI - For resolving action refs to SHAs and checking repository status
- `jq` - For processing JSON responses from GitHub API

**Optional**:

- `curl` - For direct API calls (fallback if `gh` CLI unavailable)

**Installation**:

```bash
# Install yq (YAML processor)
brew install yq  # macOS
sudo apt install yq  # Debian/Ubuntu
sudo dnf install yq  # Fedora/RHEL

# Install GitHub CLI
brew install gh  # macOS
sudo apt install gh  # Debian/Ubuntu
sudo dnf install gh  # Fedora/RHEL

# Authenticate GitHub CLI (for API access)
gh auth login
```

## Notes

- Validation is **read-only by default** (no modifications)
- `--fix` flag enables safe auto-fixes with confirmation
- Critical findings (hardcoded secrets) always require manual intervention
- Uses `approved-sources.yml` for configurable security policies
- Project-specific config (`.claude/approved-sources.yml`) overrides skill defaults
- Works offline for most checks; GitHub API used only for SHA resolution and repository status checks
- Respects GitHub API rate limits when using `gh` CLI
- Actions from local repositories (`./path/to/action`) always pass source validation

## Security Best Practices

1. **Always use explicit permissions**: Never rely on default write-all
2. **Pin actions to SHAs**: Mutable refs can be changed maliciously
3. **Maintain an approved sources list**: Only use actions from trusted owners/repos
4. **Check for deprecated actions**: Archived repos won't receive security updates
5. **Never echo secrets**: Secrets in logs are exposed to anyone with read access
6. **Trust cautiously**: Review third-party action code before adding to approved list
7. **Use pull_request, not pull_request_target**: Unless you really need write access from forks
8. **Rotate exposed secrets immediately**: If a secret appears in logs/code, it's compromised
9. **Prefer organization-maintained actions**: More likely to be maintained long-term
10. **Regularly audit workflows**: Run validation on all workflows, not just changed ones

## Advanced Usage

See [reference.md](./reference.md) for detailed implementation examples including:

- Creating organization-wide approved sources
- Automated validation in CI/CD
- Custom severity levels
- Action source scoring

## Reference

For detailed implementation steps and bash commands, see [reference.md](./reference.md).
