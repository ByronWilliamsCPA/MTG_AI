---
schema_type: planning
title: "MTG AI - Project Plan"
description: "Synthesized project plan for MTG AI with phased implementation roadmap, architecture overview, and git branch strategy"
tags:
  - planning
  - roadmap
  - project
  - strategy
status: published
owner: "core-maintainer"
authors:
  - name: "Byron Williams"
purpose: "Single source of truth for MTG AI implementation: phases, branches, acceptance criteria, quality gates, and task breakdowns"
component: "Strategy"
source: "Synthesized from project-vision.md, tech-spec.md, roadmap.md, adr-001..003 (2026-06-01); amended for adr-004..006 (2026-06-08)"
---

> **Status**: Active | **Version**: 1.1 | **Updated**: 2026-06-08
>
> Synthesized from:
> [project-vision.md](./project-vision.md),
> [tech-spec.md](./tech-spec.md),
> [roadmap.md](./roadmap.md),
> [ADR-001](./adr/adr-001-initial-architecture.md),
> [ADR-002](./adr/adr-002-data-model.md),
> [ADR-003](./adr/adr-003-engine-approach.md),
> [ADR-004](./adr/adr-004-multi-lens-critique-reviewers.md),
> [ADR-005](./adr/adr-005-archetype-critique-spines.md),
> [ADR-006](./adr/adr-006-compounding-learnings-log.md)
>
> **v1.1 amendment (2026-06-08)**: ADR-004/005/006 accepted after a multi-lens
> panel review and threaded into the phases below. ADR-005 and ADR-006 are
> deliberately scoped down for v1 (one archetype spine + override; capture-only
> learnings log) to bound solo-maintainer cost.

**Project**: MTG AI
**Repository**: https://github.com/ByronWilliamsCPA/MTG_AI
**Start Date**: 2026-06-01
**Target Completion**: ~Week 11 from start (single-maintainer pace)

---

## Executive Summary

MTG AI is a self-hosted assistant that reviews and upgrades Commander decks across all
power brackets (casual through cEDH, brackets 1-5). A player imports a decklist and
receives a trustworthy, bracket-aware scorecard computed deterministically from reused
precomputed datasets (EDHREC, Commander Spellbook, Scryfall, MTGJSON), plus ranked,
legality-correct upgrade suggestions annotated with what the player already owns and
what each addition costs.

**Key Innovation**: Card legality, bracket placement, and scoring are never delegated
to a language model. The LLM is explanation-only behind a swappable generator interface,
so correctness is guaranteed regardless of model availability or quality.

**Expected Outcomes**:

- A locally runnable deck-critique tool a small Commander playgroup can self-host on a
  single box via Docker Compose.
- Deterministic, reproducible scorecards that agree with Commander Spellbook bracket
  estimates at >= 90%.
- Ranked upgrade suggestions that are 100% legality-correct by construction.

**Success Metrics** (from [project-vision.md](./project-vision.md)):

- Suggested-add legality: 100% (deterministically enforced; illegal adds never reach
  the user).
- Decklist import resolution: > 95% auto-resolved; remainder surfaced for manual
  confirmation, never silently guessed.
- Bracket placement agreement: >= 90% vs Commander Spellbook `estimate-bracket` on a
  labeled deck set.
- Scorecard reproducibility: identical inputs and rules-version yield identical scores
  (effective-dated reference data).
- Review latency (p95): < 5s (database lookups and deterministic math, no LLM on the
  hot path).

---

## Scope

### In Scope

- Commander format, brackets 1-5 (casual through cEDH).
- Decklist and collection import (Arena/MTGO/text; Partner/Background commander
  detection; `oracle_id` resolution).
- Deterministic review scorecard: legality/identity gate, functional power
  (Disciple-of-the-Vault 1-10), WotC bracket placement (gate logic + versioned Game
  Changers list), role coverage vs archetype targets, Karsten manabase check, synergy
  and lift reported separately.
- Ranked upgrade suggestions: cuts and adds, re-validated for legality, annotated with
  ownership and price for value-per-dollar sorting. Collection ownership and price are
  soft annotations only.
- Reuse-first ingestion: EDHREC, Commander Spellbook, Scryfall, MTGJSON, Game Changers
  as refreshable versioned config.
- Plain-language explanation via a swappable LLM generator (no scoring authority).
- Light per-user accounts and session tokens (no SSO/OAuth).

### Out of Scope / Deferred

- **Standard format track**: empirical metagame engine, win-rate model, simulation.
  Deferred; the data model anticipates it via `format` partitioning.
