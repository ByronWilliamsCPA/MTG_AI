"""FastAPI application factory for the app service.

Wires correlation and security middleware and mounts the versioned API routes.
The health router lives under ``/api/v1`` so the public surface is
``GET /api/v1/health`` (and its liveness/readiness/startup probes).
"""

from __future__ import annotations

from fastapi import FastAPI

from mtg_ai.api.auth import router as auth_router
from mtg_ai.api.health import router as health_router
from mtg_ai.middleware import CorrelationMiddleware, add_security_middleware

API_V1_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    app = FastAPI(
        title="MTG AI",
        version="0.1.0",
        description=(
            "Self-hosted competitive Commander (cEDH) deck-critique assistant."
        ),
    )

    # Starlette runs middleware in reverse registration order, so register
    # security first and correlation last. That makes CorrelationMiddleware the
    # outermost layer, so it still sets the correlation id even when a security
    # middleware (rate limit, SSRF) returns early without calling the app.
    add_security_middleware(app)
    app.add_middleware(CorrelationMiddleware)

    app.include_router(health_router, prefix=API_V1_PREFIX)
    app.include_router(auth_router, prefix=API_V1_PREFIX)

    return app
