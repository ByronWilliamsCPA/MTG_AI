"""app: initial baseline (users and sessions)

Creates the app-owned authentication tables for Phase 0 with explicit operations
so the revision is an immutable snapshot: replaying it on a fresh database always
creates exactly these tables, regardless of models added in later phases. Phases
2 and 3 add decks, collections, and reviews as incremental migrations.

Revision ID: 0001_app_initial
Revises:
Create Date: 2026-06-06
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_app_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        schema="app",
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_sessions"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["app.users.id"],
            name="fk_sessions_user_id_users",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("token_hash", name="uq_sessions_token_hash"),
        schema="app",
    )
    op.create_index(
        "ix_sessions_user_id", "sessions", ["user_id"], schema="app"
    )


def downgrade() -> None:
    op.drop_index("ix_sessions_user_id", table_name="sessions", schema="app")
    op.drop_table("sessions", schema="app")
    op.drop_table("users", schema="app")
