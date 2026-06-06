"""Pytest configuration and shared fixtures for MTG AI tests.

This module provides:
- Test fixture paths and directories
- Pytest markers for test categorization
- Shared fixtures for common test resources
- Temporary directory management
"""

from pathlib import Path

import pytest

# ============================================================================
# Test Fixture Paths
# ============================================================================

# Root paths
PROJECT_ROOT = Path(__file__).parent.parent
FIXTURES_DIR = PROJECT_ROOT / "data" / "test_fixtures"
BENCHMARKS_DIR = PROJECT_ROOT / "data" / "benchmarks"


# ============================================================================
# Pytest Markers
# ============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Register custom pytest markers for test pyramid.

    Test Pyramid Markers:
        unit: Fast, isolated tests (no external dependencies)
        integration: Tests verifying component interaction
        security: Security-focused assertion tests
        perf: Performance and load tests
        slow: Tests that take significant time

    Args:
        config: Pytest configuration object.
    """
    # Test type markers (for test pyramid)
    config.addinivalue_line(
        "markers",
        "unit: Unit tests (fast, isolated, no external dependencies)",
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests (moderate speed, may use fixtures)",
    )
    config.addinivalue_line(
        "markers",
        "security: Security-focused tests (auth, input validation, etc.)",
    )
    config.addinivalue_line(
        "markers",
        "perf: Performance and load tests (benchmarking, stress testing)",
    )
    config.addinivalue_line(
        "markers",
        "performance: Alias for perf marker",
    )

    # Execution modifier markers
    config.addinivalue_line(
        "markers",
        "slow: Slow tests (can be excluded with -m 'not slow')",
    )
    config.addinivalue_line(
        "markers",
        "smoke: Smoke tests for quick sanity checks",
    )
    config.addinivalue_line(
        "markers",
        "regression: Regression tests for previously fixed bugs",
    )


# ============================================================================
# Fixture Directory Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """Return path to test fixtures directory.

    Returns:
        Path object pointing to the test fixtures directory.
    """
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def benchmarks_dir() -> Path:
    """Return path to benchmarks directory.

    Returns:
        Path object pointing to the benchmarks directory.
    """
    return BENCHMARKS_DIR


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Return temporary directory for test outputs.

    Creates and returns a clean temporary directory for each test to write
    output files.

    Args:
        tmp_path: Pytest's built-in tmp_path fixture.

    Returns:
        Path object pointing to the temporary output directory.
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def tmp_cache_dir(tmp_path: Path) -> Path:
    """Return temporary directory for caching.

    Creates and returns a clean temporary cache directory for each test.

    Args:
        tmp_path: Pytest's built-in tmp_path fixture.

    Returns:
        Path object pointing to the temporary cache directory.
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


# ============================================================================
# Logging Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def setup_logging() -> None:
    """Setup test logging configuration.

    Automatically applied to all tests to ensure consistent logging setup.
    """
    from mtg_ai.utils.logging import setup_logging

    setup_logging(level="DEBUG", json_logs=False, include_timestamp=False)


# ============================================================================
# Database and API Fixtures
# ============================================================================


@pytest.fixture
def db_engine() -> object:
    """Yield an in-memory SQLite engine with all tables created.

    The ``data`` and ``app`` schemas are attached so the schema-qualified models
    resolve on SQLite just as they do on Postgres.
    """
    from mtg_ai.db.engine import create_db_engine
    from mtg_ai.schema.base import AppBase, DataBase

    engine = create_db_engine("sqlite://")
    with engine.begin() as connection:
        DataBase.metadata.create_all(connection)
        AppBase.metadata.create_all(connection)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine: object) -> object:
    """Yield a SQLAlchemy session bound to the in-memory engine."""
    from sqlalchemy import Engine

    from mtg_ai.db.engine import create_session_factory

    assert isinstance(db_engine, Engine)
    factory = create_session_factory(db_engine)
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def auth_client(db_engine: object) -> object:
    """Yield a TestClient for a lean app exposing only the auth router.

    A lean app keeps these tests isolated from rate-limiting and other security
    middleware so they exercise authentication behavior deterministically.
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from sqlalchemy import Engine

    from mtg_ai.api.auth import router as auth_router
    from mtg_ai.db.engine import create_session_factory, get_session

    assert isinstance(db_engine, Engine)
    factory = create_session_factory(db_engine)

    app = FastAPI()
    app.include_router(auth_router, prefix="/api/v1")

    def _override_session() -> object:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = _override_session
    with TestClient(app) as client:
        yield client
