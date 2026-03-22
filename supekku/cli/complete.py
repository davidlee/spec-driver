"""Complete commands for marking artifacts as completed."""

from __future__ import annotations

from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS
from supekku.scripts.lib.changes.completion import complete_delta as complete_delta_impl
from supekku.scripts.lib.changes.completion import (
  complete_revision as complete_revision_impl,
)

app = typer.Typer(help="Complete artifacts", no_args_is_help=True)


@app.command("delta")
def complete_delta(
  delta_id: Annotated[str, typer.Argument(help="Delta ID (e.g., DE-004)")],
  dry_run: Annotated[
    bool,
    typer.Option(
      "--dry-run",
      help="Preview changes without applying them",
    ),
  ] = False,
  force: Annotated[
    bool,
    typer.Option(
      "--force",
      "-f",
      help="Skip all prompts (non-interactive mode)",
    ),
  ] = False,
  skip_sync: Annotated[
    bool,
    typer.Option(
      "--skip-sync",
      help="Skip spec sync prompt/check",
    ),
  ] = False,
  skip_update_requirements: Annotated[
    bool,
    typer.Option(
      "--skip-update-requirements",
      help="Skip updating requirements (only mark delta as completed)",
    ),
  ] = False,
) -> None:
  """Complete a delta and transition associated requirements to active status.

  Marks a delta as completed and optionally updates associated requirements
  to 'active' status in revision source files.
  """
  try:
    exit_code = complete_delta_impl(
      delta_id,
      dry_run=dry_run,
      force=force,
      skip_sync=skip_sync,
      update_requirements=not skip_update_requirements,
    )
    if exit_code == 0:
      if dry_run:
        typer.echo("Dry run completed successfully")
      else:
        typer.echo(f"Delta {delta_id} completed successfully")
      raise typer.Exit(EXIT_SUCCESS)
    raise typer.Exit(EXIT_FAILURE)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("revision")
def complete_revision(
  revision_id: Annotated[str, typer.Argument(help="Revision ID (e.g., RE-015)")],
  force: Annotated[
    bool,
    typer.Option(
      "--force",
      "-f",
      help="Complete even from unexpected statuses",
    ),
  ] = False,
) -> None:
  """Complete a revision and transition its status to completed."""
  try:
    exit_code = complete_revision_impl(revision_id, force=force)
    if exit_code == 0:
      raise typer.Exit(EXIT_SUCCESS)
    raise typer.Exit(EXIT_FAILURE)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
