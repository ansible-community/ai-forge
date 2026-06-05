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

## Workflow

### Step 1: Discover Workflow Files

Find all workflow files to validate:

```bash
# Changed workflows in current branch
git diff --name-only $(git merge-base HEAD origin/main)..HEAD | grep -E '^\.github/workflows/.*\.ya?ml$'

# Or all workflows for full audit
find .github/workflows -type f \( -name '*.yml' -o -name '*.yaml' \)
```

### Step 2: Check Permissions

For each workflow file, validate permissions configuration:

#### Check 1: Missing permissions block

```bash
# Check if workflow uses secrets but has no permissions block
if grep -q 'secrets\.' workflow.yml && ! grep -q '^permissions:' workflow.yml; then
    echo "❌ ERROR: Missing permissions block (defaults to write-all)"
fi
```

#### Check 2: Write-all permissions

```bash
# Flag dangerous write-all
if grep -q 'permissions: *write-all' workflow.yml; then
    echo "❌ ERROR: Using forbidden 'permissions: write-all'"
fi
```

#### Check 3: Recommend least privilege

```bash
# Extract actions used and suggest minimal permissions
# Example: actions/checkout needs contents:read
# Example: peter-evans/create-pull-request needs contents:write, pull-requests:write
```

**Auto-fix**: Add recommended permissions block

```yaml
permissions:
  contents: read
  pull-requests: write  # Only if needed
```

### Step 3: Check Secrets Exposure

#### Check 1: Hardcoded secrets

```bash
# Scan for common secret patterns
grep -n -E '(AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36,}|xox[baprs]-[0-9]{10,12})' workflow.yml

# Scan for generic API keys
grep -n -E '["\']?[a-zA-Z_]*(api|secret|key|token|password)["\']?\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}' workflow.yml
```

#### Check 2: Secrets in echo/print

```bash
# Dangerous: echoing secrets to logs
grep -n 'echo.*\${{ *secrets\.' workflow.yml

# Dangerous: printing secrets
grep -n -E '(print|console\.log|logger\.).*\${{ *secrets\.' workflow.yml
```

#### Check 3: Secrets in URLs

```bash
# Secrets embedded in URLs (logged by proxies)
grep -n -E 'https?://[^/]*\${{ *secrets\.' workflow.yml
```

#### Check 4: Secrets to untrusted actions

```bash
# Find steps that pass secrets to third-party (non-official) actions
# Trusted: actions/*, github/*, docker/*, aws-actions/*, azure/*, google-github-actions/*
yq eval '.jobs.*.steps[] | select(.uses and (.with | contains("secrets."))) | .uses' workflow.yml \
  | grep -v -E '^(actions|github|docker|aws-actions|azure|google-github-actions)/'
```

#### Check 5: pull_request_target with secrets

```bash
# Extremely dangerous - PRs can access secrets
if grep -q 'pull_request_target' workflow.yml && grep -q 'secrets\.' workflow.yml; then
    echo "🚨 CRITICAL: pull_request_target with secrets allows PR attacks"
fi
```

### Step 4: Check Action Sources

#### Check 1: Load approved sources configuration

```bash
# Load approved-sources.yml from skill directory or .claude/
config_file="${SKILL_DIR}/approved-sources.yml"
if [[ ! -f "$config_file" ]]; then
    config_file=".claude/approved-sources.yml"
fi

# Parse trusted owners and repos using yq
trusted_owners=$(yq eval '.trusted_owners[]' "$config_file")
trusted_repos=$(yq eval '.trusted_repos[]' "$config_file")
deprecated_repos=$(yq eval '.deprecated_repos[]' "$config_file")
```

#### Check 2: Extract all action uses

```bash
# Get all action references from workflow
yq eval '.jobs.*.steps[] | select(.uses) | .uses' workflow.yml > actions_used.txt

# Example output:
# actions/checkout@v4
# docker/build-push-action@v5
# some-user/unknown-action@main
```

