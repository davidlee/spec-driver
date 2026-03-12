"""Admin command group for niche workspace maintenance operations."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from supekku.cli import backfill, compact, resolve

app = typer.Typer(help="Workspace maintenance commands", no_args_is_help=True)

app.add_typer(compact.app, name="compact", help="Compact artifact frontmatter")
app.add_typer(resolve.app, name="resolve", help="Resolve cross-artifact references")
app.add_typer(backfill.app, name="backfill", help="Backfill incomplete artifacts")


@app.command()
def preboot(
  repo_root: Annotated[
    Path,
    typer.Argument(
      help="Repository root directory",
      exists=True,
      file_okay=False,
      resolve_path=True,
    ),
  ] = Path(),
) -> None:
  """Generate static boot context for cache-optimised agent sessions."""
  from supekku.scripts.lib.core.preboot import (  # noqa: PLC0415
    write_preboot_file,
  )

  path = write_preboot_file(repo_root)
  typer.echo(path)
