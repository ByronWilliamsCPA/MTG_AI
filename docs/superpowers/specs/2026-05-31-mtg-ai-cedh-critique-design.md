# MTG_AI Design: Competitive Commander (cEDH) Deck-Critique Assistant

> **Status**: Approved (brainstorming) | **Date**: 2026-05-31 | **Owner**: Byron Williams
>
> This spec is the approved output of the brainstorming phase. The implementation
> plan is generated from it via the writing-plans workflow.

## 1. Overview

MTG_AI is a self-hosted assistant that **critiques and upgrades** competitive
Magic: The Gathering decks. The first and primary workflow: a user imports an
existing decklist, and MTG_AI analyzes its weaknesses and proposes specific cuts
and additions with reasoning, anchored to the competitive metagame.

**Format scope**: Commander / EDH first, specifically **competitive Commander
(cEDH)**. The data model is designed so additional formats (Standard, Pioneer,
Modern, Pauper) can be added later without re-architecting.

**AI strategy**: Retrieval-Augmented Generation (RAG) now, with an explicit
swap-point so a fine-tuned generation model can replace the base model in a
later phase. Every critique is logged with its inputs, retrieved context, and
the user's accept/reject decisions, which passively accumulates a labeled
corpus for that future fine-tuning.

**Audience / hosting**: A small private group (the owner plus a few playgroup
members), self-hosted on a small cloud box via Docker Compose, with light auth.

## 2. Goals and Non-Goals

**Goals**
- Import a decklist (Arena / MTGO / plain-text) and produce a trustworthy,
  legality-correct cEDH critique with reasoning.
- Never trust the language model with legality: a deterministic rules engine is
  the source of truth.
- Keep the system cheap to run for a handful of users.
- Lay the architectural seam for phase-2 fine-tuning without committing to it now.

**Non-Goals (explicitly out of scope for v1)**
- Full deck generation from scratch (a possible later workflow; v1 is critique).
- Public multi-tenant SaaS, billing, or large-scale load.
- Formats other than Commander/cEDH (data model supports them; v1 does not ship them).
- Fine-tuning itself (only the data-capture seam is built now).

## 3. Architecture (Approach B: split services)

Two independently deployable services plus a frontend, all in one Docker Compose
stack, communicating through a **shared Postgres database with a single-writer
rule** rather than a synchronous service-to-service API.

```
┌─────────────────────┐     ┌──────────────────────────────────────┐
│   Frontend (React)  │     │            DATA SERVICE              │
│   Vite + TS         │     │  (ingestion + embeddings + scoring)  │
│   - deck import UI  │     │                                      │
│   - critique view   │     │  ┌────────────┐  scheduled jobs      │
└──────────┬──────────┘     │  │ ingestion/ │  - Scryfall bulk     │
           │ HTTPS          │  │            │  - MTGJSON legality  │
           ▼                │  │  scryfall  │  - meta/cEDH scrape   │
┌─────────────────────┐     │  │  mtgjson   │                      │
│     APP SERVICE     │     │  │  meta      │  ┌────────────┐       │
│  (user-facing API)  │     │  └─────┬──────┘  │ embeddings │       │
│                     │     │        │         │ (local ST) │       │
│  - auth (light)     │     │        ▼         └─────┬──────┘       │
│  - deck import      │     │   writes cards,        │              │
│  - rules engine     │     │   legality, meta,      │              │
│  - rag retrieval    │     │   embeddings ──────────┘              │
│  - Claude gen       │     └──────────────┬───────────────────────┘
│         │ reads     │                    │ writes
└─────────┴───────────┘                    ▼
          │                 ┌──────────────────────────────────────┐
          └────────────────▶│   Postgres + pgvector (shared store) │
                            │   cards · decks · legality · meta ·  │
                            │   embeddings · users · critique logs │
                            └──────────────────────────────────────┘
```

**Service boundary (single-writer rule)**
- The **Data Service is the only writer** of card, legality, meta, and embedding
  tables. It owns and runs the migrations for those tables.
- The **App Service only reads** those tables, and writes its own tables (users,
  imported decks, critique logs).
- The services do **not** call each other synchronously. No inter-service API to
  version, no network hop on the critique hot path.
