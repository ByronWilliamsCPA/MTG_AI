---
title: "MTG AI - Technical Specification"
schema_type: planning
status: active
owner: core-maintainer
purpose: "Document the technical architecture and implementation details."
tags:
  - planning
  - architecture
component: Development-Tools
source: "Approved spec plus tmp/ research synthesis (2026-06-01)"
---

> **Status**: Draft | **Version**: 2.0 | **Updated**: 2026-06-01
>
> Technical Implementation Spec for MTG AI. v2.0 follows the bracket-aware
> Commander re-scope and the deterministic-scorecard engine decision.

## TL;DR

A two-service Python/FastAPI backend (data service ingests reused datasets; app
service reviews decks) over one relational Postgres database under a single-writer
rule. v1 scores Commander decks deterministically (legality, power, bracket, role
coverage, manabase, synergy) and ranks upgrade suggestions annotated with
ownership and price. The LLM only explains; embeddings/RAG and Standard are
deferred. See [ADR-001](./adr/adr-001-initial-architecture.md),
[ADR-002](./adr/adr-002-data-model.md), [ADR-003](./adr/adr-003-engine-approach.md).

## Technology Stack

### Core

- **Language**: Python 3.12 (backend); TypeScript 5.x (frontend).
- **Package Manager**: UV.
- **Backend framework**: FastAPI; Pydantic v2 at every ingestion boundary.
- **Frontend**: React 18 + Vite.

### Code Quality

- **Linter/Formatter**: Ruff (88 chars, PyStrict-aligned).
- **Type Checker**: BasedPyright (strict).
- **Testing**: pytest, Hypothesis (property-based), testcontainers; Vitest +
  Playwright (frontend).

### Data Layer

- **Database**: Postgres 16, relational-first; pgvector deferred to the v2
  embeddings phase. See [ADR-002](./adr/adr-002-data-model.md).
- **ORM / Migrations**: SQLAlchemy 2.x + Alembic (per-domain `version_table`).

### Infrastructure

- **CI/CD**: GitHub Actions.
- **Container**: Docker Compose (frontend, app service, data service, Postgres).
- **Generation**: an LLM (e.g. Claude) behind a `Generator` interface, used only
  for plain-language explanation.

### Reused Data Sources

| Source | Provides | License/terms |
|---|---|---|
| Scryfall (bulk) | Card inventory, `color_identity`, legalities, prices | Free, attribution, rate-limited |
| MTGJSON | Commander-legal flag, preconstructed decks, prices | MIT |
| EDHREC (JSON) | Synergy, inclusion, lift, theme/role buckets | No open license; polite cache, no redistribute |
| Commander Spellbook | Combos, `find-my-combos`, `estimate-bracket` | MIT |
| WotC (Scryfall `is:gamechanger`) | Game Changers list, bracket rules | Versioned config, refresh ~quarterly |

## Architecture

### Pattern

Split services over a shared single-writer database
([ADR-001](./adr/adr-001-initial-architecture.md)). The data service ingests and
is the sole writer of reference/corpus/analytics tables; the app service reads
them with a restricted role and owns user/deck/collection/review tables.

### Component Diagram

```text
┌──────────────┐  HTTPS  ┌─────────────────────────────────────────┐
│  Frontend    │ ──────▶ │              APP SERVICE                │
│ React + Vite │         │ import · collection · rules · scorecard │
└──────────────┘         │ · suggestions · generator(explain) · api│
                         └────────────────────┬────────────────────┘
                                              │ read shared / write own
   ┌──────────────────────────────────────────▼──────────────────────┐
   │           Postgres (relational; pgvector in v2)                  │
   │ Reference · Corpus · Analytics  (data-owned, read-only to app)   │
   │ users · decks · collections · reviews  (app-owned)               │
   └──────────────────────────────────────────▲──────────────────────┘
                                              │ write shared (sole writer)
                         ┌────────────────────┴────────────────────┐
                         │              DATA SERVICE               │
                         │ ingestion(scryfall/mtgjson/edhrec/      │
                         │ spellbook) · tagging · reference-config │
                         │ (game changers/brackets) · scheduler    │
                         └─────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Service | Purpose |
|---|---|---|
| `mtg_ai_schema` | shared | SQLAlchemy models + data-owned migrations |
| `ingestion/scryfall` | data | Cards, legality, prices by `oracle_id` |
| `ingestion/mtgjson` | data | Commander-legal flag, precons, prices |
| `ingestion/edhrec` | data | Synergy, inclusion, lift, theme/role buckets |
| `ingestion/spellbook` | data | Combos, bracket estimate |
| `reference_config` | data | Versioned, effective-dated Game Changers + bracket rules |
| `scheduler` | data | Set-release vs daily cadence; `IngestReport` per run |
| `decks/import` | app | Parse Arena/MTGO/text; detect commander(s) |
| `collection/import` | app | Import owned-card list to `oracle_id` |
| `rules` | app | Deterministic legality/identity gate |
| `scorecard` | app | Power, bracket, role coverage, manabase |
| `suggestions` | app | Rank cuts/adds; re-validate; annotate ownership+price |
| `generator` | app | LLM explanation only (no scoring authority) |
| `api` | app | FastAPI routes, auth, schemas |

Two reliability seams: `rules` is pure and LLM-free; `suggestions` re-runs `rules`
on every proposed add and drops illegal ones.

## Data Model

Layered by volatility ([ADR-002](./adr/adr-002-data-model.md)); canonical identity
is the Scryfall `oracle_id`. Representative entities (the full ~25-entity catalog
lives in ADR-002):

```python
# --- Landing (data-owned; raw, immutable, timestamped) ---
class LandingDump:                # as-pulled source JSON; re-derivation + provenance
    id: UUID
    source: str                   # scryfall|mtgjson|edhrec|spellbook
    url: str
    payload: JSON
    ingested_at: datetime
    license: str

