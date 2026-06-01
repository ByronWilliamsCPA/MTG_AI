---
title: "Code Quality"
schema_type: common
status: published
owner: core-maintainer
purpose: "Code quality standards for MTG AI."
tags:
  - development
  - quality
---

This guide covers the code quality standards and tools for MTG AI.

## Tools

### Ruff

Fast Python linter and formatter:

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

### BasedPyright

Strict type checking:

```bash
uv run basedpyright src/
```

### Bandit

Security linting:

```bash
uv run bandit -r src/
```

## Pre-commit Hooks

Pre-commit hooks run automatically:

```bash
# Install hooks
uv run pre-commit install

# Run all hooks manually
uv run pre-commit run --all-files
```

## Standards

### Code Style

- **Line length**: 88 characters (Black compatible)
- **Docstrings**: Google style
- **Type hints**: Required for all public APIs

### Docstring Coverage

- **Target**: 85% coverage
- Check with: `uv run interrogate -c pyproject.toml src/`

## Quality Gates

All PRs must pass:
- [ ] All tests passing
- [ ] 80%+ coverage
- [ ] No type errors
- [ ] No linting errors
- [ ] Pre-commit hooks pass
