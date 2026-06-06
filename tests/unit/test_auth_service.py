"""Tests for the authentication service against an in-memory database."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest

from mtg_ai.auth.service import (
    authenticate_user,
    create_user,
    get_user_by_username,
    get_user_for_token,
    issue_session,
)
from mtg_ai.core.exceptions import ValidationError

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as DBSession

# Fixture credentials (not real secrets). Kept as constants so no literal
# username/password pair appears in the source.
_PW = "pw-fixture"
_WRONG_PW = "wrong-pw"


@pytest.mark.unit
class TestUserProvisioning:
    def test_create_user_persists_hashed_password(self, db_session: DBSession) -> None:
        user = create_user(db_session, "alice", _PW)
        assert user.id is not None
        assert user.username == "alice"
        assert user.password_hash != _PW
        assert get_user_by_username(db_session, "alice") is not None

    def test_create_user_trims_username(self, db_session: DBSession) -> None:
        user = create_user(db_session, "  bob  ", _PW)
        assert user.username == "bob"

    def test_duplicate_username_is_rejected(self, db_session: DBSession) -> None:
        create_user(db_session, "carol", _PW)
        with pytest.raises(ValidationError):
            create_user(db_session, "carol", _WRONG_PW)

    @pytest.mark.parametrize(("username", "password"), [("", _PW), ("dave", "")])
    def test_empty_fields_are_rejected(
        self, db_session: DBSession, username: str, password: str
    ) -> None:
        with pytest.raises(ValidationError):
            create_user(db_session, username, password)


@pytest.mark.unit
@pytest.mark.security
class TestAuthentication:
    def test_authenticate_success(self, db_session: DBSession) -> None:
        create_user(db_session, "erin", _PW)
        user = authenticate_user(db_session, "erin", _PW)
        assert user is not None
        assert user.username == "erin"

    def test_authenticate_wrong_password(self, db_session: DBSession) -> None:
        create_user(db_session, "frank", _PW)
        assert authenticate_user(db_session, "frank", _WRONG_PW) is None

    def test_authenticate_unknown_user(self, db_session: DBSession) -> None:
        assert authenticate_user(db_session, "ghost", _WRONG_PW) is None


@pytest.mark.unit
@pytest.mark.security
class TestSessions:
    def test_issue_and_resolve_session(self, db_session: DBSession) -> None:
        user = create_user(db_session, "heidi", _PW)
        session_row, raw_token = issue_session(db_session, user)
        assert session_row.token_hash != raw_token
        resolved = get_user_for_token(db_session, raw_token)
        assert resolved is not None
        assert resolved.id == user.id

    def test_expired_session_does_not_resolve(self, db_session: DBSession) -> None:
        user = create_user(db_session, "ivan", _PW)
        past = datetime.datetime.now(
            tz=datetime.timezone.utc,  # noqa: UP017 - timezone.utc supports py3.10
        ) - datetime.timedelta(days=1)
        _, raw_token = issue_session(db_session, user, ttl_seconds=10, now=past)
        assert get_user_for_token(db_session, raw_token) is None

    def test_unknown_token_does_not_resolve(self, db_session: DBSession) -> None:
        assert get_user_for_token(db_session, "no-such-token") is None

    def test_empty_token_does_not_resolve(self, db_session: DBSession) -> None:
        assert get_user_for_token(db_session, "") is None

    def test_token_is_user_specific(self, db_session: DBSession) -> None:
        user_a = create_user(db_session, "judy", _PW)
        user_b = create_user(db_session, "mallory", _PW)
        _, token_a = issue_session(db_session, user_a)
        _, token_b = issue_session(db_session, user_b)
        assert get_user_for_token(db_session, token_a).id == user_a.id
        assert get_user_for_token(db_session, token_b).id == user_b.id
