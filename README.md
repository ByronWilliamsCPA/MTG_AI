# MTG AI

## Quality & Security
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/ByronWilliamsCPA/mtg_ai/badge)](https://securityscorecards.dev/viewer/?uri=github.com/ByronWilliamsCPA/mtg_ai)
[![codecov](https://codecov.io/gh/ByronWilliamsCPA/mtg_ai/graph/badge.svg)](https://codecov.io/gh/ByronWilliamsCPA/mtg_ai)

## CI/CD Status
[![CI Pipeline](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/ci.yml?query=branch%3Amain)
[![Security Analysis](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/security-analysis.yml/badge.svg?branch=main)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/security-analysis.yml?query=branch%3Amain)
[![Documentation](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/docs.yml?query=branch%3Amain)
[![SBOM & Security Scan](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/sbom.yml/badge.svg?branch=main)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/sbom.yml?query=branch%3Amain)
[![PR Validation](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/pr-validation.yml/badge.svg)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/pr-validation.yml)
[![PyPI Publish](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/publish-pypi.yml/badge.svg)](https://github.com/ByronWilliamsCPA/mtg_ai/actions/workflows/publish-pypi.yml)

## Project Info

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://github.com/ByronWilliamsCPA/.github/blob/main/CODE_OF_CONDUCT.md)

| | |
|---|---|
| **Author** | Byron Williams |
| **Created** | 2026-05-31 |
| **Repository** | [ByronWilliamsCPA/MTG_AI](https://github.com/ByronWilliamsCPA/MTG_AI) |

---

## Overview

Self-hosted competitive Commander (cEDH) deck-critique assistant: RAG over Scryfall/MTGJSON/meta data with a deterministic rules engine and a swappable generation backend.

Import an existing decklist and MTG_AI analyzes its weaknesses and proposes
specific cuts and additions with reasoning, anchored to the competitive
metagame. The first format is competitive Commander (cEDH); the data model is
designed so other formats can be added later.

What it does:
- **Deck critique**: import an Arena/MTGO/text decklist, get legality-correct
  cuts and adds with reasoning.
- **RAG-grounded**: a Postgres + pgvector store of cards, metagame data, and
  embeddings feeds retrieved context to the generation model (Claude today).
- **Deterministic legality**: a pure rules engine, not the model, is the source
  of truth for Commander legality, and it re-validates every model suggestion.
- **Built for fine-tuning later**: every critique is logged with its inputs and
  the user's accept/reject decisions, accumulating a labeled corpus for a future
  fine-tuned model that swaps in behind a stable `Generator` interface.

> **Architecture, data flow, error handling, and testing strategy** are
> specified in the approved design:
> [`docs/superpowers/specs/2026-05-31-mtg-ai-cedh-critique-design.md`](docs/superpowers/specs/2026-05-31-mtg-ai-cedh-critique-design.md).
> Implementation is in progress; this scaffold establishes the tooling baseline.

## Features

- **High Quality**: 80%+ test coverage enforced via CI
- **Type Safe**: Full type hints with BasedPyright strict mode
- **Well Documented**: Clear docstrings and comprehensive guides
- **Developer Friendly**: Pre-commit hooks, automated formatting, linting
- **Security First**: Dependency scanning, security analysis, SBOM generation
- **CLI Tool**: Command-line interface via mtg_ai

## Quick Start

### Prerequisites

- Python 3.10+ (tested with 3.12)
- [UV](https://docs.astral.sh/uv/) for dependency management

**Install UV**:

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip/pipx
pip install uv
# or
pipx install uv
```

### Installation

```bash
# Clone repository
git clone https://github.com/ByronWilliamsCPA/MTG_AI.git
cd mtg_ai

# Install dependencies (includes dev tools - REQUIRED for development)
uv sync --all-extras

# Setup pre-commit hooks (required)
uv run pre-commit install
```

### Basic Usage

```bash
# Show available commands and options
uv run mtg_ai --help

# Greet with the default name
uv run mtg_ai hello

# Greet with a specific name
uv run mtg_ai hello --name "Byron"

# Display current configuration settings
uv run mtg_ai config

# Enable debug logging for any command
uv run mtg_ai --debug hello --name "Byron"
```

### CLI Usage

```bash
# Display help
uv run mtg_ai --help

# Use the CLI tool
uv run mtg_ai command --option value

# Example: Process input file
uv run mtg_ai process input.txt --output result.json
```

## Frontend Development

The frontend is a React + TypeScript application built with Vite.

### Quick Start

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000 with hot reload.

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server with HMR |
| `npm run build` | Build for production |
| `npm run test` | Run tests in watch mode |
| `npm run lint` | Lint code |
| `npm run typecheck` | Run TypeScript type checking |
| `npm run generate-client` | Generate API client from OpenAPI |

### API Client Generation

Generate a type-safe TypeScript client from the FastAPI OpenAPI schema:

```bash
# Start backend first
uv run uvicorn mtg_ai.main:app &

# Generate client
cd frontend && npm run generate-client
```

This creates typed API functions in `frontend/src/client/`.

### Docker

```bash
# Development (with hot reload)
docker-compose up frontend

# Production build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up frontend
```

## Google Assured OSS Integration

This project can use **Google Assured OSS** as the primary package source for enhanced supply chain security.

### Enabling Supply Chain Security

To enable full supply chain security features, regenerate this project with:
```bash
cruft update
# Select include_supply_chain_security: yes
```

Or manually configure by following the [Google Assured OSS documentation](https://cloud.google.com/assured-open-source-software/docs).

## Development

### Setup Development Environment

```bash
# Install all dependencies including dev tools
uv sync --all-extras

# Setup pre-commit hooks
uv run pre-commit install

# Install Qlty CLI for unified code quality checks
curl https://qlty.sh | bash

# Run tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=mtg_ai --cov-report=html

# Run all quality checks (using Qlty)
qlty check

# Or use pre-commit
uv run pre-commit run --all-files
```

### Code Quality Standards

All code must meet these requirements:

- **Formatting**: Ruff (88 char limit)
- **Linting**: Ruff with PyStrict-aligned rules (see below)
- **Type Checking**: BasedPyright strict mode
- **Testing**: Pytest with 80%+ coverage
- **Security**: Bandit + dependency scanning
- **Documentation**: Docstrings on all public APIs

**Unified Quality Tool**: This project uses [Qlty](https://qlty.sh) to consolidate all quality checks into a single fast tool. See [`.qlty/qlty.toml`](.qlty/qlty.toml) for configuration.

### PyStrict-Aligned Ruff Configuration

This project uses **PyStrict-aligned Ruff rules** for stricter code quality enforcement beyond standard Python linting:

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

These rules catch bugs that standard linting misses and enforce production-quality code patterns.

### Claude Code Standards

This project includes standardized Claude Code configuration via git subtree:

**Directory Structure**:
```text
.claude/
├── claude.md          # Project-specific Claude guidelines
└── standard/          # Standard Claude configuration (git subtree)
    ├── CLAUDE.md      # Universal development standards
    ├── commands/      # Custom slash commands
    ├── skills/        # Reusable skills
    └── agents/        # Specialized agents
```

**Updating Standards**:
```bash
# Pull latest standards from upstream
./scripts/update-claude-standards.sh

# Or manually
git subtree pull --prefix .claude/standard \
    https://github.com/ByronWilliamsCPA/.claude.git main --squash
```

**What's Included**:
- Universal development best practices
- Response-Aware Development (RAD) system for assumption tagging
- Agent assignment patterns and workflow
- Security requirements and pre-commit standards
- Git workflow and commit conventions

**Project-Specific Overrides**: Edit `.claude/claude.md` for project-specific guidelines. See [`.claude/README.md`](.claude/README.md) for details.

### Running Tests

```bash
# Run all tests
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_module.py -v

# Run with coverage report
uv run pytest --cov=mtg_ai --cov-report=term-missing

# Run tests in parallel
uv run pytest -n auto
```

### Quality Checks with Qlty

**Recommended**: Use Qlty CLI for unified code quality checks.

```bash
# Run all quality checks (fast!)
qlty check

# Run checks on only changed files (fastest)
qlty check --filter=diff

# Run specific plugins only
qlty check --plugin ruff --plugin pyright

# Auto-format code
qlty fmt

# View current configuration
qlty config show
```

**Qlty runs all these tools in a single pass:**

**Python Quality:**

- Ruff (linting + formatting)
- BasedPyright (type checking)
- Bandit (security scanning)

**Security & Secrets:**

- Gitleaks (secrets detection)
- TruffleHog (entropy-based secrets detection)
- OSV Scanner (dependency vulnerabilities)
- Semgrep (advanced SAST)

**File & Configuration:**

- Markdownlint (markdown linting)
- Yamllint (YAML linting)
- Prettier (JSON, YAML, Markdown formatting)
- Actionlint (GitHub Actions workflows)
- Shellcheck (shell script linting)

**Container & Infrastructure** (if Docker enabled):

- Hadolint (Dockerfile linting)
- Trivy (container security scanning)
- Checkov (infrastructure as code security)

**Code Quality Metrics:**

- Complexity analysis (cyclomatic, cognitive)
- Code smells detection
- Maintainability scoring

### Individual Tool Commands (if needed)

```bash
# Format code
uv run ruff format src tests

# Lint and auto-fix
uv run ruff check --fix src tests

# Type checking
uv run basedpyright src

# Security scanning
uv run bandit -r src

# Dependency vulnerabilities
qlty check --plugin osv_scanner
```

## Project Structure

```text
mtg_ai/
├── src/mtg_ai/     # Main package
│   ├── __init__.py
│   ├── core.py                           # Core functionality
│   └── utils/                            # Utility modules
├── tests/                                # Test suite
│   ├── unit/                             # Unit tests
│   └── integration/                      # Integration tests
├── docs/                                 # Documentation
│   ├── ADRs/                             # Architecture Decision Records
│   ├── planning/                         # Project planning docs
│   └── guides/                           # User guides
├── pyproject.toml                        # Dependencies & tool config
├── README.md                             # This file
├── CONTRIBUTING.md                       # Contribution guidelines
└── LICENSE                               # License
```

## Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md)**: How to contribute to the project
- **[docs/ADRs/README.md](docs/ADRs/README.md)**: Architecture Decision Records documentation
- **[docs/planning/project-plan-template.md](docs/planning/project-plan-template.md)**: Project planning guide

### Writing Documentation

- Use Markdown for all documentation
- Include code examples for clarity
- Update README.md when adding major features
- Maintain architecture documentation (see [docs/ADRs/](docs/ADRs/))

## Testing

### Testing Policy

All new functionality must include tests:

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **Coverage**: Maintain 80%+ coverage
- **Markers**: Use pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`)

### Test Guidelines

```bash
# Run all tests
uv run pytest -v

# Run only unit tests
uv run pytest -v -m unit

# Run only integration tests
uv run pytest -v -m integration

# Run with coverage requirements
uv run pytest --cov=mtg_ai --cov-fail-under=80
```

## Security

### Security-First Development

- Validate all inputs
- Use secure defaults
- Scan dependencies regularly
- Report vulnerabilities responsibly

### Reporting Security Issues

Please report security vulnerabilities to byronawilliams@gmail.com rather than using the public issue tracker.

See the [ByronWilliamsCPA Security Policy](https://github.com/ByronWilliamsCPA/.github/blob/main/SECURITY.md) for complete disclosure policy and response timelines.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Code quality standards
- Testing requirements
- Git workflow and commit conventions
- Pull request process

### Quick Checklist Before Submitting PR

- [ ] Code follows style guide (Ruff format + lint)
- [ ] All tests pass with 80%+ coverage
- [ ] BasedPyright type checking passes
- [ ] Docstrings added for new public APIs
- [ ] CHANGELOG.md updated (if significant change)
- [ ] Commits follow conventional commit format

## Versioning

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: Backwards-compatible functionality additions
- **PATCH** version: Backwards-compatible bug fixes

Current version: **0.1.0**

### Automated Releases with Semantic Release

This project uses [python-semantic-release](https://python-semantic-release.readthedocs.io/) for automated versioning based on [Conventional Commits](https://www.conventionalcommits.org/).

**How it works:**

1. **Commit messages determine version bumps:**
   - `fix:` commits trigger a **PATCH** release (1.0.0 → 1.0.1)
   - `feat:` commits trigger a **MINOR** release (1.0.0 → 1.1.0)
   - `BREAKING CHANGE:` in commit body or `!` after type triggers **MAJOR** release (1.0.0 → 2.0.0)

2. **On merge to main:**
   - Analyzes commits since last release
   - Determines appropriate version bump
   - Updates version in `pyproject.toml`
   - Generates/updates `CHANGELOG.md`
   - Creates Git tag and GitHub Release
   - Publishes to PyPI (if configured)

**Commit message examples:**

```bash
# Patch release (bug fix)
git commit -m "fix: resolve null pointer in data parser"

# Minor release (new feature)
git commit -m "feat: add CSV export functionality"

# Major release (breaking change)
git commit -m "feat!: redesign API for better ergonomics

BREAKING CHANGE: API has been redesigned for improved usability.
See migration guide in docs/migration/v2.0.0.md"
```

**Configuration:** See `[tool.semantic_release]` in `pyproject.toml` for settings.

## Template Maintenance

This project was generated from a cookiecutter template and is managed with cruft.

### Updating from Template

To sync with the latest template changes:

```bash
# Preview changes first
cruft diff

# Apply updates (recommended: use the wrapper script)
./scripts/cruft-update.sh

# Or use cruft directly (requires manual cleanup)
cruft update
python scripts/cleanup_conditional_files.py
```

### Important: Cruft Update Limitations

**Cruft only syncs file contents** - it does NOT re-run post-generation hooks that clean up conditional files.

When you change feature flags in `.cruft.json` (e.g., disabling `include_api_framework`), the corresponding files are NOT automatically removed. You must run the cleanup script:

```bash
# Check for orphaned files
python scripts/check_orphaned_files.py

# Remove orphaned files
python scripts/cleanup_conditional_files.py

# Or preview what would be removed
python scripts/cleanup_conditional_files.py --dry-run
```

### Conditional Files

Files that may need cleanup when features are disabled:

| Feature | Files to Remove |
|---------|-----------------|
| `include_api_framework: no` | `src/*/api/`, `src/*/middleware/` |
| `include_sentry: no` | `src/*/core/sentry.py` |
| `include_background_jobs: no` | `src/*/jobs/` |
| `include_caching: no` | `src/*/core/cache.py` |
| `include_docker: no` | `Dockerfile`, `docker-compose*.yml` |
| `use_mkdocs: no` | `mkdocs.yml`, `docs/` |

The CI pipeline includes automated checks for orphaned files to prevent this issue.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/ByronWilliamsCPA/MTG_AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ByronWilliamsCPA/MTG_AI/discussions)
- **Email**: byronawilliams@gmail.com

## Acknowledgments

Thank you to all contributors and the open-source community!

---

**Made with by [Byron Williams](https://github.com/ByronWilliamsCPA)**
