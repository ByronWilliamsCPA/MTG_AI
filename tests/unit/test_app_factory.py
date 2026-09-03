"""Tests for the FastAPI application factory wiring."""

from __future__ import annotations

import pytest
from fastapi import FastAPI

from mtg_ai.api.app import create_app
from mtg_ai.main import app as main_app


@pytest.mark.unit
class TestAppFactory:
    def test_create_app_returns_fastapi(self) -> None:
        assert isinstance(create_app(), FastAPI)

    def test_health_mounted_under_api_v1(self) -> None:
        # #EDGE: FastAPI >=0.141 resolves included sub-routers lazily, so
        # `app.routes` no longer exposes a flat list of `.path`-bearing
        # Route objects. The OpenAPI schema is the public, stable surface
        # for the fully-resolved path table. #VERIFY against FastAPI's
        # release notes before switching back to walking `app.routes`.
        paths = set(create_app().openapi()["paths"].keys())
        assert "/api/v1/health/live" in paths
        assert "/api/v1/health/ready" in paths

    def test_auth_routes_mounted_under_api_v1(self) -> None:
        paths = set(create_app().openapi()["paths"].keys())
        assert "/api/v1/auth/login" in paths
        assert "/api/v1/auth/me" in paths

    def test_main_module_exposes_app(self) -> None:
        assert isinstance(main_app, FastAPI)