- **Embeddings / RAG / pgvector / card2vec**: v2 enhancement, not a v1 dependency.
  See [ADR-003](./adr/adr-003-engine-approach.md).
- **Hard budget filter**: a count or dollar cap that drops suggestions. Deferred; v1
  is soft annotation and value-per-dollar ranking only.
- **Full deck generation from a commander**: later workflow.
- **Public multi-tenant SaaS, billing, large-scale load**: not planned.
- **Fine-tuning a generation model**: not planned.

---

## Architecture Overview

The architecture is recorded in three ADRs. Key decisions and rationale are summarized
below; refer to the ADRs for full context, options considered, and consequences.

### ADR-001: Split-Service Architecture with a Shared Single-Writer Database

**Decision**: Two deployable services (app + data) sharing one Postgres database under a
single-writer rule. The data service is the only writer of reference, corpus, and
analytics tables. The app service connects with a restricted role: `SELECT` on those
tables, full DML on its own tables (users, decks, collections, reviews). Services never
call each other synchronously.

**Rationale**: Isolates heavy scheduled ingestion from the latency-sensitive review path
without a synchronous inter-service API to build or version. One relational store lets a
single SQL query combine color-identity filtering with synergy/meta scores.

Reference: [adr-001-initial-architecture.md](./adr/adr-001-initial-architecture.md)

### ADR-002: Layered Data Model with Reuse-First Ingestion

**Decision**: A layered relational model (Landing, Reference, Corpus, Analytics,
Application) keyed to the Scryfall `oracle_id`. All foreign identifiers (MTGJSON,
Spellbook, EDHREC, Arena, MTGO, normalized name) resolve through an `IdentifierXref`
crosswalk. Effective dates on bracket definitions and the Game Changers list make
reviews reproducible. Provenance (source, URL, `ingested_at`, license) on every
ingested row.

**Rationale**: Matches data's natural volatility tiers; relational joins serve color,
role, and meta filters; effective dates make a beta rules system reproducible; reuse
over rebuild minimizes new code.

Reference: [adr-002-data-model.md](./adr/adr-002-data-model.md)

### ADR-003: Deterministic Scorecard Engine, LLM for Explanation

**Decision**: The v1 engine is deterministic: legality/identity gate, functional power
(Disciple-of-the-Vault 1-10), bracket gate logic over the versioned Game Changers list,
role coverage vs archetype targets, Karsten manabase check (using `Card.mana_cost` pips
and land `Card.produced_mana`). The LLM is explanation-only behind a swappable
`Generator` interface. Embeddings and RAG are deferred to v2.

**Rationale**: Authoritative signals (synergy, lift, combos, bracket estimate) already
exist as precomputed data. Determinism guarantees correctness and reproducibility;
bounding the LLM to explanation keeps it off the correctness path and bounds cost.

Reference: [adr-003-engine-approach.md](./adr/adr-003-engine-approach.md)

### ADR-004/005/006: Critique Structure, Archetype Spines, and the Learnings Loop

**Decision**: Three accepted refinements of the deterministic engine, all behind
the ADR-003 boundary (the LLM still only explains). (004) The scorecard is built
as independent, category-owning **lenses** over one app-owned, versioned
`DeckSnapshot`, aggregated by a gate; lenses are pure functions and run
sequentially in v1. (005) Lenses read **archetype spines** (role targets,
thresholds, weights) as effective-dated, data-owned config; v1 ships a single
generic-midrange spine plus a user override, deferring the deterministic
classifier and additional spines. (006) Flagged reviews append to an **app-owned,
user-scoped learnings log** referencing the reproducing snapshot; v1 captures
entries, while triage into checks/fixtures and the CI-regression meta-test land
in Phase 4.

**Rationale**: Attributable lenses remove single-pass blind spots and parallelize
later for free; archetype-as-data stops the engine from scoring every deck against
one mean; the learnings log makes review quality compound. The v1 scope-downs keep
the architectural seams (snapshot, spine-as-config, app-owned log) while bounding
solo-maintainer cost. The snapshot carries the full version vector
(`rules_version`, `spine_version`, `archetype`, `classifier_version`) so reviews
stay reproducible.

References: [adr-004](./adr/adr-004-multi-lens-critique-reviewers.md),
[adr-005](./adr/adr-005-archetype-critique-spines.md),
[adr-006](./adr/adr-006-compounding-learnings-log.md)

---

## Technology Stack

Source: [tech-spec.md](./tech-spec.md)

### Core

