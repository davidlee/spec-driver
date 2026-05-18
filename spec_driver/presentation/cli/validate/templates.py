"""``spec-driver validate templates`` — CI gate for template-frontmatter drift.

Moved from the IP-137-P02 hyphenated top-level
``spec-driver validate-templates`` into the ``validate`` Typer group per
DR-137 §5.4.

Exit codes (F-46):
- 0 — every committed template's frontmatter matches the canonical
  metadata-derived render.
- 1 — at least one template carries drift.
"""

from __future__ import annotations

from pathlib import Path

import typer

from spec_driver.orchestration.templates import validate_templates
from spec_driver.presentation.cli import constants
from spec_driver.presentation.cli.validate import app
from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS
from supekku.scripts.lib.core.repo import find_repo_root


@app.command(constants.VALIDATE_TEMPLATES)
def templates_cmd() -> None:
  """CI gate: non-zero on template-metadata drift, zero on clean."""
  repo = Path(find_repo_root())
  drifts = validate_templates(repo)
  if not drifts:
    typer.echo("templates clean")
    raise typer.Exit(EXIT_SUCCESS)
  for drift in drifts:
    typer.echo(f"DRIFT {drift.path} (kind={drift.kind})", err=True)
    typer.echo(drift.diff, err=True)
  raise typer.Exit(EXIT_FAILURE)
