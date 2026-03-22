"""List ADRs, policies, and standards commands."""

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
from supekku.scripts.lib.decisions.registry import DecisionRegistry
from supekku.scripts.lib.formatters.decision_formatters import (
  format_decision_list_table,
)
from supekku.scripts.lib.formatters.policy_formatters import format_policy_list_table
from supekku.scripts.lib.formatters.standard_formatters import (
  format_standard_list_table,
)
from supekku.scripts.lib.policies.registry import PolicyRegistry
from supekku.scripts.lib.standards.registry import StandardRegistry


@app.command("adrs")
def list_adrs(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (accepted, draft, deprecated, etc.)",
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
  spec: Annotated[
    str | None,
    typer.Option(
      "--spec",
      help="Filter by spec reference",
    ),
  ] = None,
  delta: Annotated[
    str | None,
    typer.Option(
      "--delta",
      "-d",
      help="Filter by delta reference",
    ),
  ] = None,
  requirement_filter: Annotated[
    str | None,
    typer.Option(
      "--requirement",
      help="Filter by requirement reference",
    ),
  ] = None,
  policy: Annotated[
    str | None,
    typer.Option(
      "--policy",
      "-p",
      help="Filter by policy reference",
    ),
  ] = None,
  standard: Annotated[
    str | None,
    typer.Option(
      "--standard",
      help="Filter by standard reference",
    ),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on ID or title (case-insensitive)",
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
) -> None:
  """List Architecture Decision Records (ADRs) with optional filtering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag filters on title and summary fields.
  Other flags filter on specific structured fields (status, tags, references).

  Examples:
    list adrs -s accepted             # Filter by status
    list adrs --spec SPEC-110 --json  # ADRs referencing a spec
    list adrs -t cli                  # Filter by tag
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = DecisionRegistry(root=root)

    # Apply structured filters (tag handled separately for repeatable OR)
    if any([spec, delta, requirement_filter, policy, standard]):
      decisions = registry.filter(
        spec=spec,
        delta=delta,
        requirement=requirement_filter,
        policy=policy,
        standard=standard,
      )
    else:
      decisions = list(registry.iter(status=status))

    # Tag filter (repeatable, OR logic)
    if tag:
      decisions = [d for d in decisions if any(t in d.tags for t in tag)]

    # Apply substring filter
    if substring:
      filter_lower = substring.lower()
      decisions = [
        d
        for d in decisions
        if filter_lower in d.id.lower() or filter_lower in d.title.lower()
      ]

    # Apply regexp filter on title and summary
    if regexp:
      try:
        decisions = [
          d
          for d in decisions
          if matches_regexp(regexp, [d.title, d.summary], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not decisions:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    decisions_sorted = sorted(decisions, key=lambda d: d.id)
    output = format_decision_list_table(decisions_sorted, format_type, truncate)
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

@app.command("policies")
def list_policies(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (draft, required, deprecated)",
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
  spec: Annotated[
    str | None,
    typer.Option(
      "--spec",
      help="Filter by spec reference",
    ),
  ] = None,
  delta: Annotated[
    str | None,
    typer.Option(
      "--delta",
      "-d",
      help="Filter by delta reference",
    ),
  ] = None,
  requirement_filter: Annotated[
    str | None,
    typer.Option(
      "--requirement",
      help="Filter by requirement reference",
    ),
  ] = None,
  standard: Annotated[
    str | None,
    typer.Option(
      "--standard",
      help="Filter by standard reference",
    ),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on ID or title (case-insensitive)",
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
  """List policies with optional filtering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag filters on title and summary fields.
  Other flags filter on specific structured fields (status, tags, references).
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = PolicyRegistry(root=root)

    # Apply structured filters (tag handled separately for repeatable OR)
    if any([spec, delta, requirement_filter, standard]):
      policies = registry.filter(
        spec=spec,
        delta=delta,
        requirement=requirement_filter,
        standard=standard,
      )
    else:
      policies = list(registry.iter(status=status))

    # Tag filter (repeatable, OR logic)
    if tag:
      policies = [p for p in policies if any(t in p.tags for t in tag)]

    # Apply substring filter
    if substring:
      filter_lower = substring.lower()
      policies = [
        p
        for p in policies
        if filter_lower in p.id.lower() or filter_lower in p.title.lower()
      ]

    # Apply regexp filter on title
    if regexp:
      try:
        policies = [
          p for p in policies if matches_regexp(regexp, [p.title], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not policies:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    policies_sorted = sorted(policies, key=lambda p: p.id)
    output = format_policy_list_table(
      policies_sorted, format_type, truncate, show_external=external
    )
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

@app.command("standards")
def list_standards(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (draft, required, default, deprecated)",
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
  spec: Annotated[
    str | None,
    typer.Option(
      "--spec",
      help="Filter by spec reference",
    ),
  ] = None,
  delta: Annotated[
    str | None,
    typer.Option(
      "--delta",
      "-d",
      help="Filter by delta reference",
    ),
  ] = None,
  requirement_filter: Annotated[
    str | None,
    typer.Option(
      "--requirement",
      help="Filter by requirement reference",
    ),
  ] = None,
  policy: Annotated[
    str | None,
    typer.Option(
      "--policy",
      "-p",
      help="Filter by policy reference",
    ),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on ID or title (case-insensitive)",
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
  """List standards with optional filtering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag filters on title and summary fields.
  Other flags filter on specific structured fields (status, tags, references).
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = StandardRegistry(root=root)

    # Apply structured filters (tag handled separately for repeatable OR)
    if any([spec, delta, requirement_filter, policy]):
      standards = registry.filter(
        spec=spec,
        delta=delta,
        requirement=requirement_filter,
        policy=policy,
      )
    else:
      standards = list(registry.iter(status=status))

    # Tag filter (repeatable, OR logic)
    if tag:
      standards = [s for s in standards if any(t in s.tags for t in tag)]

    # Apply substring filter
    if substring:
      filter_lower = substring.lower()
      standards = [
        s
        for s in standards
        if filter_lower in s.id.lower() or filter_lower in s.title.lower()
      ]

    # Apply regexp filter on title
    if regexp:
      try:
        standards = [
          s for s in standards if matches_regexp(regexp, [s.title], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not standards:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    standards_sorted = sorted(standards, key=lambda s: s.id)
    output = format_standard_list_table(
      standards_sorted, format_type, truncate, show_external=external
    )
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

