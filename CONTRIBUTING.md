# Contributing to MTG AI

Thank you for your interest in contributing to MTG AI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Quality Standards](#code-quality-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Convention](#commit-convention)
- [Pull Request Process](#pull-request-process)
- [Questions?](#questions)

## Code of Conduct

This project adheres to the [ByronWilliamsCPA organization Code of Conduct](https://github.com/ByronWilliamsCPA/.github/blob/main/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to byronawilliams@gmail.com.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- UV 1.7+ for dependency management
- Git
- GPG key configured for commit signing (recommended)

### Development Environment Setup

```bash
# Clone the repository
git clone https://github.com/ByronWilliamsCPA/MTG_AI.git
cd mtg_ai

# Install dependencies with UV
uv sync --all-extras
# Setup pre-commit hooks (REQUIRED)
uv run pre-commit install

# Install Qlty CLI for unified code quality checks (REQUIRED)
curl https://qlty.sh | bash

# Verify installation
uv run pytest -v
qlty check
```

### Project Structure

```
mtg_ai/
├── src/mtg_ai/       # Main package
│   ├── __init__.py
│   ├── core.py                           # Core functionality
│   └── utils/                            # Utility modules
├── tests/                                # Test suite
│   ├── unit/                             # Unit tests
│   └── integration/                      # Integration tests
├── docs/                                 # Documentation
│   ├── ADRs/                             # Architecture Decision Records
│   ├── planning/                         # Project planning
│   └── guides/                           # User guides
└── pyproject.toml                        # Dependencies & config
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Create and checkout a new branch
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b fix/issue-description

# For documentation
git checkout -b docs/documentation-update
```

### Branch Naming Convention

- `feature/` - New features or enhancements
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or improvements
- `chore/` - Maintenance tasks

### 2. Make Your Changes

- Write clean, readable code following [PEP 8](https://peps.python.org/pep-0008/)
- Add type hints to all functions and methods
- Update documentation for API changes
- Add tests for new functionality
- Ensure all tests pass locally

### 3. Run Quality Checks

Before committing, ensure all quality checks pass:

```bash
# Run all quality checks with Qlty (RECOMMENDED - fast and comprehensive)
qlty check

# Or run checks on only changed files (fastest)
qlty check --filter=diff

# Auto-format code
qlty fmt
# Or run all pre-commit hooks manually
uv run pre-commit run --all-files

# Run tests with coverage
uv run pytest --cov=mtg_ai --cov-report=term-missing
```

**Note**: Qlty consolidates all quality tools (Ruff, BasedPyright, Bandit, Markdownlint, etc.) into a single fast CLI. See [`.qlty/qlty.toml`](.qlty/qlty.toml) for configuration.

## Code Quality Standards

All contributions MUST meet these requirements:

### Formatting

- **Tool**: Ruff
- **Line Length**: 88 characters
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Sorted with Ruff
- **Quotes**: Double quotes for strings
- **Verification**: `uv run ruff format src tests`

### Linting

- **Tool**: Ruff with project configuration
- **Rules**: Comprehensive rule set (see `pyproject.toml`)
- **Auto-fix**: `uv run ruff check --fix src tests`
- **Verification**: `uv run ruff check src tests`

### Type Checking

- **Tool**: BasedPyright strict mode for `src/`
- **Coverage**: All public functions must have type hints
- **Verification**: `uv run basedpyright src`

### Security

- **No Hardcoded Secrets**: Use environment variables or secure vaults
- **Input Validation**: Validate all user inputs and file paths
- **Path Sanitization**: Use `pathlib.Path.resolve()` to prevent directory traversal
- **Dependency Security**: Run `uv run pip-audit` before submitting PRs

### Type Hints

All functions must include type hints:

```python
from pathlib import Path
from typing import Optional, Any

def process_data(
    input_path: Path,
    output_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Process data and return results.

    Args:
        input_path: Path to the input data
        output_dir: Optional output directory for results

    Returns:
        Dictionary containing processed data and metadata

    Raises:
        FileNotFoundError: If input_path does not exist
        ValueError: If data format is not supported
    """
    pass
```

### Documentation

- **Docstrings**: Use Google-style docstrings for all public APIs
- **Comments**: Explain *why*, not *what* (code should be self-documenting)
- **README Updates**: Update README.md for significant feature additions
- **Architecture Docs**: Add/update ADRs for architectural changes

## Testing Requirements

### Testing Policy

All new functionality MUST include corresponding tests:

- **Unit tests**: Required for all new functions/classes
- **Integration tests**: Required for new modules/workflows
- **Coverage**: Must maintain ≥80% overall coverage
- **Test types**: Use pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`)

### Test Guidelines

- Test both success and failure cases
- Test edge cases and boundary conditions
- Use descriptive test names: `test_<function>_<scenario>_<expected>`
- Include docstrings explaining test purpose
- Use fixtures for common setup

### Minimum Coverage

- **Overall Coverage**: 80% minimum (enforced by CI)
- **New Code**: 90% coverage for new features
- **Critical Paths**: 100% coverage for security-sensitive code

### Test Categories

```bash
# Run all tests
uv run pytest -v

# Run only unit tests
uv run pytest -v -m unit

# Run only integration tests
uv run pytest -v -m integration

# Run tests with coverage report
uv run pytest --cov=mtg_ai --cov-report=html
# Open htmlcov/index.html to view coverage report

# Run specific test file
uv run pytest tests/unit/test_module.py -v
```

### Writing Tests

```python
import pytest
from pathlib import Path
from mtg_ai.core import YourModule

def test_module_initialization():
    """Test module initializes correctly."""
    module = YourModule()
    assert module is not None

def test_module_processes_data(tmp_path: Path):
    """Test module processes data correctly."""
    module = YourModule()
    input_file = tmp_path / "input.txt"
    input_file.write_text("test data")

    result = module.process(input_file)

    assert result is not None
    assert result["status"] == "success"
```

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic changes)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```bash
# Feature addition
feat(core): add data processing function

Implements new data processing capabilities with comprehensive
validation and error handling.

Refs: #42

# Bug fix
fix(utils): handle edge case in validation

Previously, certain input patterns caused incorrect results.
Now we properly handle all edge cases.

Fixes: #56

# Breaking change
feat(core)!: redesign API for better ergonomics

BREAKING CHANGE: API has been redesigned for improved usability.
See migration guide in docs/migration/v1.0.0.md
```

## Pull Request Process

### Before Submitting

- [ ] Branch is up-to-date with `main`
- [ ] All tests pass locally
- [ ] Code coverage meets minimum requirements (80%)
- [ ] Pre-commit hooks pass
- [ ] Documentation is updated
- [ ] Commits follow conventional commit format

### Submitting a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub with:
   - **Clear title**: Following conventional commit format
   - **Description**: What changes were made and why
   - **Issue reference**: `Fixes #123` or `Refs #456`
   - **Testing notes**: How reviewers can test the changes
   - **Breaking changes**: Clearly documented (if applicable)

3. **Wait for CI checks**:
   - All GitHub Actions workflows must pass
   - Test coverage must meet requirements

4. **Address review feedback**:
   - Respond to all reviewer comments
   - Push additional commits to the same branch
   - Request re-review when ready

5. **Merge**:
   - Maintainer will merge when approved
   - Follow conventional commits for final commit message

### PR Review Criteria

Reviewers will check:

- **Code Quality**: Follows style guide and best practices
- **Tests**: Adequate test coverage and meaningful tests
- **Documentation**: Clear docstrings and updated docs
- **Security**: No security vulnerabilities introduced
- **Performance**: No performance regressions
- **Compatibility**: Maintains backward compatibility (or documents breaking changes)

## Reporting Issues

### Reporting Bugs

Use the bug report template and include:

- **Description**: Clear description of the bug
- **Reproduction Steps**: Minimal steps to reproduce
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: Python version, OS, package versions
- **Logs**: Relevant error messages or stack traces

### Requesting Features

Use the feature request template and include:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other approaches considered
- **Additional Context**: Screenshots or examples

## Questions?

- **General Questions**: Open a [GitHub Discussion](https://github.com/ByronWilliamsCPA/MTG_AI/discussions)
- **Bug Reports**: Open a [GitHub Issue](https://github.com/ByronWilliamsCPA/MTG_AI/issues)
- **Security Issues**: See [ByronWilliamsCPA Security Policy](https://github.com/ByronWilliamsCPA/.github/blob/main/SECURITY.md)
- **Email**: byronawilliams@gmail.com

## Recognition

Contributors are recognized in:

- Repository contributors page
- Release notes for significant contributions
- Project documentation

Thank you for contributing to MTG AI!
