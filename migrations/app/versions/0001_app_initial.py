"""app: initial baseline (users and sessions)

Creates the app-owned authentication tables for Phase 0. The baseline is created
directly from the model metadata so the migration and the ORM never drift.
Phases 2 and 3 add decks, collections, and reviews as incremental migrations.

Revision ID: 0001_app_initial
Revises:
Create Date: 2026-06-06
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

from mtg_ai.schema import AppBase

revision: str = "0001_app_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    AppBase.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    AppBase.metadata.drop_all(bind=op.get_bind())
