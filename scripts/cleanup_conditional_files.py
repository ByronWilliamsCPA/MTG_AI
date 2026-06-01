#!/usr/bin/env python3
"""Clean up conditional files based on .cruft.json context.

This script reads the cookiecutter context from .cruft.json and removes
files that should not exist based on the feature flags configured during
project generation.

IMPORTANT: Run this script after `cruft update` to ensure conditional files
are properly removed. Cruft updates only sync file contents - it does NOT
re-run post-generation hooks that clean up conditional files.

Usage:
    python scripts/cleanup_conditional_files.py [--dry-run]

Options:
    --dry-run    Show what would be removed without actually removing

Example:
    # After running cruft update
    cruft update
    python scripts/cleanup_conditional_files.py

    # Preview what would be removed
    python scripts/cleanup_conditional_files.py --dry-run
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from _cleanup_shared import get_cruft_context


def remove_file(filepath: Path, dry_run: bool = False) -> bool:
    """Remove a file if it exists.

    Args:
        filepath: Path to the file to remove.
        dry_run: If True, only report what would be removed.

    Returns:
        True if file was removed (or would be), False if file didn't exist.
    """
    if filepath.exists():
        if dry_run:
            print(f"  [DRY RUN] Would remove: {filepath}")
        else:
            filepath.unlink()
            print(f"  ✓ Removed: {filepath}")
        return True
    return False


def remove_dir(dirpath: Path, dry_run: bool = False) -> bool:
    """Remove a directory if it exists.

    Args:
        dirpath: Path to the directory to remove.
        dry_run: If True, only report what would be removed.

    Returns:
        True if directory was removed (or would be), False if it didn't exist.
    """
    if dirpath.exists():
        if dry_run:
            print(f"  [DRY RUN] Would remove: {dirpath}/")
        else:
            shutil.rmtree(dirpath)
            print(f"  ✓ Removed: {dirpath}/")
        return True
    return False


def get_project_slug(context: dict) -> str:
    """Extract project_slug from context.

    Args:
        context: Cookiecutter context dictionary.

    Returns:
        Project slug string.
    """
    return context.get("project_slug", "")


def _cleanup_for_no_cli(src_dir: Path, dry_run: bool) -> int:
    """Remove CLI module when include_cli is no."""
    return 1 if remove_file(src_dir / "cli.py", dry_run) else 0


def _cleanup_for_no_mkdocs(dry_run: bool) -> int:
    """Remove MkDocs files and tools when use_mkdocs is no.

    Note: the workflows/docs.yml file is handled by _cleanup_for_no_mkdocs_workflow
    so that it can also be invoked when include_github_actions is no.
    """
    count = 0
    if remove_file(Path("mkdocs.yml"), dry_run):
        count += 1
    if remove_dir(Path("docs"), dry_run):
        count += 1
    if remove_file(Path("tools/validate_front_matter.py"), dry_run):
        count += 1
    if remove_dir(Path("tools/frontmatter_contract"), dry_run):
        count += 1
    return count


def _cleanup_for_no_mkdocs_workflow(dry_run: bool) -> int:
    """Remove MkDocs-related workflow files when MkDocs is disabled."""
    count = 0
    if remove_file(Path(".github/workflows/docs.yml"), dry_run):
        count += 1
    return count


def _cleanup_for_no_nox(dry_run: bool) -> int:
    """Remove noxfile.py when include_nox is no."""
    return 1 if remove_file(Path("noxfile.py"), dry_run) else 0


def _cleanup_for_no_pre_commit(dry_run: bool) -> int:
    """Remove the pre-commit config when use_pre_commit is no."""
    return 1 if remove_file(Path(".pre-commit-config.yaml"), dry_run) else 0


def _cleanup_for_no_code_of_conduct(dry_run: bool) -> int:
    """Remove CODE_OF_CONDUCT.md when include_code_of_conduct is no."""
    return 1 if remove_file(Path("CODE_OF_CONDUCT.md"), dry_run) else 0


def _cleanup_for_no_security_policy(dry_run: bool) -> int:
    """Remove SECURITY.md when include_security_policy is no."""
    return 1 if remove_file(Path("SECURITY.md"), dry_run) else 0


def _cleanup_for_no_contributing_guide(dry_run: bool) -> int:
    """Remove CONTRIBUTING.md when include_contributing_guide is no."""
    return 1 if remove_file(Path("CONTRIBUTING.md"), dry_run) else 0


def _cleanup_for_no_codecov(dry_run: bool) -> int:
    """Remove Codecov config and workflow when include_codecov is no."""
    count = 0
    if remove_file(Path("codecov.yml"), dry_run):
        count += 1
    if remove_file(Path(".github/workflows/codecov.yml"), dry_run):
        count += 1
    return count


def _cleanup_for_no_sonarcloud(dry_run: bool) -> int:
    """Remove SonarCloud config and workflow when include_sonarcloud is no."""
    count = 0
    if remove_file(Path("sonar-project.properties"), dry_run):
        count += 1
    if remove_file(Path(".github/workflows/sonarcloud.yml"), dry_run):
        count += 1
    return count


def _cleanup_for_no_renovate(dry_run: bool) -> int:
    """Remove renovate.json when include_renovate is no."""
    return 1 if remove_file(Path("renovate.json"), dry_run) else 0


def _cleanup_for_no_coderabbit(dry_run: bool) -> int:
    """Remove .coderabbit.yaml when include_coderabbit is no."""
    return 1 if remove_file(Path(".coderabbit.yaml"), dry_run) else 0


def _cleanup_for_no_semantic_release(dry_run: bool) -> int:
    """Remove semantic release workflow when include_semantic_release is no."""
    return 1 if remove_file(Path(".github/workflows/release.yml"), dry_run) else 0


def _cleanup_for_no_reuse_licensing(dry_run: bool) -> int:
    """Remove REUSE licensing files when use_reuse_licensing is no."""
    count = 0
    if remove_file(Path("REUSE.toml"), dry_run):
        count += 1
    if remove_dir(Path("LICENSES"), dry_run):
        count += 1
    if remove_file(Path(".github/workflows/reuse.yml"), dry_run):
        count += 1
    return count


def _cleanup_for_no_docker(dry_run: bool) -> int:
    """Remove Docker files when include_docker is no."""
    count = 0
    if remove_file(Path("Dockerfile"), dry_run):
        count += 1
    if remove_file(Path("docker-compose.yml"), dry_run):
        count += 1
    if remove_file(Path("docker-compose.prod.yml"), dry_run):
        count += 1
    if remove_file(Path(".dockerignore"), dry_run):
        count += 1
    if remove_file(Path(".github/workflows/container-security.yml"), dry_run):
        count += 1
    return count


def _cleanup_for_no_api_framework(src_dir: Path, dry_run: bool) -> int:
    """Remove API framework files; also drop middleware dir if it ends up empty."""
    count = 0
    api_dir = src_dir / "api"
    if remove_dir(api_dir, dry_run):
        count += 1
    if remove_file(src_dir / "middleware" / "security.py", dry_run):
        count += 1
    if remove_file(src_dir / "middleware" / "correlation.py", dry_run):
        count += 1
    middleware_dir = src_dir / "middleware"
    if middleware_dir.exists() and not any(
        f
        for f in middleware_dir.iterdir()
        if f.name not in ("__pycache__", "__init__.py")
    ):
        if remove_dir(middleware_dir, dry_run):
            count += 1
    return count


def _cleanup_for_no_health_checks(src_dir: Path, dry_run: bool) -> int:
    """Drop the health.py module when only health-check sub-feature is disabled."""
    return 1 if remove_file(src_dir / "api" / "health.py", dry_run) else 0


def _cleanup_for_no_sentry(src_dir: Path, dry_run: bool) -> int:
    """Remove sentry.py when include_sentry is no."""
    return 1 if remove_file(src_dir / "core" / "sentry.py", dry_run) else 0


def _cleanup_for_no_background_jobs(src_dir: Path, dry_run: bool) -> int:
    """Remove jobs directory when include_background_jobs is no."""
    return 1 if remove_dir(src_dir / "jobs", dry_run) else 0


def _cleanup_for_no_caching(src_dir: Path, dry_run: bool) -> int:
    """Remove cache.py when include_caching is no."""
    return 1 if remove_file(src_dir / "core" / "cache.py", dry_run) else 0


def _cleanup_for_no_load_testing(dry_run: bool) -> int:
    """Remove tests/load directory when include_load_testing is no."""
    return 1 if remove_dir(Path("tests/load"), dry_run) else 0


def _cleanup_for_no_fuzzing(dry_run: bool) -> int:
    """Remove fuzzing files when include_fuzzing is no."""
    count = 0
    if remove_file(Path(".github/workflows/cifuzzy.yml"), dry_run):
        count += 1
    if remove_dir(Path(".clusterfuzzlite"), dry_run):
        count += 1
    if remove_dir(Path("fuzz"), dry_run):
        count += 1
    return count


def _cleanup_for_no_github_actions(dry_run: bool) -> int:
    """Remove .github directory when include_github_actions is no."""
    return 1 if remove_dir(Path(".github"), dry_run) else 0


def cleanup_conditional_files(context: dict, dry_run: bool = False) -> int:
    """Remove files based on cookiecutter context settings.

    Dispatches to per-feature helpers. Each helper handles ONE include_*
    or use_* flag and returns its own count.

    Args:
        context: Cookiecutter context from .cruft.json.
        dry_run: If True, only report what would be removed.

    Returns:
        Number of files/directories removed.
    """
    project_slug = get_project_slug(context)
    if not project_slug:
        print("❌ Could not determine project_slug from .cruft.json")
        return 0

    src_dir = Path(f"src/{project_slug}")
    print("\n🧹 Cleaning up conditional files...")

    removed = 0
    if context.get("include_cli") == "no":
        removed += _cleanup_for_no_cli(src_dir, dry_run)
    if context.get("use_mkdocs") == "no":
        removed += _cleanup_for_no_mkdocs(dry_run)
    if context.get("include_nox") == "no":
        removed += _cleanup_for_no_nox(dry_run)
    if context.get("use_pre_commit") == "no":
        removed += _cleanup_for_no_pre_commit(dry_run)
    if context.get("include_code_of_conduct") == "no":
        removed += _cleanup_for_no_code_of_conduct(dry_run)
    if context.get("include_security_policy") == "no":
        removed += _cleanup_for_no_security_policy(dry_run)
    if context.get("include_contributing_guide") == "no":
        removed += _cleanup_for_no_contributing_guide(dry_run)
    if context.get("include_codecov") == "no":
        removed += _cleanup_for_no_codecov(dry_run)
    if context.get("include_sonarcloud") == "no":
        removed += _cleanup_for_no_sonarcloud(dry_run)
    if context.get("include_renovate") == "no":
        removed += _cleanup_for_no_renovate(dry_run)
    if context.get("include_coderabbit") == "no":
        removed += _cleanup_for_no_coderabbit(dry_run)
    if context.get("include_semantic_release") == "no":
        removed += _cleanup_for_no_semantic_release(dry_run)
    if context.get("use_reuse_licensing") == "no":
        removed += _cleanup_for_no_reuse_licensing(dry_run)
    if context.get("include_docker") == "no":
        removed += _cleanup_for_no_docker(dry_run)
    if context.get("include_api_framework") == "no":
        removed += _cleanup_for_no_api_framework(src_dir, dry_run)
    elif context.get("include_health_checks") == "no":
        removed += _cleanup_for_no_health_checks(src_dir, dry_run)
    if context.get("include_sentry") == "no":
        removed += _cleanup_for_no_sentry(src_dir, dry_run)
    if context.get("include_background_jobs") == "no":
        removed += _cleanup_for_no_background_jobs(src_dir, dry_run)
    if context.get("include_caching") == "no":
        removed += _cleanup_for_no_caching(src_dir, dry_run)
    if context.get("include_load_testing") == "no":
        removed += _cleanup_for_no_load_testing(dry_run)
    if context.get("include_fuzzing") == "no":
        removed += _cleanup_for_no_fuzzing(dry_run)
    if context.get("include_github_actions") == "no":
        removed += _cleanup_for_no_github_actions(dry_run)
    if context.get("use_mkdocs") == "no":
        removed += _cleanup_for_no_mkdocs_workflow(dry_run)

    return removed


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("🔍 Running in dry-run mode (no files will be removed)")

    try:
        context = get_cruft_context()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in .cruft.json: {e}")
        return 1

    removed_count = cleanup_conditional_files(context, dry_run)

    if removed_count > 0:
        action = "would be removed" if dry_run else "removed"
        print(f"\n✅ {removed_count} file(s)/directory(ies) {action}")
    else:
        print("\n✅ No orphaned files found - project is clean!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
