"""List revisions and audits commands."""

from __future__ import annotations

import re
from typing import Annotated

import typer

from supekku.cli.common import (
  EXIT_FAILURE,
  EXIT_SUCCESS,
  CaseInsensitiveOption,
  ExternalOption,
  FormatOption,
  RegexpOption,
  RootOption,
  TruncateOption,
  load_all_artifacts,
  matches_regexp,
)
from supekku.cli.list import app
from supekku.scripts.lib.changes.registry import ChangeRegistry
from supekku.scripts.lib.core.filters import parse_multi_value_filter
from supekku.scripts.lib.formatters.change_formatters import (
  format_change_list_table,
)
from supekku.scripts.lib.relations.query import partition_by_reverse_references


@app.command("revisions")
def list_revisions(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  spec: Annotated[
    str | None,
    typer.Option("--spec", help="Filter by spec reference"),
  ] = None,
  delta: Annotated[
    str | None,
    typer.Option("--delta", help="Filter by delta reference (e.g., DE-090 or 90)"),
  ] = None,
  tag: Annotated[
    list[str] | None,
    typer.Option(
      "--tag",
      "-t",
      help="Filter by tag (repeatable, OR logic)",
    ),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on ID or name (case-insensitive)",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON (shorthand for --format=json)",
    ),
  ] = False,
  truncate: TruncateOption = False,
  external: ExternalOption = False,
) -> None:
  """List revisions with optional filtering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on ID, slug, and name fields.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = ChangeRegistry(root=root, kind="revision")
    revisions = list(registry.collect().values())

    # Apply filters (multi-value status OR logic)
    if status:
      status_values = parse_multi_value_filter(status)
      status_normalized = [s.lower() for s in status_values]
      revisions = [r for r in revisions if r.status.lower() in status_normalized]
    if spec:
      spec_upper = spec.upper()
      revisions = [
        r
        for r in revisions
        if r.relations
        and any(spec_upper in str(rel.get("target", "")).upper() for rel in r.relations)
      ]
    if delta:
      from supekku.cli.common import normalize_id  # noqa: PLC0415

      delta_normalized = normalize_id("delta", delta)
      revisions = [
        r
        for r in revisions
        if r.relations
        and any(
          delta_normalized == str(rel.get("target", "")).upper() for rel in r.relations
        )
      ]
    if tag:
      revisions = [r for r in revisions if any(t in r.tags for t in tag)]
    if substring:
      filter_lower = substring.lower()
      revisions = [
        r
        for r in revisions
        if filter_lower in r.id.lower() or filter_lower in r.name.lower()
      ]

    # Apply regexp filter on id, slug, name
    if regexp:
      try:
        revisions = [
          r
          for r in revisions
          if matches_regexp(regexp, [r.id, r.slug, r.name], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not revisions:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    revisions.sort(key=lambda r: r.id)
    output = format_change_list_table(
      revisions,
      format_type,
      not truncate,
      show_external=external,
    )
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("audits")
def list_audits(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  spec: Annotated[
    str | None,
    typer.Option("--spec", help="Filter by spec reference"),
  ] = None,
  delta: Annotated[
    str | None,
    typer.Option("--delta", help="Filter by delta reference (e.g., DE-090 or 90)"),
  ] = None,
  tag: Annotated[
    list[str] | None,
    typer.Option(
      "--tag",
      "-t",
      help="Filter by tag (repeatable, OR logic)",
    ),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on ID or name (case-insensitive)",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON (shorthand for --format=json)",
    ),
  ] = False,
  referenced_by: Annotated[
    str | None,
    typer.Option(
      "--referenced-by",
      help="Keep audits targeted by artifacts of TYPE",
    ),
  ] = None,
  not_referenced_by: Annotated[
    str | None,
    typer.Option(
      "--not-referenced-by",
      help="Keep audits NOT targeted by artifacts of TYPE",
    ),
  ] = None,
  truncate: TruncateOption = False,
  external: ExternalOption = False,
) -> None:
  """List audits with optional filtering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on ID, slug, and name fields.
  The --referenced-by/--not-referenced-by flags filter by reverse references.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Mutual exclusion: --referenced-by vs --not-referenced-by
  if referenced_by and not_referenced_by:
    typer.echo(
      "Error: --referenced-by and --not-referenced-by are mutually exclusive",
      err=True,
    )
    raise typer.Exit(EXIT_FAILURE)

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = ChangeRegistry(root=root, kind="audit")
    audits = list(registry.collect().values())

    # Apply filters (multi-value status OR logic)
    if status:
      status_values = parse_multi_value_filter(status)
      status_normalized = [s.lower() for s in status_values]
      audits = [a for a in audits if a.status.lower() in status_normalized]
    if spec:
      spec_upper = spec.upper()
      audits = [
        a
        for a in audits
        if a.relations
        and any(spec_upper in str(rel.get("target", "")).upper() for rel in a.relations)
      ]
    if delta:
      from supekku.cli.common import normalize_id  # noqa: PLC0415

      delta_normalized = normalize_id("delta", delta)
      audits = [
        a
        for a in audits
        if a.relations
        and any(
          delta_normalized == str(rel.get("target", "")).upper() for rel in a.relations
        )
      ]
    if tag:
      audits = [a for a in audits if any(t in a.tags for t in tag)]
    if substring:
      filter_lower = substring.lower()
      audits = [
        a
        for a in audits
        if filter_lower in a.id.lower() or filter_lower in a.name.lower()
      ]

    # Apply regexp filter on id, slug, name
    if regexp:
      try:
        audits = [
          a
          for a in audits
          if matches_regexp(regexp, [a.id, a.slug, a.name], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    # Apply reverse reference filtering
    if referenced_by or not_referenced_by:
      ref_type = referenced_by or not_referenced_by
      referrers = load_all_artifacts(root, ref_type)
      referenced, unreferenced = partition_by_reverse_references(
        audits,
        referrers,
      )
      audits = referenced if referenced_by else unreferenced

    if not audits:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    audits.sort(key=lambda a: a.id)
    output = format_change_list_table(
      audits,
      format_type,
      not truncate,
      show_external=external,
    )
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
