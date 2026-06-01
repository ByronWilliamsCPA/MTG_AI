"""Generate tools catalog for MkDocs documentation.

This script is used by the mkdocs-gen-files plugin to dynamically generate
a catalog of development tools and their configurations.

SPDX-FileCopyrightText: 2026 Byron Williams
SPDX-License-Identifier: MIT
"""

from pathlib import Path

import mkdocs_gen_files

# Tools catalog content
TOOLS_CATALOG = """# Development Tools Catalog

This page provides an overview of the development tools configured for this project.

## Code Quality Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Ruff** | Linting and formatting | `pyproject.toml` |
| **BasedPyright** | Type checking | `pyproject.toml` |
| **Pre-commit** | Git hooks | `.pre-commit-config.yaml` |

## Security Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Bandit** | Security scanning | `pyproject.toml` |
| **Safety** | Dependency vulnerability check | CLI |
| **Gitleaks** | Secret detection | `.gitleaks.toml` |

## Testing Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **pytest** | Test framework | `pyproject.toml` |
| **coverage** | Code coverage | `pyproject.toml` |
| **pytest-cov** | Coverage plugin | `pyproject.toml` |

## Documentation Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **MkDocs** | Documentation site | `mkdocs.yml` |
| **mkdocstrings** | API documentation | `mkdocs.yml` |

## Running Tools

```bash
# Linting and formatting
uv run ruff check .
uv run ruff format .

# Type checking
uv run basedpyright src/

# Security scanning
uv run bandit -r src/
uv run pip-audit

# Testing
uv run pytest -v --cov=src/

# Pre-commit (all checks)
uv run pre-commit run --all-files
```

## Configuration Files

The following configuration files control tool behavior:

- `pyproject.toml` - Primary configuration for most Python tools
- `.pre-commit-config.yaml` - Pre-commit hook definitions
- `mkdocs.yml` - Documentation site configuration
- `.github/workflows/` - CI/CD workflow definitions
"""


def main() -> None:
    """Generate the tools catalog page."""
    with mkdocs_gen_files.open("tools/catalog.md", "w") as f:
        f.write(TOOLS_CATALOG)

    # Set the edit path for the generated file
    mkdocs_gen_files.set_edit_path("tools/catalog.md", Path(__file__).name)


if __name__ == "__main__":
    main()
