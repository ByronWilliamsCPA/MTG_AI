"""Alembic environment for the data lineage (``data`` schema).

Runs as the data writer role and records history in ``data.alembic_version_data``.
"""

from __future__ import annotations

from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import create_engine, inspect, pool, text

from mtg_ai.core.config import settings
from mtg_ai.schema import DataBase  # noqa: F401 - import registers data models
from mtg_ai.schema.base import DATA_SCHEMA

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

TARGET_SCHEMA = DATA_SCHEMA
VERSION_TABLE = "alembic_version_data"
target_metadata = DataBase.metadata
url = settings.data_database_url


def include_object(
    obj: Any,  # noqa: ANN401 - alembic passes heterogeneous schema objects
    name: str | None,  # noqa: ARG001
    type_: str,
    reflected: bool,  # noqa: ARG001
    compare_to: Any,  # noqa: ANN401, ARG001
) -> bool:
    """Restrict autogenerate to this lineage's schema."""
    if type_ == "table":
        return getattr(obj, "schema", None) in (TARGET_SCHEMA, None)
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        version_table=VERSION_TABLE,
        version_table_schema=TARGET_SCHEMA,
        include_schemas=True,
        include_object=include_object,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(url, poolclass=pool.NullPool, future=True)
    try:
        with engine.begin() as connection:
            # #ASSUME: external_resource: the target schema is pre-created by
            # scripts/sql/init-roles.sh with role ownership, so the writer role
            # holds no CREATE-on-database privilege (single-writer rule). Only
            # attempt CREATE SCHEMA when it is genuinely absent (e.g. an admin
            # bootstrap that skipped the init script), which keeps the grant
            # model intact in normal deployments.
            # #VERIFY: tests/integration/test_db_roles.py upgrades as the
            # unprivileged role against the pre-created schema.
            if TARGET_SCHEMA not in inspect(connection).get_schema_names():
                connection.execute(
                    text(f'CREATE SCHEMA IF NOT EXISTS "{TARGET_SCHEMA}"')
                )
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                version_table=VERSION_TABLE,
                version_table_schema=TARGET_SCHEMA,
                include_schemas=True,
                include_object=include_object,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