#### Check 3: Validate against deprecated repositories

```bash
# Check each action against deprecated list
while IFS= read -r action; do
    # Extract owner/repo and ref
    action_repo=$(echo "$action" | cut -d@ -f1)
    action_ref=$(echo "$action" | cut -d@ -f2)

    # Check if action is deprecated
    if echo "$deprecated_repos" | grep -q "^$action_repo@"; then
        echo "❌ ERROR: Deprecated action: $action"
        echo "  Repository: $action_repo is deprecated/archived"

        # Find suggested replacement from config
        replacement=$(yq eval ".deprecated_repos[] | select(. == \"$action\") | comment" "$config_file")
        if [[ -n "$replacement" ]]; then
            echo "  Suggested: $replacement"
        fi
    fi
done < actions_used.txt
```

#### Check 4: Validate against approved sources

```bash
# For each action, check if it's from a trusted source
while IFS= read -r action; do
    action_repo=$(echo "$action" | cut -d@ -f1)
    action_owner=$(echo "$action_repo" | cut -d/ -f1)

    # Skip local actions
    if [[ "$action_repo" == ./* ]]; then
        continue
    fi

    # Check trusted owners
    if echo "$trusted_owners" | grep -qx "$action_owner"; then
        echo "✅ Trusted owner: $action_owner"
        continue
    fi

    # Check trusted repos
    if echo "$trusted_repos" | grep -qx "$action_repo"; then
        echo "✅ Trusted repo: $action_repo"
        continue
    fi

    # Not in approved list
    echo "⚠️ WARNING: Untrusted action source: $action"
    echo "  Repository: $action_repo is not in approved sources list"
    echo "  Review the action code before merging"

    # Check if repo exists and is public
    if command -v gh &> /dev/null; then
        repo_status=$(gh api "repos/$action_repo" --jq '{archived:.archived, private:.private}' 2>/dev/null || echo "{}")

        archived=$(echo "$repo_status" | jq -r '.archived // false')
        private=$(echo "$repo_status" | jq -r '.private // false')

        if [[ "$archived" == "true" ]]; then
            echo "  ❌ ERROR: Repository is ARCHIVED"
        fi

        if [[ "$private" == "true" ]]; then
            echo "  ⚠️ Repository is private - ensure you have access"
        fi
    fi
done < actions_used.txt
```

#### Check 5: Detect personal vs organization actions

```bash
# Personal repos are higher risk than org-maintained
while IFS= read -r action; do
    action_repo=$(echo "$action" | cut -d@ -f1)
    action_owner=$(echo "$action_repo" | cut -d/ -f1)

    # Skip if already trusted
    if echo "$trusted_owners" | grep -qx "$action_owner"; then
        continue
    fi

    # Check if owner is an organization
    if command -v gh &> /dev/null; then
        owner_type=$(gh api "users/$action_owner" --jq '.type' 2>/dev/null || echo "User")

        if [[ "$owner_type" == "User" ]]; then
            echo "ℹ️ INFO: Action from personal repository: $action"
            echo "  Owner: $action_owner (individual, not organization)"
            echo "  Consider: Using organization-maintained alternatives"
        fi
    fi
done < actions_used.txt
```

**Auto-fix**: Add untrusted actions to local approved list (with confirmation)

```bash
# Offer to add reviewed actions to .claude/approved-sources.yml
echo "Add $action_repo to trusted sources? [y/N]"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    yq eval -i '.trusted_repos += ["'$action_repo'"]' .claude/approved-sources.yml
fi
```

### Step 5: Check Action References

#### Check 1: Mutable references

```bash
# Find actions using branch refs instead of tags/SHAs
yq eval '.jobs.*.steps[].uses' workflow.yml \
  | grep -E '@(main|master|develop|HEAD)$'
```

#### Check 2: SHA pinning validation

