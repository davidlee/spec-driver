"""``spec-driver admin strict-flip-requirements`` — operational guard +
strict-mode activation for ``supekku:spec.requirements@v1`` blocks
(DE-140, DEC-140-13).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer


def strict_flip_requirements(
  root: Annotated[
    Path | None,
    typer.Option(
      "--root",
      help="Repository root (auto-detected if omitted).",
      file_okay=False,
      dir_okay=True,
      exists=True,
    ),
  ] = None,
  dry_run: Annotated[
    bool,
    typer.Option(
      "--dry-run",
      help="Check readiness without writing config.",
    ),
  ] = False,
) -> None:
  """Activate strict requirements enforcement after migration.

  Verifies all spec/prod artifacts have a spec.requirements block,
  then writes the strict toggle to workflow.toml.  Refuses if any
  artifacts are unmigrated (DEC-140-13).
  """
  from supekku.cli.common import (  # noqa: PLC0415
    EXIT_GUARD_VIOLATION,
    EXIT_SUCCESS,
  )
  from supekku.scripts.lib.core.repo import find_repo_root  # noqa: PLC0415
  from supekku.scripts.lib.validation.validator import (  # noqa: PLC0415
    check_requirements_migration_complete,
  )
  from supekku.scripts.lib.workspace import Workspace  # noqa: PLC0415

  repo_root = find_repo_root(root)
  workspace = Workspace(repo_root)
  unmigrated = check_requirements_migration_complete(workspace)

  if unmigrated:
    typer.echo(
      f"strict-flip-requirements: {len(unmigrated)} unmigrated "
      f"spec/prod artifact(s) — flip blocked",
      err=True,
    )
    for spec_id in sorted(unmigrated):
      typer.echo(f"  {spec_id}", err=True)
    raise typer.Exit(EXIT_GUARD_VIOLATION)

  if dry_run:
    typer.echo("strict-flip-requirements: all specs migrated — ready to flip")
    raise typer.Exit(EXIT_SUCCESS)

  _write_strict_toggle(repo_root)
  typer.echo("strict-flip-requirements: enabled in workflow.toml")
  raise typer.Exit(EXIT_SUCCESS)


def _write_strict_toggle(repo_root: Path) -> None:
  """Append ``[validation.strict_requirements]`` to workflow.toml."""
  workflow_path = repo_root / ".spec-driver" / "workflow.toml"
  content = workflow_path.read_text(encoding="utf-8")
  if "[validation.strict_requirements]" in content:
    return
  if not content.endswith("\n"):
    content += "\n"
  content += "\n[validation.strict_requirements]\nenabled = true\n"
  workflow_path.write_text(content, encoding="utf-8")
