"""List deltas command."""

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
from supekku.cli.list import _parse_relation_filter, app
from supekku.scripts.lib.changes.lifecycle import (
  STATUS_COMPLETED,
  VALID_STATUSES,
  normalize_status,
)
from supekku.scripts.lib.changes.registry import ChangeRegistry
from supekku.scripts.lib.core.filters import parse_multi_value_filter
from supekku.scripts.lib.formatters.change_formatters import (
  format_change_list_table,
  format_change_with_context,
)
from supekku.scripts.lib.relations.query import (
  find_by_relation,
  find_related_to,
  partition_by_reverse_references,
)


@app.command("deltas")
def list_deltas(
  root: RootOption = None,
  ids: Annotated[
    list[str] | None,
    typer.Argument(
      help="Specific delta IDs to display (e.g., DE-002 DE-005)",
    ),
  ] = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help=f"Filter by status. Valid: {', '.join(sorted(VALID_STATUSES))}",
    ),
  ] = None,
  implements: Annotated[
    str | None,
    typer.Option(
      "--implements",
      help="Filter by requirement ID (e.g., PROD-010.FR-004)",
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
  spec_filter: Annotated[
    str | None,
    typer.Option("--spec", help="Filter by spec reference"),
  ] = None,
  related_to: Annotated[
    str | None,
    typer.Option(
      "--related-to",
      help="Show deltas referencing ID in any slot",
    ),
  ] = None,
  relation: Annotated[
    str | None,
    typer.Option(
      "--relation",
      help="Filter by relation TYPE:TARGET (e.g., relates_to:IMPR-006)",
    ),
  ] = None,
  referenced_by: Annotated[
    str | None,
    typer.Option(
      "--referenced-by",
      help="Keep deltas targeted by artifacts of TYPE (e.g., audit, delta)",
    ),
  ] = None,
  not_referenced_by: Annotated[
    str | None,
    typer.Option(
      "--not-referenced-by",
      help="Keep deltas NOT targeted by artifacts of TYPE",
    ),
  ] = None,
  unaudited: Annotated[
    bool,
    typer.Option(
      "--unaudited",
      help=(
        "Show completed deltas with no audit "
        "(alias for --not-referenced-by audit -s completed)"
      ),
    ),
  ] = False,
  refs: Annotated[
    bool,
    typer.Option(
      "--refs",
      help="Include refs column (count in table, type:target in TSV)",
    ),
  ] = False,
  tag: Annotated[
    list[str] | None,
    typer.Option(
      "--tag",
      "-t",
      help="Filter by tag (repeatable, OR logic)",
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
  details: Annotated[
    bool,
    typer.Option(
      "--details",
      "-d",
      help="Show related specs, requirements, and phases (TSV format only)",
    ),
  ] = False,
  external: ExternalOption = False,
  show_all: Annotated[
    bool,
    typer.Option(
      "--all",
      "-a",
      help="Show all deltas, including completed ones (default: hide completed)",
    ),
  ] = False,
) -> None:
  """List deltas with optional filtering and status grouping.

  By default, completed deltas are hidden. Use --all to show them.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag filters on ID, name, and slug fields.
  The --implements flag filters by requirement ID (reverse relationship query).
  The --spec flag filters by spec reference (applies_to.specs + relations).
  The --related-to flag searches all reference slots.
  The --relation flag filters by TYPE:TARGET in .relations only.
  The --referenced-by/--not-referenced-by flags filter by reverse references.
  The --unaudited flag is sugar for --not-referenced-by audit -s completed.

  Examples:
    list deltas                         # Shows active deltas (hides completed)
    list deltas --all                   # Shows all deltas
    list deltas -s draft,in-progress    # Multi-value status filter
    list deltas --implements PROD-010.FR-004     # Reverse relationship query
    list deltas --spec PROD-010                  # Deltas touching a spec
    list deltas --related-to IMPR-006            # Deltas referencing IMPR-006
    list deltas --relation relates_to:IMPR-006   # By relation type and target
    list deltas --refs                           # Include refs column
    list deltas --json                           # JSON output
    list deltas --unaudited                      # Completed deltas without an audit
    list deltas --referenced-by audit            # Deltas referenced by any audit
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # --unaudited alias expansion
  if unaudited:
    if not_referenced_by:
      typer.echo(
        "Error: --unaudited and --not-referenced-by are mutually exclusive",
        err=True,
      )
      raise typer.Exit(EXIT_FAILURE)
    if status:
      typer.echo("Error: --unaudited and --status are mutually exclusive", err=True)
      raise typer.Exit(EXIT_FAILURE)
    not_referenced_by = "audit"
    status = "completed"

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
    registry = ChangeRegistry(root=root, kind="delta")
    artifacts = registry.collect()

    if not artifacts:
      raise typer.Exit(EXIT_SUCCESS)

    # Apply reverse relationship query first (if specified)
    if implements:
      filtered_by_implements = registry.find_by_implements(implements)
      # Convert to dict for consistent filtering below
      artifacts = {a.id: a for a in filtered_by_implements}
      if not artifacts:
        raise typer.Exit(EXIT_SUCCESS)

    delta_ids = set(ids) if ids else None

    # Parse multi-value status filter
    status_values = parse_multi_value_filter(status)
    status_normalized = (
      [normalize_status(s) for s in status_values] if status_values else []
    )

    # Apply default status filter if no status is specified and --all is not set
    # (Hide completed deltas by default)
    default_hidden = {STATUS_COMPLETED} if not status and not show_all else set()

    # Apply filters
    filtered_artifacts = []
    for artifact in artifacts.values():
      # Check ID filter
      if delta_ids is not None and artifact.id not in delta_ids:
        continue

      # Check status filter (multi-value OR logic)
      norm_status = normalize_status(artifact.status)
      if status_normalized and norm_status not in status_normalized:
        continue

      if norm_status in default_hidden:
        continue

      # Check substring filter
      if substring:
        filter_lower = substring.lower()
        if (
          filter_lower not in artifact.id.lower()
          and filter_lower not in artifact.name.lower()
        ):
          continue
      # Check regexp filter on id, name, slug
      if regexp:
        try:
          if not matches_regexp(
            regexp,
            [artifact.id, artifact.name, artifact.slug],
            case_insensitive,
          ):
            continue
        except re.error as e:
          typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
          raise typer.Exit(EXIT_FAILURE) from e

      # Check tag filter (repeatable, OR logic)
      if tag and not any(t in artifact.tags for t in tag):
        continue

      filtered_artifacts.append(artifact)

    # Apply generic relation filters
    if spec_filter:
      spec_upper = spec_filter.upper()
      filtered_artifacts = [
        d
        for d in filtered_artifacts
        if spec_upper in [s.upper() for s in (d.applies_to or {}).get("specs", [])]
        or (
          d.relations
          and any(
            spec_upper in str(rel.get("target", "")).upper() for rel in d.relations
          )
        )
      ]
    if related_to:
      filtered_artifacts = find_related_to(filtered_artifacts, related_to)
    if relation:
      rel_type, rel_target = _parse_relation_filter(relation)
      filtered_artifacts = find_by_relation(
        filtered_artifacts, relation_type=rel_type, target=rel_target
      )

    # Apply reverse reference filtering
    if referenced_by or not_referenced_by:
      ref_type = referenced_by or not_referenced_by
      referrers = load_all_artifacts(root, ref_type)
      referenced, unreferenced = partition_by_reverse_references(
        filtered_artifacts,
        referrers,
      )
      filtered_artifacts = referenced if referenced_by else unreferenced

    if not filtered_artifacts:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort by ID (alphabetical order)
    filtered_artifacts.sort(key=lambda x: x.id)

    # Format and output
    # For TSV with details, use old formatter; otherwise use new table formatter
    if format_type == "tsv" and details:
      for artifact in filtered_artifacts:
        output = format_change_with_context(artifact)
        typer.echo(output)
    else:
      output = format_change_list_table(
        filtered_artifacts,
        format_type=format_type,
        truncate=truncate,
        show_external=external,
        show_refs=refs,
      )
      typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
