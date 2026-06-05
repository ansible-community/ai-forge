# validate-workflows Implementation Reference

Detailed implementation guide for the validate-workflows skill. This file contains the step-by-step bash commands and checks that Claude uses when validating GitHub Actions workflows.

For the main skill documentation, see [SKILL.md](./SKILL.md).

## Table of Contents

1. [Discover Workflow Files](#step-1-discover-workflow-files)
2. [Check Permissions](#step-2-check-permissions)
3. [Check Secrets Exposure](#step-3-check-secrets-exposure)
4. [Check Action Sources](#step-4-check-action-sources)
5. [Check Action References](#step-5-check-action-references)
6. [Generate Report](#step-6-generate-report)
7. [Apply Fixes](#step-7-apply-fixes)

## Step 1: Discover Workflow Files

Find all workflow files to validate:

```bash
# Changed workflows in current branch
git diff --name-only $(git merge-base HEAD origin/main)..HEAD | grep -E '^\.github/workflows/.*\.ya?ml$'

# Or all workflows for full audit
find .github/workflows -type f \( -name '*.yml' -o -name '*.yaml' \)
```

## Step 2: Check Permissions

For each workflow file, validate permissions configuration:

### Check 1: Missing permissions block

```bash
# Check if workflow uses secrets but has no permissions block
if grep -q 'secrets\.' workflow.yml && ! grep -q '^permissions:' workflow.yml; then
    echo "❌ ERROR: Missing permissions block (defaults to write-all)"
fi
```

### Check 2: Write-all permissions

```bash
# Flag dangerous write-all
if grep -q 'permissions: *write-all' workflow.yml; then
    echo "❌ ERROR: Using forbidden 'permissions: write-all'"
fi
```

### Check 3: Recommend least privilege

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

## Step 3: Check Secrets Exposure

### Check 1: Hardcoded secrets

```bash
# Scan for common secret patterns
grep -n -E '(AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36,}|xox[baprs]-[0-9]{10,12})' workflow.yml

# Scan for generic API keys
grep -n -E '["\']?[a-zA-Z_]*(api|secret|key|token|password)["\']?\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}' workflow.yml
```

### Check 2: Secrets in echo/print

```bash
# Dangerous: echoing secrets to logs
grep -n 'echo.*\${{ *secrets\.' workflow.yml

# Dangerous: printing secrets
grep -n -E '(print|console\.log|logger\.).*\${{ *secrets\.' workflow.yml
```

### Check 3: Secrets in URLs

```bash
# Secrets embedded in URLs (logged by proxies)
grep -n -E 'https?://[^/]*\${{ *secrets\.' workflow.yml
```

### Check 4: Secrets to untrusted actions

```bash
# Find steps that pass secrets to third-party (non-official) actions
# Trusted: actions/*, github/*, docker/*, aws-actions/*, azure/*, google-github-actions/*
yq eval '.jobs.*.steps[] | select(.uses and (.with | contains("secrets."))) | .uses' workflow.yml \
  | grep -v -E '^(actions|github|docker|aws-actions|azure|google-github-actions)/'
```

### Check 5: pull_request_target with secrets

```bash
# Extremely dangerous - PRs can access secrets
if grep -q 'pull_request_target' workflow.yml && grep -q 'secrets\.' workflow.yml; then
    echo "🚨 CRITICAL: pull_request_target with secrets allows PR attacks"
fi
```

## Step 4: Check Action Sources

### Check 1: Load approved sources configuration

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

### Check 2: Extract all action uses

```bash
# Get all action references from workflow
yq eval '.jobs.*.steps[] | select(.uses) | .uses' workflow.yml > actions_used.txt
```

### Check 3: Validate against deprecated repositories

```bash
# Check each action against deprecated list
while IFS= read -r action; do
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

### Check 4: Validate against approved sources

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

### Check 5: Detect personal vs organization actions

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

## Step 5: Check Action References

### Check 1: Mutable references

```bash
# Find actions using branch refs instead of tags/SHAs
yq eval '.jobs.*.steps[].uses' workflow.yml \
  | grep -E '@(main|master|develop|HEAD)$'
```

### Check 2: SHA pinning validation

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

### Check 3: Deprecated versions

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

## Step 6: Generate Report

Create a structured report with findings. See the main SKILL.md for the complete report format.

## Step 7: Apply Fixes

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
