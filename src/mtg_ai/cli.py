"""Command-line interface for MTG AI.

Provides commands for common operations and demonstrates Click best practices
with structured logging integration.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

import click

from mtg_ai.core.config import settings
from mtg_ai.utils.logging import get_logger

if TYPE_CHECKING:
    from alembic.config import Config
    from structlog.stdlib import BoundLogger

logger: BoundLogger = get_logger(__name__)


@dataclass
class CLIContext:
    """Typed context object for Click commands."""

    debug: bool = False


def _get_context(ctx: click.Context) -> CLIContext:
    """Return ctx.obj typed as CLIContext.

    Click's stubs declare ctx.obj as Any. This helper narrows the type so
    callers receive a CLIContext without per-site casts. If ctx.obj is
    somehow not a CLIContext at runtime (e.g., subcommand invoked without
    the parent group running), fall back to a default CLIContext.
    """
    # Cast from Any to object so basedpyright can narrow via isinstance.
    obj: object = cast("object", ctx.obj)
    if isinstance(obj, CLIContext):
        return obj
    return CLIContext()


@click.group()
@click.version_option(version="0.1.0", prog_name="mtg_ai")
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """MTG AI - Self-hosted competitive Commander (cEDH) deck-critique assistant: RAG over Scryfall/MTGJSON/meta data with a deterministic rules engine and a swappable generation backend.."""
    # Store typed context object for subcommands
    ctx.obj = CLIContext(debug=debug)

    if debug:
        logger.debug("Debug mode enabled")


@cli.command()
@click.option(
    "--name",
    "-n",
    type=str,
    default="World",
    help="Name to greet",
)
@click.pass_context
def hello(ctx: click.Context, name: str) -> None:
    """Greet the user with a personalized message."""
    try:
        cli_ctx = _get_context(ctx)

        logger.info(
            "Processing hello command",
            name=name,
            debug=cli_ctx.debug,
        )

        message = f"Hello, {name}!"
        click.echo(message)

        logger.info("Command completed successfully", result=message)

    except Exception as e:
        logger.exception("Command failed", error=str(e))
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def config(ctx: click.Context) -> None:
    """Display current configuration settings.

    Shows configuration values from environment variables or defaults.
    """
    try:
        cli_ctx = _get_context(ctx)

        logger.info("Retrieving configuration")

        click.echo("Current Configuration:")
        click.echo("  Project: MTG AI")
        click.echo("  Version: 0.1.0")
        click.echo(f"  Debug: {cli_ctx.debug}")
        click.echo(f"  Log Level: {settings.log_level}")

        logger.info("Configuration displayed successfully")

    except Exception as e:
        logger.exception("Failed to display configuration", error=str(e))
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


_LINEAGES = ("data", "app")


def _alembic_config(lineage: str) -> Config:  # pragma: no cover - operational glue
    """Build an Alembic Config for one lineage from the repo ``alembic.ini``.

    The ini path can be overridden with ``MTG_AI_ALEMBIC_INI``; otherwise it is
    resolved by walking up from the current directory.
    """
    from alembic.config import Config  # noqa: PLC0415 - api extra, imported lazily

    override = os.environ.get("MTG_AI_ALEMBIC_INI")
    if override:
        ini_path = Path(override)
    else:
        ini_path = None
        for parent in [Path.cwd(), *Path.cwd().parents]:
            candidate = parent / "alembic.ini"
            if candidate.is_file():
                ini_path = candidate
                break
        if ini_path is None:
            msg = "Could not locate alembic.ini; set MTG_AI_ALEMBIC_INI"
            raise click.ClickException(msg)

    config = Config(str(ini_path), ini_section=lineage)
    config.config_ini_section = lineage
    return config


@cli.group()
def db() -> None:
    """Database migration commands (data and app lineages)."""


@db.command("upgrade")
@click.option(
    "--lineage",
    type=click.Choice([*_LINEAGES, "all"]),
    default="all",
    help="Which lineage to upgrade.",
)
def db_upgrade(lineage: str) -> None:  # pragma: no cover - requires a live database
    """Upgrade one or both lineages to the latest revision."""
    from alembic import command  # noqa: PLC0415 - api extra, imported lazily

    targets = list(_LINEAGES) if lineage == "all" else [lineage]
    for target in targets:
        logger.info("Upgrading database lineage", lineage=target)
        command.upgrade(_alembic_config(target), "head")
    click.echo(f"Upgraded: {', '.join(targets)}")


@db.command("downgrade")
@click.option("--lineage", type=click.Choice(_LINEAGES), required=True)
@click.option("--revision", default="-1", help="Target revision (default: -1).")
def db_downgrade(
    lineage: str,
    revision: str,
) -> None:  # pragma: no cover - requires a live database
    """Downgrade a lineage to a revision."""
    from alembic import command  # noqa: PLC0415 - api extra, imported lazily

    command.downgrade(_alembic_config(lineage), revision)
    click.echo(f"Downgraded {lineage} to {revision}")


@db.command("current")
@click.option(
    "--lineage",
    type=click.Choice([*_LINEAGES, "all"]),
    default="all",
)
def db_current(lineage: str) -> None:  # pragma: no cover - requires a live database
    """Show the current revision of one or both lineages."""
    from alembic import command  # noqa: PLC0415 - api extra, imported lazily

    targets = list(_LINEAGES) if lineage == "all" else [lineage]
    for target in targets:
        command.current(_alembic_config(target))


@cli.group()
def user() -> None:
    """User administration (out-of-band account provisioning)."""


@user.command("create")
@click.option("--username", required=True, help="Username to create.")
@click.password_option(help="Password for the new user.")
def user_create(
    username: str,
    password: str,
) -> None:  # pragma: no cover - requires a live database
    """Create a new application user.

    Accounts are provisioned here rather than through an open endpoint, so a
    self-hosted deployment has no unauthenticated account-creation surface.
    """
    from mtg_ai.auth.service import create_user  # noqa: PLC0415
    from mtg_ai.core.exceptions import ValidationError  # noqa: PLC0415
    from mtg_ai.db.engine import (  # noqa: PLC0415
        create_db_engine,
        create_session_factory,
    )

    engine = create_db_engine(settings.database_url)
    factory = create_session_factory(engine)
    session = factory()
    try:
        created = create_user(session, username, password)
        session.commit()
        click.echo(f"Created user {created.username} ({created.id})")
    except ValidationError as exc:
        session.rollback()
        raise click.ClickException(str(exc)) from exc
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    cli()
