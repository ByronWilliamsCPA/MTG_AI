---
title: "ADR-003: Deterministic Scorecard Engine, LLM for Explanation"
schema_type: planning
status: accepted
owner: core-maintainer
purpose: "Record the decision to make v1 a deterministic scorecard over reused data, with the LLM explaining rather than scoring."
tags:
  - planning
  - architecture
  - decisions
---

> **Status**: Accepted
> **Date**: 2026-06-01
> **Supersedes**: None

## TL;DR

The v1 engine is deterministic: it scores legality, power, bracket, role
coverage, and manabase from reused precomputed data, and ranks upgrade
suggestions. The LLM only explains the result in plain language; embeddings and
RAG are deferred to v2.

## Context

### Problem

A deck review must be trustworthy: legality-correct, bracket-aware, and
reproducible. The research shows the hard signals already exist as precomputed
data (EDHREC synergy/inclusion/lift, Commander Spellbook combos and bracket
estimate, Scryfall/MTGJSON inventory and legality) and that the scoring logic
(Disciple-of-the-Vault power, WotC bracket gate logic, role-coverage targets,
Karsten manabase math) is deterministic. We must decide what computes the
scorecard and where, if anywhere, a language model fits.

### Constraints

- **Technical**: legality and bracket placement cannot tolerate hallucination;
  reviews must be reproducible; single small box, few users, cheap to run.
- **Business**: single maintainer; ship the Commander review loop first.

### Significance

This choice sets the trust model and the v1 build size; reversing it would
re-found the whole pipeline.

## Decision

**The v1 engine is a deterministic scorecard over reused precomputed data, and
the LLM is explanation-only behind a swappable generator interface, because the
authoritative signals already exist and correctness must never depend on a
model.**

### Rationale

- **Deterministic truth**: a legality/identity gate, functional power (1-10),
  bracket gate logic over the versioned Game Changers list, role coverage vs
  archetype targets, and a Karsten manabase check produce identical output for
  identical inputs and rules-version.
- **Suggestions are deterministic too**: cuts/adds come from underfilled roles
  and bracket mismatches, ranked by commander synergy and lift, each re-validated
  for legality, then annotated with ownership and price for value-per-dollar
  sorting.
- **LLM explains, never decides**: the generator turns the scorecard into prose;
  it cannot change a score, legality, or bracket. The interface stays swappable
  so a later model (or none) is a drop-in.
- **Defer embeddings**: card2vec-style retrieval finds relationships the
  per-commander view misses, but the existing stats cover v1; embeddings are a
  v2 enhancement, not a dependency.

## Options Considered

### Option 1: Deterministic scorecard, LLM explains (chosen)

**Pros**:

- Legality and bracket are guaranteed, reproducible, and cheap.
- Little ML for v1; most work is ingestion and deterministic math.
- LLM cost is bounded and off the correctness path.

**Cons**:

- Scoring heuristics need hand-tuning and periodic rules refresh.

### Option 2: RAG + LLM as the scoring/critique core

**Pros**:

- Flexible natural-language reasoning; less explicit rule code.

**Cons**:

- Hallucinated or illegal suggestions; non-reproducible; per-review LLM cost on
  the hot path; ignores that the signals are already computed.

### Option 3: Train or fine-tune a model now

**Pros**:

- Could internalize synergy and power judgment.

**Cons**:

- No labeled corpus yet; premature and expensive. The review logs accumulate
  that corpus for a possible future phase.

## Consequences

### Positive

- The "LLM proposes, deterministic code disposes" seam holds: suggestions are
  re-validated before display.
- Review p95 is fast (DB lookups + math, not an LLM call).
- Review logs capture inputs, scores, and accept/reject as a future training set.

### Trade-offs

- Heuristic scores are tuning guides, not playtesting; surface them as such.
- The bracket system is beta; gate rules and the Game Changers list live in
  refreshable, effective-dated config (see [ADR-002](../adr/adr-002-data-model.md)).

### Technical Debt

- Functional tagging reliability is the weak point; EDHREC/Scryfall tags cover
  most cards but need hand-correction at the edges.

## Implementation

### Components Affected

1. **scorecard**: deterministic scoring modules (power, bracket, role, manabase).
2. **suggestions**: role-gap and bracket-driven ranker with re-validation and
   ownership/price annotation.
3. **generator**: swappable LLM explanation backend (no scoring authority).

### Testing Strategy

- Unit + property-based tests on the legality gate and scoring (golden decks);
  mock the generator and assert it cannot alter a score or legality verdict.

## Validation

### Success Criteria

- [ ] Identical inputs and rules-version yield identical scorecards.
- [ ] Every suggested add passes legality re-validation.
- [ ] Disabling the LLM still produces a complete scorecard and suggestions.

## Related

- [ADR-001: Architecture](../adr/adr-001-initial-architecture.md)
- [ADR-002: Data Model](../adr/adr-002-data-model.md)
- [ADR-004: Multi-Lens Critique Reviewers](../adr/adr-004-multi-lens-critique-reviewers.md)
- [ADR-005: Archetype Critique Spines](../adr/adr-005-archetype-critique-spines.md)
- [ADR-006: Compounding Learnings Log](../adr/adr-006-compounding-learnings-log.md)
- [Technical Spec](../tech-spec.md)
- [Project Vision](../project-vision.md)
