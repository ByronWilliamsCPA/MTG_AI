"""SQLAlchemy engine and session factory for the app service.

The app service connects with the restricted role (``SELECT`` on ``data``
tables, full DML on ``app`` tables). The connection URL is supplied by
configuration; nothing here grants write access it does not have.

For tests, an in-memory SQLite engine is supported. Because the models use
schema-qualified table names (``app.users``, ``data.schema_marker``), the
``data`` and ``app`` schemas are created as attached in-memory databases on
each new SQLite connection, so the same metadata resolves on both backends.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from mtg_ai.core.config import settings
from mtg_ai.core.exceptions import ConfigurationError
from mtg_ai.schema.base import APP_SCHEMA, DATA_SCHEMA

if TYPE_CHECKING:
    from collections.abc import Iterator

    from sqlalchemy.engine.interfaces import DBAPIConnection
    from sqlalchemy.pool import ConnectionPoolEntry

# Lazily-initialized process-wide app-service session factory. Tests that need a
# different engine override the FastAPI dependency instead of mutating this.
_app_session_factory: sessionmaker[Session] | None = None


def _is_sqlite(url: str) -> bool:
    """Return whether a database URL targets SQLite."""
    return url.startswith("sqlite")


def _register_sqlite_schema_attach(engine: Engine) -> None:
    """Attach ``data`` and ``app`` schemas on each new SQLite connection.

    SQLite has no native schema concept, but an attached database functions as
    one. Attaching in-memory databases named after the Postgres schemas lets
    schema-qualified models create and resolve on SQLite for tests.
    """

    @event.listens_for(engine, "connect")
    def _attach_schemas(  # pyright: ignore[reportUnusedFunction]
        dbapi_connection: DBAPIConnection,
        _connection_record: ConnectionPoolEntry,
    ) -> None:
        cursor = dbapi_connection.cursor()
        try:
            for schema in (DATA_SCHEMA, APP_SCHEMA):
                cursor.execute(f"ATTACH DATABASE ':memory:' AS {schema}")
        finally:
            cursor.close()


def create_db_engine(url: str, *, echo: bool = False) -> Engine:
    """Create a SQLAlchemy engine for the given URL.

    Args:
        url: A SQLAlchemy database URL.
        echo: Whether to log emitted SQL.

    Returns:
        A configured :class:`~sqlalchemy.Engine`.
    """
    connect_args: dict[str, Any] = {}
    engine_kwargs: dict[str, Any] = {"echo": echo, "future": True}
    if _is_sqlite(url):
        # A shared, single connection so an in-memory database persists across
        # the engine's lifetime and across requests within a test.
        connect_args["check_same_thread"] = False
        engine_kwargs["poolclass"] = StaticPool

    engine = create_engine(url, connect_args=connect_args, **engine_kwargs)
    if _is_sqlite(url):
        _register_sqlite_schema_attach(engine)
    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a session factory bound to an engine."""
    return sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


def _get_app_session_factory() -> sessionmaker[Session]:
    """Return the process-wide app-service session factory, creating it once."""
    global _app_session_factory  # noqa: PLW0603
    if _app_session_factory is None:
        if not settings.database_url:
            msg = "MTG_AI_DATABASE_URL is not set"
            raise ConfigurationError(msg)
        engine = create_db_engine(settings.database_url, echo=settings.sql_echo)
        _app_session_factory = create_session_factory(engine)
    return _app_session_factory


def reset_engine_state() -> None:
    """Discard the cached session factory.

    Used by tests that change configuration between cases. Production code never
    calls this.
    """
    global _app_session_factory  # noqa: PLW0603
    _app_session_factory = None


def get_session() -> Iterator[Session]:
    """Yield an app-service database session (FastAPI dependency).

    The session is rolled back on error and always closed. Endpoints commit
    explicitly when they intend to persist.
    """
    factory = _get_app_session_factory()
    session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
