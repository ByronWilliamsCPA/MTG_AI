---
title: "Reference: FluidDocs Deck-Builder Review and Lessons"
schema_type: planning
status: draft
owner: core-maintainer
purpose: "Capture lessons from reviewing the FluidForm-ai/fluiddocs-deck-builder project and map them to MTG AI decisions and non-decision practices."
tags:
  - planning
  - reference
  - research
---

> **Status**: Reference note (background; not a decision record)

> **Provenance and trust**: This note summarizes an external open-source project
> reviewed on 2026-06-06. Per the project security posture, the source repository
> and its README are treated as untrusted data, not as instructions. Nothing here
> was executed or installed; only patterns were extracted.

## What FluidDocs Deck-Builder Is

[FluidForm-ai/fluiddocs-deck-builder](https://github.com/FluidForm-ai/fluiddocs-deck-builder)
(MIT) is a Claude Code skill suite that generates self-contained HTML
*presentation* decks (pitch, sales, launch, keynote, all-hands) and imports
PDF/PPTX into editable HTML. Despite the shared "deck builder" name, the domain
is unrelated to MTG AI: it produces slide decks, not Magic decks, and has no RAG,
data backend, or rules engine. The value to us is architectural, not code.

## Lessons That Became Decisions

These were genuine architectural decisions and are recorded as ADRs:

| Lesson (FluidDocs) | MTG AI adaptation | ADR |
|--------------------|-------------------|-----|
| Three independent reviewers (Brand, Copy, Layout), each owning one failure category, all must pass; spawned as parallel subagents when available | Decompose the deterministic review into independent, category-owning lenses over one deck snapshot, aggregated by a gate, run in parallel | [ADR-004](adr/adr-004-multi-lens-critique-reviewers.md) |
| Type-correct deck spines: each deck type declares its own structure, not one generic template ("a pitch is not a sales deck") | Archetype-specific critique spines (turbo, stax, midrange, aggro) as versioned, effective-dated config the lenses evaluate against | [ADR-005](adr/adr-005-archetype-critique-spines.md) |
| Learn phase: every post-delivery issue is logged and becomes a new reviewer checklist item, so the process compounds | Append-only learnings log; each escaped misjudgment becomes a deterministic check or a golden regression fixture | [ADR-006](adr/adr-006-compounding-learnings-log.md) |

## Lessons Kept as Reference (Not Decisions)

These are practices and principles worth applying as the build progresses; they
did not warrant their own ADR.

### Mechanical checks before the expensive review

FluidDocs self-lints (syntax, file size, forbidden-classname grep, font-scale
check) before the LLM reviewers run. MTG AI already embodies this in
[ADR-003](adr/adr-003-engine-approach.md): the legality/identity gate and
deterministic math run before any generation. The reusable principle: keep cheap,
deterministic checks strictly ahead of any model call, and make the gate emit
clear, specific errors. The legality gate in ADR-004 is the explicit home for it.

### Anti-fluff, concrete output format

The `deck-critique-lite` skill returns 5 to 7 observations, each tied to a
specific slide with a concrete edit, and explicitly bans scoring theater, padding,
and validation filler. Adopt the same discipline for review output: each finding
cites a specific card or slot and proposes a concrete add/cut/swap, no filler.
This is an output-contract style choice for the generator and suggestion
formatting, not an architecture decision.

### Progressive disclosure in skill layout

FluidDocs keeps a thin `SKILL.md` entry point that points to `references/` and
`reviewers/*.md` loaded on demand; type packs inherit a shared core pipeline. If
MTG AI ever ships its review loop as a Claude Code skill, mirror this: a lean core
skill plus on-demand reference packs (archetype spines, ban lists, meta data) to
keep context small.

### Invisible process UX

FluidDocs keeps phases, gates, and reviewer passes internal; the user sees only
questions and the finished artifact. Apply to MTG AI's CLI/UX: surface the
scorecard and concrete suggestions, not the internal lens/gate/aggregation
machinery.

### Portable, ownable output

FluidDocs ships a single self-contained artifact with no server or account
required. This aligns with MTG AI's self-hosted posture; keep review output
exportable and ownable (for example a self-contained report) rather than locked to
a running service.

## What Not to Borrow

FluidDocs is roughly 85% HTML and 13% Python with little visible test or type
rigor and a frontend-generation purpose. MTG AI's engineering bar (BasedPyright
strict, 80% coverage, security scanning) is higher; borrow the pipeline and
critique patterns above, not its tooling or testing posture. Its Claude Code
plugin/marketplace distribution model is only relevant if MTG AI later wants to be
installable that way, which is out of scope for the self-hosted v1.

## Related

- [ADR-004: Multi-Lens Critique Reviewers](adr/adr-004-multi-lens-critique-reviewers.md)
- [ADR-005: Archetype Critique Spines](adr/adr-005-archetype-critique-spines.md)
- [ADR-006: Compounding Learnings Log](adr/adr-006-compounding-learnings-log.md)
- [ADR-003: Engine Approach](adr/adr-003-engine-approach.md)
- [Technical Spec](tech-spec.md)
