---
title: "ADR-001: Split-Service Architecture with a Shared Single-Writer Database"
schema_type: planning
status: accepted
owner: core-maintainer
purpose: "Record the split into app and data services over a shared single-writer Postgres store."
tags:
  - planning
  - architecture
  - decisions
---

> **Status**: Accepted (amended 2026-06-01 for the v2 re-scope)
> **Date**: 2026-06-01
> **Supersedes**: None

## TL;DR

MTG AI runs as two deployable services (app + data) communicating through a
shared Postgres database under a single-writer rule, isolating heavy scheduled
ingestion from the user-facing review path without a versioned API.

## Context

### Problem

MTG AI has two workloads with opposite shapes. **Ingestion** is heavy and
scheduled (Scryfall, MTGJSON, EDHREC, Spellbook, versioned bracket rules) and
must never block a user. **Review** (score a deck, suggest upgrades) is
interactive and latency sensitive. Both read the same reference data, so we need
a topology that keeps ingestion off the hot path while one query combines a
synergy/meta score with a color-identity filter.

### Constraints

- **Technical**: Self-hosted on one small box (Docker Compose); few users; cheap
  to run. v1 is deterministic scoring over reused precomputed data; embeddings
  and RAG are deferred to v2 (see [ADR-003](../adr/adr-003-engine-approach.md)).
- **Business**: Single maintainer; complexity must earn its keep.

### Significance

Service boundaries and the storage engine are the costliest to reverse.

## Decision

**We will split into an app service and a data service that share a single
Postgres database under a single-writer rule, because it isolates the two
workloads without a synchronous inter-service API.** The store is
relational-first; pgvector is added only in v2.

### Rationale

- The data service is the **only writer** of the reference, corpus, and analytics
  tables and owns their migrations. The app service connects with **one restricted
  role**: `SELECT` on those tables (the single-writer rule becomes a database-level
  guarantee), full DML on its own tables (users, decks, collections, reviews).
- Services never call each other synchronously: no API to version, no network
  hop, no cascading failure when ingestion is busy.
- One relational store lets a single SQL query combine a synergy/meta score with
  `WHERE color_identity <@ commander_identity`; v2 adds vectors in the same store
  via pgvector, not a second datastore to sync.

## Options Considered

### Option 1: Split services + shared single-writer Postgres (chosen)

**Pros**:

- Workload isolation with no inter-service API to build or version.
- One query joins structured filters and meta/synergy scores (and vectors later).
- Single-writer enforced structurally by DB roles.

**Cons**:

- Shared schema is a coupling point; needs a small shared models package.

### Option 2: Single monolith

**Pros**:

- Simplest to start; one deployable.

**Cons**:

- Heavy ingestion and the review path share one process; a bulk sync can degrade
  user requests.
- Harder to schedule the two workloads independently.

### Option 3: Microservices with a synchronous inter-service API

**Pros**:

- Strong logical decoupling; independent datastores possible.

**Cons**:

- An API contract to version and keep compatible, plus a network hop and failure
  mode on the hot path.
- Over-engineered for a few-user, single-box deployment.

## Consequences

### Positive

- Review latency is insulated from ingestion load.
- Combined retrieval (structured filters + meta/synergy) is one SQL statement.
- The restricted role makes accidental cross-writes structurally impossible.

### Trade-offs

- Shared table shapes couple the services: mitigated by a small `mtg_ai_schema`
  package (SQLAlchemy models + migrations) imported by both.
- Two Alembic lineages would collide on the default `alembic_version` table:
  each domain uses its own schema and `version_table`, so histories never clash.
- A single shared DB is a single point of failure: acceptable at this scale;
  standard Postgres backups suffice.

### Technical Debt

- When embeddings arrive in v2, store the model name and dimension so a model
  swap is a migration, not silent index corruption.

## Implementation

### Components Affected

1. **mtg_ai_schema**: shared package owning the SQLAlchemy models and migrations
   for the data-owned tables. See [ADR-002](../adr/adr-002-data-model.md).
2. **Data service**: owns ingestion, scoring inputs, scheduler; runs the
   data-owned migrations; sole writer of shared tables.
3. **App service**: owns import, rules, scorecard, suggestions, generator
   (explanation), API; runs its own migrations (separate schema + `version_table`);
   reads shared tables only.
4. **Postgres**: relational-first; two roles (data-service writer; app-service
   role with `SELECT` on data tables, full DML on app tables). pgvector in v2.

### Testing Strategy

- Integration against a seeded throwaway Postgres (testcontainers) proves the
  combined retrieval query and that the app role cannot write shared tables.

## Validation

### Success Criteria

- [ ] App service connection cannot write shared tables (role-enforced).
- [ ] Combined retrieval query returns color-legal candidates in one statement.
- [ ] An ingestion run does not raise review p95 latency above target.

Revisit at the end of Phase 2, and if scale grows beyond one box.

## Related

- [Project Vision](../project-vision.md)
- [ADR-002: Data Model](../adr/adr-002-data-model.md)
- [ADR-003: Engine Approach](../adr/adr-003-engine-approach.md)
- [Technical Spec](../tech-spec.md)
- [Roadmap](../roadmap.md)