```bash
# Check if non-trusted actions are pinned to SHA
while IFS= read -r action; do
    action_repo=$(echo "$action" | cut -d@ -f1)
    action_ref=$(echo "$action" | cut -d@ -f2)
    action_owner=$(echo "$action_repo" | cut -d/ -f1)

    # Skip local actions
    if [[ "$action_repo" == ./* ]]; then
        continue
    fi

    # Check if ref is a SHA (40 hex characters)
    if [[ "$action_ref" =~ ^[a-f0-9]{40}$ ]]; then
        echo "✅ Properly pinned: $action"
        continue
    fi

    # Check if it's from a trusted owner (may allow version tags)
    if echo "$trusted_owners" | grep -qx "$action_owner"; then
        # Trusted owners can use version tags
        if [[ "$action_ref" =~ ^v[0-9]+(\.[0-9]+)?(\.[0-9]+)?$ ]]; then
            echo "ℹ️ Trusted action with version tag: $action"
            continue
        fi
    fi

    # Mutable ref or non-SHA
    if [[ "$action_ref" =~ ^(main|master|develop|HEAD)$ ]]; then
        echo "❌ ERROR: Mutable reference: $action"
        echo "  Using branch name - can be changed maliciously"
    else
        echo "⚠️ WARNING: Not pinned to SHA: $action"
        echo "  Using tag/branch instead of commit SHA"
    fi
done < actions_used.txt
```

#### Check 3: Deprecated versions

```bash
# Check against deprecated versions list
while IFS= read -r action; do
    # Check if exact action@version is in deprecated list
    if echo "$deprecated_repos" | grep -qx "$action"; then
        echo "❌ ERROR: Deprecated action version: $action"

        # Extract suggested replacement from comments
        suggestion=$(yq eval '.deprecated_repos | to_entries[] | select(.value == "'$action'") | .key' "$config_file" 2>/dev/null)
        if [[ -n "$suggestion" ]]; then
            echo "  Upgrade to: $suggestion"
        fi
    fi
done < actions_used.txt

# Common deprecated patterns
grep -n 'actions/checkout@v[12]' workflow.yml && echo "❌ Update to actions/checkout@v4"
grep -n 'actions/setup-node@v[12]' workflow.yml && echo "❌ Update to actions/setup-node@v4"
grep -n 'actions/cache@v[12]' workflow.yml && echo "❌ Update to actions/cache@v4"
```

**Check 4: Pin to SHA** (when --fix enabled)

```bash
# Use gh CLI to resolve tag to SHA
action_ref="actions/checkout@v4"
owner_repo=$(echo "$action_ref" | cut -d@ -f1)
ref=$(echo "$action_ref" | cut -d@ -f2)

# Get SHA for ref
sha=$(gh api repos/$owner_repo/commits/$ref --jq .sha)

# Suggest fix
echo "- uses: $owner_repo@$sha  # $ref"
```

### Step 6: Generate Report

Create a structured report with findings:

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
**Pattern**: `AKIA****************` (example pattern)
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

#### Deprecated Action Version
**File**: `.github/workflows/ci.yml:12`
**Action**: `actions/checkout@v2`
**Issue**: Using deprecated version (Node.js 12 EOL)
**Fix**: Upgrade to current version
\`\`\`yaml
- uses: actions/checkout@v4
\`\`\`

#### Untrusted Action Source
**File**: `.github/workflows/test.yml:28`
**Action**: `random-user/unknown-action@main`
**Issue**: Action from unapproved source, not in trusted list
**Repository Status**: User account (not organization)
**Fix**: Review action code or use approved alternative

### ⚠️ WARNINGS

#### Mutable Action Reference
**File**: `.github/workflows/ci.yml:15`
**Action**: `actions/cache@main`
**Issue**: Using mutable branch reference
**Fix**: Pin to SHA or stable tag
\`\`\`yaml
- uses: actions/cache@v4
# Or for maximum security:
- uses: actions/cache@0c45773b623bea8c8e75f6c82b208c3cf94ea4f9  # v4.0.0
\`\`\`

#### Secret Passed to Third-Party Action
**File**: `.github/workflows/notify.yml:34`
**Action**: `some-org/slack-notify@v1`
**Issue**: Passing secrets to non-trusted action
**Fix**: Verify action code before granting secret access

### ℹ️ INFO

#### Personal Repository Action
**File**: `.github/workflows/release.yml:45`
**Action**: `softprops/action-gh-release@v1`
**Note**: Action from individual user, not organization
**Status**: Widely trusted community action

### Verdict
❌ FAILED - Fix 1 critical and 3 errors before merging
```

