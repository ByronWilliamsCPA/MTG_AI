---
title: "ADR-005: Archetype-Specific Critique Spines"
schema_type: planning
status: proposed
owner: core-maintainer
purpose: "Record the decision to evaluate decks against archetype-specific expectations (spines) rather than one universal role-coverage rubric."
tags:
  - planning
  - architecture
  - decisions
---

> **Status**: Proposed
> **Date**: 2026-06-06
> **Supersedes**: None

## TL;DR

The review classifies a deck's archetype (for example turbo/combo, stax/control,
midrange/value, aggro) and evaluates it against an archetype-specific spine of
role targets, thresholds, and lens weights stored as versioned, effective-dated
config, rather than scoring every deck against one universal rubric.

## Context

### Problem

[ADR-003](../adr/adr-003-engine-approach.md) scores "role coverage vs archetype
targets" but leaves the targets implicit. A single universal rubric misjudges
decks whose strategy intentionally departs from the average: a turbo deck running
light interaction is not under-built, and a stax deck with few creatures is not
short on threats. Without archetype-aware expectations, the lenses from
[ADR-004](../adr/adr-004-multi-lens-critique-reviewers.md) flag intended choices
as faults.

### Constraints

- **Technical**: archetype targets change as the meta shifts and must be
  reproducible against a review's run date; classification must be deterministic
  and cheap; lenses consume the spine, not hard-coded constants.
- **Business**: single maintainer; spines must be editable as data, not code.

### Significance

The spine defines what "good" means per strategy; baking the wrong expectations
into the lenses produces confidently wrong reviews and erodes trust.

## Decision

**We make archetype-specific spines first-class, versioned config that the lenses
evaluate against, because a pitch is not a sales deck and a turbo list is not a
stax list: each archetype has different success criteria.** This adapts the
FluidDocs deck-builder's type-correct deck spines, where each deck type declares
its own structure rather than inheriting one generic template.

### Rationale

- **Deterministic classification**: a deck's archetype is inferred from its
  commander, role distribution, and combo presence by explicit rules, with a
  declared fallback (generic midrange spine) when confidence is low; the chosen
  spine and its version are recorded on the review.
- **Spine as data**: each spine declares role targets (ramp, interaction, card
  advantage, threats, win lines), thresholds, and per-lens weights; spines carry
  effective dates exactly like the bracket rules and Game Changers list in
  [ADR-002](../adr/adr-002-data-model.md), so old reviews stay reproducible.
- **Lenses read the spine**: the ADR-004 lenses take the resolved spine as input;
  the same lens code judges a turbo and a stax deck differently because the
  targets differ, not because the code branches.
- **Explainable departures**: a deviation from a spine target is surfaced as an
  observation tied to the archetype, never as a silent penalty.

## Options Considered

### Option 1: Archetype-specific spines as versioned config (chosen)

**Pros**:

- Reviews respect strategy; intended departures are not flagged as faults.
- Spines are editable data with effective dates; reproducible and meta-aware.
- Lens code stays generic; only the targets vary.

**Cons**:

- A classifier and a curated spine library to build and keep current.

### Option 2: One universal role-coverage rubric

**Pros**:

- Nothing new to classify or curate.

**Cons**:

- Misjudges any deck that intentionally deviates from the average; pushes every
  deck toward a single generic shape.

### Option 3: Let the LLM infer archetype expectations per review

**Pros**:

- No spine library to maintain.

**Cons**:

- Non-reproducible and unversioned; puts judgment back on the model, violating
  ADR-003.

## Consequences

### Positive

- Suggestions move a deck toward its own archetype's targets, not a generic mean.
- Spines version and refresh with the meta without code changes.
- Misclassification is visible (the spine is on the review) and correctable.

### Trade-offs

- A wrong archetype call skews the whole review: mitigated by recording the spine,
  a conservative fallback, and letting the user override the detected archetype.

### Technical Debt

- Hybrid and transitional archetypes resist single-label classification; may need
  blended spines or a confidence band later.

## Implementation

### Components Affected

1. **archetype-classifier**: deterministic archetype inference with a fallback and
   a user override hook.
2. **spine config**: effective-dated archetype spines (targets, thresholds,
   weights) in refreshable config, owned like the bracket rules in ADR-002.
3. **lenses**: consume the resolved spine instead of universal constants.

### Testing Strategy

- Golden decks per archetype assert the expected spine is selected and that a
  deliberately archetype-correct light-interaction deck is not penalized for it.

## Validation

### Success Criteria

- [ ] Every review records the archetype and spine version it used.
- [ ] An archetype-correct deck is not flagged for an intended, on-spine choice.
- [ ] A user can override the detected archetype and re-run reproducibly.

## Related

- [ADR-002: Data Model](../adr/adr-002-data-model.md)
- [ADR-003: Engine Approach](../adr/adr-003-engine-approach.md)
- [ADR-004: Multi-Lens Critique Reviewers](../adr/adr-004-multi-lens-critique-reviewers.md)
- [FluidDocs Deck-Builder Review](../fluiddocs-deck-builder-review.md)
- [Technical Spec](../tech-spec.md)
