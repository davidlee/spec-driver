"""List specs command."""

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
from supekku.cli.list import _parse_relation_filter, app
from supekku.scripts.lib.blocks.metadata.aliases import normalize_field
from supekku.scripts.lib.core.filters import parse_multi_value_filter
from supekku.scripts.lib.formatters.spec_formatters import (
  format_spec_list_item,
  format_spec_list_table,
)
from supekku.scripts.lib.relations.query import (
  find_by_relation,
  find_related_to,
)
from supekku.scripts.lib.specs.registry import SpecRegistry


@app.command("specs")
def list_specs(
  root: RootOption = None,
  kind: Annotated[
    str,
    typer.Option(
      "--kind",
      "-k",
      help="Restrict to tech specs, product specs, or both",
    ),
  ] = "all",
  status: Annotated[
    str | None,
    typer.Option(
      "--status",
      "-s",
      help="Filter by status (draft, active, deprecated, superseded)",
    ),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring to match against spec ID, slug, or name (case-insensitive)",
    ),
  ] = None,
  category: Annotated[
    str,
    typer.Option(
      "--category",
      "-c",
      help=(
        "Filter tech specs by taxonomy category (comma-separated). "
        "Default: assembly,unknown (hides unit specs). Use 'all' to include unit specs."
      ),
    ),
  ] = "assembly,unknown",
  c4_level: Annotated[
    str,
    typer.Option(
      "--c4-level",
      help=(
        "Filter tech specs by C4 level (comma-separated). "
        "Default: all. Values: system,container,component,code,interaction,unknown."
      ),
    ),
  ] = "all",
  informed_by: Annotated[
    str | None,
    typer.Option(
      "--informed-by",
      help="Filter by ADR ID (e.g., ADR-001)",
    ),
  ] = None,
  related_to: Annotated[
    str | None,
    typer.Option(
      "--related-to",
      help="Show specs referencing ID in any slot (relations, informed_by)",
    ),
  ] = None,
  relation: Annotated[
    str | None,
    typer.Option(
      "--relation",
      help="Filter by relation TYPE:TARGET (e.g., implements:PROD-010)",
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
  refs: Annotated[
    bool,
    typer.Option(
      "--refs",
      help="Include refs column (count in table, type:target in TSV)",
    ),
  ] = False,
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
      help="Include relative file paths in the output (TSV format only)",
    ),
  ] = False,
  tags_column: Annotated[
    bool,
    typer.Option(
      "--tags",
      help="Show tags column in list output (opt-in)",
    ),
  ] = False,
  external: ExternalOption = False,
) -> None:
  """List SPEC/PROD artifacts with optional filtering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on ID, slug, and name fields.
  The --informed-by flag filters by ADR ID (reverse relationship query).
  The --related-to flag searches all reference slots (relations, informed_by).
  The --relation flag filters by TYPE:TARGET in .relations only.

  Examples:
    list specs -k prod,tech            # Multi-value kind filter
    list specs -s active --json        # JSON output with status filter
    list specs --informed-by ADR-001   # Specs informed by an ADR
    list specs --related-to ADR-001    # Specs referencing ADR-001 in any slot
    list specs --relation implements:PROD-010  # By relation type and target
    list specs --refs                  # Include refs column
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Parse multi-value kind filter
  kind_values = parse_multi_value_filter(kind) if kind != "all" else []
  # Validate kind values
  valid_kinds = {"tech", "product", "prod", "all"}
  for k in kind_values:
    if k not in valid_kinds:
      typer.echo(f"Error: invalid kind: {k}", err=True)
      raise typer.Exit(EXIT_FAILURE)

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = SpecRegistry(root)
    filter_substring = (substring or "").strip().lower()

    # Apply reverse relationship query first (if specified)
    if informed_by:
      specs = registry.find_by_informed_by(informed_by)
    else:
      specs = registry.all_specs()

    # Apply generic relation filters (after reverse relationship query)
    if related_to:
      specs = find_related_to(specs, related_to)
    if relation:
      rel_type, rel_target = _parse_relation_filter(relation)
      specs = find_by_relation(specs, relation_type=rel_type, target=rel_target)

    # Apply status filter (multi-value OR logic)
    if status:
      status_values = parse_multi_value_filter(status)
      status_normalized = [normalize_field("spec", "status", s) for s in status_values]
      specs = [
        spec
        for spec in specs
        if normalize_field("spec", "status", spec.status) in status_normalized
      ]

    if filter_substring:
      specs = [
        spec
        for spec in specs
        if filter_substring in spec.id.lower()
        or filter_substring in spec.slug.lower()
        or filter_substring in spec.name.lower()
      ]

    # Apply regexp filter on id, slug, name
    if regexp:
      try:
        specs = [
          spec
          for spec in specs
          if matches_regexp(regexp, [spec.id, spec.slug, spec.name], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if tag:
      specs = [s for s in specs if any(t in s.tags for t in tag)]

    # Filter by kind (multi-value OR logic)
    def normalise_kind(requested_kinds: list[str], spec_id: str) -> bool:
      if not requested_kinds:  # "all" or no filter
        return True
      # Check if spec matches any of the requested kinds
      for k in requested_kinds:
        if k in ("tech", "all") and spec_id.startswith("SPEC-"):
          return True
        if k in ("product", "prod", "all") and spec_id.startswith("PROD-"):
          return True
      return False

    specs = [spec for spec in specs if normalise_kind(kind_values, spec.id)]

    # Filter tech specs by taxonomy (category / c4_level).
    # Product specs are never affected by these filters.
    category_values = parse_multi_value_filter(category) if category != "all" else []
    c4_level_values = parse_multi_value_filter(c4_level) if c4_level != "all" else []

    def matches_taxonomy(spec) -> bool:
      if not spec.id.startswith("SPEC-"):
        return True  # Non-tech specs pass through
      if category_values:
        spec_cat = spec.category or "unknown"
        if spec_cat not in category_values:
          return False
      if c4_level_values:
        spec_level = spec.c4_level or "unknown"
        if spec_level not in c4_level_values:
          return False
      return True

    specs = [spec for spec in specs if matches_taxonomy(spec)]

    if not specs:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    specs.sort(key=lambda spec: spec.id)

    # For TSV with paths, use old formatter; otherwise use new table formatter
    if format_type == "tsv" and paths:
      for spec in specs:
        line = format_spec_list_item(
          spec,
          include_path=paths,
          root=registry.root,
        )
        typer.echo(line)
    else:
      output = format_spec_list_table(
        specs,
        format_type=format_type,
        truncate=truncate,
        show_external=external,
        show_refs=refs,
        show_tags=tags_column,
      )
      typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
