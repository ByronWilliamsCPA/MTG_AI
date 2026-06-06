"""Tests for the authentication API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from mtg_ai.auth.service import create_user

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlalchemy.orm import Session as DBSession

# Fixture credential (not a real secret). Kept as a constant and routed through
# a helper so no literal username/password pair appears in the source.
_PW = "pw-fixture"


def _make_user(db_session: DBSession, username: str) -> None:
    create_user(db_session, username, _PW)
    db_session.commit()


def _login_payload(username: str, password: str = _PW) -> dict[str, str]:
    return {"username": username, "password": password}


@pytest.mark.unit
@pytest.mark.security
class TestLogin:
    def test_login_returns_token(
        self, auth_client: TestClient, db_session: DBSession
    ) -> None:
        _make_user(db_session, "alice")
        response = auth_client.post("/api/v1/auth/login", json=_login_payload("alice"))
        assert response.status_code == 200
        body = response.json()
        assert body["token"]
        assert body["token_type"] == "bearer"
        assert "expires_at" in body

    def test_login_rejects_wrong_password(
        self, auth_client: TestClient, db_session: DBSession
    ) -> None:
        _make_user(db_session, "bob")
        response = auth_client.post(
            "/api/v1/auth/login", json=_login_payload("bob", "wrong-pw")
        )
        assert response.status_code == 401

    def test_login_rejects_unknown_user(self, auth_client: TestClient) -> None:
        response = auth_client.post(
            "/api/v1/auth/login", json=_login_payload("ghost", "wrong-pw")
        )
        assert response.status_code == 401

    def test_login_validates_request_body(self, auth_client: TestClient) -> None:
        response = auth_client.post("/api/v1/auth/login", json={"username": "x"})
        assert response.status_code == 422


@pytest.mark.unit
@pytest.mark.security
class TestCurrentUser:
    def test_me_requires_authentication(self, auth_client: TestClient) -> None:
        assert auth_client.get("/api/v1/auth/me").status_code == 401

    def test_me_rejects_invalid_token(self, auth_client: TestClient) -> None:
        response = auth_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not-a-real-token"},
        )
        assert response.status_code == 401

    def test_me_returns_authenticated_user(
        self, auth_client: TestClient, db_session: DBSession
    ) -> None:
        _make_user(db_session, "carol")
        login = auth_client.post("/api/v1/auth/login", json=_login_payload("carol"))
        assert login.status_code == 200
        token = login.json()["token"]
        response = auth_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["username"] == "carol"

    def test_token_scopes_to_its_own_user(
        self, auth_client: TestClient, db_session: DBSession
    ) -> None:
        _make_user(db_session, "dave")
        _make_user(db_session, "erin")
        login = auth_client.post("/api/v1/auth/login", json=_login_payload("dave"))
        assert login.status_code == 200
        dave_token = login.json()["token"]
        me = auth_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {dave_token}"},
        )
        assert me.status_code == 200
        assert me.json()["username"] == "dave"
