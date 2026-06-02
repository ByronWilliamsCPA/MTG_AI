---
title: "MTG AI - Development Roadmap"
schema_type: planning
status: active
owner: core-maintainer
purpose: "Document the phased implementation plan and milestones."
tags:
  - planning
  - roadmap
component: Strategy
source: "Approved spec plus tmp/ research synthesis (2026-06-01)"
---

> **Status**: Active | **Updated**: 2026-06-01
>
> Development Roadmap for MTG AI. v2.0 sequences ingestion before scoring, per the
> deterministic-scorecard engine decision.

## TL;DR

Foundation, then the reuse-first ingestion backbone, then the deterministic
scorecard, then ranked suggestions with collection and price, then quality and
release. Ingested data must exist before scoring can run, so ingestion leads.
Week labels are relative; the single maintainer assigns calendar dates.

## Timeline Overview

```text
Phase 0: Foundation        ███░░░░░░░░░░░░░░ (~1 wk)  - scaffold, schema, DB roles, CI
Phase 1: Ingestion Backbone░░░██████░░░░░░░░ (~3 wks) - sources, tagging, versioned rules
Phase 2: Scorecard + API   ░░░░░░░░██████░░░ (~3 wks) - rules, power, bracket, manabase
Phase 3: Suggestions + UI  ░░░░░░░░░░░░██████ (~3 wks) - ranker, collection, price, frontend
Phase 4: Quality/Release   ░░░░░░░░░░░░░░░░██ (~1 wk)  - eval harness, hardening
```

## Milestones

| Milestone | Target | Status | Dependencies |
|---|---|---|---|
| M0: Foundation ready | End Wk 1 | Planned | None |
| M1: Ingestion serving data | End Wk 4 | Planned | M0 |
| M2: Scorecard + review API | End Wk 7 | Planned | M1 |
| M3: Suggestions + collection + UI | End Wk 10 | Planned | M2 |
| M4: Quality + release | End Wk 11 | Planned | M3 |

---

## Phase 0: Foundation (~Week 1)

### Objective

Stand up the two-service skeleton, the shared schema package, and the database
with its single-writer roles. See
[adr-001-initial-architecture.md](./adr/adr-001-initial-architecture.md).

### Deliverables

- [ ] `mtg_ai_schema` package (SQLAlchemy models + Alembic, data-owned schema)
- [ ] Postgres via Docker Compose; data-service writer role and app-service
      restricted role (SELECT on data tables, DML on app tables)
- [ ] App and data service skeletons (FastAPI app; data CLI entrypoint)
- [ ] Auth: `User` model, password hashing (PBKDF2/argon2), session tokens,
      `POST /auth/login`; app routes scoped by `user_id`
- [ ] CI green on main (Ruff, BasedPyright, pytest, security scans)

### Success Criteria

- Clone to running stack via `docker-compose up` in < 15 minutes.
- App-service role provably cannot write data-owned tables.
- Two Alembic lineages run without colliding (`version_table` per domain).

---

## Phase 1: Ingestion Backbone (~Weeks 2-4)

### Objective

Populate the layered data model from reused datasets so the scorecard has
something to score. Ingestion is idempotent and degrades, not breaks. See
[adr-002-data-model.md](./adr/adr-002-data-model.md).

### Deliverables

- [ ] Landing layer: raw immutable source JSON with provenance
- [ ] `ingestion/scryfall`: cards, `mana_cost`, `color_identity`, legalities,
      prices (upsert by `oracle_id`); `oracle_id` crosswalk + name overrides
- [ ] `ingestion/mtgjson`: commander-legal flag, preconstructed decks
- [ ] `ingestion/edhrec`: synergy, inclusion, lift, theme/role buckets
- [ ] `ingestion/spellbook`: combos and bracket estimate
- [ ] `reference_config`: versioned, effective-dated Game Changers + bracket rules
- [ ] `scheduler` + `IngestReport` per run; CLI: `mtg-ai sync cards`,
      `sync edhrec`, `sync rules`

### Success Criteria

- A full sync upserts the card corpus; reruns are idempotent.
- A source schema/HTML change fails loudly into `IngestReport` (Pydantic
  boundary), never writing garbage; unresolved names are logged.
- Coverage: ingestion 80%+ with recorded fixtures (no live network in tests).

### Dependencies

- Requires: M0. Blocks: Phase 2 scoring.

---

## Phase 2: Scorecard and Review API (~Weeks 5-7)

### Objective

Compute a trustworthy, reproducible deck scorecard behind an authenticated API.
See [adr-003-engine-approach.md](./adr/adr-003-engine-approach.md).

