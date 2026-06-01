---
title: "Project Planning Documents"
schema_type: planning
status: published
owner: core-maintainer
purpose: "Index of project planning documentation."
tags:
  - planning
  - documentation
component: Context
source: "Project initialization"
---

This directory contains the essential planning documents for MTG AI.

## Quick Start

> **Complete Guide**: See [PROJECT_SETUP.md](../PROJECT_SETUP.md#project-planning-with-claude-code) for the full workflow.

```bash
# 1. Generate planning documents
/plan <your project description>

# 2. Synthesize into project plan
"Synthesize my planning documents into a project plan"

# 3. Review docs/planning/PROJECT-PLAN.md

# 4. Start development
/git/milestone start feat/phase-0-foundation
```

## Documents

| Document | Purpose | Status |
|----------|---------|--------|
| [project-vision.md](./project-vision.md) | What & Why | Awaiting Generation |
| [tech-spec.md](./tech-spec.md) | How to build | Awaiting Generation |
| [roadmap.md](./roadmap.md) | Implementation plan | Awaiting Generation |
| [adr/](./adr/) | Architecture decisions | Awaiting Generation |

## Using Documents During Development

### Starting a Session

```text
Load context from:
- project-vision.md sections 2-3
- adr/adr-001-*.md
- tech-spec.md section [relevant section]

Then implement [feature].
```

### Validating Code

```text
Review this code against:
- tech-spec.md section 6 (security)
- adr/adr-002-*.md (relevant decision)

Flag any violations.
```

### Updating Documents

Update documents when:
- **Roadmap**: After completing tasks
- **ADR**: When making architectural decisions
- **Tech Spec**: When architecture changes
- **PVS**: When scope changes

## Document Relationships

```text
┌─────────────────────────────┐
│   Project Vision & Scope    │  ← WHAT & WHY
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Architecture Decisions     │  ← KEY CHOICES
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Technical Specification    │  ← HOW
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Development Roadmap        │  ← WHEN
└─────────────────────────────┘
```

## CI/CD Integration Notes

Planning documents are **intentionally excluded** from strict validation checks to support the `/plan` workflow:

- **Front Matter Validation**: Planning docs are excluded from strict YAML front matter requirements
- **MkDocs Validation**: Link checking is relaxed for planning directory
- **Pre-commit Hooks**: Planning docs use simplified validation rules

This allows you to:

1. Generate planning documents via `/plan` command
2. Commit them immediately to a PR
3. Iterate on content without CI failures

**First PR Workflow**:

```bash
# After project generation, create planning docs
/plan <project description>

# Commit and push (CI will pass on planning docs)
git add docs/planning/
git commit -m "docs: add initial project planning documents"
git push origin docs/initial-planning

# Create PR - planning doc validation is relaxed
gh pr create --title "docs: add initial planning" --body "Initial project planning documents"
```

## More Information

- Skill instructions: `.claude/skills/project-planning/SKILL.md`
- Document templates: `.claude/skills/project-planning/templates/`
- Detailed guidance: `.claude/skills/project-planning/reference/`