- The single-writer rule is enforced **structurally**: the App Service connects
  with a **read-only Postgres role** on the Data Service's tables, so the
  convention becomes a database-level guarantee.

**Vector store**: Postgres + the `pgvector` extension. Structured data and
embeddings live in one database, so semantic similarity, the meta competitiveness
score, and the hard color-identity filter combine in a single SQL query.

**Generation stack**: local `sentence-transformers` embeddings (no per-card API
cost; cards are embedded once per set release) and Claude via API for critique
reasoning, behind a swappable `Generator` interface.

## 4. Components and Boundaries

Each package has one job, a typed interface, and is testable in isolation.

**Shared schema package (`mtg_ai_schema/`)**: a small library both services
depend on: SQLAlchemy models + Alembic migrations for the shared tables. The
Data Service owns and runs migrations; the App Service imports the models
read-only. One source of truth for table shapes.

**Data Service packages**

| Package | Job | Interface |
|---|---|---|
| `ingestion/scryfall` | Download Scryfall bulk JSON; normalize cards/rulings/prices | `sync_cards() -> IngestReport` |
| `ingestion/mtgjson` | Pull format legality + printings | `sync_legality() -> IngestReport` |
| `ingestion/meta` | Scrape cEDH lists/staples; compute play-rate | `sync_meta() -> IngestReport` |
| `embeddings` | Embed card text locally (sentence-transformers) | `embed(texts) -> vectors` |
| `scoring` | Convert meta into a per-card competitiveness signal | `score(card) -> float` |
| `scheduler` | Run syncs on a cadence (set-release vs daily) | container entrypoint |

**App Service packages**

| Package | Job | Interface |
|---|---|---|
| `decks/import` | Parse Arena/MTGO/text decklists; detect commander | `parse(raw) -> Deck` |
| `rules` | Deterministic Commander validator (100-card, singleton, color identity, banlist) | `validate(Deck) -> list[Violation]` |
| `rag/retrieval` | Retrieve stronger candidates from pgvector per card role/color | `retrieve(Deck) -> Context` |
| `critique` | Orchestrate: build context, call generator, parse, re-validate | `critique(Deck) -> Critique` |
| `generator` | Swappable generation backend (Claude now, fine-tuned later) | `Generator.generate(prompt) -> str` |
| `api` | FastAPI routes, auth, request/response models | HTTP |

**Two reliability seams**
1. `rules` is pure, deterministic, and has zero LLM involvement. Legality is
   never trusted to the model.
2. `critique` re-runs `rules` on the model's own suggestions before returning
   them. Illegal suggestions (e.g. an off-color add) are dropped or regenerated.
   The LLM proposes; deterministic code disposes.

## 5. Data Flow

**Flow A: Ingestion (Data Service, scheduled, no user present)**
- Set-release cadence: Scryfall bulk + MTGJSON -> normalize -> embed (local) ->
  upsert cards + vectors.
- Daily cadence: cEDH meta -> upsert meta + competitiveness scores.
- Each sync is idempotent (upsert by Scryfall `oracle_id`); a failed run simply
  retries on the next cadence. An `IngestReport` row records counts and status.

**Flow B: Critique request (App Service, hot path)**
1. User pastes/uploads a decklist in the frontend.
2. `decks/import` parses raw text into a `Deck` (commander detected, cards
   resolved against the DB).
3. `rules.validate` checks Commander legality and surfaces violations (critique
   still proceeds).
4. `rag.retrieve` pulls stronger cEDH candidates and weak spots from pgvector
   via a single SQL query combining vector similarity, meta score, and a hard
   color-identity filter (`WHERE color_identity <@ commander_identity`).
5. `critique` assembles a compact context (deck + candidates + meta) and calls
   `generator.generate`.
6. The generator (Claude) returns a structured critique: cuts/adds with reasoning.
7. `critique` **re-validates every suggested add** against `rules` (color
   identity, singleton, banlist) and drops or regenerates anything illegal.
8. Persist `critique_log` (input deck, retrieved context, raw suggestions, final
   suggestions).
9. Frontend renders cuts | adds | reasoning, each with accept/reject controls.

**Flow C: Training-data capture (phase-2 seam, passive)**
Step 8 logs `(deck, retrieved context, suggestions)`. The frontend accept/reject
in step 9 appends the label. The fine-tuning corpus accumulates as a column on
`critique_log`, with no extra system.

