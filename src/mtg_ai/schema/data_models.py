"""Data-owned models (``data`` schema), written only by the data service.

Phase 0 establishes the ``data`` schema and its Alembic lineage with a single
anchor table. The Reference, Corpus, and Analytics tables described in ADR-002
(cards, crosswalk, synergy, combos, bracket rules) are added in Phase 1.

The anchor table also gives the single-writer integration test a concrete
data-owned target: the app-service role must be unable to write it.
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from mtg_ai.schema.base import DataBase, TimestampMixin


class SchemaMarker(TimestampMixin, DataBase):
    """A minimal data-owned table anchoring the ``data`` schema and lineage.

    Records which data-side components have been provisioned. Phase 1 reference
    and corpus tables join it in the same schema and writer role.
    """

    __tablename__ = "schema_marker"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    component: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    note: Mapped[str] = mapped_column(String(255), default="", nullable=False)
