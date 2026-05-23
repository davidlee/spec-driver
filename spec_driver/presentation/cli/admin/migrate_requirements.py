"""``spec-driver admin migrate-requirements`` — interactive per-spec
requirement migration from prose bullets to structured
``supekku:spec.requirements@v1`` blocks (DE-140, DR-140 §6).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from spec_driver.presentation.cli import constants


def _find_spec_file(repo_root: Path, spec_id: str) -> Path | None:
  """Locate spec/prod file by scanning .spec-driver/ for matching ID."""
  sd_root = repo_root / ".spec-driver"
  if not sd_root.exists():
    return None
  for search_dir in ("product", "specs/tech"):
    parent = sd_root / search_dir / spec_id
    candidate = parent / f"{spec_id}.md"
    if candidate.exists():
      return candidate
  return None


def _report_result(
  spec_id: str,
  result,  # noqa: ANN001
  repo_root: Path,
) -> None:
  """Report migration result and write drift ledger."""
  from spec_driver.migrations.spec_requirements.migration import (  # noqa: PLC0415
    write_drift_ledger,
  )

  drift_dir = repo_root / ".spec-driver" / "drift"
  if result.drift:
    dl_path = write_drift_ledger(
      drift_dir, spec_id, result.drift,
    )
    typer.echo(
      f"migrate-requirements: {spec_id} — "
      f"migrated {result.requirements_count} requirements, "
      f"{len(result.drift)} drift entries → {dl_path}",
    )
  else:
    typer.echo(
      f"migrate-requirements: {spec_id} — "
      f"migrated {result.requirements_count} requirements",
    )


def migrate_requirements(
  spec_id: Annotated[
    str,
    typer.Argument(
      help="Spec/product ID to migrate (e.g. PROD-004).",
    ),
  ],
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
      constants.FLAG_DRY_RUN,
      help="Preview proposed block without writing.",
    ),
  ] = False,
) -> None:
  """Migrate prose requirements to structured block format."""
  from spec_driver.migrations.spec_requirements.migration import (  # noqa: PLC0415
    apply_migration,
    has_requirements_block,
  )
  from supekku.cli.common import (  # noqa: PLC0415
    EXIT_FAILURE,
    EXIT_PRECONDITION,
    EXIT_SUCCESS,
  )
  from supekku.scripts.lib.core.repo import (  # noqa: PLC0415
    find_repo_root,
  )

  repo_root = find_repo_root(root)
  spec_path = _find_spec_file(repo_root, spec_id)
  if spec_path is None:
    typer.echo(
      f"migrate-requirements: spec file not found "
      f"for {spec_id}",
      err=True,
    )
    raise typer.Exit(EXIT_PRECONDITION)

  text = spec_path.read_text(encoding="utf-8")
  if has_requirements_block(text):
    typer.echo(
      f"migrate-requirements: {spec_id} already has a "
      f"spec.requirements block — skipping",
    )
    raise typer.Exit(EXIT_SUCCESS)

  try:
    result = apply_migration(
      spec_path, spec_id, dry_run=dry_run,
    )
  except ValueError as exc:
    typer.echo(
      f"migrate-requirements: {exc}",
      err=True,
    )
    raise typer.Exit(EXIT_FAILURE) from exc

  if not result.changed:
    typer.echo(
      f"migrate-requirements: {spec_id} — "
      f"no prose requirements found",
    )
    raise typer.Exit(EXIT_SUCCESS)

  if dry_run:
    typer.echo(
      f"migrate-requirements: {spec_id} — "
      f"dry-run: {result.requirements_count} requirements "
      f"would be migrated",
    )
    typer.echo("")
    typer.echo(result.text)
    raise typer.Exit(EXIT_SUCCESS)

  _report_result(spec_id, result, repo_root)
  raise typer.Exit(EXIT_SUCCESS)
