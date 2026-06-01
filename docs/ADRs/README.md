---
title: "Architecture Decision Records (ADRs)"
schema_type: common
status: published
owner: core-maintainer
purpose: "Index of architecture decision records for this project."
tags:
  - adr
  - architecture
  - decisions
---

This directory contains Architecture Decision Records (ADRs) that document important architectural and design decisions made in MTG AI.

## What is an ADR?

An Architecture Decision Record (ADR) is a document that captures:

1. **The Decision**: What architectural choice was made?
2. **The Context**: Why was this decision needed? What problem were we solving?
3. **The Consequences**: What are the trade-offs and implications?
4. **Alternatives**: What other options were considered and why were they rejected?

ADRs serve as:

- **Historical Record**: Why decisions were made and when
- **Knowledge Sharing**: Helps new team members understand the architecture
- **Decision Rationale**: Documents the reasoning behind choices
- **Future Reference**: Helps when revisiting decisions

## When to Write an ADR?

Write an ADR when you need to document:

- Major architectural choices
- Technology selection decisions
- API design decisions
- Infrastructure decisions
- Dependency choices
- Testing strategies
- Any decision that impacts multiple components

## ADR Format

All ADRs follow a consistent structure with YAML front matter. See [adr-template.md](adr-template.md) for the complete template.

### Front Matter

```yaml
---
schema_type: adr                          # Always "adr"
title: "ADR-NNN: Short descriptive title"
description: "Brief one-line description"
tags:
  - architecture
  - decision
  - area-of-concern
status: published                         # proposed, published, deprecated, superseded
owner: "core-maintainer"                  # Primary decision owner
authors:
  - name: "Author Name"
purpose: "Why this ADR was written"
---
```

### Sections

1. **Status**: Current status (proposed, published, deprecated, superseded)
2. **Context**: Why this decision was needed
3. **Decision**: What decision was made and how
4. **Consequences**: Positive and negative impacts
5. **Alternatives**: Options considered and why rejected
6. **Implementation**: How the decision was implemented
7. **Performance Benchmarks**: Metrics and measurements (if applicable)
8. **References**: Links to related documents and code

## Status Definitions

- **proposed**: Under consideration, not yet approved
- **published**: Accepted and implemented
- **deprecated**: No longer used, replaced by newer approach
- **superseded**: Replaced by a newer ADR (should reference the new ADR)

## Naming Convention

ADR files are named with sequential numbers:

- `0001-adr-title-kebab-case.md`
- `0002-another-adr-title.md`
- `0031-comprehensive-benchmarking-framework.md`

Use the next available number and follow kebab-case for the title.

## Workflow

### Creating a New ADR

1. **Use the template**: Copy [adr-template.md](adr-template.md) to `NNNN-your-adr-title.md`
2. **Fill in the sections**: Complete all required sections
3. **Request review**: Create a PR with the ADR
4. **Iterate**: Address feedback and refine
5. **Approve and merge**: Once consensus is reached
6. **Update status**: Change status from "proposed" to "published"

### Deprecating an ADR

If an ADR is no longer valid:

1. Update the status to `deprecated`
2. Add a deprecation notice at the top
3. Reference the replacement ADR if applicable

Example:

````markdown
> **DEPRECATED (2025-11-17)**: This approach is no longer used.
> **Reason**: Replaced by more efficient algorithm
> **Reference**: See [ADR-032: Better Algorithm](0032-better-algorithm.md)
````

### Superseding an ADR

If a newer ADR replaces an existing one:

1. Update the old ADR status to `superseded`
2. Add a supersession notice referencing the new ADR
3. The new ADR should reference the old ADR in Alternatives section

## Examples from MTG AI

The repository may contain several example ADRs:

- **Infrastructure Decisions**: Platform choices, deployment strategies
- **Architectural Patterns**: Design patterns and architectural approaches
- **Technology Selections**: Framework, library, or tool choices
- **API Design**: API structure and design decisions

## Best Practices

1. **Make Decisions Explicit**: Even if a decision seems obvious, document it
2. **Include Trade-offs**: Explain what we're gaining and what we're sacrificing
3. **Be Concise**: Focus on the essential information
4. **Use Examples**: Include code samples or diagrams when helpful
5. **Reference Alternatives**: Show that alternatives were considered
6. **Document Implementation**: Explain how the decision was actually implemented
7. **Update When Needed**: If a decision changes, update the ADR

## Linking to ADRs

When referencing ADRs in code or docs, use:

````markdown
See [ADR-001: Decision Title](docs/ADRs/0001-decision-title.md) for details.
````

## Questions?

For questions about a specific ADR, reach out to:

- **ADR Author**: Listed in the `authors` field
- **Owner**: Listed in the `owner` field
- **Team Discussion**: Open a GitHub Discussion

---

**Reference**: This ADR process is based on [Nygard's ADR format](https://github.com/adr/adr-template) with modifications for MTG AI.
