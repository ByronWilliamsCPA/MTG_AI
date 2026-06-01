---
title: "Architecture"
schema_type: common
status: published
owner: core-maintainer
purpose: "Architecture documentation for MTG AI."
tags:
  - development
  - architecture
---

This document describes the architecture and design decisions for MTG AI.

## Project Structure

```text
mtg_ai/
├── src/
│   └── mtg_ai/
│       ├── __init__.py          # Package initialization
│       ├── core/                # Core functionality
│       │   ├── config.py        # Configuration with Pydantic
│       │   └── ...
│       ├── utils/               # Utility modules
│       │   ├── logging.py       # Structured logging
│       │   └── ...
│       └── cli.py               # CLI entry point
├── tests/                       # Test suite
├── docs/                        # Documentation
└── pyproject.toml               # Project configuration
```

## Design Principles

### 1. Type Safety

All code is fully typed with BasedPyright strict mode validation.

### 2. Structured Logging

Uses structlog for structured, JSON-formatted logs in production.

### 3. Configuration Management

Pydantic Settings for type-safe configuration from environment variables.

### 4. CLI Design

Click framework for robust command-line interface with subcommands.
## Dependencies

See `pyproject.toml` for the complete dependency list.

## Architecture Decision Records

See the [ADRs directory](../ADRs/README.md) for documented architecture decisions.
