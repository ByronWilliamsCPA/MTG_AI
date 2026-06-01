# GitHub Copilot Code Review Instructions

> These instructions guide Copilot code reviews to focus on issues that automated checks cannot catch.
> Pre-commit hooks and CI/CD already validate: formatting (Black), linting (Ruff), type checking
> (BasedPyright), security scanning (Bandit/Safety), and test coverage (pytest).

## Review Focus Areas

### 1. Business Logic & Intent Verification

- Does the implementation match the stated intent in PR description and commit messages?
- Are there logical errors that would produce incorrect results?
- Do conditional branches handle all expected scenarios correctly?
- Are boolean expressions correctly ordered and parenthesized?
- Do loops terminate under all conditions? Are off-by-one errors present?

### 2. Error Handling Quality

- Are exceptions specific enough (not bare `except:` - but that's caught by linting)?
- Is the error handling **appropriate** for the failure mode?
- Are error messages actionable and user-friendly?
- Do retry mechanisms have proper backoff and limits?
- Are resources properly cleaned up on all error paths?
- Is error context preserved when re-raising exceptions?

### 3. Edge Cases & Boundary Conditions

- Empty collections, None values, zero-length strings
- Maximum/minimum values, integer overflow potential
- Unicode handling, special characters in paths
- Timezone edge cases, daylight saving transitions
- Network timeouts, partial failures in batch operations
- File system edge cases (permissions, missing directories)

### 4. Concurrency & Race Conditions

- Thread safety of shared state
- Proper locking mechanisms and lock ordering
- Async/await correctness and potential deadlocks
- Resource cleanup in concurrent contexts
- Signal handling and graceful shutdown

### 5. API Design & Contracts

- Are function signatures intuitive and consistent?
- Do parameter names clearly convey purpose?
- Are return types consistent with similar functions?
- Is None-ability clearly documented and handled?
- Are breaking changes properly versioned?

### 6. Documentation Accuracy

- Do docstrings accurately describe what the code does?
- Are examples in docstrings correct and runnable?
- Do comments explain **why**, not just **what**?
- Are TODO/FIXME comments actionable with context?
- Is README documentation consistent with actual behavior?

### 7. Test Quality (Beyond Coverage)

- Do tests verify behavior, not just execution?
- Are edge cases and error conditions tested?
- Are test names descriptive of what they verify?
- Do tests use appropriate assertions (not just `assert True`)?
- Are test fixtures appropriate, or do they over-mock?
- Would tests catch regressions in the feature being tested?

### 8. Security Logic Flaws

- Authorization checks before sensitive operations
- Input validation at trust boundaries
- Time-of-check-time-of-use (TOCTOU) vulnerabilities
- Information leakage in error messages or logs
- Secure comparison for sensitive data (constant-time)
- Path traversal prevention in file operations

### 9. Maintainability & Readability

- Is the code self-documenting through clear naming?
- Are magic numbers replaced with named constants?
- Is complexity appropriate, or could it be simplified?
- Will future developers understand the intent?
- Are related changes grouped logically?

### 10. CLI-Specific Concerns

- Are command-line arguments validated appropriately?
- Do error messages guide users to correct usage?
- Is help text accurate and helpful?
- Are exit codes meaningful and consistent?
- Does the CLI handle signals (Ctrl+C) gracefully?

## Review Style Guidelines

When providing feedback:

1. **Be specific** - Reference exact lines and provide concrete suggestions
2. **Explain the "why"** - Help authors understand the reasoning
3. **Acknowledge good patterns** - Reinforce positive practices
4. **Ask clarifying questions** - When intent is unclear, ask rather than assume
5. **Prioritize by impact** - Security and correctness issues first
6. **Suggest, don't demand** - Offer alternatives for style preferences

## What NOT to Review (Already Automated)

These are handled by CI/CD and pre-commit hooks:

- Code formatting (Black)
- Import sorting (Ruff/isort)
- Basic linting violations (Ruff)
- Type annotation presence (BasedPyright)
- Test coverage percentage (pytest-cov)
- Known security vulnerabilities (Bandit, pip-audit, OSV-Scanner)
- Credential detection (pre-commit hooks)
- Assumption tag presence (#CRITICAL, #ASSUME - LLM governance checks)

## Project Context

- **Package**: `mtg_ai`
- **Source**: `src/mtg_ai/`
- **Tests**: `tests/`
- **CLI Entry**: `src/mtg_ai/cli.py`
