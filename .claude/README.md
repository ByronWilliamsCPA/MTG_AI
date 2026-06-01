# Claude Configuration Directory

This directory contains Claude Code configuration and standards for this project.

## Directory Structure

```
.claude/
├── README.md           # This file
├── claude.md           # Project-specific Claude guidelines
├── context/            # Project-specific context files
│   ├── python-standards.md   # Project Python conventions
│   └── testing-patterns.md   # Project testing patterns
└── standard/           # Standard Claude configuration (git subtree)
    ├── claude.md       # Base guidelines and standards
    ├── commands/       # Custom slash commands
    ├── skills/         # Reusable skills
    ├── agents/         # Specialized agents
    └── standards/      # Development standards
        ├── git-workflow.md   # Git branching, commits, PRs
        ├── git-worktree.md   # Git worktree workflows
        ├── linting.md        # Multi-language linting
        ├── python.md         # Python development standards
        └── security.md       # Security requirements
```

## Standard vs Project-Specific Configuration

### Standard Configuration (`standard/`)

This directory is managed as a **git subtree** from [ByronWilliamsCPA/.claude](https://github.com/ByronWilliamsCPA/.claude). It contains:

- Universal Claude Code development standards
- Best practices and coding guidelines
- Reusable commands, skills, and agents
- Security and quality requirements
- **Development standards** (`standards/`):
  - Git workflow and branching strategies
  - Git worktree patterns for parallel development
  - Multi-language linting configuration
  - Python development best practices
  - Security requirements and compliance

**Do not edit files in `standard/` directly** - they will be overwritten when updating from the upstream repository.

### Project-Specific Configuration (`claude.md`)

The `claude.md` file in this directory contains **project-specific** guidelines that extend the standards:

- Project overview and architecture
- Technology stack and dependencies
- Project-specific conventions and patterns
- Environment setup instructions
- Common tasks and troubleshooting

### Project Context Files (`context/`)

The `context/` directory contains **project-specific** reference documents:

- `python-standards.md` - Project-specific Python conventions (supplements global `/standards/python.md`)
- `testing-patterns.md` - Project-specific testing patterns and fixtures

These files extend the universal standards with project-specific examples and patterns. Edit these freely to match your project's needs.

## Updating Standard Configuration

To pull the latest standards from the upstream repository:

```bash
# Using the helper script
./scripts/update-claude-standards.sh

# Or manually
git subtree pull --prefix .claude/standard \
    https://github.com/ByronWilliamsCPA/.claude.git main --squash
```

## Contributing Changes to Standards

If you develop a pattern or guideline that would benefit all projects:

```bash
# Push changes back to the standard repository
git subtree push --prefix .claude/standard \
    https://github.com/ByronWilliamsCPA/.claude.git main
```

**Note**: This requires write access to the upstream repository.

## How Claude Code Uses These Files

1. **Global Settings**: Claude Code first loads `~/.claude/CLAUDE.md` (user-level)
2. **Standard Guidelines**: Then loads `.claude/standard/claude.md` (universal standards)
3. **Project Overrides**: Finally loads `.claude/claude.md` (project-specific)

This layered approach ensures:
- Consistent standards across all projects
- Project flexibility where needed
- Easy updates to universal guidelines

## First-Time Setup

The git subtree is automatically configured during project generation via the `post_gen_project.py` hook. If you need to set it up manually:

```bash
# Initialize git if not already done
git init

# Add the subtree
git subtree add --prefix .claude/standard \
    https://github.com/ByronWilliamsCPA/.claude.git main --squash
```

---

**Last Updated**: 2026-06-01
