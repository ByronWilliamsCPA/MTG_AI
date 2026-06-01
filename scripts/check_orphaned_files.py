#!/usr/bin/env python3
"""Check for orphaned conditional files based on .cruft.json context.

This script validates that the project's file structure matches the feature
flags configured in .cruft.json. It detects files that exist but shouldn't
based on disabled features.

IMPORTANT: This is a CI validation script. It does NOT modify files - it only
reports mismatches. Use cleanup_conditional_files.py to fix issues.

Usage:
    python scripts/check_orphaned_files.py

Exit Codes:
    0 - No orphaned files found
    1 - Orphaned files detected (CI should fail)
    2 - Configuration error (missing .cruft.json, etc.)

Example in CI:
    - name: Check for orphaned conditional files
      run: python scripts/check_orphaned_files.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from _cleanup_shared import get_cruft_context


def check_orphaned_files(context: dict) -> list[tuple[str, str, Path]]:
    """Check for orphaned files based on context settings.

    Args:
        context: Cookiecutter context from .cruft.json.

    Returns:
        List of tuples: (feature_name, setting, orphaned_path)
    """
    project_slug = context.get("project_slug", "")
    if not project_slug:
        return []

    src_dir = Path(f"src/{project_slug}")
    orphaned: list[tuple[str, str, Path]] = []

    # Define conditional file mappings
    # Each entry is a tuple of (feature_key, disabled_value, paths_to_check).
    conditional_files: list[tuple[str, str, list[Path]]] = [
        ("include_cli", "no", [src_dir / "cli.py"]),
        (
            "use_mkdocs",
            "no",
            [
                Path("mkdocs.yml"),
                Path("docs"),
                Path("tools/validate_front_matter.py"),
                Path("tools/frontmatter_contract"),
                Path(".github/workflows/docs.yml"),
            ],
        ),
        ("include_nox", "no", [Path("noxfile.py")]),
        ("use_pre_commit", "no", [Path(".pre-commit-config.yaml")]),
        ("include_code_of_conduct", "no", [Path("CODE_OF_CONDUCT.md")]),
        ("include_security_policy", "no", [Path("SECURITY.md")]),
        ("include_contributing_guide", "no", [Path("CONTRIBUTING.md")]),
        (
            "include_codecov",
            "no",
            [Path("codecov.yml"), Path(".github/workflows/codecov.yml")],
        ),
        (
            "include_sonarcloud",
            "no",
            [
                Path("sonar-project.properties"),
                Path(".github/workflows/sonarcloud.yml"),
            ],
        ),
        ("include_renovate", "no", [Path("renovate.json")]),
        ("include_coderabbit", "no", [Path(".coderabbit.yaml")]),
        ("include_semantic_release", "no", [Path(".github/workflows/release.yml")]),
        (
            "use_reuse_licensing",
            "no",
            [Path("REUSE.toml"), Path("LICENSES"), Path(".github/workflows/reuse.yml")],
        ),
        (
            "include_docker",
            "no",
            [
                Path("Dockerfile"),
                Path("docker-compose.yml"),
                Path("docker-compose.prod.yml"),
                Path(".dockerignore"),
                Path(".github/workflows/container-security.yml"),
            ],
        ),
        (
            "include_api_framework",
            "no",
            [
                src_dir / "api",
                src_dir / "middleware" / "security.py",
                src_dir / "middleware" / "correlation.py",
            ],
        ),
        ("include_sentry", "no", [src_dir / "core" / "sentry.py"]),
        ("include_background_jobs", "no", [src_dir / "jobs"]),
        ("include_caching", "no", [src_dir / "core" / "cache.py"]),
        ("include_load_testing", "no", [Path("tests/load")]),
        (
            "include_fuzzing",
            "no",
            [
                Path(".github/workflows/cifuzzy.yml"),
                Path(".clusterfuzzlite"),
                Path("fuzz"),
            ],
        ),
    ]

    for feature_key, disabled_value, paths in conditional_files:
        if context.get(feature_key) == disabled_value:
            orphaned.extend(
                (feature_key, disabled_value, path) for path in paths if path.exists()
            )

    return orphaned


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0=clean, 1=orphaned files found, 2=error).
    """
    print("🔍 Checking for orphaned conditional files...")

    try:
        context = get_cruft_context()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 2
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in .cruft.json: {e}")
        return 2

    orphaned = check_orphaned_files(context)

    if not orphaned:
        print("✅ No orphaned files found - project structure matches configuration!")
        return 0

    print(f"\n❌ ORPHANED FILES DETECTED: {len(orphaned)} file(s)/directory(ies)\n")
    print("The following files exist but should NOT based on .cruft.json settings:\n")

    for feature, setting, path in orphaned:
        print(f"  • {path}")
        print(f"    Feature: {feature} = '{setting}'")
        print()

    print("=" * 60)
    print("How to fix:")
    print("  1. Run: python scripts/cleanup_conditional_files.py")
    print("  2. Or manually delete the orphaned files")
    print("  3. Then commit the changes")
    print()
    print("Why did this happen?")
    print("  Cruft update only syncs file contents - it does NOT re-run")
    print("  post-generation hooks that clean up conditional files.")
    print("=" * 60)

    return 1


if __name__ == "__main__":
    sys.exit(main())
