"""Find commands for locating artifacts by ID across the repository."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS, RootOption

app = typer.Typer(help="Find artifacts by ID across the repository")


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