# --- Reference (data-owned; slow, versioned) ---
class Card:                       # keyed by Scryfall oracle_id
    oracle_id: UUID
    name: str
    cmc: float
    mana_cost: str | None         # pips, e.g. "{3}{W}{W}" (Karsten/power math)
    produced_mana: list[str]      # colors a land/rock taps for (mana sources)
    type_line: str
    color_identity: list[str]     # e.g. ["U", "B"]
    can_be_commander: bool
    legalities: dict[str, str]    # format -> legal|banned|restricted

class IdentifierXref:             # crosswalk to mtgjson/edhrec/arena/mtgo/name
    oracle_id: UUID
    system: str
    external_id: str

class CardRole:                   # functional tag (ramp/draw/tutor/...)
    oracle_id: UUID
    role_id: str
    weight: float

class CardPrice:                  # optional, advisory; stale after ~24h
    oracle_id: UUID
    source: str
    date: date
    price: Decimal

class GameChanger:                # versioned membership, effective-dated
    oracle_id: UUID
    effective_date: date
    is_member: bool

class BracketDef:                 # versioned bracket gate rules
    bracket: int                  # 1..5
    effective_date: date
    gate_rules: dict

# --- Analytics (data-owned; recomputed) ---
class CommanderSynergy:
    commander_oracle_id: UUID
    oracle_id: UUID
    snapshot_date: date
    synergy_score: float
    inclusion_rate: float

class CardPairLift:               # sparse; only observed pairs above threshold
    oracle_id_a: UUID
    oracle_id_b: UUID
    snapshot_date: date
    lift: float                   # unobserved pairs default to 0 at query time

# --- Application (app-owned) ---
class User:
    id: UUID
    username: str
    password_hash: str            # PBKDF2/argon2 (FIPS-safe)

class Deck:
    id: UUID
    user_id: UUID
    commander_oracle_ids: list[UUID]   # 1-2 (Partner/Background)
    color_identity: list[str]          # union, computed at import
    target_bracket: int | None         # user's intended bracket
    raw_source: str

class Collection:                 # a user's owned cards
    id: UUID
    user_id: UUID
    name: str

class CollectionCard:
    collection_id: UUID
    oracle_id: UUID
    quantity: int

class DeckReview:
    id: UUID
    deck_id: UUID
    power_score: float            # Disciple-of-the-Vault 1-10
    bracket_estimate: int         # 1-5
    rules_version: date           # Game Changers/bracket effective date used
    synergy_commander: float
    synergy_avg_lift: float

class ReviewSuggestion:
    review_id: UUID
    action: str                   # add | cut
    oracle_id: UUID
    rationale: str
    score: float
    owned: bool                   # from the user's collection
    price: Decimal | None         # advisory; for value-per-dollar sort
```

### Relationships

- `Card` 1-to-many `IdentifierXref`, `CardRole`, `CardPrice`, `CommanderSynergy`.
- `User` 1-to-many `Deck` and `Collection`; `Collection` 1-to-many `CollectionCard`.
- `Deck` 1-to-many `DeckReview`; `DeckReview` 1-to-many `ReviewSuggestion`.
- Retrieval filters candidates with `WHERE color_identity <@ :deck_color_identity`.

## Review Pipeline

1. `decks/import` parses the list, detects commander(s), resolves to `oracle_id`
   (unresolved names surfaced, never guessed), computes `Deck.color_identity`.
2. `rules` runs the legality/identity gate (color identity, singleton, banlist,
   commander-legal).
3. `scorecard` computes functional power, bracket placement, role coverage, and
   a Karsten manabase check. Power is a deterministic Disciple-of-the-Vault
   function of card attributes (`cmc`, `mana_cost`) and functional role tags
   (`CardRole`, with tutors then ramp weighted heaviest); its formula weights live
   in versioned `reference_config`, and it does not use EDHREC salt. Bracket uses
   gate logic over the versioned Game Changers list; the manabase check uses
   `mana_cost` pips and land `produced_mana`. Synergy and average lift are
   reported separately, never blended.
4. `suggestions` proposes cuts (off-curve, low-synergy, bracket-violating) and
   adds (underfilled roles), ranked by commander synergy and lift, re-validates
   each add against `rules`, and annotates `owned` and `price`. Ownership resolves
   against an optional `collection_id` on the request, defaulting to the union of
   the user's collections.
5. `generator` turns the scorecard and suggestions into plain-language rationale;
   it cannot alter any score, legality verdict, or bracket.
6. Persist `DeckReview` + `ReviewSuggestion` (with `rules_version`); the frontend
   renders the scorecard and accept/reject controls, sortable by value-per-dollar.

### Scorecard Object (example)

```yaml
review:
  legal: true
  power_score: 6.5            # 1-10
  bracket: {estimate: 3, target: 3, match: true}
  role_coverage:
    ramp: {count: 8, target: "10-12", status: low}
    interaction: {count: 6, target: "8-12", status: low}
  synergy: {commander: 0.42, avg_lift: 1.8}
  flags: ["Interaction below target for Bracket 3"]
  suggest_add: [{oracle_id: "...", owned: true, price: 0.50, score: 0.9}]
  suggest_cut: [{oracle_id: "...", reason: "off-curve, low synergy"}]
