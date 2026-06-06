"""Declarative bases, schema names, and shared mixins for the data model.

Two declarative bases keep the data-owned and app-owned tables in separate
Postgres schemas with separate ``MetaData`` objects. This is what lets the two
Alembic lineages run without colliding: each lineage targets one base's
metadata and records its history in a ``version_table`` scoped to its own schema
(see ADR-001).
"""

from __future__ import annotations

# Runtime imports: SQLAlchemy resolves Mapped[...] annotations at mapping time
# and uses uuid.uuid4 as a column default, so these cannot be typing-only.
import datetime  # noqa: TC003
import uuid

from sqlalchemy import DateTime, MetaData, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Postgres schema names. The same names are used as attached-database names when
# the test suite runs on in-memory SQLite (see mtg_ai.db.engine), so that
# schema-qualified table names resolve in both engines.
DATA_SCHEMA = "data"
APP_SCHEMA = "app"

# Deterministic constraint and index names. Required for Alembic autogenerate to
# emit stable, reviewable migration names instead of backend-default ones.
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class DataBase(DeclarativeBase):
    """Declarative base for data-owned tables (``data`` schema).

    The data service is the only writer of these tables. The app service
    connects with a restricted role that holds ``SELECT`` only.
    """

    metadata = MetaData(schema=DATA_SCHEMA, naming_convention=NAMING_CONVENTION)


class AppBase(DeclarativeBase):
    """Declarative base for app-owned tables (``app`` schema).

    The app service holds full DML on these tables.
    """

    metadata = MetaData(schema=APP_SCHEMA, naming_convention=NAMING_CONVENTION)


class UUIDPrimaryKeyMixin:
    """Mixin providing a UUID surrogate primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    """Mixin providing a database-populated ``created_at`` column."""

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
