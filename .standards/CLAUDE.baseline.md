# Baseline Development Standards

> **Source**: ByronWilliamsCPA/cookiecutter-python-template
> **Version**: 0.1.0
> **Updated**: 2026-06-01
>
> This file contains **baseline standards** that cruft updates automatically.
> Merge changes into root `CLAUDE.md` using: `/merge-standards` or ask Claude.

---

## Core Development Standards

### Essential Requirements

- **Code Quality**: Ruff formatting (88 chars), Ruff linting (PyStrict-aligned), BasedPyright type checking (strict mode)
- **Security**: GPG/SSH key validation, dependency scanning, encrypted secrets
- **Testing**: Minimum 80% coverage, tiered testing approach
- **Git**: Conventional commits, signed commits, feature branch workflow
- **Response-Aware Development**: Assumption tagging and verification

---

## Response-Aware Development (RAD)

### Assumption Tagging Standards

When writing code, ALWAYS tag assumptions that could cause production failures:

```python
# #CRITICAL: [category]: [assumption that could cause outages/data loss]
# #VERIFY: [defensive code required]
# Example: Payment processing, auth flows, concurrent writes

# #ASSUME: [category]: [assumption that could cause bugs]
# #VERIFY: [validation needed]
# Example: UI state, form validation, API responses

# #EDGE: [category]: [assumption about uncommon scenarios]
# #VERIFY: [optional improvement]
# Example: Browser compatibility, slow networks
```

### Critical Assumption Categories (MANDATORY tagging)

- **Timing Dependencies**: State updates, async operations, race conditions
- **External Resources**: API availability, file existence, network connectivity
- **Data Integrity**: Type safety at boundaries, null/undefined handling
- **Concurrency**: Shared state, transaction isolation, deadlock potential
- **Security**: Authentication, authorization, input validation
- **Payment/Financial**: Transaction integrity, retry logic, rollback handling

---

## Branch Workflow Requirement (CRITICAL)

**NEVER work directly on the `main` branch.** Always create a feature branch before making any code changes.

### Before ANY Code Changes

```bash
# 1. Check current branch
git branch --show-current

# 2. If on main/master, create a feature branch FIRST
git checkout -b feat/{descriptive-slug}

# 3. Or for bug fixes
git checkout -b fix/{issue-or-description}
```

### Branch Naming Convention

| Task Type | Branch Prefix | Commit Type | Version Impact |
|-----------|---------------|-------------|----------------|
| New feature | `feat/` | `feat:` | Minor (0.X.0) |
| Bug fix | `fix/` | `fix:` | Patch (0.0.X) |
| Breaking change | `feat/` or `fix/` | `feat!:` or `fix!:` | Major (X.0.0) |
| Documentation | `docs/` | `docs:` | No release |
| Refactoring | `refactor/` | `refactor:` | No release |
| Performance | `perf/` | `perf:` | Patch (0.0.X) |
| Testing | `test/` | `test:` | No release |
| Chore/maintenance | `chore/` | `chore:` | No release |

### Branch Creation (MANDATORY)

**ALWAYS create a new branch when:**

1. Starting ANY implementation task - Never commit directly to `main` or `develop`
2. TODO item involves code changes - Each feature/fix should have its own branch
3. Multiple independent features - Create separate branches for parallel work
4. User explicitly requests a feature/fix - Branch immediately before coding

---

## Security-First Development (CRITICAL)

Claude MUST adopt a security-first approach in all development:

### 1. Proactive Security Suggestions

- **Dependencies**: Suggest vulnerability scanning (`pip-audit`, `osv-scanner`)
- **APIs**: Suggest authentication, rate limiting, input validation
- **Data**: Suggest encryption at rest and in transit, access controls

### 2. Never Bypass Security Issues

- **ALL security findings** from scanners should be addressed, not dismissed
- If a finding is a false positive, document WHY with inline comments
- Use baseline files only for truly unavoidable exceptions with justification

### 3. Code Quality Standards

- Treat linting warnings as errors to fix, not ignore
- Address ALL type checker warnings, not just errors
- Don't accumulate technical debt by deferring quality issues

### 4. Default to Strictest Settings

- Security scanners: fail on HIGH/CRITICAL by default
- Type checking: strict mode (already configured)
- Linting: no ignored rules without documented reason

### 5. FIPS 140-2/140-3 Compliance

For deployment on FIPS-enabled systems (Ubuntu LTS with fips-updates, government systems, healthcare, finance):

**Prohibited algorithms** (will fail in FIPS mode):
- MD5, MD4, SHA-1 (for security purposes)
- DES, 3DES, RC2, RC4, Blowfish
- Non-approved key exchange methods

