---
title: "Contributing"
schema_type: common
status: published
owner: core-maintainer
purpose: "Contributing guide for MTG AI."
tags:
  - development
  - contributing
---

Thank you for your interest in contributing to MTG AI!

## Getting Started

### Prerequisites

- Python 3.12+
- UV package manager
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/ByronWilliamsCPA/MTG_AI
cd mtg_ai

# Install dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feat/your-feature-name
```

### 2. Make Changes

- Write code with type hints
- Add tests for new functionality
- Update documentation

### 3. Run Quality Checks

```bash
# Run tests
uv run pytest -v

# Run linting
uv run ruff check .

# Run type checking
uv run basedpyright src/
```

### 4. Commit Changes

Use conventional commit messages:

```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in module"
git commit -m "docs: update documentation"
```

### 5. Create Pull Request

Push your branch and create a PR against `main`.

## Code Review

All contributions require:
- Passing CI checks
- Code review approval
- Documentation updates (if applicable)

## Questions?

Open an issue for questions or discussions.
