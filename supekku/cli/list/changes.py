"""List changes and plans commands."""

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
from supekku.scripts.lib.changes.registry import ChangeRegistry, discover_plans
from supekku.scripts.lib.core.filters import parse_multi_value_filter
from supekku.scripts.lib.formatters.change_formatters import (
  format_change_list_table,
  format_plan_list_table,
)


@app.command("changes")
def list_changes(
  root: RootOption = None,
  kind: Annotated[
    str,
    typer.Option(
      "--kind",
      "-k",
      help="Change artifact kind to list (delta, revision, audit, all)",
    ),
  ] = "all",
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring to match against ID, slug, or name (case-insensitive)",
    ),
  ] = None,
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (exact match)",
    ),
  ] = None,
  applies_to: Annotated[
    str | None,
    typer.Option(
      "--applies-to",
      "-a",
      help="Filter artifacts that reference a requirement",
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
  paths: Annotated[
    bool,
    typer.Option(
      "--paths",
      help="Include relative file paths (TSV format only)",
    ),
  ] = False,
  relations: Annotated[
    bool,
    typer.Option(
      "--relations",
      help="Include relation tuples (type:target) (TSV format only)",
    ),
  ] = False,
  applies: Annotated[
    bool,
    typer.Option(
      "--applies",
      help="Include applies_to.requirements list (TSV format only)",
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
  plan: Annotated[
    bool,
    typer.Option(
      "--plan",
      help="Include plan overview for deltas (TSV format only)",
    ),
  ] = False,
  external: ExternalOption = False,
) -> None:
  """List change artifacts (deltas, revisions, audits) with optional filters.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on ID, slug, and name fields.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Parse multi-value kind filter
  kind_values = parse_multi_value_filter(kind) if kind != "all" else []
  # Validate kind values
  valid_change_kinds = {"delta", "revision", "audit", "all"}
  for k in kind_values:
    if k not in valid_change_kinds:
      typer.echo(f"Error: invalid kind: {k}", err=True)
      raise typer.Exit(EXIT_FAILURE)

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    # Multi-value kind filter - expand "all" or use parsed values
    kinds = kind_values if kind_values else ["delta", "revision", "audit"]
    all_artifacts = []

    # Parse multi-value status filter
    status_values = parse_multi_value_filter(status)
    status_normalized = [s.lower() for s in status_values] if status_values else []

    for current_kind in kinds:
      registry = ChangeRegistry(root=root, kind=current_kind)
      artifacts = registry.collect()

      for artifact in artifacts.values():
        # Check substring filter
        if substring:
          text = substring.lower()
          if not (
            text in artifact.id.lower()
            or text in artifact.slug.lower()
            or text in artifact.name.lower()
          ):
            continue

        # Check regexp filter
        if regexp:
          try:
            if not matches_regexp(
              regexp,
              [artifact.id, artifact.slug, artifact.name],
              case_insensitive,
            ):
              continue
          except re.error as e:
            typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
            raise typer.Exit(EXIT_FAILURE) from e

        # Check status filter (multi-value OR logic)
        if status_normalized and artifact.status.lower() not in status_normalized:
          continue

        # Check tag filter (repeatable, OR logic)
        if tag and not any(t in artifact.tags for t in tag):
          continue

        # Check applies_to filter
        if applies_to:
          match = applies_to.lower()
          applies_list = []
          reqs = artifact.applies_to.get("requirements") if artifact.applies_to else []
          if isinstance(reqs, list):
            applies_list.extend(str(item).lower() for item in reqs)
          for relation in artifact.relations:
            target = str(relation.get("target", "")).lower()
            applies_list.append(target)
          if match not in applies_list:
            continue

        all_artifacts.append((current_kind, artifact))

    if not all_artifacts:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort by ID (alphabetical order)
    all_artifacts.sort(key=lambda x: x[1].id)

    # Format and output
    # For TSV with extra columns, use old formatter; otherwise use new table formatter
    has_extra_columns = paths or relations or applies or plan
    if format_type == "tsv" and has_extra_columns:
      for current_kind, artifact in all_artifacts:
        line = f"{artifact.id}\t{artifact.name}"

        if paths and hasattr(artifact, "path"):
          try:
            rel = artifact.path.relative_to(root)
          except (ValueError, AttributeError):
            rel = artifact.path if hasattr(artifact, "path") else ""
          line += f"\t{rel.as_posix() if rel else ''}"

        if relations and artifact.relations:
          rel_str = ", ".join(
            f"{r.get('type', '?')}:{r.get('target', '?')}" for r in artifact.relations
          )
          line += f"\t{rel_str}"

        if applies and artifact.applies_to:
          reqs = artifact.applies_to.get("requirements", [])
          if reqs:
            line += f"\t{', '.join(str(r) for r in reqs)}"

        if plan and current_kind == "delta" and artifact.plan:
          plan_id = artifact.plan.get("plan_id", "")
          phases = artifact.plan.get("phases", [])
          phase_count = len(phases) if phases else 0
          line += f"\t{plan_id}\t{phase_count} phases"

        typer.echo(line)
    else:
      # Extract just the artifacts
      artifacts_only = [artifact for _, artifact in all_artifacts]
      output = format_change_list_table(
        artifacts_only,
        format_type=format_type,
        truncate=truncate,
        show_external=external,
      )
      typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

@app.command("plans")
def list_plans(
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on ID or name (case-insensitive)",
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
  """List implementation plans with optional filtering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on ID, slug, and name fields.
  """
  if json_output:
    format_type = "json"

  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    from supekku.scripts.lib.core.repo import find_repo_root  # noqa: PLC0415

    repo_root = find_repo_root(root)
    plans = discover_plans(repo_root)

    if status:
      status_values = parse_multi_value_filter(status)
      status_normalized = [s.lower() for s in status_values]
      plans = [p for p in plans if p.status.lower() in status_normalized]
    if tag:
      plans = [p for p in plans if any(t in p.tags for t in tag)]
    if substring:
      filter_lower = substring.lower()
      plans = [
        p
        for p in plans
        if filter_lower in p.id.lower() or filter_lower in p.name.lower()
      ]
    if regexp:
      try:
        plans = [
          p
          for p in plans
          if matches_regexp(regexp, [p.id, p.slug, p.name], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not plans:
      raise typer.Exit(EXIT_SUCCESS)

    # Convert PlanSummary to dicts for formatter
    plan_dicts = [
      {
        "id": p.id,
        "status": p.status,
        "name": p.name,
        "delta_ref": p.delta_id,
        "kind": "plan",
      }
      for p in plans
    ]
    output = format_plan_list_table(plan_dicts, format_type, truncate)
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e

