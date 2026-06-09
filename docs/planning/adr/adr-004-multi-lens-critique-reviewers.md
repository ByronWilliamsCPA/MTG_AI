---
title: "ADR-004: Multi-Lens Critique Reviewers Over the Scorecard"
schema_type: planning
status: accepted
owner: core-maintainer
purpose: "Record the decision to structure the review as independent, category-owning lenses aggregated by a gate, rather than one monolithic scorer."
tags:
  - planning
  - architecture
  - decisions
---

> **Status**: Accepted
> **Date**: 2026-06-08 (proposed 2026-06-06)
> **Supersedes**: None
> **Decision note**: Accepted after a multi-lens panel review on 2026-06-08
> (roadmap-fit, architecture-coherence, and solo-maintainer-feasibility lenses).
> Scoped for v1: the lenses run sequentially; concurrent execution is a recorded
> future option, not a v1 requirement. The shared `DeckSnapshot` contract below
> is the reconciliation point for ADR-005 and ADR-006.

## TL;DR

The deterministic review is composed of independent, category-owning lenses
(legality/identity, power/bracket, consistency/manabase, interaction/role,
wincon/combo), each emitting its own verdict and observations over a single
versioned deck snapshot, aggregated by a gate; the lenses are pure functions of
that snapshot. They run sequentially in v1 (parallel execution is a recorded
future option), with the LLM explanation remaining the only swappable, off-path
step.

## Context

### Problem

[ADR-003](../adr/adr-003-engine-approach.md) fixed the engine as a deterministic
scorecard with the LLM explaining, not deciding. It did not fix how the scoring
is internally organized. A single monolithic scorer concentrates every failure
category (an illegal card, a flat curve, missing interaction, no win line) into
one code path and one verdict, which is hard to test, hard to attribute, and
prone to one category masking another.

### Constraints

- **Technical**: verdicts must be reproducible and attributable to a specific
  category; the lenses read the same versioned data and rules state; single small
  box, latency sensitive.
- **Business**: single maintainer; the structure must make failures easy to
  locate and easy to add to over time.

### Significance

How the review is decomposed sets the testing seams, the parallelism, and how
suggestions are attributed; reworking it later re-touches every scoring module.

## Decision

**We decompose the review into independent, category-owning lenses over one
immutable deck snapshot, aggregated by a gate, because independent lenses remove
single-pass blind spots, attribute each finding to a category, and parallelize
cleanly.** The pattern is adapted from the FluidDocs deck-builder's three
independent reviewers (Brand, Copy, Layout) that each own one failure category
and must all pass before release.

### Rationale

- **One snapshot, many lenses**: each lens reads the same resolved deck (cards by
  `oracle_id`, commander, rules-version) and owns exactly one failure category,
  so no lens can silently compensate for another.
- **Gate, not average**: a hard legality/identity lens is a blocking gate;
  power/bracket, consistency/manabase, interaction/role, and wincon/combo each
  emit a verdict plus observations that the aggregator composes into the
  scorecard. A failing legality gate short-circuits before the soft lenses run.

  > **RAD** `#CRITICAL` data-integrity: lenses are pure functions of one snapshot,
  > so no lens can read or silently compensate for another's state. `#CRITICAL`
  > timing: a failing legality gate must short-circuit before any soft lens runs.
  > `#VERIFY`: aggregation test proving lens order does not change output and that a
  > failing legality gate short-circuits (see Testing Strategy and Success Criteria
  > below).
- **Pure, order-independent, parallelizable later**: the soft lenses are pure
  functions of the snapshot and rules-version with no shared mutable state, so
  their output is independent of execution order. v1 runs them sequentially
  (they are fast database lookups well within the p95 < 5s budget, so concurrency
  buys no latency at this scale while adding execution-order test burden);
  concurrent execution remains available as a future option without changing the
  contract. This is the deterministic analogue of FluidDocs spawning a subagent
  per reviewer.
- **Explanation stays off the path**: the swappable generator narrates the
  aggregated lens output; it cannot change a lens verdict (preserves ADR-003).

## Options Considered

### Option 1: Independent category-owning lenses + gate (chosen)

**Pros**:

- Findings are attributable; one lens cannot mask another.
- Pure functions parallelize and unit-test in isolation (one golden deck per lens).
- New failure modes become a new lens or a lens check, not a rewrite.

