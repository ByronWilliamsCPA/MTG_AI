---
title: "MTG AI - Project Vision & Scope"
schema_type: planning
status: active
owner: core-maintainer
purpose: "Document the project vision, scope, and success criteria."
tags:
  - planning
  - scope
component: Strategy
source: "Approved brainstorming spec plus tmp/ research synthesis (2026-06-01)"
---

> **Status**: Active | **Version**: 2.0 | **Updated**: 2026-06-01
>
> Project Vision & Scope for MTG AI. v2.0 widens scope from cEDH-only to
> bracket-aware Commander and pivots the engine to deterministic scoring over
> reused precomputed data.

## TL;DR

MTG AI is a self-hosted assistant that reviews and upgrades Commander decks
across all power brackets (casual through cEDH). It scores a deck deterministically
(legality, power, bracket, role coverage, manabase, synergy) and proposes ranked
cuts and adds, annotated with what you own and what each add costs. Card legality
is never delegated to a language model.

## Problem Statement

### Pain Point

Tuning a Commander deck to a target power level is slow and expertise-bound. A
player must cross-reference ~30,000 legal cards against color identity, the
singleton and banlist rules, the beta and fast-moving bracket system (Game
Changers, combos, mass land denial), archetype role ratios, and manabase math,
then judge which swaps actually move the deck. The data to do this well already
exists (EDHREC synergy and lift, Commander Spellbook combos, Scryfall and MTGJSON
inventory and prices) but is scattered across sites. General LLM chatbots answer
unreliably: they hallucinate cards and suggest off-color, banned, or
bracket-breaking additions. There is no trustworthy, bracket-aware critique tool
a private playgroup can self-host.

### Target Users

- **Primary**: The owner plus a few Commander playgroup members.
- **Context**: Self-hosted; used when building or upgrading a deck toward a
  chosen bracket, from casual (B1-B2) through optimized and cEDH (B4-B5), by
  importing a decklist and reading back a scorecard and ranked suggestions.

### Success Metrics

- Legality of suggested adds: 100% (deterministically enforced; an off-color,
  non-singleton, or banned add must never reach the user).
- Decklist import resolution: > 95% auto-resolved; the rest surfaced for manual
  confirmation, never silently guessed.
- Bracket placement agreement: >= 90% match with Commander Spellbook
  `estimate-bracket` on a labeled deck set.
- Scorecard reproducibility: identical inputs and rules-version yield identical
  scores (effective-dated reference data).
- Review latency (p95): < 5s, since v1 is database lookups and deterministic
  math rather than an LLM on the hot path.

## Solution Overview

### Core Value

Import a Commander decklist and get a trustworthy, bracket-aware scorecard plus
ranked, legality-correct upgrade suggestions, with ownership and price shown, so
you can tune toward a target power level without illegal or unaffordable picks.

### Key Capabilities (MVP)

1. **Decklist and collection import**: parse Arena/MTGO/text decklists and import
   a user's owned-card collection, detect commander(s) including Partner/Background
   pairs, resolve cards to Scryfall `oracle_id`.
2. **Deterministic review scorecard**: legality/identity gate; functional power
   (Disciple-of-the-Vault 1-10); WotC bracket placement (1-5) via gate logic and
   the versioned Game Changers list; role coverage vs archetype targets; manabase
   (Karsten) check; synergy and lift reported separately, never blended.
3. **Ranked upgrade suggestions**: cuts and adds for underfilled roles and
   bracket mismatches, ranked by commander synergy and lift, each re-validated
   for legality, and annotated with ownership and price for value-per-dollar
   sorting.
4. **Reuse-first ingestion**: cache EDHREC, Commander Spellbook, Scryfall, and
   MTGJSON keyed to `oracle_id`, with Game Changers and bracket rules as
   refreshable, effective-dated config.
5. **Plain-language explanation**: a swappable LLM backend turns the deterministic
   scorecard and suggestions into readable rationale; it never decides legality,
   scores, or bracket placement (those are deterministic).

## Scope Definition

### In Scope (MVP)

- Commander format, brackets 1-5 (casual through cEDH).
- Review + ranked upgrade suggestions for an existing deck.
- Collection ownership and card price as soft annotations and a value-per-dollar
  ranking (no hard budget filter in v1).
- Deterministic scoring over reused precomputed datasets.

### Out of Scope / Deferred

- 🔄 Standard track (empirical metagame engine, win-rate model, simulation):
  later phase; the data model anticipates it.
- 🔄 Embeddings / card2vec retrieval (RAG): v2 enhancement, not a v1 dependency.
- 🔄 Hard budget filter (cap by count or dollars that drops adds): later; v1 is
  soft annotation only.
- 🔄 Full deck generation from a commander: later workflow.
- ❌ Public multi-tenant SaaS, billing, large-scale load.
- ❌ Fine-tuning a generation model.

## Constraints

### Technical

- **Platform**: React + Vite + TypeScript frontend over a FastAPI backend, split
  into ingestion (data) and app services. See [Technical Spec](./tech-spec.md)
  and [adr-001-initial-architecture.md](./adr/adr-001-initial-architecture.md).
- **Language**: Python 3.12 (backend); TypeScript (frontend).
- **Storage**: relational Postgres core (layered data model, `oracle_id`
  crosswalk); pgvector deferred to the v2 embeddings phase. See
  [adr-002-data-model.md](./adr/adr-002-data-model.md) and
  [adr-003-engine-approach.md](./adr/adr-003-engine-approach.md).
- **Reuse first**: ingest MIT/free datasets (MTGJSON, Commander Spellbook,
  Scryfall) and adapt MIT code rather than rebuild; bracket rules are beta and
  must be refreshable config, not hardcoded.

### Business

- **Timeline**: phased; the review-plus-suggestions loop is the first shippable
  milestone (see [Roadmap](./roadmap.md)).
- **Resources**: single maintainer plus playgroup feedback; cheap to operate.
- **Legal**: Scryfall (attribution, rate limits) and MTGJSON/Commander Spellbook
  (MIT) under their terms; EDHREC has no open license, so cache politely and do
  not redistribute; card names, text, and art are Wizards of the Coast IP under
  the Fan Content Policy (non-commercial). Code is MIT.

## Assumptions to Validate

- [ ] EDHREC public JSON remains usable under polite-cache terms for a private
      project; revisit if the app ever goes public.
- [ ] Commander Spellbook `estimate-bracket` is an acceptable ground truth for
      the bracket-agreement metric.
- [ ] "Light auth" means simple per-user accounts (not SSO/OAuth) is acceptable.
- [ ] A price source (Scryfall/MTGJSON prices) at ~24h staleness is adequate for
      soft value-per-dollar ranking.

## Related Documents

- [Architecture Decisions](./adr/)
- [Technical Spec](./tech-spec.md)
- [Roadmap](./roadmap.md)