| Layer | Technology |
|---|---|
| Backend language | Python 3.12 |
| Frontend language | TypeScript 5.x |
| Package manager | UV |
| Backend framework | FastAPI; Pydantic v2 at every ingestion boundary |
| Frontend | React 18 + Vite |
| Database | Postgres 16 (relational-first; pgvector deferred to v2) |
| ORM / migrations | SQLAlchemy 2.x + Alembic (per-domain `version_table`) |
| Containerization | Docker Compose (frontend, app service, data service, Postgres) |
| CI/CD | GitHub Actions |
| LLM backend | Swappable `Generator` interface (e.g. Claude); explanation-only |

### Code Quality

| Tool | Configuration |
|---|---|
| Linter/Formatter | Ruff (88 chars, PyStrict-aligned) |
| Type checker | BasedPyright (strict) |
| Backend testing | pytest, Hypothesis (property-based), testcontainers |
| Frontend testing | Vitest + Playwright |

### Reused Data Sources

| Source | Provides | License/Terms |
|---|---|---|
| Scryfall (bulk) | Card inventory, `color_identity`, legalities, prices | Free, attribution, rate-limited |
| MTGJSON | Commander-legal flag, preconstructed decks, prices | MIT |
| EDHREC (JSON) | Synergy, inclusion, lift, theme/role buckets | No open license; polite cache, no redistribute |
| Commander Spellbook | Combos, `find-my-combos`, `estimate-bracket` | MIT |
| WotC (Scryfall `is:gamechanger`) | Game Changers list, bracket rules | Versioned config, refresh quarterly |

---

## Review Pipeline

The six-step pipeline is the central workflow of the application:

1. `decks/import` parses the decklist, detects commander(s) (including
   Partner/Background), resolves to `oracle_id` (unresolved names surfaced, never
   guessed), and computes `Deck.color_identity`.
2. `rules` runs the deterministic legality/identity gate (color identity, singleton,
   banlist, commander-legal).
3. `scorecard` computes functional power, bracket placement (gate logic over versioned
   Game Changers), role coverage vs archetype targets, and a Karsten manabase check
   using `Card.mana_cost` pips and land `Card.produced_mana`. Synergy and average lift
   are reported separately.
4. `suggestions` proposes cuts (off-curve, low-synergy, bracket-violating) and adds
   (underfilled roles), ranked by commander synergy and lift, re-validates each add
   against `rules`, annotates `owned` and `price`.
5. `generator` turns the scorecard and suggestions into plain-language rationale
   (explanation only; cannot alter any score, legality verdict, or bracket).
6. Persist `DeckReview` + `ReviewSuggestion` (with `rules_version`); frontend renders
   the scorecard with accept/reject controls and value-per-dollar sorting.

---

## Quality Gate Thresholds

Every phase must satisfy all gates before its branch is merged. Thresholds apply
uniformly unless a phase section notes a tighter path-specific target.

| Gate | Threshold | Tool |
|---|---|---|
| Line coverage (overall) | >= 80% | pytest-cov |
| Branch coverage (overall) | >= 70% | pytest-cov |
| Critical-path coverage (`rules`, `scorecard`) | >= 90% | pytest-cov |
| Patch coverage (new code in PR) | >= 90% | Codecov / pytest-cov |
| Linting | 0 errors | Ruff (check + format) |
| Type checking | 0 errors | BasedPyright strict |
| Security (SAST) | No high/critical | Bandit |
| Dependency audit | Clean | pip-audit |
| Pre-commit hooks | All pass | pre-commit run --all-files |
| Signed commits | Required | GPG (`git commit -S`) |

---

## Phased Development

### Timeline Overview

| Phase | Branch | Duration | Focus | Milestone |
|---|---|---|---|---|
| 0 | `chore/phase-0-foundation` | ~Week 1 | Scaffold, schema, DB roles, CI | M0 |
| 1 | `feat/phase-1-ingestion-backbone` | ~Weeks 2-4 | Sources, tagging, versioned rules | M1 |
| 2 | `feat/phase-2-scorecard-api` | ~Weeks 5-7 | Rules, power, bracket, manabase | M2 |
| 3 | `feat/phase-3-suggestions-ui` | ~Weeks 8-10 | Ranker, collection, price, frontend | M3 |
| 4 | `chore/phase-4-quality-release` | ~Week 11 | Eval harness, hardening, ship | M4 |

### Git Branch Strategy

Branches follow the convention in `.claude/rules/git-workflow.md`:
`{type}/phase-{N}-{description}`