**Cons**:

- An aggregation contract and a shared snapshot model to define and maintain.

### Option 2: Single monolithic scorer

**Pros**:

- Fewer moving parts initially.

**Cons**:

- Failures are hard to attribute and one category masks another; the scorer grows
  into a tangle that resists testing and parallelism.

### Option 3: LLM-orchestrated multi-agent critique

**Pros**:

- Flexible natural-language lenses with little explicit code.

**Cons**:

- Non-reproducible and hallucination-prone on the correctness path; violates
  ADR-003; per-review cost on the hot path.

## Consequences

### Positive

- Each lens has a narrow, testable contract and a clear owner of its rules.
- The legality gate fails fast and cheaply before soft scoring runs.
- Parallel pure lenses keep review p95 within target.

### Trade-offs

- A shared snapshot and aggregation schema couple the lenses: mitigated by the
  small typed `DeckSnapshot` model defined below (see Implementation) and a fixed
  lens-result contract (verdict + observations + rules-version + spine-version).

### Technical Debt

- Lens weighting and how soft-lens verdicts roll into the headline score need
  tuning; surface them as guides, not verdicts (consistent with ADR-003).

## Implementation

### Deck Snapshot Contract (shared with ADR-005 and ADR-006)

The "deck snapshot" is a first-class, app-owned, persisted artifact, not a
transient in-memory object. Defining it once here closes a gap the panel review
flagged: ADR-005 and ADR-006 both depend on the snapshot being durable and fully
versioned, so its contents and ownership are fixed at this layer.

- **Ownership**: app-owned (Application layer per ADR-002), written by the app
  service alongside `DeckReview`. It is never a data-owned (Corpus/Reference)
  row, so it does not touch the single-writer rule in ADR-001.
- **Contents**: resolved cards by `oracle_id`, commander(s), computed
  `color_identity`, and the full version vector needed to reproduce a review:
  `rules_version`, `spine_version` and `archetype` (ADR-005), and
  `classifier_version` (ADR-005). Any user override (e.g. a forced archetype) is
  captured here as a recorded input.
- **Reproducibility invariant**: a review is a pure function of the `DeckSnapshot`
  alone, since the snapshot carries the full version vector above (`rules_version`,
  `spine_version`, `archetype`, `classifier_version`). Identical snapshots yield
  identical lens results regardless of execution order.
- **Lens-result contract**: each lens returns `{lens, verdict, observations,
  rules_version, spine_version}` so every finding is attributable to its category
  and its versioned inputs. The `archetype` and `classifier_version` needed for
  full reproducibility live on the `DeckSnapshot`, not on each lens result, so
  they are not repeated per lens.

> **RAD** `#CRITICAL` data-integrity/concurrency: a review is a pure function of the
> `DeckSnapshot`; identical snapshots yield identical lens results regardless of
> execution order or parallelism. `#VERIFY`: property test that re-running scoring on
> the same persisted snapshot reproduces identical lens verdicts under shuffled lens
> order (see Success Criteria below).

### Components Affected

1. **scorecard**: refactored into a `lenses/` package, one module per category,
   each consuming a typed deck snapshot and returning a lens result.
2. **aggregator**: composes lens results, enforces the legality gate, builds the
   scorecard.
3. **suggestions**: attributes each add/cut to the lens whose gap it closes.
4. **generator**: explains the aggregated result; no lens-verdict authority.

### Testing Strategy

- Unit and property tests per lens on golden decks; an aggregation test proving a
  failing legality gate short-circuits and that lens order does not change output.

## Validation

### Success Criteria

- [ ] Each finding names the lens (category) that produced it.
- [ ] Soft lenses are pure: identical snapshot and rules-version yield identical
      lens results regardless of execution order or parallelism.
- [ ] A failing legality gate short-circuits before soft lenses run.

## Related

- [ADR-003: Engine Approach](../adr/adr-003-engine-approach.md)
- [ADR-005: Archetype Critique Spines](../adr/adr-005-archetype-critique-spines.md)
- [ADR-006: Compounding Learnings Log](../adr/adr-006-compounding-learnings-log.md)
- [FluidDocs Deck-Builder Review](../fluiddocs-deck-builder-review.md)
- [Technical Spec](../tech-spec.md)
