"""data: initial baseline (schema marker anchor)

Creates the data-owned tables for Phase 0 with explicit operations so the
revision is an immutable snapshot: replaying it on a fresh database always
creates exactly these tables, regardless of models added in later phases. Phase 1
adds the reference, corpus, and analytics tables as incremental migrations.

Revision ID: 0001_data_initial
Revises:
Create Date: 2026-06-06
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_data_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "schema_marker",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("component", sa.String(length=64), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_schema_marker"),
        sa.UniqueConstraint("component", name="uq_schema_marker_component"),
        schema="data",
    )


def downgrade() -> None:
    op.drop_table("schema_marker", schema="data")
