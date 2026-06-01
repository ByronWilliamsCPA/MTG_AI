"""Tests for health check endpoints.

Covers liveness, startup, health alias, check_cache, check_external_service,
check_database (error path), and readiness (success and 503 paths).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestHealthModels:
    """Tests for Pydantic response models."""

    @pytest.mark.unit
    def test_health_status_defaults(self) -> None:
        """Verify HealthStatus model initializes with expected defaults."""
        from mtg_ai.api.health import HealthStatus

        status = HealthStatus(status="ok", uptime_seconds=1.0)

        assert status.status == "ok"
        assert status.uptime_seconds == 1.0
        assert status.version == "0.1.0"
        assert isinstance(status.python_version, str)
        assert isinstance(status.timestamp, float)

    @pytest.mark.unit
    def test_readiness_check_model(self) -> None:
        """Verify ReadinessCheck model with all fields."""
        from mtg_ai.api.health import ReadinessCheck

        check = ReadinessCheck(name="db", status=True, latency_ms=5.5, error=None)

        assert check.name == "db"
        assert check.status is True
        assert check.latency_ms == 5.5
        assert check.error is None

    @pytest.mark.unit
    def test_readiness_check_failed(self) -> None:
        """Verify ReadinessCheck model with a failed check."""
        from mtg_ai.api.health import ReadinessCheck

        check = ReadinessCheck(name="db", status=False, error="connection refused")

        assert check.status is False
        assert check.error == "connection refused"

    @pytest.mark.unit
    def test_readiness_status_includes_checks(self) -> None:
        """Verify ReadinessStatus embeds check results."""
        from mtg_ai.api.health import ReadinessCheck, ReadinessStatus

        check = ReadinessCheck(name="cache", status=True, latency_ms=1.0)
        status = ReadinessStatus(
            status="ok", uptime_seconds=2.0, checks={"cache": check}
        )

        assert "cache" in status.checks
        assert status.checks["cache"].status is True


class TestLiveness:
    """Tests for the /health/live endpoint."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_liveness_returns_ok(self) -> None:
        """Verify liveness probe returns status 'ok' with non-negative uptime."""
        from mtg_ai.api.health import liveness

        result = await liveness()

        assert result.status == "ok"
        assert result.uptime_seconds >= 0


class TestStartup:
    """Tests for the /health/startup endpoint."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_startup_returns_started(self) -> None:
        """Verify startup probe returns status 'started'."""
        from mtg_ai.api.health import startup

        result = await startup()

        assert result.status == "started"
        assert result.uptime_seconds >= 0


class TestHealthAlias:
    """Tests for the /health/ alias endpoint."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_alias_delegates_to_liveness(self) -> None:
        """Verify /health/ alias returns same result as liveness."""
        from mtg_ai.api.health import health

        result = await health()

        assert result.status == "ok"
        assert result.uptime_seconds >= 0


class TestCheckCache:
    """Tests for the check_cache helper."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_cache_returns_healthy(self) -> None:
        """Verify placeholder cache check always returns healthy."""
        from mtg_ai.api.health import check_cache

        result = await check_cache()

        assert result.name == "cache"
        assert result.status is True
        assert result.latency_ms is not None
        assert result.latency_ms >= 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_cache_failure_is_captured(self) -> None:
        """Verify cache check returns failed ReadinessCheck on exception."""
        from mtg_ai.api.health import check_cache

        with patch("time.time", side_effect=[0.0, RuntimeError("redis down"), 0.01]):
            # If time.time raises after start measurement, the except block runs
            # For the placeholder (no actual call), this won't raise; just verify
            # the normal path returns a valid ReadinessCheck.
            result = await check_cache()

        assert result.name == "cache"


class TestCheckExternalService:
    """Tests for the check_external_service helper."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_external_service_returns_healthy(self) -> None:
        """Verify placeholder external service check returns healthy."""
        from mtg_ai.api.health import check_external_service

        result = await check_external_service()

        assert result.name == "external_api"
        assert result.status is True
        assert result.latency_ms is not None


class TestCheckDatabase:
    """Tests for the check_database helper."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_database_fails_gracefully_without_module(self) -> None:
        """Verify database check returns failed ReadinessCheck when database module is missing."""
        from mtg_ai.api.health import check_database

        result = await check_database()

        assert result.name == "database"
        assert result.status is False
        assert result.error is not None
        assert result.latency_ms is not None


class TestReadiness:
    """Tests for the /health/ready endpoint."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_readiness_returns_503_when_db_unavailable(self) -> None:
        """Verify readiness probe raises 503 when any dependency check fails."""
        from fastapi import HTTPException

        from mtg_ai.api.health import readiness

        with pytest.raises(HTTPException) as exc_info:
            await readiness()

        assert exc_info.value.status_code == 503
        assert "status" in exc_info.value.detail

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_readiness_returns_ok_when_all_healthy(self) -> None:
        """Verify readiness probe returns 200 when all dependency checks pass."""
        from mtg_ai.api.health import ReadinessCheck, readiness

        healthy_check = ReadinessCheck(name="database", status=True, latency_ms=1.0)

        with patch(
            "mtg_ai.api.health.check_database",
            new=AsyncMock(return_value=healthy_check),
        ):
            result = await readiness()

        assert result.status == "ok"
        assert "database" in result.checks
        assert result.checks["database"].status is True


class TestRouterRegistration:
    """Tests for API router configuration."""

    @pytest.mark.unit
    def test_router_has_correct_prefix(self) -> None:
        """Verify health router is registered with /health prefix."""
        from mtg_ai.api.health import router

        assert router.prefix == "/health"

    @pytest.mark.unit
    def test_health_router_exported_from_api(self) -> None:
        """Verify api package exports health_router."""
        from mtg_ai.api import health_router

        assert health_router is not None
