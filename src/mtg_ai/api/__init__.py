"""API package for MTG AI.

This package contains FastAPI routers and API-related functionality.
"""

from __future__ import annotations

from mtg_ai.api.health import router as health_router

__all__ = ["health_router"]