- Phase 0 is infrastructure setup: `chore/`
- Phases 1, 2, and 3 deliver new features: `feat/`
- Phase 4 is quality hardening and release prep: `chore/`

Start each phase with:

```bash
git checkout main && git pull origin main
git checkout -b {branch-name}
# or with a worktree:
git worktree add .worktrees/{branch-slug} -b {branch-name}
```

---

### Phase 0: Foundation (~Week 1)

**Branch**: `chore/phase-0-foundation`
**Milestone**: M0 (end Week 1)
**Dependencies**: None

#### Goal

Stand up the two-service skeleton, the shared schema package, and the database with its
single-writer roles so that all subsequent phases have a running, tested foundation to
build on. See [ADR-001](./adr/adr-001-initial-architecture.md).

#### Deliverables

Traced to [roadmap.md Phase 0 deliverables](./roadmap.md):

- `mtg_ai_schema` package: SQLAlchemy models + Alembic migrations for data-owned tables.
- Postgres via Docker Compose with the two database roles: data-service writer role and
  app-service restricted role (`SELECT` on data tables, full DML on app tables).
- App service skeleton (FastAPI; `GET /api/v1/health`).
- Data service skeleton (Click CLI entrypoint).
- Auth: `User` model, PBKDF2/argon2 password hashing (FIPS-safe; bcrypt is prohibited),
  session tokens, `POST /api/v1/auth/login`, all routes scoped by `user_id`.
- CI green on main: Ruff, BasedPyright, pytest, Bandit, pip-audit.

#### Acceptance Criteria

From [roadmap.md](./roadmap.md):

- Clone to running stack via `docker-compose up` in < 15 minutes.
- App-service role provably cannot write data-owned tables (integration test, not just
  configuration assertion).
- Two Alembic lineages run without colliding (each domain uses its own schema and
  `version_table`).

#### Quality Gates

