# validate-workflows Implementation Reference

Detailed implementation guide for the validate-workflows skill. This file contains the step-by-step bash commands and checks that Claude uses when validating GitHub Actions workflows.

For the main skill documentation, see [SKILL.md](./SKILL.md).

## Table of Contents

1. [Load Configuration](#step-1-load-configuration)
2. [Discover Workflow Files](#step-2-discover-workflow-files)
3. [Check Permissions](#step-3-check-permissions)
4. [Check Secrets Exposure](#step-4-check-secrets-exposure)
5. [Check Action Sources](#step-5-check-action-sources)
6. [Check Action References](#step-6-check-action-references)
7. [Generate Report](#step-7-generate-report)
8. [Apply Fixes](#step-8-apply-fixes)

## Step 1: Load Configuration

Load the trusted-actions configuration using a three-tier model: remote fetch from ai-forge, local fallback, then project overrides merged on top.

### Tier 1: Fetch latest from ai-forge (best-effort)

```bash
remote_url="https://raw.githubusercontent.com/ansible-community/ai-forge/main/ansible-collection-sdlc/module/skills/validate-workflows/trusted-actions.yml"
remote_config=$(curl -sf --connect-timeout 5 --max-time 10 "$remote_url" 2>/dev/null) || remote_config=""
```

### Tier 2: Fall back to local skill copy

```bash
if [[ -n "$remote_config" ]]; then
    base_config_source="remote (latest from ai-forge)"
    echo "$remote_config" > /tmp/validate-wf-base-config.yml
    base_config="/tmp/validate-wf-base-config.yml"
else
    base_config="${SKILL_DIR}/trusted-actions.yml"
    base_config_source="local (installed with skill)"
fi

# Parse base trusted lists
trusted_owners=$(yq eval '.trusted_owners[]' "$base_config" 2>/dev/null)
trusted_repos=$(yq eval '.trusted_repos[]' "$base_config" 2>/dev/null)
deprecated_repos=$(yq eval '.deprecated_repos[]' "$base_config" 2>/dev/null)
```

### Tier 3: Merge project-specific overrides

```bash
project_config=".claude/approved-sources.yml"
if [[ -f "$project_config" ]]; then
    # Detect old-format config (flat trusted_owners key)
    has_flat_owners=$(yq eval '.trusted_owners // ""' "$project_config" 2>/dev/null)
    has_additive_owners=$(yq eval '.additional_trusted_owners // ""' "$project_config" 2>/dev/null)

    if [[ -n "$has_flat_owners" && -z "$has_additive_owners" ]]; then
        # Old format: treat flat keys as full overrides
        echo "ℹ️ Project config uses legacy format (flat trusted_owners)."
        echo "  Consider migrating to additional_* keys for additive merging."
        echo "  See: ${SKILL_DIR}/examples/project-approved-sources.yml"
        trusted_owners=$(yq eval '.trusted_owners[]' "$project_config" 2>/dev/null)
        trusted_repos=$(yq eval '.trusted_repos[]' "$project_config" 2>/dev/null)
        deprecated_repos=$(yq eval '.deprecated_repos[]' "$project_config" 2>/dev/null)
    else
        # New format: merge additive keys
        additional_owners=$(yq eval '.additional_trusted_owners[]' "$project_config" 2>/dev/null)
        additional_repos=$(yq eval '.additional_trusted_repos[]' "$project_config" 2>/dev/null)
        additional_deprecated=$(yq eval '.additional_deprecated_repos[]' "$project_config" 2>/dev/null)

        if [[ -n "$additional_owners" ]]; then
            trusted_owners=$(printf '%s\n%s' "$trusted_owners" "$additional_owners")
        fi
        if [[ -n "$additional_repos" ]]; then
            trusted_repos=$(printf '%s\n%s' "$trusted_repos" "$additional_repos")
        fi
        if [[ -n "$additional_deprecated" ]]; then
            deprecated_repos=$(printf '%s\n%s' "$deprecated_repos" "$additional_deprecated")
        fi
    fi

    # Policy sections override defaults when present
    # (sha_pinning, permissions, secret_patterns, etc.)
fi

# Build trusted-owner pattern for grep exclusions
trusted_pattern=$(echo "$trusted_owners" | tr '\n' '|' | sed 's/|$//')

# Report config sources
echo "Configuration:"
echo "  Base: $base_config_source"
if [[ -f "$project_config" ]]; then
    echo "  Project overrides: $project_config"
fi
```

## Step 2: Discover Workflow Files

Find all workflow files to validate:

```bash
# Changed workflows in current branch
git diff --name-only $(git merge-base HEAD origin/main)..HEAD | grep -E '^\.github/workflows/.*\.ya?ml$'

# Or all workflows for full audit
find .github/workflows -type f \( -name '*.yml' -o -name '*.yaml' \)
```

## Step 3: Check Permissions

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

## Step 4: Check Secrets Exposure

### Check 1: Hardcoded secrets

```bash
# Scan for common secret patterns (loaded from config secret_patterns)
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
# Find steps that pass secrets to non-trusted actions
# Uses $trusted_pattern built from loaded config in Step 1
yq eval '.jobs.*.steps[] | select(.uses and (.with | contains("secrets."))) | .uses' workflow.yml \
  | grep -v -E "^($trusted_pattern)/"
```

### Check 5: pull_request_target with secrets

```bash
# Extremely dangerous - PRs can access secrets
if grep -q 'pull_request_target' workflow.yml && grep -q 'secrets\.' workflow.yml; then
    echo "🚨 CRITICAL: pull_request_target with secrets allows PR attacks"
fi
```

## Step 5: Check Action Sources

### Check 1: Extract all action uses

```bash
# Get all action references from workflow
yq eval '.jobs.*.steps[] | select(.uses) | .uses' workflow.yml > actions_used.txt
```

### Check 2: Validate against deprecated repositories

```bash
# Check each action against deprecated list (loaded from config in Step 1)
while IFS= read -r action; do
    action_repo=$(echo "$action" | cut -d@ -f1)

    # Check if exact action or action@version is deprecated
    if echo "$deprecated_repos" | grep -qx "$action"; then
        echo "❌ ERROR: Deprecated action version: $action"
    elif echo "$deprecated_repos" | grep -qx "$action_repo"; then
        echo "❌ ERROR: Deprecated action: $action"
        echo "  Repository: $action_repo is deprecated/archived"
    fi
done < actions_used.txt
```

### Check 3: Validate against approved sources

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

### Check 4: Detect personal vs organization actions

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

**Auto-fix**: Add untrusted actions to project approved list (with confirmation)

```bash
# Offer to add reviewed actions to .claude/approved-sources.yml
echo "Add $action_repo to project trusted sources? [y/N]"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    if [[ ! -f .claude/approved-sources.yml ]]; then
        echo "additional_trusted_repos: []" > .claude/approved-sources.yml
    fi
    yq eval -i '.additional_trusted_repos += ["'$action_repo'"]' .claude/approved-sources.yml
fi
```

## Step 6: Check Action References

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
# Check against deprecated list loaded from config in Step 1
while IFS= read -r action; do
    if echo "$deprecated_repos" | grep -qx "$action"; then
        echo "❌ ERROR: Deprecated action version: $action"
    fi
done < actions_used.txt
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

## Step 7: Generate Report

Create a structured report with findings. See the main SKILL.md for the complete report format.

## Step 8: Apply Fixes

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