### Step 7: Apply Fixes (if --fix)

When `--fix` flag is provided, automatically apply safe fixes:

1. **Add permissions blocks**:
   - Analyze actions used
   - Calculate minimal permissions needed
   - Insert at workflow level

2. **Pin action versions**:
   - Resolve tags to SHAs via GitHub API
   - Add inline comments with original version
   - Replace mutable refs

3. **Remove dangerous patterns**:
   - Comment out secret echo statements
   - Add warning comments

**Note**: Critical issues (hardcoded secrets) require manual remediation.

## Configuration

### Approved Sources Configuration

The skill uses `approved-sources.yml` to define trusted action sources, deprecated repositories, and security policies.

**Load Order** (first found is used):

1. `.claude/approved-sources.yml` (project-specific overrides)
2. `${SKILL_DIR}/approved-sources.yml` (skill defaults)

**Customize for your project**: Copy the default `approved-sources.yml` to `.claude/` and modify:

```bash
# Create project-specific configuration
cp ~/.claude/skills/validate-workflows/approved-sources.yml .claude/
```

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

**See `approved-sources.yml` for complete configuration options**, including:

- Secret exposure patterns
- Dangerous workflow patterns
- Untrusted source detection rules
- Custom severity levels

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
/validate-workflows --check-all

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
# ❌ old-org/deprecated-action@v1 - DEPRECATED
#    Suggested: Use new-org/replacement@v2 instead
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

Include workflow security in security reviews:

```bash
/security-review  # Automatically runs workflow validation
```

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
- Works offline for most checks; GitHub API used only for:
  - SHA resolution when pinning actions
  - Repository status checks (archived, private, org vs user)
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

### Creating Organization-Wide Approved Sources

For organizations with multiple repositories, create a shared approved sources configuration:

```bash
# Create organization config repository
mkdir -p github-config/.claude
cp approved-sources.yml github-config/.claude/

# In each repository, symlink or copy the org config
ln -s ../github-config/.claude/approved-sources.yml .claude/
```

### Automated Validation in CI/CD

Add workflow validation to your CI pipeline:

```yaml
# .github/workflows/validate.yml
name: Validate Workflows
on:
  pull_request:
    paths:
      - '.github/workflows/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y yq

      - name: Validate workflows
        run: |
          # Run Claude Code validation skill
          claude /validate-workflows
```

### Custom Severity Levels

Adjust severity levels in your project's `.claude/approved-sources.yml`:

```yaml
# Stricter policy: require SHA pinning (error instead of warning)
sha_pinning:
  required: true
  allow_version_tags_from_trusted: false  # Force SHAs even for trusted

# Stricter policy: block all non-approved sources
untrusted_patterns:
  - pattern: "^(?!actions|github|docker|your-org).*"
    severity: error  # Block instead of warn
    description: "Only pre-approved sources allowed"
```

### Action Source Scoring

The skill can generate a security score for each action based on:

- **Trust level**: Official (10) > Org-approved (8) > Community-trusted (6) > Unknown (2)
- **Reference security**: SHA-pinned (10) > Version tag (7) > Mutable ref (3)
- **Repository status**: Active (10) > Archived (0) > Unknown (5)
- **Maintenance**: Recent commits (10) > Stale (5)

**Usage**:

```bash
/validate-workflows --score
# Output:
# actions/checkout@v4 - Score: 27/30 (EXCELLENT)
# random-user/action@main - Score: 8/30 (POOR)
```
