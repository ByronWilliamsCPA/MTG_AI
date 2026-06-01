# MTG_AI

A self-hosted assistant that **critiques and upgrades competitive Magic: The
Gathering decks**, starting with competitive Commander (cEDH). Import a decklist
and MTG_AI analyzes its weaknesses and proposes specific cuts and additions with
reasoning, anchored to the current metagame.

> **Status**: In planning. The approved design lives at
> [`docs/superpowers/specs/2026-05-31-mtg-ai-cedh-critique-design.md`](docs/superpowers/specs/2026-05-31-mtg-ai-cedh-critique-design.md).
> Implementation has not started yet.

## What it does

- **Primary workflow**: import an existing deck, get a legality-correct critique
  (cuts/adds + reasoning) for competitive Commander.
- **RAG-based**: a vector database of cards, decks, and metagame data retrieves
  relevant context for a base model (Claude); a deterministic rules engine, not
  the model, is the source of truth for legality.
- **Designed for fine-tuning later**: every critique is logged with its inputs
  and the user's accept/reject decisions, building a labeled corpus for a future
  fine-tuned model that can be swapped in behind a stable interface.

## Architecture (summary)

Two self-hosted services plus a React frontend, sharing one Postgres + pgvector
database under a single-writer rule:

- **Data Service**: ingests Scryfall, MTGJSON, and cEDH metagame data; generates
  embeddings; the only writer of card/meta/embedding tables.
- **App Service**: user-facing FastAPI; deck import, the deterministic rules
  engine, RAG retrieval, and critique generation; reads the shared tables.
- **Frontend**: React + Vite + TypeScript.

See the design spec for the full architecture, data flow, error handling, and
testing strategy.

## Data sources

Scryfall (cards, rulings, prices), MTGJSON (legality, printings), competitive
metagame data, and user-provided decklists/collections.

## Legal

Card names, text, and imagery are property of Wizards of the Coast. This project
consumes data under the source providers' terms and does not redistribute
proprietary assets. The code is licensed under MIT (see [LICENSE](LICENSE)); the
card data is not.
