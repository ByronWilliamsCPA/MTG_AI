---
title: "Usage"
schema_type: common
status: published
owner: core-maintainer
purpose: "Usage guide for MTG AI."
tags:
  - guide
  - usage
---

This guide covers common usage patterns for MTG AI.

## Installation

### From PyPI

```bash
pip install mtg-ai
```

### From Source

```bash
git clone https://github.com/ByronWilliamsCPA/MTG_AI
cd mtg_ai
uv sync --all-extras
```

## Command Line Interface

### Available Commands

```bash
# Show help
mtg_ai --help

# Hello command
mtg_ai hello --name "World"

# Show configuration
mtg_ai config
```

### Debug Mode

Enable debug logging:

```bash
mtg_ai --debug hello --name "Test"
```
## Library Usage

### Basic Import

```python
from mtg_ai import __version__

print(f"Version: {__version__}")
```

### Logging

```python
from mtg_ai.utils.logging import get_logger, setup_logging

# Setup logging
setup_logging(level="DEBUG", json_logs=False)

# Get a logger
logger = get_logger(__name__)
logger.info("Hello from MTG AI")
```
