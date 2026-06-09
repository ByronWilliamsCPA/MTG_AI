---
title: "ADR-005: Archetype-Specific Critique Spines"
schema_type: planning
status: accepted
owner: core-maintainer
purpose: "Record the decision to evaluate decks against archetype-specific expectations (spines) rather than one universal role-coverage rubric."
tags:
  - planning
  - architecture
  - decisions
---

> **Status**: Accepted
> **Date**: 2026-06-08 (proposed 2026-06-06)
> **Supersedes**: None
> **Decision note**: Accepted after the 2026-06-08 multi-lens panel review. The
> architecturally expensive part, archetype targets as effective-dated config the
> lenses read (the "spine seam"), is adopted now because retrofitting it is
> costly. The implementation is deliberately scoped down for v1 (see
> "v1 scope" below): a single generic-midrange spine plus a user-supplied
> archetype override, with the deterministic classifier and the multi-archetype
> spine library deferred until real reviews justify them. This bounds the ongoing
> meta-curation burden the feasibility lens flagged as the single largest
> solo-maintainer risk in the set.

## TL;DR

The review evaluates a deck against an archetype-specific spine of role targets,
thresholds, and lens weights stored as versioned, effective-dated config, rather
than against one universal rubric. The lenses read the resolved spine as data.
v1 ships one generic-midrange spine plus a user override; deterministic
archetype classification and additional archetype spines (turbo/combo,
stax/control, aggro) are added incrementally post-v1.

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

- **Deterministic classification (post-v1)**: a deck's archetype is inferred from
  its commander, role distribution, and combo presence by explicit rules, with a
  declared fallback (generic midrange spine) when confidence is low. Because the
  classifier is code, not effective-dated data, the ADR-002 reproducibility
  guarantee does not cover it automatically: the snapshot therefore records a
  `classifier_version` alongside `rules_version` and `spine_version`, so a
  classifier rule change cannot silently alter a past review for identical
  inputs. The chosen archetype, spine version, and classifier version are all
  recorded on the review (in the `DeckSnapshot` defined in ADR-004).

  > **RAD** `#CRITICAL` data-integrity: a classifier-code change must not silently
  > alter a past review for identical inputs (ADR-002 effective-dating covers data,
  > not code). `#VERIFY`: `classifier_version` is recorded on the snapshot and a
  > golden test asserts a past review re-runs to the same archetype under a bumped
  > classifier (see Success Criteria below).
- **Spine as data**: each spine declares role targets (ramp, interaction, card
  advantage, threats, win lines), thresholds, and per-lens weights; spines carry
  effective dates exactly like the bracket rules and Game Changers list in
  [ADR-002](../adr/adr-002-data-model.md), so old reviews stay reproducible.
  Spines are **data-owned** reference config (written only by the data service,
  read by the app via `SELECT`), consistent with the single-writer rule in
  [ADR-001](../adr/adr-001-initial-architecture.md).
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

### v1 Scope (what ships first)

- **Ship now**: the spine config schema (effective-dated, data-owned), a single
  generic-midrange spine seeded in `reference_config`, the lenses reading the
  resolved spine instead of hard-coded constants, and a user-supplied archetype
  override persisted as a review input. This is the full architectural seam at
  minimal curation cost.
- **Defer (add incrementally post-v1, one per real misjudgment)**: the
  deterministic `archetype-classifier` and the additional archetype spines
  (turbo/combo, stax/control, aggro). Until the classifier exists, the archetype
  is either the generic-midrange default or the user override. Adding a spine or
  the classifier later does not change the contract, only the data and one
  app-side module.

### Components Affected

1. **spine config** (v1): effective-dated archetype spines (targets, thresholds,
   weights) in refreshable, data-owned config, owned like the bracket rules in
   ADR-002. v1 seeds one generic-midrange spine.
2. **lenses** (v1): consume the resolved spine instead of universal constants.
3. **user override** (v1): a user-forced archetype, captured in the `DeckSnapshot`
   (ADR-004) as a recorded input so re-runs are reproducible.
4. **archetype-classifier** (post-v1): deterministic archetype inference with a
   low-confidence fallback to the generic-midrange spine; records
   `classifier_version` on the review.

### Testing Strategy

- Golden decks per archetype assert the expected spine is selected and that a
  deliberately archetype-correct light-interaction deck is not penalized for it.

## Validation

### Success Criteria

- [ ] Every review records the archetype, spine version, and (once the classifier
      ships) classifier version it used, on the `DeckSnapshot`.
- [ ] An archetype-correct deck is not flagged for an intended, on-spine choice.
- [ ] A user can override the archetype; the override is persisted as a review
      input and the review re-runs reproducibly.
- [ ] v1 acceptance: lenses read the generic-midrange spine from config (no
      hard-coded role constants); a user override selects an alternate spine when
      one exists.

## Related

- [ADR-002: Data Model](../adr/adr-002-data-model.md)
- [ADR-003: Engine Approach](../adr/adr-003-engine-approach.md)
- [ADR-004: Multi-Lens Critique Reviewers](../adr/adr-004-multi-lens-critique-reviewers.md)
- [FluidDocs Deck-Builder Review](../fluiddocs-deck-builder-review.md)
- [Technical Spec](../tech-spec.md)
