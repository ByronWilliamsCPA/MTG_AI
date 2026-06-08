"""Shared ``mtg_ai_schema`` package: SQLAlchemy models for both services.

This package is the single source of truth for the database shape, imported by
both the app service and the data service (see ADR-001). It defines two
independent declarative bases mapped to two Postgres schemas:

- :data:`mtg_ai.schema.base.DataBase` maps to the ``data`` schema. The data
  service is the sole writer of these tables (single-writer rule). The app
  service holds ``SELECT`` only.
- :data:`mtg_ai.schema.base.AppBase` maps to the ``app`` schema. The app
  service holds full DML on these tables (users, sessions, and, in later
  phases, decks, collections, and reviews).

Each base owns its own ``MetaData`` so the two Alembic lineages never collide
on a shared ``alembic_version`` table (see ADR-001).
"""

from __future__ import annotations

from mtg_ai.schema.app_models import Session, User
from mtg_ai.schema.base import (
    APP_SCHEMA,
    DATA_SCHEMA,
    NAMING_CONVENTION,
    AppBase,
    DataBase,
)
from mtg_ai.schema.data_models import SchemaMarker

__all__ = [
    "APP_SCHEMA",
    "DATA_SCHEMA",
    "NAMING_CONVENTION",
    "AppBase",
    "DataBase",
    "SchemaMarker",
    "Session",
    "User",
]
