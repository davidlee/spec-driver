"""Workspace-level commands: install and validate."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption

# Add parent to path for imports
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from supekku.scripts.install import initialize_workspace
from supekku.scripts.lib.backlog import find_repo_root
from supekku.scripts.lib.validator import validate_workspace as validate_ws
from supekku.scripts.lib.workspace import Workspace

app = typer.Typer(help="Workspace management commands")


@app.command("install")
def install(
  target_dir: Annotated[
    Path | None,
    typer.Argument(
      help="Target directory to initialize (default: current directory)",
    ),
  ] = None,
) -> None:
  """Initialize spec-driver workspace structure and registry files.

  Creates the necessary directory structure and initializes registry files
  for a new spec-driver workspace.
  """
  target_path = target_dir if target_dir else Path.cwd()
  try:
    initialize_workspace(target_path)
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
) -> None:
  """Validate workspace metadata and relationships.

  Checks workspace integrity, validates cross-references between documents,
  and reports any issues found.
  """
  try:
    ws = Workspace(find_repo_root(root))

    if sync:
      ws.reload_specs()
      ws.sync_change_registries()
      ws.sync_requirements()

    issues = validate_ws(ws, strict=strict)
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
