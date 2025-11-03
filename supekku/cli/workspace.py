"""Workspace-level commands: install and validate."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption
from supekku.scripts.install import initialize_workspace
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.validation.validator import validate_workspace as validate_ws
from supekku.scripts.lib.workspace import Workspace

app = typer.Typer(help="Workspace management commands", no_args_is_help=True)


@app.command("install")
def install(
  target_dir: Annotated[
    Path | None,
    typer.Argument(
      help="Target directory to initialize (default: current directory)",
    ),
  ] = None,
  dry_run: Annotated[
    bool,
    typer.Option(
      "--dry-run",
      help="Show what would be done without making changes",
    ),
  ] = False,
  auto_yes: Annotated[
    bool,
    typer.Option(
      "--yes",
      "-y",
      help="Automatically confirm all prompts",
    ),
  ] = False,
) -> None:
  """Initialize spec-driver workspace structure and registry files.

  Creates the necessary directory structure and initializes registry files
  for a new spec-driver workspace.
  """
  target_path = target_dir if target_dir else Path.cwd()
  try:
    initialize_workspace(target_path, dry_run=dry_run, auto_yes=auto_yes)
    if not dry_run:
      typer.echo(f"Workspace initialized in {target_path.resolve()}")
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("validate")
def validate(
  root: RootOption = None,
  sync: Annotated[
    bool,
    typer.Option(
      "--sync",
      help="Synchronise registries before validation",
    ),
  ] = False,
  strict: Annotated[
    bool,
    typer.Option(
      "--strict",
      help="Enable strict validation (warn about deprecated ADR references)",
    ),
  ] = False,
  verbose: Annotated[
    bool,
    typer.Option(
      "--verbose",
      "-v",
      help="Show info-level messages (planned verification artifacts, etc.)",
    ),
  ] = False,
) -> None:
  """Validate workspace metadata and relationships.

  Checks workspace integrity, validates cross-references between documents,
  and reports any issues found.

  By default, only errors and warnings are shown. Use --verbose to see
  info-level messages about planned verification artifacts.
  """
  try:
    ws = Workspace(find_repo_root(root))

    if sync:
      ws.sync_all_registries()

    issues = validate_ws(ws, strict=strict)

    # Filter issues based on verbosity
    if not verbose:
      issues = [i for i in issues if i.level != "info"]

    if not issues:
      typer.echo("Workspace validation passed")
      raise typer.Exit(EXIT_SUCCESS)

    for issue in issues:
      typer.echo(f"Issue: {issue}", err=True)
    raise typer.Exit(EXIT_FAILURE)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
