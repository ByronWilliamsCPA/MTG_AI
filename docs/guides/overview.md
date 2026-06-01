---
title: "Overview"
schema_type: common
status: published
owner: core-maintainer
purpose: "Overview of MTG AI features and capabilities."
tags:
  - guide
  - overview
---

Self-hosted competitive Commander (cEDH) deck-critique assistant: RAG over Scryfall/MTGJSON/meta data with a deterministic rules engine and a swappable generation backend.

## Key Features

### Modern Python Development

- **Python 3.12+** with full type annotations
- **UV** for fast dependency management
- **Ruff** for linting and formatting
- **BasedPyright** for strict type checking

### Quality Assurance

- **pytest** with comprehensive coverage
- **Pre-commit hooks** for automated checks
- **GitHub Actions** CI/CD pipeline

### Command Line Interface

Built with Click for a robust CLI experience:

```bash
mtg_ai --help
```
## Getting Started

1. **Installation**: See the [Configuration Guide](configuration.md)
2. **Usage**: Check the [Usage Guide](usage.md)
3. **API**: Browse the [API Reference](../api-reference.md)

## Architecture

For details on the project architecture, see [Architecture](../development/architecture.md).