### Deliverables

- [ ] Eval harness scaffold: known decks with expected scores, used to tune the
      scorecard during development (promoted to a CI regression gate in Phase 4)
- [ ] `decks/import`: Arena/MTGO/text parse + commander detection
      (Partner/Background; compute `Deck.color_identity`); exact-match resolution
      first, fuzzy resolution as a refinement
- [ ] `rules`: deterministic legality/identity gate (TDD, property-based)
- [ ] `scorecard`: functional power (Disciple-of-the-Vault), bracket placement
      (gate logic over versioned Game Changers), role coverage vs archetype
      targets, Karsten manabase check
- [ ] `POST /decks/{id}/review`: returns the scorecard only and persists
      `DeckReview` with `rules_version` (suggestions/collection added in Phase 3)

### Success Criteria

- Identical inputs and rules-version yield identical scorecards.
- More than 95% of cards auto-resolve on import; unresolved are surfaced, not guessed.
- Bracket agreement >= 90% vs Commander Spellbook `estimate-bracket` on a labeled
  set; review API p95 < 5s; cross-user access denied.

### Dependencies

- Requires: M1 (data to score). Blocks: Phase 3.

---

## Phase 3: Suggestions, Collection, and Frontend (~Weeks 8-10)

### Objective

Turn the scorecard into ranked upgrade suggestions, add collection ownership and
price as soft annotations, and put a usable UI on it.

### Deliverables

- [ ] `suggestions`: cuts/adds from role gaps and bracket mismatches, ranked by
      synergy and lift, each re-validated against `rules`; expand the
      `POST /decks/{id}/review` payload to include suggestions and accept the
      optional `collection_id`
- [ ] `collection/import`: import owned cards to `oracle_id`; annotate suggestions
      with `owned` and `price`; value-per-dollar sorting (soft, no hard filter)
- [ ] `generator`: LLM explanation of scorecard and suggestions (explanation only)
- [ ] Frontend: import, collection, and review views with accept/reject controls
- [ ] `POST /reviews/{id}/feedback` wired to persist accept/reject labels
- [ ] One Playwright happy-path e2e: import -> review -> feedback

### Success Criteria

- Every suggested add passes legality re-validation (100%).
- Suggestions show ownership and price and sort by value-per-dollar.
- Disabling the LLM still returns a complete scorecard and suggestions.

### Dependencies

- Requires: M2 (scorecard + API). Blocks: Phase 4.

---

## Phase 4: Quality and Release (~Week 11)

### Objective

Prove review quality, guard LLM cost, harden, and ship.

### Deliverables

- [ ] Promote the Phase 2 eval harness to a CI regression gate on review quality
- [ ] Per-user rate limit + LLM cost guard; structured JSON logging
- [ ] Coverage >= 80% overall, 90% on `rules` and `scorecard`; security review clean
- [ ] Deploy guide; CHANGELOG and README updated

### Success Criteria

- Eval harness runs and flags review-quality regressions.
- No high/critical security findings; secrets never logged or committed.
- Release tagged per SemVer with an updated CHANGELOG.

---

## Future Phases (Deferred)

- **v2 embeddings / RAG**: pgvector + card2vec on Commander decklists for
  relationship discovery beyond per-commander synergy.
- **Standard track**: empirical payoff matrix, Nash mixtures, win-rate predictor,
  Forge simulation, BO1/BO3 partitioning (the data model partitions by `format`).
- **Hard budget filter** (drop adds over a count or dollar cap) and **deck
  generation from a commander**.

## Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| EDHREC terms/availability change | M | H | Polite cache; provenance; degrade to stale; revisit if public |
| Bracket rules drift (beta) | H | M | Versioned, effective-dated config; review records `rules_version` |
| Functional-tag reliability | M | M | Reuse EDHREC/Scryfall tags; hand-correct edges; flag low-confidence |
| Card resolution edge cases (DFC/split) | M | M | Crosswalk + override table; surface unresolved, never guess |
| LLM cost/latency | L | M | Explanation is optional and off the hot path; rate + cost guard |
| Solo capacity slip | M | M | Phases independently shippable; cut Phase 4 scope first |

## Definition of Done

A feature is complete when:

- [ ] Code reviewed; tests written and passing
- [ ] Coverage meets target; Ruff + BasedPyright clean
- [ ] Documentation updated; no high/critical security findings
- [ ] Merged to main via signed conventional commit

## Related Documents

- [Project Vision](./project-vision.md)
- [Technical Spec](./tech-spec.md)
- [Architecture Decisions](./adr/README.md)
