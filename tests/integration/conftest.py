"""Fixtures for Postgres integration tests.

These tests prove database-level guarantees that SQLite cannot model: the
single-writer role rule and two non-colliding Alembic lineages (ADR-001). They
require a live Postgres with the roles and schemas from
``scripts/sql/init-roles.sh`` already applied (this is exactly what
``docker-compose up`` does on first start).

Provide two role connection URLs to enable them, otherwise they skip (replace
``<password>`` with the configured role passwords)::

    MTG_AI_IT_DATA_URL=postgresql+psycopg://mtg_ai_data:<password>@localhost:5432/mtg_ai
    MTG_AI_IT_APP_URL=postgresql+psycopg://mtg_ai_app:<password>@localhost:5432/mtg_ai
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator

DATA_URL_ENV = "MTG_AI_IT_DATA_URL"
APP_URL_ENV = "MTG_AI_IT_APP_URL"

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _require_role_urls() -> tuple[str, str]:
    data_url = os.environ.get(DATA_URL_ENV)
    app_url = os.environ.get(APP_URL_ENV)
    if not data_url or not app_url:
        pytest.skip(
            f"Set {DATA_URL_ENV} and {APP_URL_ENV} to run Postgres integration tests"
        )
    return data_url, app_url


@pytest.fixture(scope="session")
def role_urls() -> tuple[str, str]:
    """Return ``(data_url, app_url)`` or skip if not configured."""
    return _require_role_urls()


@pytest.fixture(scope="session")
def migrated_database(
    role_urls: tuple[str, str],
) -> Iterator[tuple[str, str]]:
    """Upgrade both lineages to head, then yield the role URLs.

    Each lineage is run as its owning role: the data lineage as the data writer,
    the app lineage as the app role (owner of the app schema). The environment
    variables and the settings object are mutated to point Alembic at the
    integration URLs, then restored afterwards so the rest of the suite is not
    affected.
    """
    from alembic import command
    from alembic.config import Config

    from mtg_ai.core import config as config_module

    data_url, app_url = role_urls
    ini_path = _PROJECT_ROOT / "alembic.ini"

    # Save state to restore after the session.
    saved_env = {
        key: os.environ.get(key)
        for key in ("MTG_AI_DATA_DATABASE_URL", "MTG_AI_DATABASE_URL")
    }
    saved_settings = config_module.settings

    try:
        # Point settings at the integration URLs before env.py imports them.
        # Done inside the try so a Settings() failure still triggers cleanup.
        os.environ["MTG_AI_DATA_DATABASE_URL"] = data_url
        os.environ["MTG_AI_DATABASE_URL"] = app_url
        config_module.settings = config_module.Settings()
        for section in ("data", "app"):
            config = Config(str(ini_path), ini_section=section)
            config.config_ini_section = section
            command.upgrade(config, "head")
        yield data_url, app_url
    finally:
        config_module.settings = saved_settings
        for key, value in saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
