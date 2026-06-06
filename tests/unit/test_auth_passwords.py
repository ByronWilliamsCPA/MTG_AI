"""Tests for PBKDF2 password hashing."""

from __future__ import annotations

import pytest

from mtg_ai.auth.passwords import hash_password, verify_password


@pytest.mark.unit
@pytest.mark.security
class TestPasswordHashing:
    """Behavioral tests for hash_password / verify_password."""

    def test_hash_is_self_describing_pbkdf2(self) -> None:
        encoded = hash_password("correct horse battery staple")
        algorithm, iterations, salt, digest = encoded.split("$")
        assert algorithm == "pbkdf2_sha256"
        assert int(iterations) > 0
        assert salt
        assert digest

    def test_verify_accepts_correct_password(self) -> None:
        encoded = hash_password("s3cret-passphrase")
        assert verify_password("s3cret-passphrase", encoded) is True

    def test_verify_rejects_wrong_password(self) -> None:
        encoded = hash_password("s3cret-passphrase")
        assert verify_password("not-the-password", encoded) is False

    def test_hashes_are_salted_and_unique(self) -> None:
        first = hash_password("same-password")
        second = hash_password("same-password")
        assert first != second
        assert verify_password("same-password", first)
        assert verify_password("same-password", second)

    def test_custom_iteration_count_is_recorded(self) -> None:
        encoded = hash_password("pw", iterations=12345)
        assert encoded.split("$")[1] == "12345"
        assert verify_password("pw", encoded) is True

    @pytest.mark.parametrize(
        "malformed",
        [
            "",
            "notahash",
            "pbkdf2_sha256$only$three",
            "bcrypt$12$salt$digest",
            "pbkdf2_sha256$notanint$c2FsdA==$ZGln",
            "pbkdf2_sha256$1000$!!!notbase64$ZGln",
            "pbkdf2_sha256$0$c2FsdA==$ZGln",
        ],
    )
    def test_verify_returns_false_for_malformed_hash(self, malformed: str) -> None:
        assert verify_password("anything", malformed) is False
