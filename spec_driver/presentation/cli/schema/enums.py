"""``spec-driver schema enums [kind[.field]]`` — controlled-vocab CLI.

Reads ``FRONTMATTER_METADATA_REGISTRY`` (POL-001 single source of truth)
and surfaces canonical values + permanent aliases + tolerated aliases
for every controlled-vocab field. Supports three invocation forms per
DR-137 §5.3:

- ``schema enums`` — list every kind with ≥1 controlled-vocab field.
- ``schema enums <kind>`` — table of every controlled-vocab field for
  that kind.
- ``schema enums <kind>.<field>`` — full canonical/aliases/tolerated
  breakdown for that one field.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from spec_driver.presentation.cli import constants
from spec_driver.presentation.cli.schema import app
from supekku.cli.common import EXIT_FAILURE, EXIT_SUCCESS
from supekku.scripts.lib.blocks.metadata.schema import (
  BlockMetadata,
  FieldMetadata,
)
from supekku.scripts.lib.core.frontmatter_metadata import (
  FRONTMATTER_METADATA_REGISTRY,
)

console = Console()


def _controlled_fields(metadata: BlockMetadata) -> dict[str, FieldMetadata]:
  """Return the kind's top-level fields whose ``enum_values`` is non-empty."""
  return {
    name: field
    for name, field in metadata.fields.items()
    if field.enum_values
  }


def _kinds_with_controlled_vocab() -> dict[str, dict[str, FieldMetadata]]:
  return {
    kind: controlled
    for kind, metadata in FRONTMATTER_METADATA_REGISTRY.items()
    for controlled in (_controlled_fields(metadata),)
    if controlled
  }


def _list_all_kinds() -> None:
  catalogue = _kinds_with_controlled_vocab()
  table = Table(title="Controlled-vocab fields by kind")
  table.add_column("kind")
  table.add_column("fields", justify="right")
  table.add_column("field names")
  for kind in sorted(catalogue):
    fields = catalogue[kind]
    table.add_row(kind, str(len(fields)), ", ".join(sorted(fields)))
  console.print(table)


def _list_kind(kind: str) -> int:
  metadata = FRONTMATTER_METADATA_REGISTRY.get(kind)
  if metadata is None:
    console.print(f"[red]unknown kind:[/red] {kind}", style="bold")
    return EXIT_FAILURE
  controlled = _controlled_fields(metadata)
  if not controlled:
    console.print(f"{kind}: no controlled-vocab fields")
    return EXIT_SUCCESS
  table = Table(title=f"{kind} — controlled-vocab fields")
  table.add_column("field")
  table.add_column("canonical")
  table.add_column("aliases", justify="right")
  table.add_column("tolerated", justify="right")
  for field_name in sorted(controlled):
    field = controlled[field_name]
    canonical = ", ".join(str(v) for v in (field.enum_values or []))
    alias_count = len(field.aliases) if field.aliases else 0
    tolerated_count = (
      len(field.tolerated_aliases) if field.tolerated_aliases else 0
    )
    table.add_row(field_name, canonical, str(alias_count), str(tolerated_count))
  console.print(table)
  return EXIT_SUCCESS


def _show_field(kind: str, field_name: str) -> int:
  metadata = FRONTMATTER_METADATA_REGISTRY.get(kind)
  if metadata is None:
    console.print(f"[red]unknown kind:[/red] {kind}", style="bold")
    return EXIT_FAILURE
  field = metadata.fields.get(field_name)
  if field is None or not field.enum_values:
    console.print(
      f"[red]{kind}.{field_name}:[/red] not a controlled-vocab field",
      style="bold",
    )
    return EXIT_FAILURE

  console.print(f"[bold]{kind}.{field_name}[/bold]")
  console.print(
    f"  Canonical values: {', '.join(str(v) for v in field.enum_values)}"
  )

  if field.aliases:
    console.print("  Permanent aliases:")
    for alias, canonical in sorted(field.aliases.items()):
      console.print(f"    {alias:<12} -> {canonical}")
  else:
    console.print("  Permanent aliases: (none)")

  if field.tolerated_aliases:
    console.print("  Tolerated aliases:")
    for alias, entry in sorted(field.tolerated_aliases.items()):
      sunset = getattr(entry, "sunset_after", None) or "(no sunset)"
      rationale = getattr(entry, "rationale", "") or ""
      canonical = getattr(entry, "canonical", "")
      line = f"    {alias:<12} -> {canonical}  sunset={sunset}"
      if rationale:
        line += f"  ({rationale})"
      console.print(line)
  else:
    console.print("  Tolerated aliases: (none)")
  return EXIT_SUCCESS


@app.command(constants.SCHEMA_ENUMS)
def enums_cmd(
  target: Annotated[
    str | None,
    typer.Argument(
      help="Optional 'kind' or 'kind.field' selector",
    ),
  ] = None,
) -> None:
  """List controlled-vocab fields by kind / inspect a single field."""
  if not target:
    _list_all_kinds()
    raise typer.Exit(EXIT_SUCCESS)

  if "." in target:
    kind, field_name = target.split(".", 1)
    exit_code = _show_field(kind, field_name)
  else:
    exit_code = _list_kind(target)
  raise typer.Exit(exit_code)
