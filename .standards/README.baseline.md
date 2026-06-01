# README Baseline Standards

> **Source**: ByronWilliamsCPA/cookiecutter-python-template
> **Version**: 0.1.0
> **Updated**: 2026-06-01
>
> This file contains **baseline README sections** that cruft updates automatically.
> Merge changes into root `README.md` using: `/merge-standards` or ask Claude.

---

## Badge Section (Copy to README.md)

### Quality & Security Badges

```markdown
## Quality & Security
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/ByronWilliamsCPA/mtg_ai/badge)](https://securityscorecards.dev/viewer/?uri=github.com/ByronWilliamsCPA/mtg_ai)
[![codecov](https://codecov.io/gh/ByronWilliamsCPA/mtg_ai/graph/badge.svg)](https://codecov.io/gh/ByronWilliamsCPA/mtg_ai)
```

### CI/CD Status Badges

```markdown
## CI/CD Status
[![CI Pipeline](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/ci.yml?query=branch%3Amain)
[![Security Analysis](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/security-analysis.yml/badge.svg?branch=main)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/security-analysis.yml?query=branch%3Amain)
[![Documentation](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/docs.yml?query=branch%3Amain)
[![SBOM & Security Scan](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/sbom.yml/badge.svg?branch=main)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/sbom.yml?query=branch%3Amain)
[![PR Validation](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/pr-validation.yml/badge.svg)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/pr-validation.yml)
[![PyPI Publish](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/publish-pypi.yml/badge.svg)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/publish-pypi.yml)
```

### Project Info Badges

```markdown
## Project Info

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://github.com/ByronWilliamsCPA/.github/blob/main/CODE_OF_CONDUCT.md)
```

---

## Standard Sections (Reference)

The following sections are part of the template baseline. When updating, compare your
`README.md` against these sections and merge any improvements.

### Prerequisites Section

```markdown
### Prerequisites

- Python 3.10+ (tested with 3.12)
- [UV](https://docs.astral.sh/uv/) for dependency management

**Install UV**:

\`\`\`bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip/pipx
pip install uv
# or
pipx install uv
\`\`\`
```

### Code Quality Standards Section

```markdown
### Code Quality Standards

All code must meet these requirements:

- **Formatting**: Ruff (88 char limit)
- **Linting**: Ruff with PyStrict-aligned rules
- **Type Checking**: BasedPyright strict mode
- **Testing**: Pytest with 80%+ coverage
- **Security**: Bandit + dependency scanning
- **Documentation**: Docstrings on all public APIs

**Unified Quality Tool**: This project uses [Qlty](https://qlty.sh) to consolidate
all quality checks into a single fast tool.
```

### PyStrict Rules Table

```markdown
### PyStrict-Aligned Ruff Configuration

| Rule | Category | Purpose |
|------|----------|---------|
| **BLE** | Blind except | Prevent bare `except:` clauses |
| **EM** | Error messages | Enforce descriptive error messages |
| **SLF** | Private access | Prevent access to private members |
| **INP** | Implicit packages | Require explicit `__init__.py` |
| **ISC** | Implicit concatenation | Prevent implicit string concatenation |
| **PGH** | Pygrep hooks | Advanced pattern-based checks |
| **RSE** | Raise statement | Proper exception raising |
| **TID** | Tidy imports | Clean import organization |
| **YTT** | sys.version | Safe version checking |
| **FA** | Future annotations | Modern annotation syntax |
| **T10** | Debugger | No debugger statements in production |
| **G** | Logging format | Safe logging string formatting |
```

### Semantic Release Section

```markdown
### Automated Releases with Semantic Release

This project uses [python-semantic-release](https://python-semantic-release.readthedocs.io/)
for automated versioning based on [Conventional Commits](https://www.conventionalcommits.org/).

**How it works:**

1. **Commit messages determine version bumps:**
   - `fix:` commits trigger a **PATCH** release (1.0.0 → 1.0.1)
   - `feat:` commits trigger a **MINOR** release (1.0.0 → 1.1.0)
   - `BREAKING CHANGE:` in commit body or `!` after type triggers **MAJOR** release

2. **On merge to main:**
   - Analyzes commits since last release
   - Determines appropriate version bump
   - Updates version in `pyproject.toml`
   - Generates/updates `CHANGELOG.md`
   - Creates Git tag and GitHub Release
   - Publishes to PyPI (if configured)
```

---

## Merge Instructions

When `.standards/README.baseline.md` is updated by cruft:

1. **Compare badge sections** - Copy updated badges to your README.md
2. **Review standard sections** - Merge any improvements to instructions
3. **Preserve project content** - Keep your custom Overview, Features, etc.

**What to merge:**
- Badge URLs and formats (may add new badges)
- Tool installation instructions (versions may change)
- Quality standards tables (rules may be added)
- Workflow documentation (process improvements)

**What NOT to merge:**
- Your project's Overview section
- Your project's Features section
- Project-specific configuration
- Custom acknowledgments

---

*This baseline is automatically updated by cruft. Merge changes into root README.md.*
