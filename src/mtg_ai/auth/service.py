"""Authentication service operating on a SQLAlchemy session.

These functions are pure with respect to the web layer (no FastAPI types), so
they are exercised directly by unit tests and reused by the CLI for user
provisioning.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from mtg_ai.auth.passwords import hash_password, verify_password
from mtg_ai.auth.tokens import generate_session_token, hash_token
from mtg_ai.core.config import settings
from mtg_ai.core.exceptions import ValidationError
from mtg_ai.schema.app_models import Session, User

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as DBSession

# datetime.UTC is 3.11+; the project supports 3.10, so use timezone.utc.
_UTC = datetime.timezone.utc  # noqa: UP017

# A fixed hash to verify against when a user is missing, so a failed login does
# exactly one PBKDF2 verification whether or not the user exists. This keeps the
# timing similar without doubling the work (one hash, not a fresh hash + verify).
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-equalization")


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(tz=_UTC)


def get_user_by_username(session: DBSession, username: str) -> User | None:
    """Return the user with the given username, or ``None``."""
    return session.scalars(select(User).where(User.username == username)).first()


def create_user(session: DBSession, username: str, password: str) -> User:
    """Create and persist a new user.

    Args:
        session: An open database session.
        username: The desired username (must be unique and non-empty).
        password: The plaintext password to hash and store.

    Returns:
        The persisted :class:`~mtg_ai.schema.app_models.User`.

    Raises:
        ValidationError: If the username is empty or already taken.
    """
    normalized = username.strip()
    if not normalized:
        msg = "Username must not be empty"
        raise ValidationError(msg, field="username")
    if not password:
        msg = "Password must not be empty"
        raise ValidationError(msg, field="password")
    if get_user_by_username(session, normalized) is not None:
        msg = "Username already exists"
        raise ValidationError(msg, field="username", value=normalized)

    user = User(username=normalized, password_hash=hash_password(password))
    session.add(user)
    session.flush()
    return user


def authenticate_user(
    session: DBSession,
    username: str,
    password: str,
) -> User | None:
    """Return the user if the credentials are valid, otherwise ``None``.

    Always runs exactly one password verification (against the real hash, or a
    fixed dummy hash when the user is missing) so a missing user is not
    detectably faster.
    """
    user = get_user_by_username(session, username.strip())
    password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
    is_valid = verify_password(password, password_hash)
    if user is None or not is_valid:
        return None
    return user


def issue_session(
    session: DBSession,
    user: User,
    *,
    ttl_seconds: int | None = None,
    now: datetime.datetime | None = None,
) -> tuple[Session, str]:
    """Create a session for a user and return ``(session_row, raw_token)``.

    The raw token is returned only here and is never stored; only its hash is
    persisted.
    """
    ttl = ttl_seconds if ttl_seconds is not None else settings.session_ttl_seconds
    issued_at = now if now is not None else _utcnow()
    raw_token = generate_session_token()
    session_row = Session(
        user_id=user.id,
        token_hash=hash_token(raw_token),
        expires_at=issued_at + datetime.timedelta(seconds=ttl),
    )
    session.add(session_row)
    session.flush()
    return session_row, raw_token


def get_user_for_token(
    session: DBSession,
    token: str,
    *,
    now: datetime.datetime | None = None,
) -> User | None:
    """Resolve a raw token to its user, or ``None`` if invalid or expired."""
    if not token:
        return None
    current = now if now is not None else _utcnow()
    session_row = session.scalars(
        select(Session).where(Session.token_hash == hash_token(token))
    ).first()
    if session_row is None:
        return None
    expires_at = session_row.expires_at
    # SQLite returns naive datetimes; treat them as UTC for comparison.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=_UTC)
    if expires_at <= current:
        return None
    return session_row.user
