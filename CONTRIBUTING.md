# Contributing

Refer to the [Ansible community guide](https://docs.ansible.com/projects/ansible/devel/community/index.html).

## Development

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. Install them with:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Linting

#### Markdown

```bash
# Check markdown files
npm run lint:md

# Auto-fix markdown issues
npm run lint:md:fix
```

#### YAML

Frontmatter in markdown files is linted automatically by pre-commit hooks.

### What Gets Checked

Pre-commit hooks run automatically on `git commit` and check:

- **Markdown** - Using markdownlint-cli2 with .markdownlint.json config
- **YAML** - Frontmatter validation and syntax checking
- **Shell scripts** - Using shellcheck
- **JSON** - Syntax validation
- **File formatting** - Trailing whitespace, end-of-file, line endings

These same checks run in GitHub Actions CI.

## Adding a New Skill

Skills are AI assistant capabilities that can be invoked by users. Follow these steps to add a new skill:

### Step 1: Create the skill folder

Create a new folder under the appropriate module's skills directory:

```bash
mkdir -p <module>/module/skills/<skill-name>/
```

For example:

```bash
mkdir -p ansible-collection-development/module/skills/my-new-skill/
```

### Step 2: Create the SKILL.md file

Create a `SKILL.md` file in the skill folder with the required frontmatter:

```markdown
---
name: my-new-skill
description: >-
  A brief description of what this skill does and when it should be invoked.
---

# Skill: my-new-skill

## Purpose

Describe the purpose of this skill.

## When to Invoke

TRIGGER when:
- User asks to...
- User wants to...

DO NOT TRIGGER when:
- ...

## Steps

1. First step...
2. Second step...
```

**Required frontmatter fields:**

- `name` - The skill identifier (should match the folder name)
- `description` - A concise description shown in skill listings

### Step 3: Add supporting files (optional)

Add any additional files the skill needs (templates, reference data, etc.) in the same folder.

### Step 4: Update AGENTS.md

Add an entry for your skill in the module's `AGENTS.md` file:

```markdown
- **my-new-skill skill**: Use the `my-new-skill` skill when you want to...
  Invoke when the user asks to...
```

### Step 5: Update the module README

Add your skill to the Components section in the module's `README.md`.

### Making the Skill Available

After adding your skill, users can install it using [Lola](https://lobstertrap.org/lola/):

```bash
# Register or update the module
lola mod add https://github.com/ansible-community/ai-forge/<module>

# Install to an AI assistant (project-level)
lola install <module> -a claude-code

# Or install globally (available in all projects)
lola install <module> -a claude-code ~
```

## Submitting a Pull Request

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes following the guidelines above
4. Run pre-commit checks: `pre-commit run --all-files`
5. Commit your changes with a clear, descriptive message
6. Push to your fork and open a pull request against `main`

Pull requests are automatically validated by GitHub Actions CI.
