"""Opaque session tokens.

A token is high-entropy random data returned to the client once. Only its
SHA-256 hash is stored, so a database disclosure does not yield usable tokens.
SHA-256 is FIPS-approved.
"""

from __future__ import annotations

import hashlib
import secrets

_TOKEN_BYTES = 32


def generate_session_token() -> str:
    """Return a new URL-safe, high-entropy session token."""
    return secrets.token_urlsafe(_TOKEN_BYTES)


def hash_token(token: str) -> str:
    """Return the hex SHA-256 hash of a session token for storage and lookup."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
