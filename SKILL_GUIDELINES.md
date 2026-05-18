# Skill Guidelines

Guidelines, steps, and criteria for writing new AI skills in this repository.

## What Belongs Here

This repository is for **public, community-facing** skills that help with Ansible collection development. Skills should:

- Be useful to the broader Ansible community
- Not contain internal business logic or proprietary workflows
- Follow Ansible best practices and conventions
- Be well-documented and testable

Internal or business-specific skills belong in the private repository.

## Skill Structure

Each skill lives in its own folder under a module's `skills/` directory:

```
module_name/
└── module/
    └── skills/
        └── skill-name/
            ├── SKILL.md      # Required: Skill definition
            └── *.txt/*.md    # Optional: Supporting files
```

### SKILL.md Format

```markdown
---
name: skill-name
description: One-line description shown in skill listings
triggers:
  - keyword or phrase that activates the skill
  - another trigger phrase
---

# Skill Name

Detailed instructions for the AI assistant when this skill is invoked.

## When to Use

Describe scenarios where this skill applies.

## Steps

1. Step-by-step guidance
2. For the assistant to follow

## Output Format

Describe expected outputs or artifacts.
```

## Criteria for Acceptance

### Required

- [ ] Clear, descriptive name using kebab-case
- [ ] One-line description that explains purpose
- [ ] At least one trigger phrase
- [ ] Detailed instructions in the body
- [ ] Works without external paid services (or clearly documents requirements)

### Recommended

- [ ] Examples of expected input/output
- [ ] Error handling guidance
- [ ] Links to relevant documentation
- [ ] Test cases or validation steps

### Style

- Use imperative mood ("Generate a commit message" not "Generates")
- Be specific about expected formats and outputs
- Include context the AI needs to make good decisions
- Avoid ambiguous instructions

## Module Organization

Choose the appropriate module for your skill:

| Module | Purpose |
|--------|---------|
| `ansible-collection-sdlc` | Development lifecycle: commits, PRs, releases, testing |
| `ansible-collection-standards` | Standards, reviews, scaffolding |
| `ansible-role` | Role development and scaffolding |
| `network_content` | Network automation specific skills |
| `cloud_content` | Cloud automation specific skills |

## Commit Message Guidelines

### Format

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer(s)]
```

**Valid types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**Examples**:

```
feat(commit): add FQCN scope detection for Ansible modules
fix(pr-review): handle PRs with more than 100 changed files
docs(skills): add AGENTS.md documentation requirements
```

### AI Attribution

If AI tools assisted with your contribution, add an attribution trailer:

```
feat(release): add changelog generation step

Assisted-by: Claude Sonnet 4.5
```

Or using git's Co-Authored-By format:

```
feat(release): add changelog generation step

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

See [Ansible AI Policy](https://docs.ansible.com/ansible/latest/community/ai_policy.html) for more details.

## Contribution Process

1. **Propose**: Open an issue describing the skill and its use case
2. **Discuss**: Get feedback from maintainers on scope and placement
3. **Implement**: Create the skill following this guide
4. **Test**: Verify the skill works as expected
5. **Submit**: Open a PR with your skill

## AGENTS.md Requirements

Each module has an `AGENTS.md` file that documents available skills, commands, and agents. When adding or modifying skills, update the corresponding `AGENTS.md`.

### AGENTS.md Format

```markdown
---
name: module-name
description: One-line description of the module
---

# Module Name

Module description and overview.

## When to Use

Describe when to use each skill/command in this module:

- **skill-name skill**: Use when... Invoke with `/skill-name`.
- **command-name command**: Use when... Invoke with `/command-name`.

## Configuration

Optional dependencies and configuration notes.

## Notes

Additional context about the module.
```

### Required Fields

- **Frontmatter**: `name` and `description` fields
- **Body**: Must include a `## When to Use` section

## Testing Your Skill

Before submitting:

1. Install the module locally with `lola mod add ./path/to/module`
2. Test the skill triggers correctly
3. Verify output matches documented expectations
4. Check edge cases and error conditions

## Examples

See existing skills for reference:

- [`commit`](ansible-collection-sdlc/module/skills/commit/SKILL.md) - Conventional commit generation
- [`pr-review`](ansible-collection-sdlc/module/skills/pr-review/SKILL.md) - PR review workflow
- [`ansible-zen`](ansible-collection-standards/module/skills/ansible-zen/SKILL.md) - Philosophical guidance

## Questions?

- Open an issue for skill proposals or questions
- See [CONTRIBUTING.md](CONTRIBUTING.md) for general contribution guidelines
