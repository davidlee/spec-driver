"""List requirements command."""

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
from supekku.scripts.lib.formatters.requirement_formatters import (
  format_requirement_list_table,
)
from supekku.scripts.lib.relations.query import partition_by_reverse_references


@app.command("requirements")
def list_requirements(
  root: RootOption = None,
  spec: Annotated[
    str | None,
    typer.Option("--spec", "-s", help="Filter by spec ID"),
  ] = None,
  status: Annotated[
    str | None,
    typer.Option("--status", help="Filter by status"),
  ] = None,
  kind: Annotated[
    str | None,
    typer.Option("--kind", "-k", help="Filter by kind (FR|NF)"),
  ] = None,
  category: Annotated[
    str | None,
    typer.Option("--category", "-c", help="Filter by category (substring match)"),
  ] = None,
  verified_by: Annotated[
    str | None,
    typer.Option(
      "--verified-by",
      help="Filter by verification artifact (supports glob patterns, e.g., 'VT-*')",
    ),
  ] = None,
  vstatus: Annotated[
    str | None,
    typer.Option(
      "--vstatus",
      help="Filter by verification status "
      "(planned,in-progress,verified,failed,blocked)",
    ),
  ] = None,
  vkind: Annotated[
    str | None,
    typer.Option(
      "--vkind",
      help="Filter by verification kind (VT,VA,VH)",
    ),
  ] = None,
  substring: Annotated[
    str | None,
    typer.Option(
      "--filter",
      "-f",
      help="Substring filter on label or title (case-insensitive)",
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
  implemented_by: Annotated[
    str | None,
    typer.Option(
      "--implemented-by",
      help="Filter to requirements implemented by delta ID (e.g., DE-090 or 90)",
    ),
  ] = None,
  referenced_by: Annotated[
    str | None,
    typer.Option(
      "--referenced-by",
      help="Keep requirements targeted by artifacts of TYPE (e.g., delta)",
    ),
  ] = None,
  not_referenced_by: Annotated[
    str | None,
    typer.Option(
      "--not-referenced-by",
      help="Keep requirements NOT targeted by artifacts of TYPE",
    ),
  ] = None,
  unimplemented: Annotated[
    bool,
    typer.Option(
      "--unimplemented",
      help=(
        "Show requirements not implemented by any delta "
        "(alias for --not-referenced-by delta)"
      ),
    ),
  ] = False,
  source_kind: Annotated[
    str | None,
    typer.Option(
      "--source-kind",
      help="Filter by source kind (spec,issue,problem,improvement).",
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
  truncate: TruncateOption = False,
  external: ExternalOption = False,
) -> None:
  """List requirements with optional filtering.

  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on UID, label, title, and category fields.
  The --category flag does substring matching on category field.
  The --verified-by flag filters by verification artifact (supports glob patterns).
  The --implemented-by flag filters to requirements a delta implements.
  Use --case-insensitive (-i) to make regexp and category filters case-insensitive.

  Examples:
    list requirements -k FR,NF                   # Multi-value kind filter
    list requirements --verified-by "VT-CLI-*"   # Glob pattern match
    list requirements --vstatus verified --json   # Verification status filter
    list requirements --spec SPEC-110 --vkind VT  # Combined filters
    list requirements --source-kind issue          # Filter by source
    list requirements --implemented-by DE-090      # Requirements delta implements
    list requirements --unimplemented              # Requirements without a delta
    list requirements --referenced-by delta        # Requirements referenced by deltas
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # --unimplemented alias expansion
  if unimplemented:
    if not_referenced_by:
      typer.echo(
        "Error: --unimplemented and --not-referenced-by are mutually exclusive",
        err=True,
      )
      raise typer.Exit(EXIT_FAILURE)
    not_referenced_by = "delta"

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
    from pathlib import Path

    from supekku.scripts.lib.core.paths import get_registry_dir
    from supekku.scripts.lib.requirements.registry import RequirementsRegistry

    repo_root = Path(root) if root else Path.cwd()
    registry_path = get_registry_dir(repo_root) / "requirements.yaml"
    registry = RequirementsRegistry(registry_path)

    # Apply reverse relationship query first (if specified)
    if verified_by:
      requirements = registry.find_by_verified_by(verified_by)
    else:
      requirements = list(registry.records.values())

    # Apply filters
    if spec:
      requirements = [r for r in requirements if spec.upper() in r.specs]

    if implemented_by:
      from supekku.cli.common import normalize_id  # noqa: PLC0415
      from supekku.scripts.lib.blocks.delta import (  # noqa: PLC0415
        extract_delta_relationships,
      )
      from supekku.scripts.lib.core.spec_utils import (  # noqa: PLC0415
        load_markdown_file,
      )

      delta_id = normalize_id("delta", implemented_by)
      delta_registry = ChangeRegistry(root=root, kind="delta")
      delta_art = delta_registry.find(delta_id)
      if delta_art is None:
        typer.echo(f"Error: delta not found: {delta_id}", err=True)
        raise typer.Exit(EXIT_FAILURE)

      _, body = load_markdown_file(delta_art.path)
      rels_block = extract_delta_relationships(body)
      impl_ids: set[str] = set()
      if rels_block:
        impl_ids = {
          r.upper()
          for r in rels_block.data.get("requirements", {}).get("implements", [])
        }
      requirements = [r for r in requirements if r.uid.upper() in impl_ids]

    # Multi-value status filter (OR logic)
    if status:
      status_values = parse_multi_value_filter(status)
      status_normalized = [s.lower() for s in status_values]
      requirements = [r for r in requirements if r.status.lower() in status_normalized]

    # Multi-value kind filter (OR logic)
    if kind:
      kind_values = parse_multi_value_filter(kind)
      kind_prefixes = [k.upper() for k in kind_values]
      requirements = [
        r
        for r in requirements
        if any(r.label.startswith(prefix) for prefix in kind_prefixes)
      ]

    # Source kind filter (multi-value OR; "" passes all per DEC-076-05)
    if source_kind:
      sk_values = {v.lower() for v in parse_multi_value_filter(source_kind)}
      requirements = [
        r
        for r in requirements
        if not r.source_kind or r.source_kind.lower() in sk_values
      ]

    if tag:
      requirements = [r for r in requirements if any(t in r.tags for t in tag)]

    # Category filter (substring match, respects --case-insensitive)
    if category:
      if case_insensitive:
        category_lower = category.lower()
        requirements = [
          r for r in requirements if r.category and category_lower in r.category.lower()
        ]
      else:
        requirements = [
          r for r in requirements if r.category and category in r.category
        ]

    if substring:
      filter_lower = substring.lower()
      requirements = [
        r
        for r in requirements
        if filter_lower in r.label.lower() or filter_lower in r.title.lower()
      ]

    # Apply regexp filter on uid, label, title, category
    if regexp:
      try:
        requirements = [
          r
          for r in requirements
          if matches_regexp(
            regexp, [r.uid, r.label, r.title, r.category or ""], case_insensitive
          )
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    # Verification status filter (OR across values, AND with other flags)
    if vstatus:
      vstatus_values = parse_multi_value_filter(vstatus)
      vstatus_set = set(vstatus_values)
      requirements = [
        r
        for r in requirements
        if any(e.get("status") in vstatus_set for e in r.coverage_entries)
      ]

    # Verification kind filter (OR across values, AND with other flags)
    if vkind:
      vkind_values = parse_multi_value_filter(vkind)
      vkind_set = set(vkind_values)
      requirements = [
        r
        for r in requirements
        if any(e.get("kind") in vkind_set for e in r.coverage_entries)
      ]

    # Apply reverse reference filtering
    if referenced_by or not_referenced_by:
      ref_type = referenced_by or not_referenced_by
      referrers = load_all_artifacts(repo_root, ref_type)
      referenced, unreferenced = partition_by_reverse_references(
        requirements,
        referrers,
        candidate_id_fn=lambda r: r.uid,
      )
      requirements = referenced if referenced_by else unreferenced

    if not requirements:
      raise typer.Exit(EXIT_SUCCESS)

    # Sort and format
    requirements.sort(key=lambda r: r.uid)
    output = format_requirement_list_table(
      requirements, format_type, truncate, show_external=external
    )
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
