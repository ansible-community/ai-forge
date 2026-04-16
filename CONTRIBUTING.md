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
