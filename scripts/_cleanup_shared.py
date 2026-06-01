"""Shared helpers for cleanup_conditional_files.py and check_orphaned_files.py.

Centralizes utilities that both scripts need (the cruft context loader).
Both scripts import the shared function via sibling import:

    from _cleanup_shared import get_cruft_context

This module has no module-level side effects and is safe to import.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def get_cruft_context() -> dict[str, Any]:
    """Read cookiecutter context from .cruft.json.

    Returns:
        Dictionary of cookiecutter context values.

    Raises:
        FileNotFoundError: If .cruft.json doesn't exist.
        json.JSONDecodeError: If .cruft.json is invalid JSON.
        ValueError: If .cruft.json does not contain a JSON object, or if
            the ``context`` or ``context.cookiecutter`` keys are missing
            or not a dict.
    """
    cruft_file = Path(".cruft.json")
    if not cruft_file.exists():
        msg = ".cruft.json not found. Is this a cruft-managed project?"
        raise FileNotFoundError(msg)

    cruft_data = json.loads(cruft_file.read_text(encoding="utf-8"))
    if not isinstance(cruft_data, dict):
        msg = f".cruft.json must contain a JSON object, got {type(cruft_data).__name__}"
        raise ValueError(msg)
    # #CRITICAL: Data Integrity: .cruft.json may exist but lack context.cookiecutter,
    # causing all callers to silently skip conditional cleanup with an empty dict.
    # #VERIFY: Both context and cookiecutter keys must be dicts before returning.
    context = cruft_data.get("context")
    if not isinstance(context, dict):
        msg = ".cruft.json missing or invalid 'context' key (expected dict)"
        raise ValueError(msg)
    cookiecutter = context.get("cookiecutter")
    if not isinstance(cookiecutter, dict):
        msg = (
            ".cruft.json missing or invalid 'context.cookiecutter' key (expected dict)"
        )
        raise ValueError(msg)
    return cookiecutter
