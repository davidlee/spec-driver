"""List drift, issues, problems, improvements, and risks commands."""

from __future__ import annotations

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
from supekku.cli.list.backlog import list_backlog


@app.command("drift")
def list_drift(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status (open|closed)"),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on name (case-insensitive)",
    ),
  ] = None,
  regexp: RegexpOption = None,
  case_insensitive: CaseInsensitiveOption = False,
  format_type: FormatOption = "table",
  truncate: TruncateOption = False,
) -> None:
  """List drift ledgers."""
  try:
    from supekku.scripts.lib.drift.registry import DriftLedgerRegistry
    from supekku.scripts.lib.formatters.drift_formatters import format_drift_list_table

    registry = DriftLedgerRegistry(root=root)
    ledgers = list(registry.iter(status=status))

    # Apply substring filter
    if substring:
      sub_lower = substring.lower()
      ledgers = [
        dl
        for dl in ledgers
        if sub_lower in dl.name.lower() or sub_lower in dl.id.lower()
      ]

    # Apply regexp filter
    if regexp:
      ledgers = [
        dl
        for dl in ledgers
        if matches_regexp(regexp, [dl.name, dl.id], case_insensitive)
      ]

    output = format_drift_list_table(
      ledgers,
      format_type=format_type,
      truncate=truncate,
    )
    typer.echo(output)
    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

@app.command("issues")
def list_issues(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  severity: Annotated[
    str | None,
    typer.Option(
      "--severity",
      help="Filter by severity (e.g. p1, p2, p3)",
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
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on title (case-insensitive)",
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
  """List backlog issues with optional filtering.

  Shortcut for: list backlog --kind issue

  By default, resolved/implemented items are excluded. Use --all to show all.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  list_backlog(
    root=root,
    kind="issue",
    status=status,
    severity=severity,
    tag=tag,
    substring=substring,
    regexp=regexp,
    case_insensitive=case_insensitive,
    format_type=format_type,
    truncate=truncate,
    order=order,
    prioritize=prioritize,
    show_all=show_all,
    limit=limit,
    pager=pager,
    external=external,
  )

@app.command("problems")
def list_problems(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  severity: Annotated[
    str | None,
    typer.Option(
      "--severity",
      help="Filter by severity (e.g. p1, p2, p3)",
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
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on title (case-insensitive)",
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
  """List backlog problems with optional filtering.

  Shortcut for: list backlog --kind problem

  By default, resolved/implemented items are excluded. Use --all to show all.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  list_backlog(
    root=root,
    kind="problem",
    status=status,
    severity=severity,
    tag=tag,
    substring=substring,
    regexp=regexp,
    case_insensitive=case_insensitive,
    format_type=format_type,
    truncate=truncate,
    order=order,
    prioritize=prioritize,
    show_all=show_all,
    limit=limit,
    pager=pager,
    external=external,
  )

@app.command("improvements")
def list_improvements(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  severity: Annotated[
    str | None,
    typer.Option(
      "--severity",
      help="Filter by severity (e.g. p1, p2, p3)",
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
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on title (case-insensitive)",
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
  """List backlog improvements with optional filtering.

  Shortcut for: list backlog --kind improvement

  By default, resolved/implemented items are excluded. Use --all to show all.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  list_backlog(
    root=root,
    kind="improvement",
    status=status,
    severity=severity,
    tag=tag,
    substring=substring,
    regexp=regexp,
    case_insensitive=case_insensitive,
    format_type=format_type,
    truncate=truncate,
    order=order,
    prioritize=prioritize,
    show_all=show_all,
    limit=limit,
    pager=pager,
    external=external,
  )

@app.command("risks")
def list_risks(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  severity: Annotated[
    str | None,
    typer.Option(
      "--severity",
      help="Filter by severity (e.g. p1, p2, p3)",
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
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on title (case-insensitive)",
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
  """List backlog risks with optional filtering.

  Shortcut for: list backlog --kind risk

  By default, resolved/implemented items are excluded. Use --all to show all.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  list_backlog(
    root=root,
    kind="risk",
    status=status,
    severity=severity,
    tag=tag,
    substring=substring,
    regexp=regexp,
    case_insensitive=case_insensitive,
    format_type=format_type,
    truncate=truncate,
    order=order,
    prioritize=prioritize,
    show_all=show_all,
    limit=limit,
    pager=pager,
    external=external,
  )

