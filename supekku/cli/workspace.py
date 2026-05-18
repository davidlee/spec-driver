"""Workspace-level commands: install and doctor.

``validate`` moved to the ``spec_driver/presentation/cli/validate`` Typer
group in IP-137-P03; see
``spec_driver/presentation/cli/validate/workspace.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption
from supekku.scripts.install import initialize_workspace
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.diagnostics.runner import overall_exit_code, run_checks
from supekku.scripts.lib.formatters.diagnostic_formatters import (
  format_doctor_json,
  format_doctor_text,
)
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


@app.command("doctor")
def doctor(
  root: RootOption = None,
  check: Annotated[
    str | None,
    typer.Option(
      "--check",
      help="Run single category only (deps|config|structure|registries|refs|lifecycle)",
    ),
  ] = None,
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output results as JSON",
    ),
  ] = False,
  verbose: Annotated[
    bool,
    typer.Option(
      "--verbose",
      "-v",
      help="Include passing results in output",
    ),
  ] = False,
) -> None:
  """Run workspace health diagnostics.

  Checks dependencies, configuration, directory structure, registries,
  cross-references, and lifecycle hygiene. Reports pass/warn/fail per check
  with actionable suggestions.

  Exit codes: 0 = all pass, 1 = warnings, 2 = failures.
  """
  try:
    ws = Workspace(find_repo_root(root))
    categories = [check] if check else None
    summaries = run_checks(ws, categories=categories)
    exit_code = overall_exit_code(summaries)

    if json_output:
      typer.echo(format_doctor_json(summaries))
    else:
      use_color = sys.stdout.isatty() and not json_output
      typer.echo(
        format_doctor_text(
          summaries,
          verbose=verbose,
          color=use_color,
        )
      )

    raise typer.Exit(exit_code)
  except ValueError as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
