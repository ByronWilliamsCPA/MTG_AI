# Quality Check Command

Run code quality checks including formatting, linting, and type checking.

## Usage

```
/quality [scope]
```

**Arguments:**
- `scope` (optional): `all`, `format`, `lint`, `types` (default: `all`)

## Workflow

1. **Format Check**: Verify code formatting with Black and Ruff
2. **Lint Check**: Run Ruff linter with project rules
3. **Type Check**: Run BasedPyright in strict mode
4. **Summary**: Report any issues found

## Commands Executed

### Format
```bash
uv run black --check .
uv run ruff format --check .
```

### Lint
```bash
uv run ruff check .
```

### Types
```bash
uv run basedpyright src/
```

### All (Pre-commit)
```bash
uv run pre-commit run --all-files
```

## Quality Standards

- **Line Length**: 88 characters
- **Type Checking**: Strict mode
- **Coverage Target**: 80%

## Fix Issues

To automatically fix formatting and some lint issues:
```bash
uv run black .
uv run ruff check --fix .
```
