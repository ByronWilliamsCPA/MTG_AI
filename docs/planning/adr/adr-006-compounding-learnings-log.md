---
title: "ADR-006: Compounding Learnings Log for Critique Quality"
schema_type: planning
status: accepted
owner: core-maintainer
purpose: "Record the decision to convert every escaped review misjudgment into a deterministic check or regression fixture via an append-only learnings log."
tags:
  - planning
  - architecture
  - decisions
---

> **Status**: Accepted
> **Date**: 2026-06-08 (proposed 2026-06-06)
> **Supersedes**: None
> **Decision note**: Accepted after the 2026-06-08 multi-lens panel review, with
> two corrections the panel required. (1) The learnings log is **app-owned**, not
> a data-owned Corpus artifact: the flagging event arrives through the
> app-service feedback route, and the app role has `SELECT`-only on data-owned
> tables, so a Corpus placement would violate the single-writer rule in ADR-001.
> (2) Capturing user decklists needs its own privacy posture (see "Privacy and
> retention"); ADR-002 provenance covers external licensed data, not private user
> decks. v1 ships only reproducible capture; the triage workflow and the
> CI-regression machinery are deferred to Phase 4 with the eval harness.

## TL;DR

Every escaped misjudgment (a wrong, illegal, or off-archetype review the user
flags) is recorded in an **app-owned**, append-only learnings log with the
reproducing `DeckSnapshot` (ADR-004) and its version vector, then triaged into
either a new deterministic lens check or a golden regression fixture, so review
quality compounds instead of regressing. v1 captures entries; triage and the
CI-regression gate land in Phase 4.

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

- **Reproducible capture**: a flagged review writes a log entry referencing the
  persisted `DeckSnapshot` (ADR-004) and its full version vector (`rules_version`,
  `spine_version`, `archetype`, `classifier_version`), the lens verdicts, and the
  human correction, so the case re-runs deterministically. The snapshot is the
  durable app-owned entity ADR-004 defines, which is why that contract had to be
  pinned down rather than left transient.
- **Triage into one of two durable forms**: either (a) a new or tightened lens
  check (a missing rule the deterministic engine should have caught) or (b) a
  golden regression fixture asserting the corrected verdict; prose alone is not an
  accepted resolution.
- **Compounding, not one-off**: the fixture set and lens checks only grow, so a
  fixed misjudgment cannot silently return; this is the deterministic counterpart
  to FluidDocs adding a reviewer item per escape.
- **Feeds the existing seam**: entries live as an **app-owned**, Application-layer
  append-only artifact (see [ADR-002](../adr/adr-002-data-model.md)), written by
  the app service that owns the feedback route, never as a data-owned Corpus row
  (which the app role cannot write under ADR-001). They double as the labeled
  corpus ADR-003 anticipated for a possible future model phase; promotion into a
  data-owned training corpus, if it ever happens, is a separate data-service
  ingestion step governed by the privacy posture below.

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

- Capturing full user decklists costs storage and demands a real privacy posture.
  ADR-002 provenance fields describe external licensed reference data, not private
  user decks, so they do not cover this case: the posture is defined explicitly
  under "Privacy and retention" below (user-scoped, consent-gated, retention-
  bounded) rather than assumed from ADR-002.

### Technical Debt

- Triage can backlog; needs a lightweight status on each entry (captured, triaged,
  resolved) so escapes are not lost.

### Privacy and retention

- The learnings log stores private user decklists, so it is user-scoped: every
  entry is owned by the user whose review produced it, and access follows the
  same `user_id` scoping as `DeckReview`.
- Capture is consent-gated: a review is logged for learning only when the user
  flags it (the explicit feedback action), never silently on every review.
- Retention is bounded and the snapshot is minimized to what reproduces the case
  (resolved `oracle_id` list, commander, version vector, verdicts, correction),
  not free-form user data.
- Any future promotion of entries into a shared, data-owned training corpus is a
  separate, explicitly consented data-service step, not an automatic consequence
  of logging.

> **RAD** `#CRITICAL` security/privacy: the learnings log stores private user
> decklists; capture must be user-scoped, consent-gated (written only on an explicit
> user flag), and retention-bounded, and any promotion to a shared corpus must be
> separately consented. `#VERIFY`: the feedback route writes a log entry only on an
> explicit flag (never on every review); access tests assert `user_id` scoping
> matches `DeckReview`; no implicit logging path exists.

### v1 Scope (what ships first)

- **v1 (capture only, Phase 3)**: persist `DeckReview` with the full
  `DeckSnapshot` and version vector (already in the plan) plus a `flagged`
  field/reason on the feedback route (`POST /reviews/{id}/feedback`). That alone
  is the reproducible corpus and the labeled training set.
- **Phase 4 (triage + CI gate)**: the triage workflow, the captured/triaged/
  resolved status model, the conversion of entries into lens checks or golden
  fixtures, and the meta-test, all land with the eval-harness-to-CI-regression
  work in Phase 4. The backlog-policing meta-test is explicitly a Phase 4 item so
  it cannot fail CI before the pipeline that produces escapes even exists.

### Components Affected

1. **learnings log** (v1 capture): app-owned, user-scoped, append-only store of
   flagged-review cases with the `DeckSnapshot` reference, version vector, lens
   verdicts, and human correction.
2. **triage workflow** (Phase 4): converts an entry into a lens check or a golden
   fixture and marks it resolved.
3. **test suite** (Phase 4): consumes the golden fixtures as regression tests in
   CI.

### Testing Strategy

- Each resolved entry adds a regression test; a meta-test (Phase 4) asserts no
  entry sits in the captured state without a linked check or fixture beyond a
  grace window. The meta-test is gated to Phase 4 so backlog policing never blocks
  CI during earlier phases.

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
