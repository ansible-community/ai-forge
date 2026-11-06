---
name: stable-release
description: >
  Orchestrates end-to-end stable-branch collection releases. Use this skill
  when you want to release a collection with stable-X branches by coordinating
  stable-release-analyze, stable-release-prep, docs-generate, tox-lint, and
  sanity in sequence.
user-invocable: true
---

# Stable Branch Release Orchestrator

Complete end-to-end release workflow for collections with stable-X branches.

## Author

**Alina Buzachis (alinabuzachis)** - Ansible Cloud Content Team

## Reference Documentation

- Ansible Cloud Content Handbook: https://github.com/ansible-collections/cloud-content-handbook
- Release Process: https://github.com/ansible-collections/cloud-content-handbook/blob/main/stable-release.md

## Purpose

Orchestrates all release steps from analysis to PR creation for stable-branch workflows. Imports
and coordinates individual skills (stable-release-analyze, stable-release-prep, docs-generate,
tox-lint, sanity) in the correct order with proper error handling and user interaction.

## Pre-Flight Validation

Before starting the release workflow, validate environment and prerequisites.

```bash
#!/usr/bin/env bash
set -e

echo "🔍 Running pre-flight checks..."

# Check 1: Required tools
MISSING_TOOLS=()
for cmd in git gh tox ansible-test; do
  if ! command -v $cmd &> /dev/null; then
    MISSING_TOOLS+=("$cmd")
  fi
done

# antsibull-changelog check (may be in venv)
if ! command -v antsibull-changelog &> /dev/null && ! python3 -m pip show antsibull-changelog &> /dev/null; then
  MISSING_TOOLS+=("antsibull-changelog")
fi

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
  echo "❌ Missing required tools: ${MISSING_TOOLS[*]}"
  echo "   Install missing tools before proceeding"
  exit 1
fi
echo "✓ All required tools present"

# Check 2: gh CLI authentication
if ! gh auth status &> /dev/null; then
  echo "❌ gh CLI not authenticated"
  echo "   Run: gh auth login"
  exit 1
fi
echo "✓ gh CLI authenticated"

# Check 3: Clean working tree (allow untracked files, but no modifications)
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
  echo "❌ Working tree has uncommitted changes"
  echo ""
  git status --short
  echo ""
  echo "Commit or stash changes before releasing"
  exit 1
fi
echo "✓ Working tree clean"

# Check 4: Target branch exists on upstream
BRANCH="$1"
if [ -n "$BRANCH" ]; then
  if ! git rev-parse --verify "upstream/$BRANCH" &> /dev/null 2>&1; then
    echo "❌ Branch upstream/$BRANCH does not exist"
    echo "   Available branches:"
    git branch -r | grep upstream/stable- | sed 's|^  ||'
    exit 1
  fi
  echo "✓ Target branch exists: upstream/$BRANCH"
fi

# Check 5: Changelog fragments exist (if in a collection)
if [ -f "galaxy.yml" ] && [ -d "changelogs/fragments" ]; then
  # Count .yml files excluding .keep
  FRAGMENT_COUNT=$(find changelogs/fragments -name '*.yml' ! -name '.keep' 2>/dev/null | wc -l)
  if [ "$FRAGMENT_COUNT" -eq 0 ]; then
    echo "⚠️  No changelog fragments found"
    echo "   This may be intentional for a version-only release"
  else
    echo "✓ Found $FRAGMENT_COUNT changelog fragment(s)"
  fi
fi

echo ""
echo "✅ All pre-flight checks passed"
echo ""
```

**Usage in orchestrator:**
Run this before Step 1 (Analysis). If it fails, abort early and save time.

## Shared Virtual Environment

The orchestrator creates ONE virtual environment shared by all sub-skills.

**Setup (at start of workflow):**

```bash
# Create shared venv with timestamp to avoid conflicts
export ANSIBLE_RELEASE_VENV="$PWD/.venv-release-$(date +%s)"

echo "Creating shared virtual environment: $ANSIBLE_RELEASE_VENV"
python3 -m venv "$ANSIBLE_RELEASE_VENV"
source "$ANSIBLE_RELEASE_VENV/bin/activate"

# Install all dependencies at once (use uv for speed if available)
if command -v uv &> /dev/null; then
  uv pip install antsibull-changelog ansible-core tox pyyaml
else
  pip install --quiet antsibull-changelog ansible-core tox pyyaml
fi

echo "✓ Shared venv created and activated"
```

**Benefits:**

- Sub-skills check `$ANSIBLE_RELEASE_VENV` and reuse if present
- Saves ~30-45 seconds (no duplicate venv creation)
- Ensures version consistency across skills
- Automatic cleanup at end

**Cleanup (at end of workflow):**

```bash
# After PR creation or on error
if [ -n "$ANSIBLE_RELEASE_VENV" ] && [ -d "$ANSIBLE_RELEASE_VENV" ]; then
  rm -rf "$ANSIBLE_RELEASE_VENV"
  echo "✓ Cleaned up shared venv"
fi
```

## File Operations - Batch Processing

**CRITICAL**: This orchestrator must minimize permission prompts by batching operations.

**Key principles**:

1. **Pre-flight validation first**: Check prerequisites before any operations
2. **Shared virtual environment**: Set up ONE .venv with all required dependencies
3. **Batch all file reads**: Read galaxy.yml, changelog fragments, and other files in ONE message with parallel tool calls
4. **Parallel quality checks**: Run `/tox-lint` and `/sanity` in parallel using background agents
5. **Sequential git operations**: Git operations via Bash tool are naturally batched in commands

