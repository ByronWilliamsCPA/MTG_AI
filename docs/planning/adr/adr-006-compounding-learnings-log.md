---
title: "ADR-006: Compounding Learnings Log for Critique Quality"
schema_type: planning
status: proposed
owner: core-maintainer
purpose: "Record the decision to convert every escaped review misjudgment into a deterministic check or regression fixture via an append-only learnings log."
tags:
  - planning
  - architecture
  - decisions
---

> **Status**: Proposed
> **Date**: 2026-06-06
> **Supersedes**: None

## TL;DR

Every escaped misjudgment (a wrong, illegal, or off-archetype review the user
flags) is recorded in an append-only learnings log with the deck snapshot and
rules-version, then triaged into either a new deterministic lens check or a golden
regression fixture, so review quality compounds instead of regressing.

## Context

### Problem

[ADR-003](../adr/adr-003-engine-approach.md) noted that review logs accumulate a
corpus and that heuristic scores need tuning, but it left no mechanism that turns
a bad review into a durable fix. Without one, the same misjudgment recurs, fixes
are ad hoc, and there is no growing regression set guarding the deterministic
lenses ([ADR-004](../adr/adr-004-multi-lens-critique-reviewers.md)) and spines
([ADR-005](../adr/adr-005-archetype-critique-spines.md)).

### Constraints

- **Technical**: a captured case must reproduce exactly, which requires the deck
  snapshot plus the rules-version and spine version used; the log must feed the
  test suite, not just sit as prose.
- **Business**: single maintainer; the loop must be low-ceremony or it will not be
  used.

### Significance

This is the quality flywheel: it decides whether the heuristics improve over time
or drift; retrofitting reproducible capture later loses the early corpus.

## Decision

**We adopt an append-only learnings log where each escaped misjudgment is captured
with its reproducing snapshot and triaged into a deterministic check or a golden
fixture, because a review system without a compounding feedback loop silently
regresses.** This adapts the FluidDocs deck-builder's Learn phase, where every
post-delivery issue is logged and becomes a new reviewer checklist item so the
process compounds across decks.

### Rationale

- **Reproducible capture**: a flagged review writes a log entry with the resolved
  deck snapshot, archetype/spine version, rules-version, the lens verdicts, and the
  human correction, so the case re-runs deterministically.
- **Triage into one of two durable forms**: either (a) a new or tightened lens
  check (a missing rule the deterministic engine should have caught) or (b) a
  golden regression fixture asserting the corrected verdict; prose alone is not an
  accepted resolution.
- **Compounding, not one-off**: the fixture set and lens checks only grow, so a
  fixed misjudgment cannot silently return; this is the deterministic counterpart
  to FluidDocs adding a reviewer item per escape.
- **Feeds the existing seam**: entries live as a Corpus-layer append-only artifact
  (see [ADR-002](../adr/adr-002-data-model.md)) and double as the labeled corpus
  ADR-003 anticipated for a possible future model phase.

## Options Considered

### Option 1: Append-only learnings log triaged into checks/fixtures (chosen)

**Pros**:

- Each escape becomes a permanent guard; quality compounds.
- Reproducible cases feed CI directly as golden fixtures.
- Builds the labeled corpus for a future training phase at no extra cost.

**Cons**:

- Discipline cost: every accepted escape must produce a check or a fixture.

### Option 2: Ad hoc fixes without a log

**Pros**:

- Nothing to maintain.

**Cons**:

- Misjudgments recur; no regression guard; the corpus never forms.

### Option 3: Track issues only in an external tracker

**Pros**:

- Uses existing tooling.

**Cons**:

- Cases are not reproducible or wired to the test suite; prose drifts from the
  deterministic engine it is meant to correct.

## Consequences

### Positive

- The lens and spine heuristics improve monotonically against a growing corpus.
- A labeled training set accrues for the deferred model phase (ADR-003).
- Fixes are reproducible and enforced in CI, not narrative.

### Trade-offs

- Capturing full snapshots costs storage and a privacy/provenance posture:
  mitigated by reusing the Corpus-layer append-only pattern and provenance fields
  from ADR-002.

### Technical Debt

- Triage can backlog; needs a lightweight status on each entry (captured, triaged,
  resolved) so escapes are not lost.

## Implementation

### Components Affected

1. **learnings log**: append-only store of escaped-review cases with snapshot,
   versions, lens verdicts, and human correction.
2. **triage workflow**: converts an entry into a lens check or a golden fixture
   and marks it resolved.
3. **test suite**: consumes the golden fixtures as regression tests in CI.

### Testing Strategy

- Each resolved entry adds a regression test; a meta-test asserts no entry sits in
  the captured state without a linked check or fixture beyond a grace window.

## Validation

### Success Criteria

- [ ] A flagged review produces a reproducible log entry (re-runs to the same
      lens verdicts).
- [ ] Every resolved entry is backed by a deterministic check or a golden fixture.
- [ ] A previously fixed misjudgment fails CI if it regresses.

## Related

- [ADR-002: Data Model](../adr/adr-002-data-model.md)
- [ADR-003: Engine Approach](../adr/adr-003-engine-approach.md)
- [ADR-004: Multi-Lens Critique Reviewers](../adr/adr-004-multi-lens-critique-reviewers.md)
- [ADR-005: Archetype Critique Spines](../adr/adr-005-archetype-critique-spines.md)
- [FluidDocs Deck-Builder Review](../fluiddocs-deck-builder-review.md)
