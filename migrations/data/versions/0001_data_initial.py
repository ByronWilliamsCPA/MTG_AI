"""data: initial baseline (schema marker anchor)

Creates the data-owned tables for Phase 0. The baseline is created directly from
the model metadata so the migration and the ORM never drift. Phase 1 adds the
reference, corpus, and analytics tables as incremental migrations.

Revision ID: 0001_data_initial
Revises:
Create Date: 2026-06-06
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

from mtg_ai.schema import DataBase

revision: str = "0001_data_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    DataBase.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    DataBase.metadata.drop_all(bind=op.get_bind())
