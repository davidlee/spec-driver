"""List cards, memories, and schemas commands."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

import typer

from supekku.cli.common import (
  EXIT_FAILURE,
  EXIT_SUCCESS,
  CaseInsensitiveOption,
  FormatOption,
  RegexpOption,
  RootOption,
  TruncateOption,
  matches_regexp,
)
from supekku.cli.list import app
from supekku.scripts.lib.cards import CardRegistry
from supekku.scripts.lib.formatters.card_formatters import (
  format_card_list_json,
  format_card_list_table,
)
from supekku.scripts.lib.formatters.memory_formatters import (
  format_memory_list_table,
  format_staleness_table,
)
from supekku.scripts.lib.memory.registry import MemoryRegistry
from supekku.scripts.lib.memory.selection import MatchContext, select
from supekku.scripts.lib.memory.staleness import compute_batch_staleness


@app.command("cards")
def list_cards(
  root: RootOption = None,
  lane: Annotated[
    str | None,
    typer.Option(
      "--lane",
      "-l",
      help="Filter by lane (backlog/doing/done)",
    ),
  ] = None,
  all_lanes: Annotated[
    bool,
    typer.Option(
      "--all",
      "-a",
      help="Show all cards including done/archived (default hides done/archived)",
    ),
  ] = False,
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
  """List kanban cards with optional filtering.

  By default, hides cards in done/ and archived/ lanes. Use --all to show everything.
  The --filter flag does substring matching (case-insensitive).
  The --regexp flag does pattern matching on ID and title fields.
  """
  # --json flag overrides --format
  if json_output:
    format_type = "json"

  # Validate format
  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = CardRegistry(root=root)

    # Get cards, optionally filtered by lane
    if lane:
      cards = registry.cards_by_lane(lane)
    else:
      cards = registry.all_cards()
      # Filter out done/archived unless --all specified
      if not all_lanes:
        cards = [c for c in cards if c.lane not in ("done", "archived")]

    # Apply substring filter
    if substring:
      filter_lower = substring.lower()
      cards = [
        c
        for c in cards
        if filter_lower in c.id.lower() or filter_lower in c.title.lower()
      ]

    # Apply regexp filter on id, title
    if regexp:
      try:
        cards = [
          c for c in cards if matches_regexp(regexp, [c.id, c.title], case_insensitive)
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    if not cards:
      raise typer.Exit(EXIT_SUCCESS)

    # Format and output
    if format_type == "json":
      output = format_card_list_json(cards)
    else:
      output = format_card_list_table(cards, format_type, truncate)

    typer.echo(output)
    raise typer.Exit(EXIT_SUCCESS)

  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


@app.command("memories")
def list_memories(  # noqa: PLR0913
  root: RootOption = None,
  status: Annotated[
    str | None,
    typer.Option("--status", "-s", help="Filter by status"),
  ] = None,
  memory_type: Annotated[
    str | None,
    typer.Option("--type", "-t", help="Filter by memory type"),
  ] = None,
  tag: Annotated[
    str | None,
    typer.Option("--tag", help="Filter by tag (metadata pre-filter)"),
  ] = None,
  path: Annotated[
    list[str] | None,
    typer.Option(
      "--path",
      "-p",
      help="Scope match: paths (repeatable)",
    ),
  ] = None,
  command: Annotated[
    str | None,
    typer.Option(
      "--command",
      "-c",
      help="Scope match: command string (token-prefix)",
    ),
  ] = None,
  match_tag: Annotated[
    list[str] | None,
    typer.Option(
      "--match-tag",
      help="Scope match: tags (repeatable, OR with path/command)",
    ),
  ] = None,
  include_draft: Annotated[
    bool,
    typer.Option("--include-draft", help="Include draft memories"),
  ] = False,
  limit: Annotated[
    int | None,
    typer.Option("--limit", "-n", help="Max results"),
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
  links_to: Annotated[
    str | None,
    typer.Option(
      "--links-to",
      help="Show memories that link to this ID (backlinks)",
    ),
  ] = None,
  truncate: TruncateOption = False,
  stale: Annotated[
    bool,
    typer.Option(
      "--stale",
      help="Show staleness ranking (three-tier scope-aware output)",
    ),
  ] = False,
) -> None:
  """List memory records with optional filtering and scope matching.

  The --filter flag does substring matching (case-insensitive).
  Metadata pre-filters (--type, --status, --tag) apply first (AND logic).
  Scope matching (--path, --command, --match-tag) filters by context (OR).
  Results ordered deterministically by severity/weight/specificity/recency/id.
  """
  if json_output:
    format_type = "json"

  if format_type not in ["table", "json", "tsv"]:
    typer.echo(f"Error: invalid format: {format_type}", err=True)
    raise typer.Exit(EXIT_FAILURE)

  try:
    registry = MemoryRegistry(root=root)

    # Step 0: backlink filter (overrides normal filter pipeline)
    if links_to:
      from supekku.scripts.lib.memory.ids import normalize_memory_id  # noqa: PLC0415
      from supekku.scripts.lib.memory.links import compute_backlinks  # noqa: PLC0415

      target_id = normalize_memory_id(links_to)
      bodies = registry.collect_bodies()
      backlinks = compute_backlinks(bodies)
      source_ids = set(backlinks.get(target_id, []))
      all_records = registry.collect()
      records = [all_records[sid] for sid in sorted(source_ids) if sid in all_records]
    # Step 1: metadata pre-filter
    elif any([memory_type, tag]):
      records = registry.filter(
        memory_type=memory_type,
        tag=tag,
        status=status,
      )
    else:
      records = list(registry.iter(status=status))

    # Step 1.5: substring filter
    if substring:
      filter_lower = substring.lower()
      records = [
        r
        for r in records
        if filter_lower in r.id.lower() or filter_lower in r.name.lower()
      ]

    # Step 2: regexp filter
    if regexp:
      try:
        records = [
          r
          for r in records
          if matches_regexp(
            regexp,
            [r.name, r.summary],
            case_insensitive,
          )
        ]
      except re.error as e:
        typer.echo(f"Error: invalid regexp pattern: {e}", err=True)
        raise typer.Exit(EXIT_FAILURE) from e

    # Step 3: build context and apply selection pipeline
    has_context = any([path, command, match_tag])
    context = (
      MatchContext(
        paths=path or [],
        command=command,
        tags=match_tag or [],
      )
      if has_context
      else None
    )

    records = select(
      records,
      context,
      include_draft=include_draft,
      skip_status_filter=status is not None,
      limit=limit,
    )

    if not records:
      raise typer.Exit(EXIT_SUCCESS)

    if stale:
      output = _format_stale_memories(records, root)
    else:
      output = format_memory_list_table(records, format_type, truncate)
    typer.echo(output)

    raise typer.Exit(EXIT_SUCCESS)
  except (FileNotFoundError, ValueError, KeyError) as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e


def _format_stale_memories(
  records: list,
  root: Path | None,
) -> str:
  """Compute staleness and format as tiered table."""
  from supekku.scripts.lib.core.repo import find_repo_root  # noqa: PLC0415

  repo_root = find_repo_root(root)
  infos = compute_batch_staleness(records, repo_root)
  records_by_id = {r.id: r for r in records}
  return format_staleness_table(infos, records_by_id)


@app.command("schemas")
def list_schemas_cmd(
  schema_type: Annotated[
    str | None,
    typer.Argument(help="Schema type: 'blocks', 'frontmatter', or omit for both"),
  ] = None,
) -> None:
  """List available block and/or frontmatter schemas."""
  from supekku.cli.schema import list_schemas  # noqa: PLC0415

  list_schemas(schema_type=schema_type)


# Singular command aliases - dynamically register
_PLURAL_TO_SINGULAR = {
  "specs": "spec",
  "deltas": "delta",
  "changes": "change",
  "adrs": "adr",
  "policies": "policy",
  "standards": "standard",
  "requirements": "requirement",
  "revisions": "revision",
  "audits": "audit",
  "issues": "issue",
  "problems": "problem",
  "improvements": "improvement",
  "risks": "risk",
  "cards": "card",
  "memories": "memory",
  "plans": "plan",
}

# schemas uses a different function name, register singular alias directly
app.command("schema", hidden=True)(list_schemas_cmd)

for plural, singular in _PLURAL_TO_SINGULAR.items():
  plural_func = globals().get(f"list_{plural}")
  if plural_func and callable(plural_func):
    app.command(singular)(plural_func)


if __name__ == "__main__":  # pragma: no cover
  app()
