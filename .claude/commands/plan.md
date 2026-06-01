---
description: Generate project planning documents (PVS, ADR, Tech Spec, Roadmap) with expert review
argument-hint: <project-description>
allowed-tools:
  - Read
  - Write
  - Bash
  - mcp__zen__consensus
---

# Generate Project Planning Documents

You are generating the initial project planning documents for MTG AI.

## Project Description

The user's project concept:

$ARGUMENTS

## Your Task

Using the `project-planning` skill, generate these four documents with expert review:

1. **Project Vision & Scope** → `docs/planning/project-vision.md`
2. **Architecture Decision Record** → `docs/planning/adr/adr-001-initial-architecture.md`
3. **Technical Implementation Spec** → `docs/planning/tech-spec.md`
4. **Development Roadmap** → `docs/planning/roadmap.md`

## Process

For EACH document, follow this generate-review-refine cycle:

### 1. Generate Document
- Read the corresponding template from `.claude/skills/project-planning/templates/`
- Generate project-specific content based on the user's description
- Write to the appropriate location in `docs/planning/`

### 2. Expert Review (Consensus)
After writing each document, request expert review:

```
mcp__zen__consensus with gemini-3-pro-preview:

Review this [Document Type] for MTG AI.

EVALUATION CRITERIA:
1. SPECIFICITY - Can a developer implement from these requirements?
2. COMPLETENESS - All sections filled with project-specific content?
3. FEASIBILITY - Realistic scope for the described constraints?
4. CLARITY - Unambiguous success criteria and scope boundaries?
5. GAPS - Any critical missing information?

RESPOND:
- READY: Sufficient to proceed
- NEEDS REVISION: [Specific improvements required]

DOCUMENT:
[Full document content]
```

### 3. Refine if Needed
- If NEEDS REVISION: Incorporate feedback and re-submit for review
- If READY: Proceed to next document
- Each document must be READY before generating the next

### 4. Final Validation
After all documents pass review:
- Run validation script
- Ensure cross-references are valid
- Summarize outcomes

## Pre-filled Context

This project was created from the cookiecutter-python-template with:

- **Project Name**: MTG AI
- **Package**: mtg_ai
- **Python Version**: 3.12
- **Author**: Byron Williams
- **CLI**: Yes (Click framework)
- **Docker**: Yes
- **Documentation**: MkDocs Material

## Quality Requirements

- Be specific to this project (no generic boilerplate)
- Use concrete technologies and measurable criteria
- Keep documents within length guidelines
- Ensure all cross-references are valid
- Flag assumptions needing user validation

## After Generation

1. **Report Review Outcomes**: Show which documents passed review and any revisions made
2. **Summarize Created Documents**: Brief overview of each document's key content
3. **Highlight Critical Decisions**: Flag any assumptions or choices needing user validation
4. **Run Validation**: `python .claude/skills/project-planning/scripts/validate-planning-docs.py`
5. **Next Steps**: Recommend optimal order for beginning implementation

## Fallback (No MCP Server)

If `mcp__zen__consensus` is not available:
- Skip the expert review step
- Generate all documents sequentially
- Run validation script for basic checks
- Instruct user to manually review before starting development
