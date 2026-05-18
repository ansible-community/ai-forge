# Skills Index

> Auto-generated from SKILL.md files. Do not edit manually.
> Last updated: 2026-05-18 18:13 UTC

## ansible-collection-sdlc

| Skill | Description |
|-------|-------------|
| [changelog-fragment](ansible-collection-sdlc/module/skills/changelog-fragment/SKILL.md) | Creates or updates changelog fragments for documenting changes in Ansible collections. Use when asked to create a changelog fragment, add a fragment, or update fragments with PR URLs. Automatically detects repository context from git. |
| [commit](ansible-collection-sdlc/module/skills/commit/SKILL.md) | This skill should be used when the user asks to 'commit', 'create a commit', or 'git commit'. It creates conventional commits with FQCN scopes for Ansible collection content (roles, modules, plugins). |
| [configure-sonarcloud-collection](ansible-collection-sdlc/module/skills/configure-sonarcloud-collection/SKILL.md) | Adds SonarCloud (SonarQube Cloud) static analysis to an Ansible collection repo: sonar-project.properties, GitHub Actions scanner workflow, XML coverage for Sonar, and contributor-facing docs; includes fork/secret and assistant-safe patterns (see Security section). Use when onboarding SonarCloud, wiring CI secrets, producing coverage.xml, or mirroring ansible-collections setups like amazon.aws. |
| [configure-sonarcloud-coverage](ansible-collection-sdlc/module/skills/configure-sonarcloud-coverage/SKILL.md) | Second-phase SonarCloud setup for Ansible collections: CI emits XML coverage (ansible-test and/or tox/pytest-cov), passes reports to the scanner via workflow_run + artifacts, reusable workflow_call Sonar, or inline scan, aggregator gates, README badges. Use after Sonar project and sonar-project.properties exist; mirrors ansible-collections/amazon.aws coverage patterns (e.g. PR 2871). |
| [create-branch](ansible-collection-sdlc/module/skills/create-branch/SKILL.md) | Create a new feature branch following project conventions. Fetches latest from origin, bases branch off origin/main, and unsets upstream for fork workflows. |
| [create-pr](ansible-collection-sdlc/module/skills/create-pr/SKILL.md) | Create a draft pull request with all required checks and formatting |
| [current-release](ansible-collection-sdlc/module/skills/current-release/SKILL.md) | Fetches the current release version from git tags and stable branches, falling back to galaxy.yml if not found. Helper skill used by other skills that need version information. |
| [get-branch-changes](ansible-collection-sdlc/module/skills/get-branch-changes/SKILL.md) | Determines merge-base and changed files for current branch. Helper skill used by changelog-fragment and create-pr to correctly identify branch changes. |
| [get-pr-action-results](ansible-collection-sdlc/module/skills/get-pr-action-results/SKILL.md) | Get GitHub Actions/GitLab CI results for a pull request or branch and analyze failures. Identifies failing tests, examines logs, and suggests specific fixes. Helper skill typically invoked by check-pr-actions command. |
| [get-pr-number](ansible-collection-sdlc/module/skills/get-pr-number/SKILL.md) | Determines the pull request number for a branch using gh CLI. Returns PR number, status, and URL. This is a helper skill used by other skills. |
| [get-upstream-info](ansible-collection-sdlc/module/skills/get-upstream-info/SKILL.md) | Determines upstream repository information using gh CLI. Returns organisation, repository name, and derived identifiers. This is a helper skill used by other skills. |
| [implement-sonarcloud-fixes](ansible-collection-sdlc/module/skills/implement-sonarcloud-fixes/SKILL.md) | Implement fixes for SonarCloud issues identified by the sonarcloud-analysis skill. Creates feature branches, applies code changes, runs tests, and creates pull requests. Use after reviewing SonarCloud analysis results. |
| [next-release](ansible-collection-sdlc/module/skills/next-release/SKILL.md) | Calculates next patch/minor/major release versions following Semantic Versioning. Used to determine version_added values for new features. |
| [pr-review](ansible-collection-sdlc/module/skills/pr-review/SKILL.md) | Reviews pull requests and code changes in an Ansible collection against project standards and the Ansible Collection Review Checklist. Use when asked to review a PR, patch, diff, or set of code changes. Do not use for GitHub Issues or general Q&A. |
| [release](ansible-collection-sdlc/module/skills/release/SKILL.md) | Guides the release of an Ansible collection following the upstream process (without release branches). Automatically determines the next version from changelog fragments. Outputs step-by-step instructions with commands for changelog generation, release PR, tagging, Galaxy publication, version bump, and GitHub release. Use when asked to release, publish, or tag a new collection version. |
| [remove-deprecations](ansible-collection-sdlc/module/skills/remove-deprecations/SKILL.md) | Find and remediate overdue deprecation warnings in Ansible collection code. Identifies deprecated code past removal date/version and helps implement necessary changes. Use when preparing releases or cleaning up technical debt. |
| [run-tests](ansible-collection-sdlc/module/skills/run-tests/SKILL.md) | Runs and writes tests (sanity, unit, integration) for an Ansible collection using ansible-test. Use when asked to run, check, or write tests for a module or utility. Do not use for PR reviews or questions unrelated to testing. |
| [sonarcloud-analysis](ansible-collection-sdlc/module/skills/sonarcloud-analysis/SKILL.md) | Fetch and analyse SonarCloud issues for a project or pull request. Use when asked to check, review, or analyse SonarCloud issues, code quality, security hotspots, or technical debt. |

## ansible-collection-standards

| Skill | Description |
|-------|-------------|
| [ansible-zen](ansible-collection-standards/module/skills/ansible-zen/SKILL.md) | Display the Zen of Ansible principles and review Ansible code against them. Use when the user wants to see the Zen of Ansible, get philosophical guidance on their automation approach, or review code for simplicity, readability, and clarity. Use when user says "zen of ansible", "simplify my playbook", "is this too complex", or "clean code review". Do NOT use for strict rule compliance (use ansible-cop-review instead). |

---
Total skills: 19