**Example flow**:

```
Message 1: Run pre-flight validation
Message 2: Setup shared venv with uv/pip (antsibull-changelog, ansible-core, tox)
Message 3: Read galaxy.yml + all changelog fragments (parallel)
Message 4: Run git operations (single bash command with &&)
Message 5: Invoke /tox-lint and /sanity (parallel, run_in_background)
Message 6: Write/Edit files after analysis complete
```

## Configuration

Reads from `~/.ansible-release.conf`:

```bash
export GITHUB_USERNAME="alinabuzachis"
export ANSIBLE_COLLECTIONS_PATH="~/dev/collections/ansible_collections"
export SANITY_MODE="smart"
export AUTO_CREATE_PR="prompt" # true | false | prompt
export LINT_ON_COMMIT="true"
export SANITY_ON_COMMIT="true"
```

## When to Use This Skill

- Performing a complete collection release
- Automating the release process from start to finish
- After changelog fragments have been created
- When asked to release, publish, or ship a new version
- To follow the cloud-content-handbook release process

## Usage Examples

```bash
# Full automated release (interactive prompts)
/stable-release

# Analyze only (no changes)
/stable-release --analyze-only

# Prepare specific version
/stable-release --collection amazon.ai --version 1.0.1 --branch stable-1

# Custom release date (future-dated or backdated)
/stable-release --collection amazon.ai --version 1.0.1 --branch stable-1 --release-date 2026-06-15

# Skip specific steps
/stable-release --skip-lint --skip-sanity

# Full automation (no prompts)
/stable-release --auto --create-pr

# Dry run (show what would happen)
/stable-release --dry-run
```

## Workflow Steps

The orchestrator executes in this order:

### Step 0: Pre-Flight Validation

- Check required tools (git, gh, tox, ansible-test, antsibull-changelog)
- Verify gh CLI authentication
- Ensure clean working tree
- Validate target branch exists
- Confirm changelog fragments exist

**On failure:** Abort immediately, provide actionable error message

### Step 1: Setup Shared Environment

- Create shared virtual environment
- Install all dependencies once
- Export `ANSIBLE_RELEASE_VENV` for sub-skills
- Activate venv for current session

### Step 2: Analysis

- Run `stable-release-analyze` to determine version needed
- Calculate SemVer bump from changelog fragments
- Prompt user to proceed (unless `--auto`)

### Step 3: Preparation

- Run `stable-release-prep` (reuses shared venv)
- Update galaxy.yml version
- Generate changelog with antsibull-changelog
- Create release summary fragment

### Step 4: Documentation (Optional)

- Run `docs-generate` if not `--skip-docs`
- Update module RST files and README.md

### Step 5: Quality Checks (Parallel)

- Run `tox-lint` and `sanity` in parallel
- Unless `--skip-lint` or `--skip-sanity`
- Fail workflow if checks fail (unless `--force`)

### Step 6: Commit & Push

- Stage all changes
- Create commit with standard message
- Push to origin (fork)

### Step 7: Pull Request (Conditional)

- Create PR if `--create-pr` or `AUTO_CREATE_PR=true`
- Otherwise prompt user

### Step 8: Cleanup

- Remove shared virtual environment
- Display summary and next steps

See [references/workflow-steps.md](references/workflow-steps.md) for detailed command examples.

## Complete Output Example

See [references/output-example.md](references/output-example.md) for a full end-to-end run.

## Error Handling & Recovery

See [references/error-handling.md](references/error-handling.md) for recoverable and
non-recoverable errors and resume capability.

## Flags & Options

| Flag | Description |
| ----- | ----------- |
| `--analyze-only` | Run analysis and stop |
| `--release-date YYYY-MM-DD` | Custom release date (default: today) |
| `--skip-lint` | Skip linting step |
| `--skip-sanity` | Skip sanity testing |
| `--skip-docs` | Skip documentation generation |
| `--force` | Continue even if quality checks fail |
| `--auto` | No interactive prompts (use config defaults) |
| `--create-pr` | Automatically create PR |
| `--dry-run` | Show what would happen without making changes |
| `--resume` | Resume from last successful step |

## Integration Points

This orchestrator imports:

- `/stable-release-analyze` - Determine version needed
- `/stable-release-prep` - Create branch and changelog (uses shared venv)
- `/docs-generate` - Update documentation
- `/tox-lint` - Run linters
- `/sanity` - Run sanity tests
- `git commit and git push` - Commit and push

## Requirements

### System Requirements

- `git` with configured remotes
- `tox` with lint environments
- `antsibull-changelog` (installed in shared venv)
- `ansible-test` for sanity checks
- `gh` CLI (for PR creation)

### Repository Requirements

- Git remotes: `origin` (fork), `upstream` (canonical)
- `galaxy.yml` with valid version
- `tox.ini` with lint environments
- `changelogs/fragments/` with at least one fragment

### Configuration Requirements

- `~/.ansible-release.conf` with GITHUB_USERNAME (optional)
- SSH keys or HTTPS credentials for GitHub
- gh CLI authenticated (`gh auth login`)

## Exit Codes

- `0`: Release workflow completed successfully
- `1`: Workflow failed at any step
- `2`: Configuration error or missing requirements (from pre-flight)
- `130`: User aborted (Ctrl+C)

## Implementation Notes

See [references/implementation-notes.md](references/implementation-notes.md) for parallel
execution, state management, user interaction, and handbook compliance guidance.
