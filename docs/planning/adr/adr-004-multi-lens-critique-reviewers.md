---
title: "ADR-004: Multi-Lens Critique Reviewers Over the Scorecard"
schema_type: planning
status: proposed
owner: core-maintainer
purpose: "Record the decision to structure the review as independent, category-owning lenses aggregated by a gate, rather than one monolithic scorer."
tags:
  - planning
  - architecture
  - decisions
---

> **Status**: Proposed
> **Date**: 2026-06-06
> **Supersedes**: None

## TL;DR

The deterministic review is composed of independent, category-owning lenses
(legality/identity, power/bracket, consistency/manabase, interaction/role,
wincon/combo), each emitting its own verdict and observations over a single deck
snapshot, aggregated by a gate; the lenses are pure functions and run in
parallel, with the LLM explanation remaining the only swappable, off-path step.

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
- **Embarrassingly parallel**: the soft lenses are pure functions of the snapshot
  and rules-version, so they run concurrently with no shared mutable state; this
  is the deterministic analogue of FluidDocs spawning a subagent per reviewer.
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

- A shared snapshot and aggregation schema couple the lenses: mitigated by a small
  typed snapshot model and a fixed lens-result contract (verdict + observations +
  rules-version).

### Technical Debt

- Lens weighting and how soft-lens verdicts roll into the headline score need
  tuning; surface them as guides, not verdicts (consistent with ADR-003).

## Implementation

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
