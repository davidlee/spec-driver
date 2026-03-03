"""Compact commands for stripping default/derived frontmatter fields."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS
from supekku.scripts.lib.changes.registry import ChangeRegistry
from supekku.scripts.lib.core.frontmatter_metadata import (
  compact_frontmatter,
  get_frontmatter_metadata,
)
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.spec_utils import dump_markdown_file, load_markdown_file

app = typer.Typer(help="Compact artifact frontmatter", no_args_is_help=True)


@app.command("delta")
def compact_deltas(
  delta_id: Annotated[
    str | None,
    typer.Argument(help="Specific delta ID (e.g., DE-004). Omit for all."),
  ] = None,
  dry_run: Annotated[
    bool,
    typer.Option("--dry-run", help="Show what would change without writing"),
  ] = False,
  root: Annotated[
    Path | None,
    typer.Option("--root", help="Repository root (auto-detected if omitted)"),
  ] = None,
) -> None:
  """Compact delta frontmatter by stripping default/derived fields.

  Uses FieldMetadata persistence annotations to remove fields that carry
  no information (empty defaults, derived values). Safe: read-side tolerance
  means existing parsers handle compacted files unchanged.
  """
  root = find_repo_root(root)
  registry = ChangeRegistry(root=root, kind="delta")
  metadata = get_frontmatter_metadata("delta")
  artifacts = registry.collect()

  if delta_id:
    if delta_id not in artifacts:
      typer.echo(f"Delta not found: {delta_id}", err=True)
      raise typer.Exit(EXIT_FAILURE)
    targets = {delta_id: artifacts[delta_id]}
  else:
    targets = artifacts

  compacted_count = 0
  for aid, artifact in sorted(targets.items()):
    if not artifact.path or not Path(artifact.path).exists():
      continue

    fm_data, body = load_markdown_file(artifact.path)
    result = compact_frontmatter(fm_data, metadata)

    if result == fm_data:
      continue

    compacted_count += 1
    typer.echo(
      f"{'[dry run] ' if dry_run else ''}{aid}: "
      f"removed {', '.join(sorted(set(fm_data) - set(result)))}"
    )

    if not dry_run:
      dump_markdown_file(artifact.path, result, body)

  if compacted_count == 0:
    typer.echo("No deltas needed compaction.")
  elif dry_run:
    typer.echo(f"\n{compacted_count} delta(s) would be compacted.")
  else:
    typer.echo(f"\n{compacted_count} delta(s) compacted.")

  raise typer.Exit(EXIT_SUCCESS)


if __name__ == "__main__":  # pragma: no cover
  app()
