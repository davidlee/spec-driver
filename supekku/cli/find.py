"""Find commands for locating artifacts by ID across the repository."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption
from supekku.scripts.lib.changes.registry import ChangeRegistry
from supekku.scripts.lib.decisions.registry import DecisionRegistry
from supekku.scripts.lib.policies.registry import PolicyRegistry
from supekku.scripts.lib.specs.registry import SpecRegistry
from supekku.scripts.lib.standards.registry import StandardRegistry

app = typer.Typer(help="Find artifacts by ID across the repository")


def _matches_pattern(artifact_id: str, pattern: str) -> bool:
  """Check if artifact ID matches pattern (case-insensitive)."""
  return fnmatch.fnmatch(artifact_id, pattern) or fnmatch.fnmatch(
    artifact_id, pattern.upper()
  )


@app.command("spec")
def find_spec(
  pattern: Annotated[str, typer.Argument(help="ID pattern (e.g., SPEC-*, PROD-01*)")],
  root: RootOption = None,
) -> None:
  """Find specs matching ID pattern.

  Supports fnmatch patterns: * matches everything, ? matches single char.
  Examples: SPEC-*, PROD-01?, *-009
  """
  try:
    registry = SpecRegistry(root=root)
    for spec in registry.all_specs():
      if _matches_pattern(spec.id, pattern):
        typer.echo(spec.path)
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("delta")
def find_delta(
  pattern: Annotated[str, typer.Argument(help="ID pattern (e.g., DE-*, DE-01?)")],
  root: RootOption = None,
) -> None:
  """Find deltas matching ID pattern.

  Supports fnmatch patterns: * matches everything, ? matches single char.
  Examples: DE-*, DE-00?, DE-02*
  """
  try:
    registry = ChangeRegistry(root=root, kind="delta")
    for artifact_id, artifact in registry.collect().items():
      if _matches_pattern(artifact_id, pattern):
        typer.echo(artifact.path)
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("adr")
def find_adr(
  pattern: Annotated[str, typer.Argument(help="ID pattern (e.g., ADR-*, ADR-00?)")],
  root: RootOption = None,
) -> None:
  """Find ADRs matching ID pattern.

  Supports fnmatch patterns: * matches everything, ? matches single char.
  Examples: ADR-*, ADR-00?, ADR-01*
  """
  try:
    registry = DecisionRegistry(root=root)
    for artifact_id, artifact in registry.collect().items():
      if _matches_pattern(artifact_id, pattern):
        typer.echo(artifact.path)
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("revision")
def find_revision(
  pattern: Annotated[str, typer.Argument(help="ID pattern (e.g., RE-*, RE-00?)")],
  root: RootOption = None,
) -> None:
  """Find revisions matching ID pattern.

  Supports fnmatch patterns: * matches everything, ? matches single char.
  Examples: RE-*, RE-00?, RE-01*
  """
  try:
    registry = ChangeRegistry(root=root, kind="revision")
    for artifact_id, artifact in registry.collect().items():
      if _matches_pattern(artifact_id, pattern):
        typer.echo(artifact.path)
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("policy")
def find_policy(
  pattern: Annotated[str, typer.Argument(help="ID pattern (e.g., POL-*, POL-00?)")],
  root: RootOption = None,
) -> None:
  """Find policies matching ID pattern.

  Supports fnmatch patterns: * matches everything, ? matches single char.
  Examples: POL-*, POL-00?, POL-01*
  """
  try:
    registry = PolicyRegistry(root=root)
    for artifact_id, artifact in registry.collect().items():
      if _matches_pattern(artifact_id, pattern):
        typer.echo(artifact.path)
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("standard")
def find_standard(
  pattern: Annotated[str, typer.Argument(help="ID pattern (e.g., STD-*, STD-00?)")],
  root: RootOption = None,
) -> None:
  """Find standards matching ID pattern.

  Supports fnmatch patterns: * matches everything, ? matches single char.
  Examples: STD-*, STD-00?, STD-01*
  """
  try:
    registry = StandardRegistry(root=root)
    for artifact_id, artifact in registry.collect().items():
      if _matches_pattern(artifact_id, pattern):
        typer.echo(artifact.path)
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("card")
def find_card(
  card_id: Annotated[str, typer.Argument(help="Card ID to search for (e.g., T123)")],
  root: RootOption = None,
) -> None:
  """Find all files matching card ID (repo-wide filename search).

  Searches for files matching the pattern T###-*.md anywhere in the repository.
  Prints one path per line.
  """
  try:
    search_root = Path(root) if root else Path.cwd()

    # Repo-wide search for T###-*.md pattern
    pattern = f"{card_id}-*.md"
    matches = sorted(search_root.rglob(pattern))

    if not matches:
      # Exit silently if no matches (consistent with Unix find behavior)
      raise typer.Exit(EXIT_SUCCESS)

    # Print all matches, one per line
    for match in matches:
      typer.echo(str(match))

    raise typer.Exit(EXIT_SUCCESS)

  except (PermissionError, OSError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


# For direct testing
if __name__ == "__main__":  # pragma: no cover
  app()