## 6. Error Handling and Failure Modes

Guiding principle: **degrade, don't break.** Stale data still serves; a partial
critique beats an error; unresolved input is surfaced, not guessed. External
dependencies (four data sources + the LLM API) are tagged per RAD
"external resources".

| Failure | Where | Strategy |
|---|---|---|
| Data source down / rate-limited | `ingestion/*` | Per-source isolation; idempotent upserts; retry next cadence; `IngestReport` records failure; stale data keeps serving. |
| Source schema/HTML changed | `ingestion/meta`, `mtgjson` | Parse into a validated Pydantic model at the boundary; a shape change fails loudly into `IngestReport` rather than writing garbage. |
| Card name won't resolve | `decks/import` | Fuzzy-match against the card DB; surface unresolved cards to the user; never guess. |
| LLM timeout / rate limit | `generator` | Bounded retry with backoff; per-user rate limit + cost guard. |
| LLM malformed/illegal output | `critique` | Parse failure -> reject + bounded retry; illegal suggestions -> re-validate drops them; after N tries return the valid subset with an honest note. |
| App Service writes shared tables | DB boundary | Prevented structurally via a read-only Postgres role on the shared tables. |
| Embedding model/version drift | `embeddings` | Store model name + vector dimension; a model change is a migration, not silent index corruption. |

## 7. Testing Strategy

Correctness-critical parts are pure; expensive/nondeterministic parts sit behind
interfaces. No live network and no live LLM calls in the test suite.

| Layer | What | How | Coverage target |
|---|---|---|---|
| `rules` validator | Commander legality | Unit + property-based (Hypothesis); golden legal/illegal decks. **Test-first (TDD).** | 90%+ (critical) |
| `decks/import` | Parse + fuzzy resolution | Fixture decklists per format; assert unresolved cards surfaced | 85%+ |
| `ingestion/*` | Download + normalize | Recorded fixtures (saved JSON/HTML), never live network; assert Pydantic boundary rejects drift | 80% |
| `rag/retrieval` | Combined vector + color + score SQL | Integration against a seeded throwaway pgvector DB (testcontainers) | 80% |
| `critique` + `generator` | Orchestration + re-validate loop | Mock the `Generator`; feed an illegal suggestion and assert step-7 drops it | 85%+ |
| `api` | Routes, auth, schemas | FastAPI `TestClient`; assert cross-user deck isolation | 80% |
| Frontend | Import + critique views | Vitest component tests; one Playwright happy-path e2e | key paths |

**Eval harness**: a small set of known decks with "obvious" expected cuts/adds.
Not a unit test, a quality tripwire that detects critique-quality regressions
across prompt or model changes, and the baseline for measuring whether a phase-2
fine-tuned model beats RAG-Claude.

## 8. Tech Stack

- **Scaffold**: the owner's cookiecutter-python-template (FastAPI API, React+Vite+TS
  frontend, ML dependencies, SQLAlchemy/Postgres, Docker, pre-commit, CI, OpenSSF
  baseline), extended with the `pgvector` extension and the two-service layout.
- **Backend**: Python 3.12, FastAPI, SQLAlchemy + Alembic, Pydantic v2.
- **Vector store**: Postgres + pgvector.
- **Embeddings**: local sentence-transformers.
- **Generation**: Claude via API, behind a `Generator` interface.
- **Frontend**: React + Vite + TypeScript.
- **Deploy**: Docker Compose (frontend, app service, data service, Postgres).

## 9. Future Phases

- **Phase 2 (fine-tuning)**: once `critique_log` has enough labeled examples,
  train/evaluate a fine-tuned generation model against the eval harness and swap
  it in behind the `Generator` interface.
- **More formats**: extend the schema and meta ingestion to Standard/Pioneer/
  Modern/Pauper.
- **Deck generation workflow**: build-from-commander, reusing retrieval + rules.

## 10. Legal Note

Card names, text, and imagery are intellectual property of Wizards of the Coast.
This project consumes data under the source providers' terms (Scryfall, MTGJSON)
and does not redistribute proprietary assets. The code is MIT-licensed; the data
is not.
