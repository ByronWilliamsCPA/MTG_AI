---
title: "ADR-002: Layered Data Model with Reuse-First Ingestion"
schema_type: planning
status: accepted
owner: core-maintainer
purpose: "Record the layered, oracle_id-keyed relational data model and the reuse-first ingestion strategy."
tags:
  - planning
  - architecture
  - decisions
---

> **Status**: Accepted
> **Date**: 2026-06-01
> **Supersedes**: None

## TL;DR

MTG AI stores data in a layered relational model (Landing, Reference, Corpus,
Analytics, Application) keyed to the Scryfall `oracle_id`, ingesting existing
free and MIT datasets rather than rebuilding them, with provenance on every row
and effective dates on fast-moving reference data.

## Context

### Problem

The deterministic scorecard (see [ADR-003](../adr/adr-003-engine-approach.md)) needs
many kinds of data with different volatilities: a stable card spine, slowly
changing reference data (themes, archetypes, combos, brackets, the Game Changers
list), appended facts (decklists, tournament results), and derived analytics
(synergy, lift, meta). Most of this is already computed by EDHREC, Commander
Spellbook, Scryfall, and MTGJSON. We must shape one model that holds all of it,
keeps a fast-moving rules system reproducible, and minimizes new code.

### Constraints

- **Technical**: single shared Postgres (see [ADR-001](../adr/adr-001-initial-architecture.md));
  ~30,000 cards; pairwise data is large; EDHREC has no open license.
- **Business**: single maintainer; "reuse first, build only the gaps."

### Significance

The data model and identity scheme are expensive to reverse: every downstream
score, suggestion, and future format depends on them.

## Decision

**We adopt a layered relational model keyed to `oracle_id`, populated by
reuse-first ingestion, because it matches the data's natural volatility tiers and
keeps a beta, fast-changing rules system reproducible.**

### Rationale

- **Canonical identity**: one `oracle_id` per unique card; all other identifiers
  (MTGJSON, Spellbook, EDHREC, Arena, MTGO, normalized name) resolve to it through
  a crosswalk, never a join condition. Unresolved names are logged, never dropped.
- **Layers by volatility**: Landing (raw, immutable, timestamped), Reference
  (conformed, slow, versioned), Corpus (appended dated facts), Analytics
  (recomputed), Application (transactional user data).
- **Effective-date what moves**: bracket definitions and the Game Changers list
  carry effective dates so a review is reproducible against the rules state on
  its run date.
- **Provenance everywhere**: each ingested row records source, URL, `ingested_at`,
  and license, which the licensing posture (EDHREC polite-cache) requires.
- **Reuse over rebuild**: ingest Scryfall (inventory/legality/prices), MTGJSON
  (decks, commander flag, prices), EDHREC (synergy, inclusion, lift, themes), and
  Commander Spellbook (combos, bracket estimate). New code is plumbing, not models.

## Options Considered

### Option 1: Layered relational model keyed to oracle_id (chosen)

**Pros**:

- Matches volatility tiers; reference data versioned, facts appended.
- Relational joins serve the color/role/meta filters the scorecard needs.
- Provenance and effective dates make reviews reproducible and license-compliant.

**Cons**:

- More tables (~25) and an ingestion layer to maintain.

### Option 2: Flat, denormalized per-feature tables

**Pros**:

- Fewer joins; quick to start.

**Cons**:

- No provenance or versioning; rules drift makes old reviews irreproducible.
- Duplicated card facts drift out of sync.

### Option 3: Document/NoSQL store

**Pros**:

- Flexible shapes for heterogeneous source JSON.

**Cons**:

- The core queries are relational (color identity, role counts, pairwise lift);
  a document store fights them and adds a second engine.

## Consequences

### Positive

- One identity scheme; ingestion is idempotent upserts by `oracle_id`.
- Adding Standard later is a new format partition, not a re-architecture.
- Pairwise lift can be materialized sparsely (observed pairs above a threshold).

### Trade-offs

- Landing-layer raw JSON costs storage: acceptable; it makes re-derivation cheap.
- ~30k cards means ~900M ordered pairs: the data service materializes only
  observed lift above a support threshold; the app service treats unobserved
  pairs as neutral (zero) at query time, never computing lift on the hot path
  (it has no write access and the aggregation would blow the latency target).

### Technical Debt

- Name resolution for double-faced, split, adventure, and token cards needs an
  override table beyond the crosswalk.
- `card_price` is optional and stale after ~24h; treat it as advisory.

## Implementation

### Components Affected

1. **mtg_ai_schema**: defines the Reference, Corpus, and Analytics tables and
   the crosswalk; owned by the data service.
2. **Ingestion packages**: one per source (Scryfall, MTGJSON, EDHREC, Spellbook),
   each validating into a Pydantic boundary model before upsert.
3. **App tables**: users, decks, collections, reviews (see the tech spec).

### Testing Strategy

- Recorded source fixtures (no live network); assert the Pydantic boundary
  rejects schema drift and unresolved names are logged.

## Validation

### Success Criteria

- [ ] Every card row resolves to exactly one `oracle_id`.
- [ ] A review run records the Game Changers/bracket effective dates it used.
- [ ] Re-running an ingest is idempotent (no duplicate facts).

## Related

- [ADR-001: Architecture](../adr/adr-001-initial-architecture.md)
- [ADR-003: Engine Approach](../adr/adr-003-engine-approach.md)
- [Technical Spec](../tech-spec.md)
- [Project Vision](../project-vision.md)
