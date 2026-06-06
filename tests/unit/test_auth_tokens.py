"""Tests for opaque session token generation and hashing."""

from __future__ import annotations

import hashlib

import pytest

from mtg_ai.auth.tokens import generate_session_token, hash_token


@pytest.mark.unit
@pytest.mark.security
class TestSessionTokens:
    def test_generated_tokens_are_unique(self) -> None:
        tokens = {generate_session_token() for _ in range(100)}
        assert len(tokens) == 100

    def test_generated_token_has_high_entropy_length(self) -> None:
        token = generate_session_token()
        # token_urlsafe(32) yields ~43 url-safe characters.
        assert len(token) >= 40

    def test_hash_token_is_sha256_hex(self) -> None:
        token = "a-known-token"
        assert hash_token(token) == hashlib.sha256(token.encode()).hexdigest()

    def test_hash_token_is_deterministic(self) -> None:
        token = generate_session_token()
        assert hash_token(token) == hash_token(token)

    def test_different_tokens_hash_differently(self) -> None:
        assert hash_token("token-a") != hash_token("token-b")
