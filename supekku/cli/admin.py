"""Admin command group for niche workspace maintenance operations."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from spec_driver.presentation.cli import constants as cli_constants
from spec_driver.presentation.cli.admin.migrate import migrate as migrate_cmd
from spec_driver.presentation.cli.admin.migrate_requirements import (
  migrate_requirements as migrate_requirements_cmd,
)
from supekku.cli import backfill, compact, regenerate_templates, resolve

app = typer.Typer(help="Workspace maintenance commands", no_args_is_help=True)

app.add_typer(compact.app, name="compact", help="Compact artifact frontmatter")
app.add_typer(resolve.app, name="resolve", help="Resolve cross-artifact references")
app.add_typer(backfill.app, name="backfill", help="Backfill incomplete artifacts")
app.add_typer(
  regenerate_templates.app,
  name="regenerate-templates",
  help="Regenerate template frontmatter from metadata (IP-137-P02)",
)
app.command(
  cli_constants.ADMIN_MIGRATE,
  help="Schema-version migration orchestrator (DE-137; DR-137 §5.6).",
)(migrate_cmd)
app.command(
  "migrate-requirements",
  help="Migrate prose requirements to structured block (DE-140).",
)(migrate_requirements_cmd)


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