All thresholds from the [Quality Gate Thresholds](#quality-gate-thresholds) section.
Coverage target for this phase is >= 80% line; critical-path code does not yet exist.

#### Task Breakdown

```text
[ ] Verify Docker Compose: Postgres, app-service, data-service containers start.
[ ] Create `mtg_ai_schema` package with SQLAlchemy 2.x base and Alembic config.
[ ] Define data-service Alembic lineage (schema + version_table).
[ ] Create app-service Alembic lineage (separate schema + version_table).
[ ] Write database role grants: data-service writer; app-service restricted.
[ ] Integration test: assert app role cannot INSERT/UPDATE data-owned tables.
[ ] Implement `User` model, PBKDF2/argon2 hashing, session token issuance.
[ ] Implement `POST /api/v1/auth/login` and `GET /api/v1/health`.
[ ] Scope all app routes by `user_id`; write cross-user access denial test.
[ ] Click CLI skeleton with `mtg-ai --help` functioning.
[ ] GitHub Actions CI: Ruff, BasedPyright, pytest, Bandit, pip-audit, pre-commit.
[ ] Verify CI green on branch before merge.
```

---

### Phase 1: Ingestion Backbone (~Weeks 2-4)

**Branch**: `feat/phase-1-ingestion-backbone`
**Milestone**: M1 (end Week 4)
**Dependencies**: M0 (Phase 0 complete)

#### Goal

Populate the layered data model from reused datasets so the Phase 2 scorecard has
data to score. Ingestion is idempotent and degrades, not breaks. See
[ADR-002](./adr/adr-002-data-model.md).

#### Deliverables

Traced to [roadmap.md Phase 1 deliverables](./roadmap.md):

- Landing layer: `LandingDump` table; raw, immutable, timestamped source JSON with
  provenance (source, url, `ingested_at`, license).
- `ingestion/scryfall`: upsert cards by `oracle_id`; populate `Card.mana_cost`,
  `Card.produced_mana`, `Card.color_identity`, legalities, prices; build
  `IdentifierXref` crosswalk and name-override table.
- `ingestion/mtgjson`: commander-legal flag, preconstructed decks.
- `ingestion/edhrec`: `CommanderSynergy` (synergy, inclusion, lift), `CardRole`
  (theme/role buckets). Polite cache; no redistribution.
- `ingestion/spellbook`: combos (`CardCombo`), bracket estimate reference data.
- `reference_config`: versioned, effective-dated `GameChanger` and `BracketDef` records;
  refreshable independent of card data. Includes the effective-dated **archetype
  spine** schema with one seeded generic-midrange spine (ADR-005, data-owned).
- `scheduler` with set-release vs daily cadence; `IngestReport` per run.
- CLI commands: `mtg-ai sync cards`, `mtg-ai sync edhrec`, `mtg-ai sync rules`.

#### Acceptance Criteria

From [roadmap.md](./roadmap.md):

- A full sync upserts the card corpus; reruns are idempotent (no duplicate facts).
- A source schema/HTML change fails loudly into `IngestReport` (Pydantic boundary
  validation), never writing garbage; unresolved names are logged.
- Coverage: ingestion >= 80% with recorded fixtures (no live network in tests).

#### Quality Gates

All thresholds from [Quality Gate Thresholds](#quality-gate-thresholds).

Additional ingestion-specific gate: Pydantic boundary tests use recorded source
fixtures; the test suite must not make live network calls.

#### Task Breakdown

```text
[ ] Define Landing layer model (`LandingDump`) and Alembic migration.
[ ] Implement `ingestion/scryfall`: fetch bulk JSON, parse, upsert by oracle_id.
[ ] Populate Card.mana_cost and Card.produced_mana from Scryfall card objects.
[ ] Build IdentifierXref crosswalk (mtgjson/edhrec/arena/mtgo/name).
[ ] Implement name-override table for DFC, split, adventure, and token cards.
[ ] Implement `ingestion/mtgjson`: commander-legal flag, preconstructed decks.
[ ] Implement `ingestion/edhrec`: CommanderSynergy, CardRole (polite-cache only).
[ ] Implement `ingestion/spellbook`: combo table, bracket estimate reference.
[ ] Implement `reference_config`: GameChanger and BracketDef with effective dates.
[ ] Implement `scheduler` with set-release vs daily cadence; IngestReport per run.
[ ] Wire CLI: `mtg-ai sync cards`, `sync edhrec`, `sync rules`.
[ ] Record source fixtures for each ingestion target (no live network in tests).
[ ] Write Pydantic boundary tests: assert schema drift is rejected and logged.
[ ] Write idempotency tests: run ingest twice, assert no duplicate rows.
[ ] Verify coverage >= 80% on all ingestion paths.
[ ] Verify all quality gates pass before merge.
```

---

### Phase 2: Scorecard and Review API (~Weeks 5-7)

**Branch**: `feat/phase-2-scorecard-api`
**Milestone**: M2 (end Week 7)
**Dependencies**: M1 (ingestion serving data)

#### Goal

Compute a trustworthy, reproducible deck scorecard behind an authenticated API. This
is the core correctness layer of the system. See
[ADR-003](./adr/adr-003-engine-approach.md).

#### Deliverables

Traced to [roadmap.md Phase 2 deliverables](./roadmap.md):

- Eval harness scaffold: known decks with expected scores, used to tune the scorecard
  during development (promoted to a CI regression gate in Phase 4).
- `decks/import`: Arena/MTGO/text parse; commander detection (Partner/Background;
  computes `Deck.color_identity`); exact-match resolution first, fuzzy as a refinement;
  unresolved names surfaced, never guessed.
- `rules`: deterministic legality/identity gate. Developed with TDD and property-based
  tests (Hypothesis). No LLM involvement.
- `scorecard` built as independent, category-owning **lenses** (legality/identity,
  power/bracket, consistency/manabase, interaction/role, wincon/combo) over one
  `DeckSnapshot`, composed by an **aggregator** that enforces the legality gate
  first (ADR-004): functional power (Disciple-of-the-Vault 1-10); bracket placement
  (gate logic over versioned Game Changers); role coverage vs the resolved archetype
  spine (ADR-005, generic-midrange or user override in v1); Karsten manabase check
  using `Card.mana_cost` pips and land `Card.produced_mana`. Synergy and average lift
  reported separately, never blended into the power score. Lenses run sequentially.
- `DeckSnapshot`: app-owned, persisted resolved-deck artifact carrying the version
  vector (`rules_version`, `spine_version`, `archetype`, `classifier_version`); the
  shared reproducibility contract for scoring and the Phase 3 learnings log.
- `POST /api/v1/decks/import` and `GET /api/v1/decks/{id}` (owner only).
- `POST /api/v1/decks/{id}/review`: returns scorecard only; persists `DeckReview`
  with the `DeckSnapshot` and `rules_version`; suggestions and collection added in
  Phase 3.

#### Acceptance Criteria

From [roadmap.md](./roadmap.md):

- Identical inputs and rules-version yield identical scorecards.
- More than 95% of cards auto-resolve on import; unresolved are surfaced, not guessed.
- Bracket agreement >= 90% vs Commander Spellbook `estimate-bracket` on a labeled set.
- Review API p95 < 5s.
- Cross-user access denied and tested.

#### Quality Gates

All thresholds from [Quality Gate Thresholds](#quality-gate-thresholds), plus:

- `rules` module: >= 90% line coverage (critical path).
- `scorecard` module: >= 90% line coverage (critical path).
- Property-based tests (Hypothesis) must pass for `rules` legality gate.
- Golden deck tests must pass for `scorecard`.
- Mock the `Generator` interface; assert it cannot alter any score or legality verdict.

#### Task Breakdown

```text
[ ] Scaffold eval harness: load known decks with expected score fixtures.
[ ] Implement `decks/import`: Arena/MTGO/text parser and commander detection.
[ ] Implement Partner/Background pair detection; compute Deck.color_identity.
[ ] Implement exact-match oracle_id resolution; fuzzy fallback; override table.
[ ] Surface unresolved names in API response; assert no silent guess.
[ ] Implement `rules` legality/identity gate (TDD; property-based with Hypothesis).
[ ] Write property tests: all color-identity violations are caught; all banlisted
    cards are caught; all non-commander cards as commander are caught.
[ ] Implement `scorecard` power module (Disciple-of-the-Vault; weights in
    versioned reference_config).
[ ] Implement bracket placement via gate logic over GameChanger/BracketDef tables.
[ ] Implement role coverage check vs archetype targets from CardRole.
[ ] Implement Karsten manabase check using Card.mana_cost and Card.produced_mana.
[ ] Report CommanderSynergy and avg CardPairLift separately (not blended).
[ ] Implement POST /api/v1/decks/import and GET /api/v1/decks/{id}.
[ ] Implement POST /api/v1/decks/{id}/review (scorecard only, persists DeckReview
    with rules_version; suggestions deferred to Phase 3).
[ ] Add cross-user access denial test on each route.
[ ] Verify review API p95 < 5s in testcontainers integration test.
[ ] Run eval harness on labeled deck set; verify bracket agreement >= 90%.
[ ] Verify rules >= 90% line coverage; scorecard >= 90% line coverage.
[ ] Verify all quality gates pass before merge.
```

---

### Phase 3: Suggestions, Collection, and Frontend (~Weeks 8-10)

**Branch**: `feat/phase-3-suggestions-ui`
**Milestone**: M3 (end Week 10)
**Dependencies**: M2 (scorecard + review API)

#### Goal

Turn the Phase 2 scorecard into ranked upgrade suggestions, add collection ownership
and price as soft annotations, wire the LLM explanation layer, and put a usable
frontend on the full pipeline.

#### Deliverables

Traced to [roadmap.md Phase 3 deliverables](./roadmap.md):

- `suggestions`: cuts (off-curve, low-synergy, bracket-violating) and adds
  (underfilled roles), ranked by commander synergy and lift; each proposed add
  re-validated against `rules` and dropped if illegal; expand
  `POST /api/v1/decks/{id}/review` payload to include suggestions and accept an
  optional `collection_id`.
- `collection/import`: import owned cards to `oracle_id`; `POST /api/v1/collections/import`.
  Annotate suggestions with `owned` (bool) and `price` (Decimal, advisory); value-per-dollar
  sorting. Soft annotation only; no hard budget filter.
- `generator`: swappable LLM `Generator` interface; plain-language explanation of
  scorecard and suggestions; no scoring authority; disabling it returns a complete
  response without prose.
- Frontend: React 18 + Vite; import view, collection view, and review view with
  accept/reject controls and value-per-dollar sort.
- `POST /api/v1/reviews/{id}/feedback`: persist accept/reject labels and a
  `flagged` field/reason. A flagged review appends an entry to the app-owned,
  user-scoped **learnings log** referencing the `DeckSnapshot` (ADR-006, capture
  only; triage deferred to Phase 4).
- One Playwright happy-path e2e: import deck -> review -> feedback.

#### Acceptance Criteria

From [roadmap.md](./roadmap.md):

- Every suggested add passes legality re-validation (100%).
- Suggestions show ownership and price; sort by value-per-dollar works.
- Disabling the LLM still returns a complete scorecard and suggestions (no prose is
  acceptable; empty rationale is acceptable).

#### Quality Gates

All thresholds from [Quality Gate Thresholds](#quality-gate-thresholds), plus:

- `suggestions` re-validation: integration test asserts 0 illegal adds reach the
  response across a representative fixture set.
- `generator` interface test: mock the LLM; assert the generator cannot alter any
  score, legality verdict, or bracket in the response.
- Playwright e2e happy-path must pass in CI.

#### Task Breakdown

```text
[ ] Implement `suggestions` ranker: query role gaps and bracket mismatches from
    scorecard; rank by CommanderSynergy.synergy_score and CardPairLift.lift.
[ ] Re-validate every proposed add through `rules`; drop illegal ones; never
    surface an illegal suggestion.
[ ] Extend POST /api/v1/decks/{id}/review payload to include suggestions and
    accept optional collection_id in request body.
[ ] Implement `collection/import`: parse owned-card list; upsert CollectionCard
    by oracle_id.
[ ] Implement POST /api/v1/collections/import.
[ ] Annotate suggestions with owned=True/False from CollectionCard lookup.
[ ] Populate ReviewSuggestion.price from CardPrice (advisory; stale after ~24h).
[ ] Implement value-per-dollar sort (score / price where price > 0).
[ ] Implement `generator` swappable interface; wire to LLM (e.g. Claude API).
[ ] Assert generator cannot mutate scores, legality, or bracket in tests.
[ ] Assert disabling the generator returns complete scorecard + suggestions.
[ ] Implement POST /api/v1/reviews/{id}/feedback (persist accept/reject labels).
[ ] Scaffold React + Vite frontend; import view.
[ ] Implement collection import view.
[ ] Implement review view: scorecard, suggestions, accept/reject controls,
    value-per-dollar sort toggle.
[ ] Write Playwright e2e: import -> review -> feedback happy path.
[ ] Confirm 0 illegal suggested adds across fixture set (integration gate).
[ ] Verify all quality gates pass before merge.
```

---

### Phase 4: Quality and Release (~Week 11)

**Branch**: `chore/phase-4-quality-release`
**Milestone**: M4 (end Week 11)
**Dependencies**: M3 (suggestions + collection + UI)

#### Goal

Prove review quality, guard LLM cost, harden the system, and ship a versioned
release.

#### Deliverables

Traced to [roadmap.md Phase 4 deliverables](./roadmap.md):

- Promote the Phase 2 eval harness to a CI regression gate on review quality:
  known decks with expected cuts/adds run on every CI build.
- Learnings-log **triage workflow** (ADR-006): convert each captured entry into a
  lens check or a golden regression fixture; a meta-test asserts no entry sits
  captured-but-unresolved beyond a grace window. This backlog-policing test is
  gated to Phase 4 so it never blocks CI in earlier phases.
- Per-user rate limit and LLM cost guard.
- Structured JSON logging with correlation IDs; secrets never logged.
- Coverage >= 80% overall, >= 90% on `rules` and `scorecard`; security review clean.
- Deploy guide (Docker Compose single-box); CHANGELOG and README updated.
- Release tagged per SemVer with an updated CHANGELOG.

#### Acceptance Criteria

From [roadmap.md](./roadmap.md):

- Eval harness runs in CI and flags review-quality regressions.
- No high/critical security findings (Bandit, pip-audit); secrets never logged or
  committed.
- Release tagged per SemVer with an updated CHANGELOG.

#### Quality Gates

All thresholds from [Quality Gate Thresholds](#quality-gate-thresholds). This phase
must also satisfy:

- Eval harness passes in CI (quality regression gate).
- Per-user rate limit tested: requests above the limit return 429.
- LLM cost guard tested: a request that would exceed the configured token budget is
  rejected before calling the LLM.
- Deploy guide reviewed: a fresh `docker-compose up` from the guide succeeds.

#### Task Breakdown

```text
[ ] Promote eval harness to CI job: runs on every push to main; blocks merge on
    regression.
[ ] Implement per-user rate limiter (requests per window) at the API layer.
[ ] Implement LLM cost guard: token budget per request or per user per day;
    reject calls that would exceed it before sending to the LLM API.
[ ] Audit structured JSON logging: assert no API keys, passwords, or secrets appear
    in any log fixture.
[ ] Run pip-audit and Bandit; resolve or document any high/critical findings in
    docs/known-vulnerabilities.md per the global CLAUDE.md template.
[ ] Confirm overall coverage >= 80%; rules and scorecard paths >= 90%.
[ ] Write deploy guide: single-box Docker Compose setup from scratch in < 15 min.
[ ] Update CHANGELOG with all phase deliverables.
[ ] Update README with quick-start and feature summary.
[ ] Tag v1.0.0 (SemVer) with a signed commit; create GitHub release.
[ ] Verify all quality gates pass before merge.
```

---

## Risk Register

From [roadmap.md](./roadmap.md) and cross-referenced with [project-vision.md](./project-vision.md):

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| EDHREC terms or availability change | Medium | High | Polite cache; provenance on every row; degrade to stale data; revisit if the app ever becomes public |
| Bracket rules drift (WotC system is beta) | High | Medium | Versioned, effective-dated `GameChanger` and `BracketDef`; every review records `rules_version` used |
| Functional-tag reliability (CardRole) | Medium | Medium | Reuse EDHREC/Scryfall tags; hand-correct edges; flag low-confidence tags |
| Card resolution edge cases (DFC, split, adventure, token) | Medium | Medium | `IdentifierXref` crosswalk + name-override table; surface unresolved, never guess |
| LLM cost or latency spike | Low | Medium | Explanation is optional and off the correctness path; per-user rate limit and cost guard (Phase 4) |
| Solo maintainer capacity slip | Medium | Medium | Phases are independently shippable; cut Phase 4 scope (docs, not gates) before cutting quality gates |
| EDHREC polite-cache assumption (private only) | Low | High | Verified before any public release; assumption tagged in [project-vision.md](./project-vision.md) |

---

## Success Metrics

From [project-vision.md](./project-vision.md):

| Metric | Target | Verification |
|---|---|---|
| Suggested-add legality | 100% | Deterministic re-validation in `suggestions`; integration test gate |
| Decklist import resolution | > 95% auto-resolved | Measured on labeled import fixture set |
| Bracket placement agreement | >= 90% | Eval harness vs Commander Spellbook `estimate-bracket` |
| Scorecard reproducibility | 100% identical on same inputs + rules-version | Property-based and golden tests in `rules` and `scorecard` |
| Review latency (p95) | < 5s | Integration test against seeded testcontainers Postgres |

---

## Phase 0 Setup Checklist (Immediate Next Actions)

These tasks are ready to begin on the current branch. Complete them before starting
Phase 1.

```text
Environment and Repository
[ ] Confirm Python 3.12 is active: `python --version`
[ ] Confirm UV is installed: `uv --version`
[ ] Run `uv sync --all-extras` to install all development dependencies.
[ ] Run `uv run pre-commit install` to install hooks.
[ ] Run `pre-commit run --all-files` and resolve any failures.

Docker Compose Stack
[ ] Verify `docker-compose up` starts Postgres, app service, and data service.
[ ] Confirm Postgres is reachable at the configured port.

Database and Schema
[ ] Create `mtg_ai_schema` package skeleton with `__init__.py` and SQLAlchemy base.
[ ] Add Alembic configuration for the data-service domain (separate schema and
    version_table from the app domain).
[ ] Add Alembic configuration for the app-service domain.
[ ] Write and apply the initial data-service migration (empty, establishes lineage).
[ ] Write and apply the initial app-service migration (empty, establishes lineage).

Database Roles
[ ] Create the data-service writer role in Postgres.
[ ] Create the app-service restricted role (SELECT on data tables, DML on app tables).
[ ] Write an integration test that asserts the restricted role cannot write a
    data-owned table.

Auth Skeleton
[ ] Implement the `User` model (id, username, password_hash).
[ ] Implement PBKDF2/argon2 password hashing (no bcrypt; FIPS requirement).
[ ] Implement session token issuance and validation.
[ ] Implement `POST /api/v1/auth/login`.
[ ] Scope all existing and future app routes by `user_id`.

CI
[ ] Confirm GitHub Actions CI runs Ruff, BasedPyright, pytest, Bandit, pip-audit.
[ ] Confirm CI is green on the Phase 0 branch before merging to main.
```

---

## Related Documents

- [Project Vision and Scope](./project-vision.md)
- [Technical Specification](./tech-spec.md)
- [Development Roadmap](./roadmap.md)
- [ADR-001: Split-Service Architecture](./adr/adr-001-initial-architecture.md)
- [ADR-002: Layered Data Model](./adr/adr-002-data-model.md)
- [ADR-003: Deterministic Scorecard Engine](./adr/adr-003-engine-approach.md)
- [ADR Index](./adr/README.md)
- [Contributing Guide](https://github.com/ByronWilliamsCPA/MTG_AI/blob/main/CONTRIBUTING.md)
- [Security Policy](https://github.com/ByronWilliamsCPA/MTG_AI/blob/main/SECURITY.md)

---

**Last Updated**: 2026-06-08
**Next Review**: Before Phase 1 kickoff (or after any roadmap change)
**Approved By**: Byron Williams (core-maintainer)