**Required patterns**:
```python
# ✗ WRONG - Will fail on FIPS systems
import hashlib
h = hashlib.md5(data)

# ✓ CORRECT - Non-security use is allowed
h = hashlib.md5(data, usedforsecurity=False)

# ✓ CORRECT - Use FIPS-approved algorithms for security
h = hashlib.sha256(data)
```

**Check FIPS compatibility**:
```bash
uv run python scripts/check_fips_compatibility.py --fix-hints
```

**Problematic packages** (need verification or replacement):
- `bcrypt` → Use `passlib` with PBKDF2 or `argon2-cffi`
- `pycrypto` → Use `pycryptodome` with FIPS mode
- Verify `cryptography` version >= 3.4.6 with OpenSSL FIPS provider

---

## Code Quality Standards

### Type Checking with BasedPyright

BasedPyright replaces MyPy as the standard type checker (3-5x faster, stricter analysis):

- **Mode**: `strict` (recommended)
- **Strict Inference**: `strictListInference`, `strictDictionaryInference`, `strictSetInference` enabled
- **Configuration**: In `pyproject.toml` under `[tool.basedpyright]`

### PyStrict-Aligned Ruff Rules

- **BLE**: Blind except detection (no bare `except:` or `except Exception:`)
- **EM**: Error message best practices
- **SLF**: Private member access violations
- **INP**: Require `__init__.py` in packages
- **ISC**: Implicit string concatenation
- **PGH**: Deprecated type comments, blanket ignores
- **RSE**: Raise statement best practices
- **TID**: Banned imports, relative import rules
- **YTT**: Python version checks
- **FA**: Future annotations
- **T10**: Debugger statements (no `breakpoint()`, `pdb`)
- **G**: Logging format strings

### File-Type Standards

- **Python**: 88-char line length, comprehensive rule compliance
- **Markdown**: 120-char line length, consistent formatting
- **YAML**: 2-space indentation, 120-char line length
- **Validation**: Pre-commit hooks enforce all standards

---

## Claude Code Supervisor Role

**Claude Code acts as the SUPERVISOR for all development tasks and MUST:**

1. **Always Use TodoWrite Tool**: Create and maintain TODO lists for ALL tasks
2. **Assign Tasks to Agents**: Each TODO item should be assigned to a specialized agent
3. **Review Agent Work**: Validate all agent outputs before proceeding
4. **Use Temporary Reference Files**: Create `.tmp-` prefixed files in `tmp_cleanup/` for complex tasks
5. **Maintain Continuity**: Use reference files to preserve context across conversation compactions

### Agent Assignment Patterns

```text
- Security tasks       -> Security Agent (mcp__zen__secaudit)
- Code reviews         -> Code Review Agent (mcp__zen__codereview)
- Testing              -> Test Engineer Agent (mcp__zen__testgen)
- Documentation        -> Documentation Agent (mcp__zen__docgen)
- Debugging            -> Debug Agent (mcp__zen__debug)
- Analysis             -> Analysis Agent (mcp__zen__analyze)
- Refactoring          -> Refactor Agent (mcp__zen__refactor)
```

---

## OpenSSF Best Practices Compliance

### Required Project Files

- `LICENSE` - Open source license
- `SECURITY.md` - Security policy and vulnerability reporting
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - Release history
- `README.md` - Project documentation

### Quality Gates

- All tests pass (80%+ coverage)
- Ruff linting (no errors)
- BasedPyright type checking
- Security scans (no high/critical)
- Pre-commit hooks pass

---

## Development Philosophy

**Security First** -> **Quality Standards** -> **Documentation** -> **Testing** -> **Collaboration**

### Core Principles

1. **Security First**: Always validate keys, encrypt secrets, scan dependencies
2. **Reuse First**: Check existing repositories for solutions before building new code
3. **Configure, Don't Build**: Prefer configuration and orchestration over custom implementation
4. **Quality Standards**: Maintain consistent code quality across all projects
5. **Documentation**: Keep documentation current and well-formatted
6. **Testing**: Maintain high test coverage and run tests before commits
7. **Collaboration**: Use consistent Git workflows and clear commit messages

---

## Pre-Commit Checklist

Before committing ANY changes, ensure:

- [ ] Working on appropriate feature branch (not main/develop)
- [ ] Branch follows `{type}/{descriptive-slug}` convention
- [ ] TodoWrite used for task tracking
- [ ] File-specific linter has been run and passes
- [ ] Pre-commit hooks execute successfully
- [ ] No linting warnings or errors remain
- [ ] Code formatting is consistent with project standards
- [ ] Security scanning shows no vulnerabilities

---

*This baseline is automatically updated by cruft. Merge changes into root CLAUDE.md.*
