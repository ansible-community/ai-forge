# Skills Index

> Auto-generated from SKILL.md files. Do not edit manually.
> Last updated: 2026-06-01 16:39 UTC

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
| [docs-generate](ansible-collection-sdlc/module/skills/docs-generate/SKILL.md) | Generate or update Ansible collection documentation using collection_prep. Use when module documentation needs updating, after changing module arguments or return values, before releases, or when README needs regeneration. Automatically updates module RST files and README.md with current module information. |
| [get-branch-changes](ansible-collection-sdlc/module/skills/get-branch-changes/SKILL.md) | Determines merge-base and changed files for current branch. Helper skill used by changelog-fragment and create-pr to correctly identify branch changes. |
| [get-pr-action-results](ansible-collection-sdlc/module/skills/get-pr-action-results/SKILL.md) | Get GitHub Actions/GitLab CI results for a pull request or branch and analyze failures. Identifies failing tests, examines logs, and suggests specific fixes. Helper skill typically invoked by check-pr-actions command. |
| [get-pr-number](ansible-collection-sdlc/module/skills/get-pr-number/SKILL.md) | Determines the pull request number for a branch using gh CLI. Returns PR number, status, and URL. This is a helper skill used by other skills. |
| [get-pr-zuul-results](ansible-collection-sdlc/module/skills/get-pr-zuul-results/SKILL.md) | Get Zuul CI build status and log URLs for a pull request in ansible-collections repositories. Identifies failing builds, provides log URLs, and summarizes build results. Helper skill typically invoked by check-pr-actions or other workflows. |
| [get-upstream-info](ansible-collection-sdlc/module/skills/get-upstream-info/SKILL.md) | Determines upstream repository information using gh CLI. Returns organisation, repository name, and derived identifiers. This is a helper skill used by other skills. |
| [implement-sonarcloud-fixes](ansible-collection-sdlc/module/skills/implement-sonarcloud-fixes/SKILL.md) | Implement fixes for SonarCloud issues identified by the sonarcloud-analysis skill. Creates feature branches, applies code changes, runs tests, and creates pull requests. Use after reviewing SonarCloud analysis results. |
| [next-release](ansible-collection-sdlc/module/skills/next-release/SKILL.md) | Calculates next patch/minor/major release versions following Semantic Versioning. Used to determine version_added values for new features. |
| [pr-review](ansible-collection-sdlc/module/skills/pr-review/SKILL.md) | Reviews pull requests and code changes in an Ansible collection against project standards and the Ansible Collection Review Checklist. Use when asked to review a PR, patch, diff, or set of code changes. Do not use for GitHub Issues or general Q&A. |
| [python-virtual-env](ansible-collection-sdlc/module/skills/python-virtual-env/SKILL.md) | Creates or validates a project-local Python virtual environment (.venv by default) for isolated pip installs and local tooling. Typically invoked by setup-python-venv command. Use when setting up local Python dev, installing Python dependencies with pip, or before running non-Docker Python commands. Do not use when the user requests system Python, containers only, or ansible-test --docker. |
| [release](ansible-collection-sdlc/module/skills/release/SKILL.md) | Guides the release of an Ansible collection following the upstream process (without release branches). Automatically determines the next version from changelog fragments. Outputs step-by-step instructions with commands for changelog generation, release PR, tagging, Galaxy publication, version bump, and GitHub release. Use when asked to release, publish, or tag a new collection version. |
| [remove-deprecations](ansible-collection-sdlc/module/skills/remove-deprecations/SKILL.md) | Find and remediate overdue deprecation warnings in Ansible collection code. Identifies deprecated code past removal date/version and helps implement necessary changes. Use when preparing releases or cleaning up technical debt. |
| [run-tests](ansible-collection-sdlc/module/skills/run-tests/SKILL.md) | Runs and writes tests (sanity, unit, integration) for an Ansible collection using ansible-test. Use when asked to run, check, or write tests for a module or utility. Do not use for PR reviews or questions unrelated to testing. |
| [sanity](ansible-collection-sdlc/module/skills/sanity/SKILL.md) | Run Ansible sanity tests with smart change detection. Use when testing Ansible collections, validating module code, running pre-commit checks, or preparing releases. Supports smart mode (tests only changed files - fast), full mode (all files), and changed-only mode (custom range). |
| [security-scan](ansible-collection-sdlc/module/skills/security-scan/SKILL.md) | Scan Ansible collection dependencies, CI workflows, and code for security vulnerabilities. Checks for hardcoded secrets, vulnerable packages, and supply chain risks. Use when asked to scan for vulnerabilities, check for compromised packages, audit security, or before releases. |
| [sonarcloud-analysis](ansible-collection-sdlc/module/skills/sonarcloud-analysis/SKILL.md) | Fetch and analyse SonarCloud issues for a project or pull request. Use when asked to check, review, or analyse SonarCloud issues, code quality, security hotspots, or technical debt. |
| [stable-release](ansible-collection-sdlc/module/skills/stable-release/SKILL.md) | Complete end-to-end release workflow orchestrator for Ansible collections using stable-X branch strategy. Coordinates stable-release-analyze, stable-release-prep, docs-generate, lint, and sanity skills for a fully automated stable branch release process. Use when the user wants to release a collection with multiple stable branches. |
| [stable-release-analyze](ansible-collection-sdlc/module/skills/stable-release-analyze/SKILL.md) | Analyzes Ansible collection stable branches to determine pending releases and calculate appropriate SemVer versions. Checks for unreleased commits, analyzes changelog fragments, and recommends next version. Use when asked to check which collections need releases or what version to release. |
| [stable-release-prep](ansible-collection-sdlc/module/skills/stable-release-prep/SKILL.md) | Prepare Ansible collection release by creating prep branch from stable branch, updating galaxy.yml version, creating release summary fragment with proper backtick formatting for module names, and running antsibull-changelog release. Use after stable-release-analyze determines a version is needed. |
| [tox-lint](ansible-collection-sdlc/module/skills/tox-lint/SKILL.md) | Run all configured tox linters on an Ansible collection or Python project. Executes ansible-lint, black, isort, flake8, pylint, flynt, and ruff to ensure code quality and style consistency. Use before commits or as part of release workflow. |

