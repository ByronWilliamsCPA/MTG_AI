"""Tests for the shared schema package structure."""

from __future__ import annotations

import pytest

from mtg_ai.schema import AppBase, DataBase, Session, User
from mtg_ai.schema.base import APP_SCHEMA, DATA_SCHEMA
from mtg_ai.schema.data_models import SchemaMarker


@pytest.mark.unit
class TestSchemaSeparation:
    def test_data_and_app_use_distinct_metadata(self) -> None:
        assert DataBase.metadata is not AppBase.metadata

    def test_app_tables_live_in_app_schema(self) -> None:
        assert User.__table__.schema == APP_SCHEMA
        assert Session.__table__.schema == APP_SCHEMA

    def test_data_tables_live_in_data_schema(self) -> None:
        assert SchemaMarker.__table__.schema == DATA_SCHEMA

    def test_app_metadata_contains_only_app_tables(self) -> None:
        assert set(AppBase.metadata.tables) == {"app.users", "app.sessions"}

    def test_data_metadata_contains_only_data_tables(self) -> None:
        assert set(DataBase.metadata.tables) == {"data.schema_marker"}


@pytest.mark.unit
class TestModelColumns:
    def test_user_has_unique_username(self) -> None:
        assert User.__table__.c.username.unique is True

    def test_session_references_user(self) -> None:
        foreign_keys = list(Session.__table__.c.user_id.foreign_keys)
        assert len(foreign_keys) == 1
        assert foreign_keys[0].column.table.name == "users"

    def test_session_token_hash_is_unique(self) -> None:
        assert Session.__table__.c.token_hash.unique is True
