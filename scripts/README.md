# Project Scripts

Utility scripts for MTG AI.

## Available Scripts

### update-claude-standards.sh

Updates the Claude Code standards from the upstream repository.

**Usage**:
```bash
./scripts/update-claude-standards.sh
```

**What it does**:
- Pulls the latest Claude Code standards from [ByronWilliamsCPA/.claude](https://github.com/ByronWilliamsCPA/.claude)
- Updates the `.claude/standard/` directory via git subtree
- Preserves project-specific configuration in `.claude/claude.md`

**When to run**:
- Periodically to get latest standards and best practices
- When new Claude Code features are announced
- When security or quality updates are released

**Note**: The update uses `git subtree pull --squash` to maintain a clean commit history.

## Adding New Scripts

When adding new scripts to this directory:

1. Make them executable: `chmod +x scripts/your-script.sh`
2. Add shebang line: `#!/bin/bash` (or appropriate interpreter)
3. Add usage documentation to this README
4. Use `set -e` to exit on errors
5. Add colorized output for better UX

## Script Conventions

- **Exit codes**: 0 for success, non-zero for errors
- **Output**: Use colors (GREEN for success, YELLOW for warnings, RED for errors)
- **Error handling**: Always check preconditions (e.g., git repo exists)
- **User interaction**: Confirm destructive operations
- **Documentation**: Include usage examples in this README