## ansible-collection-standards

| Skill | Description |
|-------|-------------|
| [ansible-zen](ansible-collection-standards/module/skills/ansible-zen/SKILL.md) | Display the Zen of Ansible principles and review Ansible code against them. Use when the user wants to see the Zen of Ansible, get philosophical guidance on their automation approach, or review code for simplicity, readability, and clarity. Use when user says "zen of ansible", "simplify my playbook", "is this too complex", or "clean code review". Do NOT use for strict rule compliance (use ansible-cop-review instead). |

## ansible-content-development

| Skill | Description |
|-------|-------------|
| [write-content](ansible-content-development/module/skills/write-content/SKILL.md) | Write or improve Ansible content (playbooks, tasks, handlers, templates, variables, inventories, argument specs) following Red Hat CoP automation good practices. Use when writing new Ansible YAML content from a description, or improving existing content against best practices. Do NOT use for Python module development (use write-module), role/collection scaffolding (use ansible-scaffold-role / ansible-scaffold-collection), compliance auditing (use ansible-cop-review), or style review (use ansible-zen). |
| [write-content-tests](ansible-content-development/module/skills/write-content-tests/SKILL.md) | Write functional tests for Ansible content (roles, playbooks) using Molecule. Focuses on verifying intended outcomes — does the automation achieve its goal? — not retesting built-in modules. Use when writing new Molecule scenarios, verify playbooks, or improving existing tests. Do NOT use for Python module unit/integration tests (use write-module-tests). |
| [write-module](ansible-content-development/module/skills/write-module/SKILL.md) | Scaffold new Ansible modules or review existing ones against official best practices from docs.ansible.com. Use when writing a new module from scratch, reviewing module code for compliance, or asking how to structure an Ansible module. Do NOT use for role scaffolding, playbook review, or PR-level review. |
| [write-module-tests](ansible-content-development/module/skills/write-module-tests/SKILL.md) | Write unit and integration tests for Ansible modules using ansible-test and pytest. Covers test structure, mocking AnsibleModule, argument validation, and integration test patterns. Do NOT use for Ansible content tests (use write-content-tests for Molecule). |

## cloud_content

| Skill | Description |
|-------|-------------|
| [aws-terminator-analyze](cloud_content/module/skills/aws-terminator-analyze/SKILL.md) | Analyze an Ansible AWS collection PR to determine what aws-terminator resources and permissions are needed |
| [aws-terminator-implement](cloud_content/module/skills/aws-terminator-implement/SKILL.md) | Implement terminator classes and IAM permissions in aws-terminator repository based on analysis |
| [aws-terminator-workflow](cloud_content/module/skills/aws-terminator-workflow/SKILL.md) | Complete end-to-end workflow for aws-terminator PR creation - analyze, implement, test, and submit |

## network_content

| Skill | Description |
|-------|-------------|
| [network-collection-triage](network_content/module/skills/network-collection-triage/SKILL.md) | Triage bug reports, CI failures, and GitHub issues across Ansible network collections (cisco.ios, cisco.iosxr, cisco.nxos, arista.eos, junos, ansible.netcommon, ansible.utils). Two modes: scan mode for bulk weekly triage across all repos, and direct mode for deep triage of a single issue. Network-specific: uses cross-collection cascade detection for shared dependencies (netcommon, utils) and known network CI failure patterns. Outputs structured JSON and markdown. Use when asked to triage network issues, scan network issues, weekly triage, triage CI failure, or triage collection issue. Do not use for non-network collections or general Ansible questions. |

---
Total skills: 36
