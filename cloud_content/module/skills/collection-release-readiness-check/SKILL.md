---
name: collection-release-readiness-check
description: >-
  Checks whether a given Ansible collection Git repository needs a minor or
  patch release and whether it is ready to create a release prep PR. By default,
  checks the two most recent stable branches. Requires collection_git_url (or
  local path). Does not perform the release itself. For major releases, redirect
  to the handbook and release skill.
version: "1.0"
---

# Skill: collection-release-readiness-check

## Purpose

Answer two questions for each stable branch (default: **two most recent** stable branches), in order:

1. **Is a release needed?** — are there substantial changes on the stable branch worth releasing?
2. **Is the repo ready to create a prep PR?** — are all backports merged and patchback failures resolved?

If the answer to (1) is no, stop — there is nothing to prepare for that branch.

**Out of scope:** Major releases, prep PR execution, tagging, publishing. For those use the **`release`** skill.

## When to invoke

- "Is `<repo>` ready for a minor/patch release?"
- "Do I need to release `<collection>`?"
- "Can I create a prep PR for `stable-X`?"

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| `collection_git_url` | **Yes** | Clone URL or absolute path to a local clone |
| `target_stable_branch` | No | e.g. `stable-11`. Defaults to the highest `stable-*` branch found. |
| `release_kind` | No | `minor`, `patch`, or **`auto`** (default — infer from fragments). |

## Prerequisites

- `git` in PATH; network if cloning
- Optional: `gh` + `jq` for backport PR checks

---

## Workflow

### Step 1 — Obtain checkout

**Local path:**

```bash
cd <collection_git_url> && git fetch --all --prune
```

**Remote URL:**

```bash
short_hash=$(echo "<collection_git_url>" | md5sum | cut -c1-8)
git clone --filter=blob:none <collection_git_url> /tmp/collection-release-readiness-${short_hash}
cd /tmp/collection-release-readiness-${short_hash}
git fetch origin 'refs/heads/stable-*:refs/remotes/origin/stable-*' 2>/dev/null || true
git fetch origin
```

Record default branch name:

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' \
  || git remote show origin | grep 'HEAD branch' | awk '{print $NF}'
```

### Step 2 — Resolve upstream remote and repo

Use **`get-upstream-info`** to determine:

- `UPSTREAM_REMOTE` — canonical remote name (`upstream` in fork workflows, `origin` in direct clones)
- `UPSTREAM_PATH` — `org/repo` for `gh` commands (e.g. `ansible-collections/amazon.aws`)

Use `UPSTREAM_REMOTE` in all `git` commands, `UPSTREAM_PATH` in all `gh` commands.

### Step 3 — Find target stable branch(es)

```bash
git branch -r \
  | grep -E "${UPSTREAM_REMOTE}/stable-[0-9]+$" \
  | sed "s|^[[:space:]]*${UPSTREAM_REMOTE}/||" \
  | sort -V
```

If `target_stable_branch` is given, use only that branch. Otherwise:

- Select the **two most recent** stable branches (e.g., `stable-11` and `stable-10`)
- Check both branches for release readiness
- Team policy expects patch fixes to be assessed for multiple supported stable lines

Extract major number `N` for each branch (e.g. `stable-11` → `N=11`).

If no `stable-*` branches exist, **STOP** — collection does not use stable branches.

---

### Question 1 — Is a release needed?

Checkout the target stable branch and scan changelog fragments:

```bash
git checkout ${UPSTREAM_REMOTE}/<target_stable_branch> --detach 2>/dev/null

find changelogs/fragments -maxdepth 1 \( -name '*.yml' -o -name '*.yaml' \) 2>/dev/null \
  | grep -v 'changelogs/fragments/archive'

git checkout <default_branch> 2>/dev/null || git checkout -
```

Classify top-level keys found ([full category reference](https://docs.ansible.com/projects/ansible/latest/community/collection_development_process.html#creating-a-changelog-fragment)):

| Fragment key(s) | Indicates |
| --------------- | --------- |
| `minor_changes`, `deprecated_features`, `add plugin.*`, `add object.*` | **Minor** release |
| `bugfixes`, `security_fixes`, `known_issues` | **Patch** release |
| `trivial` | Not a release driver — ignore |
| `breaking_changes`, `major_changes`, `removed_features` | **Major** — out of scope for this skill; redirect to major release process |

**Note:** New modules and plugins do not generate changelog fragments — tooling detects them via `version_added`. If no fragments exist, also check for new module/plugin commits since the last tag:

```bash
last_tag=$(git describe --tags --abbrev=0 ${UPSTREAM_REMOTE}/<target_stable_branch> 2>/dev/null)
git log "${last_tag}..${UPSTREAM_REMOTE}/<target_stable_branch>" --oneline --no-merges \
  | grep -v 'Merge\|changelog\|version bump'
