"""ASGI entrypoint for the app service.

Referenced by the container image as ``mtg_ai.main:app`` and runnable locally
with ``uvicorn mtg_ai.main:app``.
"""

from __future__ import annotations

from mtg_ai.api.app import create_app

app = create_app()
