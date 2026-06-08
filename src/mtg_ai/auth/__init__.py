"""Authentication: password hashing, session tokens, and the auth service."""

from __future__ import annotations

from mtg_ai.auth.passwords import hash_password, verify_password
from mtg_ai.auth.service import (
    authenticate_user,
    create_user,
    get_user_by_username,
    get_user_for_token,
    issue_session,
)
from mtg_ai.auth.tokens import generate_session_token, hash_token

__all__ = [
    "authenticate_user",
    "create_user",
    "generate_session_token",
    "get_user_by_username",
    "get_user_for_token",
    "hash_password",
    "hash_token",
    "issue_session",
    "verify_password",
]