```

New module commits with no fragments still indicate a **minor** release.

**Verdict for Question 1:**

- Patch or minor drivers found → **Release needed** — proceed to Question 2.
- Only `trivial` / no drivers and no new module commits → **NO RELEASE NEEDED** — stop here.
- `release_kind` mismatch (e.g. patch requested but only minor fragments) → report the conflict and ask RM to confirm.
- Major-category fragments → **NOT IN SCOPE** — redirect to major release process.

---

### Question 2 — Is the repo ready for a prep PR?

Run both checks. Any blocker means **NOT READY**.

#### Check A — Open backport PRs (requires `gh` + `jq`)

```bash
# Open patchback-created PRs targeting stable-N not yet merged → BLOCKER
gh pr list --repo UPSTREAM_PATH \
  --base <target_stable_branch> \
  --state open \
  --json number,title,url,labels \
  --limit 20 \
  | jq '[.[] | select(.labels | map(.name) | contains(["backport-N"]))]'
```

**Also check for PRs with backport labels that target other branches** (these may need to be merged to stable-N as well):

```bash
gh pr list --repo UPSTREAM_PATH \
  --state open \
  --json number,title,url,labels \
  --limit 50 \
  | jq '.[] | select(.labels | map(.name) | contains(["backport-N"]))'
```

**Note:** The jq filter `map(.name) | contains(["backport-N"])` correctly checks if the array of label names contains the backport label.
The simpler `.labels[].name == "backport-N"` syntax does not work reliably with jq's select function.

Open backport PRs → **BLOCKER** — merge them before creating the prep PR.

#### Check B — Patchback failures on main-branch PRs (requires `gh` + `jq`)

```bash
# Get the last tag on the stable branch
last_tag=$(git describe --tags --abbrev=0 ${UPSTREAM_REMOTE}/<target_stable_branch> 2>/dev/null)

# Get the actual tag creation date from GitHub API (not git commit date)
if [ -n "$last_tag" ]; then
  last_tag_date=$(gh api repos/${UPSTREAM_PATH}/git/refs/tags/${last_tag} 2>/dev/null \
    | jq -r '.object.url' \
    | xargs gh api 2>/dev/null \
    | jq -r '.tagger.date // .committer.date' \
    | cut -d'T' -f1)
else
  last_tag_date="2000-01-01"
fi
last_tag_date=${last_tag_date:-"2000-01-01"}

# Merged main PRs where patchback failed for stable-N since last tag → BLOCKER
gh pr list --repo UPSTREAM_PATH \
  --base <default_branch> \
  --label "backport-N" \
  --label "backport_failed" \
  --state closed \
  --json number,title,url,mergedAt \
  --limit 50 \
  | jq --arg since "$last_tag_date" '[.[] | select(.mergedAt != null and .mergedAt > $since)]'
```

**Important:** Use GitHub API to get the **actual tag creation date** (when the tag was pushed to GitHub), not the git commit date.
This ensures accurate scoping of the backport failure check to the current release cycle.
The Galaxy/Automation Hub publish date may lag by hours or days after the tag is created.

Patchback failures → **BLOCKER** — manually cherry-pick the change to `stable-N` before the prep PR:

```bash
git fetch upstream
git checkout -b <fix-branch> upstream/<target_stable_branch>
git cherry-pick -x <sha>          # use -m 1 if merge commit
```

If `gh` / `jq` unavailable: mark both checks as **SKIPPED** — recommend manually reviewing open PRs on `stable-N` and checking for `backport_failed` labels.

---

### Final output

When checking a single branch:

```text
## Stable Branch: <target_stable_branch>

### Question 1 — Release needed?
YES (minor) | YES (patch) | NO | OUT OF SCOPE (major)

### Question 2 — Ready for prep PR?
READY | NOT READY | SKIPPED (gh unavailable)

### Blockers (if NOT READY)
- <list each>

### Notes
- Last tag: <tag_name> (created <YYYY-MM-DD> from GitHub API, ~N weeks/months ago)
- <warnings, informational items>

### Next steps (if READY)
1. Create prep branch: git checkout -b prep_release_x_y_z <target_stable_branch>
2. Bump galaxy.yml version, run: antsibull-changelog release
3. Open prep PR targeting <target_stable_branch>
4. Follow the `release` skill for CI, tagging, and publish steps
```

When checking multiple branches (default behavior), repeat the above structure for each branch, ordered from newest to oldest (e.g., `stable-11` then `stable-10`).

**Important:** Always report tag dates using the actual GitHub tag creation date from the API, and include a human-readable time reference (e.g., "~2 weeks ago", "~3 months ago") to provide context.

---

## Integration

- **`get-upstream-info`** — required in step 2
- **`next-release`** — determine the version number for the prep PR
- **`release`** — execute the release after prep PR is merged

## Notes

- `hashicorp.vault` canonical repo is `ansible-automation-platform/hashicorp.vault` — `get-upstream-info` resolves this.
- Release manager decisions override this skill's output; it **informs**, it does **not** approve.
- **Tag dates**: Always use GitHub API (`gh api repos/<org>/<repo>/git/refs/tags/<tag>`) to get actual tag creation dates, not `git log` which returns commit dates.
  Verify against GitHub tags page (`https://github.com/<org>/<repo>/tags`) if in doubt.
- **Backport PR checks**: Check both PRs targeting the stable branch AND PRs with backport labels across all open PRs (some may target main but need to be backported).
- **Multi-branch default**: By default, checks the two most recent stable branches (e.g., `stable-11` and `stable-10`). Override with `target_stable_branch` to check only one.
