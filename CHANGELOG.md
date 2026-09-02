# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed

- The `github/codeql-action/upload-sarif` step in `scorecard.yml`. SARIF
  ingestion into the Security tab requires GitHub Advanced Security (Code
  Security), which GitHub now bills separately and which is not enabled on
  this repository. `scorecard.yml` already uploaded `results.sarif` as a
  plain workflow artifact separately, so no replacement step was needed.
  Pruned the now-unused `security-events: write` permission from
  `scorecard.yml` and from `security-analysis.yml`'s workflow-level grant
  (which had no consumer either before or after this change). Actual
  SAST/SCA coverage for this repository is Bandit and OSV-Scanner
  (`security-analysis.yml`); OpenSSF Scorecard continues to publish to the
  public Scorecard API independent of the Security tab.

### Added
- Initial project setup and structure
- Phase 0 foundation: shared `mtg_ai.schema` package with two declarative bases
  mapped to separate `data` and `app` Postgres schemas (ADR-001/ADR-002)
- Two independent Alembic lineages (`migrations/data`, `migrations/app`) with
  per-schema version tables so histories never collide
- Database engine and session factory with SQLite schema-attach support for tests
- Authentication: `User`/`Session` models, PBKDF2-HMAC-SHA256 password hashing
  (FIPS-approved; bcrypt prohibited), opaque session tokens stored as SHA-256
  hashes, auth service, and `POST /api/v1/auth/login` + `GET /api/v1/auth/me`
- FastAPI application factory (`mtg_ai.main:app`) serving the health probes
  under `/api/v1/health` (`/live`, `/ready`, `/startup`)
- Postgres role/schema bootstrap (`scripts/sql/init-roles.sh`) enforcing the
  single-writer rule at the database level
- Data-service CLI commands: `mtg_ai db upgrade/downgrade/current` and
  `mtg_ai user create`
- docker-compose `data` service plus role-aware database wiring

### Changed

- Dockerfile installs the `api` extra and points the healthcheck at
  `/api/v1/health/live`

### Fixed
- Renovate now manages the `frontend/` npm ecosystem: added `npm` to
  `enabledManagers` (previously limited to `pep621` and `github-actions`, so
  npm dependency updates were silently skipped). npm is also included in the
  high-priority security-update rule and gets dedicated grouping rules
  matching the Python dependency grouping pattern.

## [0.1.0] - TBD

### Added
- Initial project structure with Poetry package management
- Pydantic v2 JSON schema validation
- Structured logging with structlog and rich console output
- Pre-commit hooks (Ruff format, Ruff lint, BasedPyright, Bandit, pip-audit)
- Comprehensive test suite with pytest
- GitHub Actions CI/CD pipeline with quality gates
- CLI tool foundation
- License

### Documentation
- README with project overview and quick start
- CONTRIBUTING guidelines with development workflow
- References to ByronWilliamsCPA org-level Security Policy
- References to ByronWilliamsCPA org-level Code of Conduct

### Infrastructure
- Poetry dependency management with lock file
- pytest test framework with coverage reporting
- GitHub issue tracking and templates
- Automated dependency security scanning (Safety, Bandit)
- Code quality enforcement (Ruff, BasedPyright)
- CI/CD pipeline with multiple quality gates

### Security
- Bandit security linting
- Safety dependency vulnerability scanning
- Pre-commit hooks for security validation

[Unreleased]: https://github.com/ByronWilliamsCPA/mtg_ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ByronWilliamsCPA/mtg_ai/releases/tag/v0.1.0
