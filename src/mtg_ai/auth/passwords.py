"""Password hashing using PBKDF2-HMAC-SHA256 (FIPS-approved).

The encoded hash is self-describing::

    pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>

so verification never depends on current configuration. Project policy
prohibits bcrypt; PBKDF2 and Argon2 are the approved choices, and PBKDF2 via the
standard library adds no dependency and is FIPS-approved.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from mtg_ai.core.config import settings

_ALGORITHM = "pbkdf2_sha256"
_SALT_BYTES = 16
_DIGEST = "sha256"


def _b64encode(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _b64decode(encoded: str) -> bytes:
    return base64.b64decode(encoded.encode("ascii"))


def hash_password(password: str, *, iterations: int | None = None) -> str:
    """Hash a password and return a self-describing encoded string.

    Args:
        password: The plaintext password.
        iterations: PBKDF2 iteration count; defaults to the configured value.

    Returns:
        The encoded ``pbkdf2_sha256$...`` hash string.
    """
    rounds = iterations if iterations is not None else settings.pbkdf2_iterations
    salt = secrets.token_bytes(_SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(_DIGEST, password.encode("utf-8"), salt, rounds)
    return f"{_ALGORITHM}${rounds}${_b64encode(salt)}${_b64encode(derived)}"


def verify_password(password: str, encoded: str) -> bool:
    """Verify a plaintext password against an encoded hash.

    Uses a constant-time comparison. Returns ``False`` for any malformed or
    unknown-algorithm hash rather than raising, so callers can treat all
    verification failures uniformly.

    Args:
        password: The plaintext password to check.
        encoded: A previously produced :func:`hash_password` string.

    Returns:
        ``True`` if the password matches, otherwise ``False``.
    """
    parts = encoded.split("$")
    expected_fields = 4
    if len(parts) != expected_fields:
        return False
    algorithm, rounds_str, salt_b64, hash_b64 = parts
    if algorithm != _ALGORITHM:
        return False
    try:
        rounds = int(rounds_str)
        salt = _b64decode(salt_b64)
        expected = _b64decode(hash_b64)
    except (ValueError, TypeError):
        # binascii.Error (raised by b64decode) is a subclass of ValueError.
        return False
    if rounds <= 0:
        return False
    derived = hashlib.pbkdf2_hmac(_DIGEST, password.encode("utf-8"), salt, rounds)
    return hmac.compare_digest(derived, expected)
