---
name: release
description: >-
  Guides the release of an Ansible collection following the
  upstream process (without release branches). Automatically
  determines the next version from changelog fragments. Outputs
  step-by-step instructions with commands for changelog generation,
  release PR, tagging, Galaxy publication, version bump, and GitHub
  release. Use when asked to release, publish, or tag a new
  collection version.
---

# Skill: release

## Purpose

Guide the release of an Ansible collection. This skill is collection-generic —
it derives namespace, name, and current version from `galaxy.yml`,
and automatically determines the next version from changelog fragment categories.

## When to Invoke

TRIGGER when:

- A user asks to release, publish, or tag a new collection version
- A user asks about the release process or release checklist

DO NOT TRIGGER when:

- Reviewing a PR (use `pr-review` skill instead)
- Running tests (use `run-tests` skill instead)
- General changelog or versioning questions unrelated to performing a release

## Inputs

- `version` (optional): the target release version, e.g. `2.1.0`. If not provided, the version is automatically determined from changelog fragments (see Step 2).

## Prerequisites

- `antsibull-changelog` installed (`pip install antsibull-changelog`)
- `gh` CLI installed and authenticated
- Push access to the upstream remote
- Git remote named `upstream` configured to point to the canonical repository

## Human Confirmation Gates

**Do not proceed past a confirmation gate without explicit human approval.**
Present the relevant information and wait for the human to confirm
before continuing to the next step. Gates are marked with **CONFIRM** below.

## Release Steps

### Step 1 — Determine repository information

Use the `get-upstream-info` helper skill to determine the upstream repository.

This returns:

- `UPSTREAM_ORG`: GitHub organisation (e.g., `ansible-collections`)
- `UPSTREAM_REPO`: Repository name (e.g., `amazon.aws`)
- `UPSTREAM_PATH`: Full path (e.g., `ansible-collections/amazon.aws`)

Cache these values for use in subsequent steps.

### Step 2 — Read collection context and determine version

Extract collection identity from `galaxy.yml`:

```bash
grep -E '^(namespace|name|version):' galaxy.yml
```

Use the extracted values as `NAMESPACE`, `COLLECTION`, and `CURRENT_VERSION` in all subsequent steps.

#### Determine next version

If the user did not provide a target version, determine it automatically:

1. Scan all YAML files in `changelogs/fragments/` and collect the top-level keys (category names) from each file.
2. Determine the version bump using the highest-severity category found:

| Bump  | Fragment categories                                      |
|-------|----------------------------------------------------------|
| Major | `breaking_changes`, `removed_features`, `major_changes`  |
| Minor | `minor_changes`, `deprecated_features`                   |
| Patch | `bugfixes`, `security_fixes`, `known_issues`, `trivial`  |

1. Apply the bump to `CURRENT_VERSION` (e.g. `2.0.0` + minor -> `2.1.0`).
   When bumping major, reset minor and patch to 0. When bumping minor, reset patch to 0.

Use the resulting version as `VERSION`.

**CONFIRM:** Present the extracted `NAMESPACE`, `COLLECTION`, `CURRENT_VERSION`,
the detected fragment categories, the determined bump type, and the resulting `VERSION`
to the human. Ask them to confirm these values are correct before proceeding.
The human may override the version at this point.

### Step 3 — Pre-flight checks

```bash
git status
git checkout main
git pull --rebase upstream main
```

Verify before continuing:

- Working tree is clean (no uncommitted changes)
- Changelog fragments exist: `ls changelogs/fragments/`

### Step 4 — Update galaxy.yml version

If `CURRENT_VERSION` in `galaxy.yml` does not match `VERSION`, update it:

```bash
sed -i "s/^version: .*/version: VERSION/" galaxy.yml
```

### Step 5 — Create release branch

```bash
git checkout -b release_VERSION
```

### Step 6 — Generate changelog

Determine the release type from `VERSION` and suggest a release summary using this template:

- **Major** (`X.0.0`): `This is a major release of the ``NAMESPACE.COLLECTION`` collection.`
- **Minor** (`X.Y.0`): `This is a minor release of the ``NAMESPACE.COLLECTION`` collection.`
- **Patch** (`X.Y.Z`): `This is a patch release of the ``NAMESPACE.COLLECTION`` collection.`

Followed by:
`This changelog contains all changes to the modules and plugins in this collection that have been made after the previous release.`

**CONFIRM:** Present the suggested release summary and the list of changelog fragments that will be included. Ask the human to approve or edit the text before writing the fragment.

Create the release summary fragment:

```bash
cat > changelogs/fragments/VERSION.yml << 'EOF'
release_summary: |-
  This is a <major/minor/patch> release of the ``NAMESPACE.COLLECTION`` collection.
  This changelog contains all changes to the modules and plugins in this collection
  that have been made after the previous release.
EOF
```

Generate the changelog:

```bash
antsibull-changelog release --reload-plugins
```

**CONFIRM:** Show the human the generated `CHANGELOG.rst` diff and ask them to confirm the content is correct before continuing.

### Step 7 — Commit and push release branch

```bash
git add -A
git commit -m "Release VERSION"
git push origin release_VERSION
```

### Step 8 — Create pull request

```bash
gh pr create --repo UPSTREAM_PATH --title "Release VERSION" --body "Release VERSION of NAMESPACE.COLLECTION."
```

**CONFIRM:** Wait for the human to confirm that CI has passed and the PR has been reviewed and merged before continuing.

### Step 9 — Update local main

After the PR is merged:

```bash
git checkout main
git pull --rebase upstream main
```

### Step 10 — Tag and push

**CONFIRM:** Ask the human to confirm before creating and pushing the tag. This action is irreversible.

```bash
git tag -a VERSION -m "NAMESPACE.COLLECTION: VERSION"
git push upstream VERSION
```

### Step 11 — Create GitHub release

```bash
gh release create VERSION --repo UPSTREAM_PATH --title "VERSION" --notes "See [CHANGELOG.rst](https://github.com/UPSTREAM_PATH/blob/main/CHANGELOG.rst) for details."
```

### Step 12 — Bullhorn release announcement

Generate and present the following announcement text for the user to post
in the [Bullhorn newsletter](https://forum.ansible.com/c/news/bullhorn/17)
after the user ensures the release has appeared on Ansible Galaxy:

```
The [NAMESPACE.COLLECTION](https://galaxy.ansible.com/ui/repo/published/NAMESPACE/COLLECTION/) collection version [VERSION](https://github.com/UPSTREAM_PATH/blob/main/CHANGELOG.rst#vVERSION) has been released!
```

Replace `NAMESPACE`, `COLLECTION`, `VERSION`, and `UPSTREAM_PATH` with the actual values. In the anchor fragment (`#vVERSION`), replace dots with hyphens (e.g. `#v2-1-0` for version `2.1.0`).

## Output Format

Present each step as a numbered section containing:

1. What the step does (one line)
2. The exact command(s) to run (with placeholders replaced by actual values)
3. What to verify before proceeding to the next step

## Integration with Other Skills

- **get-upstream-info**: Used in Step 1 to determine upstream repository path for gh CLI commands (`gh pr create`, `gh release create`)
- **current-release**: Not currently used; release skill reads galaxy.yml directly to get namespace, name, and version together
- **next-release**: Not used; release skill has unique logic to scan changelog fragments and determine bump type for actual releases (next-release is for version_added tags)
