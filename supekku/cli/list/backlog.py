"""List backlog command."""

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
  matches_regexp,
)
from supekku.cli.list import app
from supekku.scripts.lib.formatters.backlog_formatters import format_backlog_list_table
from supekku.scripts.lib.relations.query import matches_related_to


@app.command("backlog")
def list_backlog(
  root: RootOption = None,
  kind: Annotated[
    str,
    typer.Option(
      "--kind",
      "-k",
      help="Filter by kind (issue|problem|improvement|risk|all)",
    ),
  ] = "all",
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on title (case-insensitive)",
    ),
  ] = None,
  severity: Annotated[
    str | None,
    typer.Option(
      "--severity",
      help="Filter by severity (e.g. p1, p2, p3)",
    ),
  ] = None,
  related_to: Annotated[
    str | None,
    typer.Option(
      "--related-to",
      help="Filter items referencing ID in relations (e.g., DE-090, SPEC-110)",
    ),
  ] = None,
  tag: Annotated[
    list[str] | None,
    typer.Option(
      "--tag",
      "-t",
      help="Filter by tag (repeatable, OR logic)",
    ),
  ] = None,
  json_output: Annotated[
    bool,
    typer.Option(
      "--json",
      help="Output result as JSON (shorthand for --format=json)",
    ),
  ] = False,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  truncate: TruncateOption = False,
  order: Annotated[
    str | None,
    typer.Option(
      "--order",
      "-o",
      help="Order by field: id, severity, status, kind (default: priority)",
    ),
  ] = None,
  prioritize: Annotated[
    bool,
    typer.Option(
      "--prioritize/--no-prioritize",
      "--prioritise/--no-prioritise",
      "-p",
      help="Open filtered items in editor for reordering",
    ),
  ] = False,
  show_all: Annotated[
    bool,
    typer.Option(
      "--all",
      "-a",
      help="Include resolved/implemented items (default: exclude them)",
    ),
  ] = False,
  limit: Annotated[
    int | None,
    typer.Option(
      "--limit",
      help="Maximum number of items to display (default: 20)",
    ),
  ] = 20,
  pager: Annotated[
    bool,
    typer.Option(
      "--pager",
      "-P",
      help="Display output using pager for scrolling",
    ),
  ] = False,
  external: ExternalOption = False,
) -> None:
  """List backlog items with optional filtering.

  By default, items are sorted by priority (registry order → severity → ID) and
  resolved/implemented items are excluded. Use --all to include all statuses.
  Use --order to sort by: id, severity, status, or kind.
  Use --severity to filter by priority level (e.g. p1, p2, p3).

  Use --prioritize to open the filtered items in your editor for interactive reordering.
  After saving, the registry will be updated with your new ordering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on ID and title fields.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  if kind not in ["issue", "problem", "improvement", "risk", "all"]:
    typer.echo(f"Error: invalid kind: {kind}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    from pathlib import Path

    from supekku.scripts.lib.backlog.models import DEFAULT_HIDDEN_STATUSES
    from supekku.scripts.lib.backlog.priority import (
      edit_backlog_ordering,
      sort_by_priority,
    )
    from supekku.scripts.lib.backlog.registry import (
      BacklogRegistry,
      load_backlog_registry,
      save_backlog_registry,
    )
    from supekku.scripts.lib.core.editor import (
      EditorInvocationError,
      EditorNotFoundError,
    )

    repo_root = Path(root) if root else None
    registry = BacklogRegistry(root=repo_root)
    kind_filter = kind if kind != "all" else None
    all_items = sorted(registry.iter(kind=kind_filter), key=lambda x: x.id)
    items = all_items.copy()

    # Apply default status filter (exclude resolved/implemented unless --all specified)
    if not show_all:
      items = [i for i in items if i.status.lower() not in DEFAULT_HIDDEN_STATUSES]

    # Apply filters
    if status:
      items = [i for i in items if i.status.lower() == status.lower()]
    if severity:
      sev_lower = severity.lower()
      items = [i for i in items if i.severity.lower() == sev_lower]
    if substring:
      filter_lower = substring.lower()
      items = [i for i in items if filter_lower in i.title.lower()]
    if related_to:
      items = [item for item in items if matches_related_to(item, related_to)]
    if tag:
      items = [i for i in items if any(t in i.tags for t in tag)]

    # Apply regexp filter on id, title
    if regexp:
      try:
        items = [
          i for i in items if matches_regexp(regexp, [i.id, i.title], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not items:
      raise typer.Exit(EXIT_SUCCESS)

    # Interactive prioritization mode
    if prioritize:
      ordering = load_backlog_registry(root=repo_root)
      try:
        new_ordering = edit_backlog_ordering(all_items, items, ordering)
        if new_ordering is None:
          typer.echo("Prioritization cancelled (no changes made).", err=True)
          raise typer.Exit(EXIT_SUCCESS)

        save_backlog_registry(new_ordering, root=repo_root)
        count = len(items)
        typer.echo(f"✓ Updated backlog priority ordering ({count} items reordered)")
        raise typer.Exit(EXIT_SUCCESS)

      except EditorNotFoundError as err:
        typer.echo(
          "Error: No editor found. Set $EDITOR or $VISUAL environment variable.",
          err=True,
        )
        raise typer.Exit(EXIT_FAILURE) from err
      except EditorInvocationError as err:
        typer.echo(f"Error invoking editor: {err}", err=True)
        raise typer.Exit(EXIT_FAILURE) from err
      except ValueError as err:
        typer.echo(f"Error parsing editor output: {err}", err=True)
        typer.echo("No changes made to registry.", err=True)
        raise typer.Exit(EXIT_FAILURE) from err

    # Apply ordering
    if order:
      # Validate order field
      valid_orders = ["id", "severity", "status", "kind"]
      if order.lower() not in valid_orders:
        typer.echo(f"Error: invalid order field: {order}", err=True)
        typer.echo(f"Valid options: {', '.join(valid_orders)}", err=True)
        raise typer.Exit(EXIT_FAILURE)

      # Sort by requested field
      order_lower = order.lower()
      if order_lower == "id":
        items = sorted(items, key=lambda x: x.id)
      elif order_lower == "severity":
        items = sorted(items, key=lambda x: (not x.severity, x.severity or ""))
      elif order_lower == "status":
        items = sorted(items, key=lambda x: x.status)
      elif order_lower == "kind":
        items = sorted(items, key=lambda x: x.kind)
    else:
      # Default: priority ordering
      ordering = load_backlog_registry(root=repo_root)
      items = sort_by_priority(items, ordering)

    # Store total count before limiting
    total_count = len(items)

    # Apply limit if specified
    if limit is not None and limit > 0:
      items = items[:limit]

    # Format and output
    output = format_backlog_list_table(
      items, format_type, truncate, show_external=external
    )

    # Add pagination info if results were limited
    if limit is not None and total_count > limit and format_type == "table":
      output += f"\n\nShowing {len(items)} of {total_count} items. "
      output += "Use --limit to see more or --all to include resolved/implemented."

    # Output via pager or normal echo
    if pager and format_type == "table":
      from rich.console import Console

      console = Console()
      with console.pager():
        console.print(output, markup=False)
    else:
      typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

