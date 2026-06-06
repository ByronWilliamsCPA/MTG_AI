"""App-owned models (``app`` schema), written by the app service.

Phase 0 defines authentication tables only. Decks, collections, and reviews are
added in Phases 2 and 3. Every per-user table added later carries a ``user_id``
foreign key so the API can scope all access by owner.
"""

from __future__ import annotations

# Runtime imports: SQLAlchemy resolves Mapped[...] annotations at mapping time.
import datetime  # noqa: TC003
import uuid  # noqa: TC003

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mtg_ai.schema.base import APP_SCHEMA, AppBase, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, AppBase):
    """An application user with a hashed password.

    The password is never stored in plaintext. ``password_hash`` holds a
    self-describing PBKDF2-HMAC-SHA256 digest (see :mod:`mtg_ai.auth.passwords`),
    which is FIPS-approved; bcrypt is prohibited by project policy.
    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    sessions: Mapped[list[Session]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Session(UUIDPrimaryKeyMixin, TimestampMixin, AppBase):
    """An opaque, expiring session token bound to a user.

    Only the SHA-256 hash of the token is stored; the raw token is returned to
    the client once at login and never persisted. Lookups hash the presented
    token and match it here, so a database leak does not expose usable tokens.
    """

    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{APP_SCHEMA}.users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="sessions")