```

## API Specification

| Method | Path | Purpose | Auth |
|---|---|---|---|
| POST | /api/v1/auth/login | Issue session token | No |
| POST | /api/v1/decks/import | Parse + resolve a decklist | Yes |
| GET | /api/v1/decks/{id} | Fetch a deck (owner only) | Yes |
| POST | /api/v1/collections/import | Import owned-card list | Yes |
| POST | /api/v1/decks/{id}/review | Run the review pipeline (optional `collection_id` in body) | Yes |
| POST | /api/v1/reviews/{id}/feedback | Record accept/reject | Yes |
| GET | /api/v1/health | Liveness/readiness | No |

## CLI Specification

A Click CLI (data service entrypoint) drives ingestion and ops:

| Command | Purpose |
|---|---|
| `mtg-ai sync cards` | Scryfall + MTGJSON sync |
| `mtg-ai sync edhrec` | EDHREC synergy/lift/themes |
| `mtg-ai sync rules` | Refresh Game Changers + bracket config |

## Security

- **Authentication**: light per-user accounts with session tokens; password
  hashing via PBKDF2/argon2 (FIPS-safe, no bcrypt).
- **Authorization**: every deck, collection, and review query is scoped by
  `user_id`; cross-user access is denied and tested.
- **Single-writer enforcement**: the app role has `SELECT` only on data-owned
  tables (database-level guarantee).
- **Data Protection**: TLS in transit; secrets via environment/`.env` (never
  committed); the LLM API key is server-side only.

## Error Handling

Guiding principle: **degrade, don't break.** Stale data still serves; a partial
review beats an error; unresolved input is surfaced, not guessed.

| Failure | Strategy |
|---|---|
| Source down / rate-limited | Per-source isolation; idempotent upserts; retry next cadence; `IngestReport` records it; stale data serves |
| Source schema/HTML drift | Pydantic boundary fails loudly into `IngestReport`, never writes garbage |
| Card won't resolve | Fuzzy-match + override table; surface to user; never guess |
| LLM timeout/unavailable | Return the full scorecard and suggestions without prose (explanation is optional) |
| Stale Game Changers/brackets | Review records the `rules_version` used; flagged if older than a threshold |

Structured JSON logging with correlation IDs; API keys and secrets are never logged.

## Performance Requirements

| Metric | Target | Measurement |
|---|---|---|
| Review latency (p95) | < 5s | end-to-end, deterministic path (no LLM dependency) |
| Card resolution rate | > 95% | resolved / total on import |
| Suggested-add legality | 100% | post re-validation |
| Bracket agreement | >= 90% | vs Commander Spellbook `estimate-bracket` |

## Testing Strategy

No live network or LLM in the suite (mock the `Generator`).

- **Unit**: `rules` gate + `scorecard` (property-based, golden decks), 90%+;
  `decks/import` fuzzy resolution, 85%+.
- **Integration**: ingestion against recorded fixtures (assert Pydantic boundary
  rejects drift); retrieval against a seeded throwaway Postgres (testcontainers);
  assert the app role cannot write shared tables.
- **E2E**: one Playwright happy-path (import -> review -> feedback).
- **Eval harness**: known decks with expected cuts/adds as a quality tripwire.

Coverage: 80% overall, 90% on the critical `rules` and `scorecard` paths.

## Future (Deferred)

- **Embeddings / RAG**: pgvector + card2vec on Commander decklists for relationship
  discovery (v2).
- **Standard track**: empirical payoff matrix, Nash mixtures, win-rate predictor,
  Forge simulation, BO1/BO3 partitioning (later phase; the data model partitions
  by `format`).
- **Hard budget filter** and **deck generation from a commander**.

## Related Documents

- [Project Vision](./project-vision.md)
- [Architecture Decisions](./adr/)
- [Development Roadmap](./roadmap.md)
