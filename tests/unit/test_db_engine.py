"""Tests for the database engine and session helpers."""

from __future__ import annotations

import pytest
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session

from mtg_ai.db import engine as engine_module
from mtg_ai.db.engine import (
    create_db_engine,
    create_session_factory,
    get_session,
    reset_engine_state,
)


@pytest.mark.unit
class TestEngineCreation:
    def test_create_sqlite_engine_attaches_schemas(self) -> None:
        engine = create_db_engine("sqlite://")
        try:
            with engine.connect() as connection:
                rows = connection.execute(text("PRAGMA database_list")).fetchall()
            names = {row[1] for row in rows}
            assert {"data", "app"}.issubset(names)
        finally:
            engine.dispose()

    def test_session_factory_yields_sessions(self, db_engine: object) -> None:
        assert isinstance(db_engine, Engine)
        factory = create_session_factory(db_engine)
        with factory() as session:
            assert isinstance(session, Session)


@pytest.mark.unit
class TestGetSessionDependency:
    def test_get_session_yields_and_closes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            engine_module.settings, "database_url", "sqlite://", raising=False
        )
        reset_engine_state()
        try:
            generator = get_session()
            session = next(generator)
            assert isinstance(session, Session)
            close_calls: list[bool] = []
            monkeypatch.setattr(
                session, "close", lambda: close_calls.append(True), raising=False
            )
            # Exhaust the generator to trigger the finally/close branch.
            with pytest.raises(StopIteration):
                next(generator)
            assert close_calls == [True]
        finally:
            reset_engine_state()

    def test_get_session_requires_database_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from mtg_ai.core.exceptions import ConfigurationError

        monkeypatch.setattr(engine_module.settings, "database_url", "", raising=False)
        reset_engine_state()
        try:
            with pytest.raises(ConfigurationError, match="MTG_AI_DATABASE_URL"):
                next(get_session())
        finally:
            reset_engine_state()

    def test_get_session_rolls_back_on_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from sqlalchemy import text

        monkeypatch.setattr(
            engine_module.settings, "database_url", "sqlite://", raising=False
        )
        reset_engine_state()
        try:
            generator = get_session()
            session = next(generator)
            # Open a transaction so the in_transaction() rollback branch runs.
            session.execute(text("SELECT 1"))
            rollback_calls: list[bool] = []
            close_calls: list[bool] = []
            monkeypatch.setattr(
                session,
                "rollback",
                lambda: rollback_calls.append(True),
                raising=False,
            )
            monkeypatch.setattr(
                session, "close", lambda: close_calls.append(True), raising=False
            )
            # Throwing into the generator exercises the rollback/close branch.
            with pytest.raises(ValueError, match="boom"):
                generator.throw(ValueError("boom"))
            assert rollback_calls == [True]
            assert close_calls == [True]
        finally:
            reset_engine_state()
