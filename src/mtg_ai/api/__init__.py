"""API package for MTG AI.

This package contains the FastAPI application factory and routers.
"""

from __future__ import annotations

from mtg_ai.api.app import create_app
from mtg_ai.api.auth import router as auth_router
from mtg_ai.api.health import router as health_router

__all__ = ["auth_router", "create_app", "health_router"]
