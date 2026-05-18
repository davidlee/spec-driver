"""`spec-driver validate-templates` — CI gate for template drift.

P02 ships a minimal hyphenated top-level command. IP-137-P03 promotes
`validate` to a Typer group with `workspace` / `file` / `templates`
subcommands; at that point this command moves into the group.
"""

from __future__ import annotations

from pathlib import Path

import typer

from spec_driver.orchestration.templates import validate_templates
from supekku.scripts.lib.core.repo import find_repo_root


def templates_cmd() -> None:
  """CI gate: non-zero on template-metadata drift, zero on clean."""
  repo = Path(find_repo_root())
  drifts = validate_templates(repo)
  if not drifts:
    typer.echo("templates clean")
    return
  for drift in drifts:
    typer.echo(f"DRIFT {drift.path} (kind={drift.kind})", err=True)
    typer.echo(drift.diff, err=True)
  raise typer.Exit(code=1)
