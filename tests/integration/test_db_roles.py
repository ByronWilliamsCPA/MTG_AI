"""Integration tests for the single-writer rule and Alembic lineages (ADR-001).

Skipped unless ``MTG_AI_IT_DATA_URL`` and ``MTG_AI_IT_APP_URL`` are set (see the
integration conftest). They prove guarantees that only a real Postgres with
distinct roles can enforce.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import DBAPIError

pytestmark = [pytest.mark.integration]


def _engine(url: str) -> Engine:
    return create_engine(url, future=True)


@pytest.mark.security
def test_app_role_cannot_write_data_tables(
    migrated_database: tuple[str, str],
) -> None:
    """The app role holds SELECT on data tables but cannot write them."""
    _data_url, app_url = migrated_database
    app_engine = _engine(app_url)
    try:
        # SELECT is allowed.
        with app_engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM data.schema_marker")).fetchall()
        # INSERT must be denied at the database level.
        with (
            pytest.raises(DBAPIError),
            app_engine.begin() as connection,
        ):
            connection.execute(
                text(
                    "INSERT INTO data.schema_marker (component, note) "
                    "VALUES ('illegal', 'should be denied')"
                )
            )
    finally:
        app_engine.dispose()


def test_data_role_can_write_data_tables(
    migrated_database: tuple[str, str],
) -> None:
    """The data writer role can write its own tables."""
    data_url, _app_url = migrated_database
    data_engine = _engine(data_url)
    marker = f"phase0-{uuid.uuid4()}"
    try:
        with data_engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO data.schema_marker (component, note) "
                    "VALUES (:component, 'ok')"
                ),
                {"component": marker},
            )
        with data_engine.connect() as connection:
            count = connection.execute(
                text("SELECT COUNT(*) FROM data.schema_marker WHERE component = :c"),
                {"c": marker},
            ).scalar_one()
        assert count == 1
    finally:
        data_engine.dispose()


def test_app_role_can_write_app_tables(
    migrated_database: tuple[str, str],
) -> None:
    """The app role holds full DML on its own tables."""
    _data_url, app_url = migrated_database
    app_engine = _engine(app_url)
    username = f"it-user-{uuid.uuid4()}"
    try:
        with app_engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO app.users (id, username, password_hash, created_at) "
                    "VALUES (:id, :username, 'x', now())"
                ),
                {"id": uuid.uuid4(), "username": username},
            )
        with app_engine.connect() as connection:
            count = connection.execute(
                text("SELECT COUNT(*) FROM app.users WHERE username = :username"),
                {"username": username},
            ).scalar_one()
        assert count == 1
    finally:
        app_engine.dispose()


def test_two_lineages_do_not_collide(
    migrated_database: tuple[str, str],
) -> None:
    """Each lineage records history in its own schema-scoped version table."""
    data_url, app_url = migrated_database
    data_engine = _engine(data_url)
    app_engine = _engine(app_url)
    try:
        with data_engine.connect() as connection:
            data_rev = connection.execute(
                text("SELECT version_num FROM data.alembic_version_data")
            ).scalar_one()
        with app_engine.connect() as connection:
            app_rev = connection.execute(
                text("SELECT version_num FROM app.alembic_version_app")
            ).scalar_one()
        assert data_rev == "0001_data_initial"
        assert app_rev == "0001_app_initial"
    finally:
        data_engine.dispose()
        app_engine.dispose()
