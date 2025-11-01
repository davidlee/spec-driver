"""Decision/ADR display formatters.

Pure formatting functions with no business logic.
Formatters take DecisionRecord objects and return formatted strings for display.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.table_utils import (
  add_row_with_truncation,
  create_table,
  format_as_json,
  format_as_tsv,
  get_terminal_width,
  render_table,
)
from supekku.scripts.lib.formatters.theme import get_adr_status_style

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.models.decision import Decision


def _format_basic_fields(decision: Decision) -> list[str]:
  """Format basic decision fields (id, title, status)."""
  return [
    f"ID: {decision.id}",
    f"Title: {decision.title}",
    f"Status: {decision.status}",
  ]


def _format_timestamps(decision: Decision) -> list[str]:
  """Format timestamp fields if present."""
  lines = []
  timestamp_fields = [
    ("Created", decision.created),
    ("Decided", decision.decided),
    ("Updated", decision.updated),
    ("Reviewed", decision.reviewed),
  ]
  for label, value in timestamp_fields:
    if value:
      lines.append(f"{label}: {value}")
  return lines


def _format_people(decision: Decision) -> list[str]:
  """Format people-related fields (authors, owners)."""
  lines = []
  if decision.authors:
    lines.append(f"Authors: {', '.join(str(a) for a in decision.authors)}")
  if decision.owners:
    lines.append(f"Owners: {', '.join(str(o) for o in decision.owners)}")
  return lines


def _format_relationships(decision: Decision) -> list[str]:
  """Format decision relationship fields (supersedes, superseded_by)."""
  lines = []
  if decision.supersedes:
    lines.append(f"Supersedes: {', '.join(decision.supersedes)}")
  if decision.superseded_by:
    lines.append(f"Superseded by: {', '.join(decision.superseded_by)}")
  return lines


def _format_artifact_references(decision: Decision) -> list[str]:
  """Format references to other artifacts (specs, requirements, etc)."""
  lines = []
  artifact_refs = [
    ("Related specs", decision.specs),
    ("Requirements", decision.requirements),
    ("Deltas", decision.deltas),
    ("Revisions", decision.revisions),
    ("Audits", decision.audits),
  ]
  for label, refs in artifact_refs:
    if refs:
      lines.append(f"{label}: {', '.join(refs)}")
  return lines


def _format_related_items(decision: Decision) -> list[str]:
  """Format related decisions and policies."""
  lines = []
  if decision.related_decisions:
    lines.append(f"Related decisions: {', '.join(decision.related_decisions)}")
  if decision.related_policies:
    lines.append(f"Related policies: {', '.join(decision.related_policies)}")
  return lines


def _format_tags_and_backlinks(decision: Decision) -> list[str]:
  """Format tags and backlinks."""
  lines = []
  if decision.tags:
    lines.append(f"Tags: {', '.join(decision.tags)}")

  if decision.backlinks:
    lines.append("\nBacklinks:")
    for link_type, refs in decision.backlinks.items():
      lines.append(f"  {link_type}: {', '.join(refs)}")
  return lines


def format_decision_details(decision: Decision) -> str:
  """Format decision details as multi-line string for display.

  Args:
    decision: Decision object to format

  Returns:
    Formatted string with all decision details
  """
  sections = [
    _format_basic_fields(decision),
    _format_timestamps(decision),
    _format_people(decision),
    _format_relationships(decision),
    _format_artifact_references(decision),
    _format_related_items(decision),
    _format_tags_and_backlinks(decision),
  ]

  # Flatten all non-empty sections
  lines = [line for section in sections for line in section]
  return "\n".join(lines)


def _format_decision_as_tsv_rows(decisions: Sequence[Decision]) -> list[list[str]]:
  """Convert decisions to TSV row format."""
  rows = []
  for decision in decisions:
    updated_date = decision.updated.strftime("%Y-%m-%d") if decision.updated else "N/A"
    rows.append([decision.id, decision.status, decision.title, updated_date])
  return rows


def _calculate_column_widths(terminal_width: int) -> dict[int, int]:
  """Calculate optimal column widths for decision table.

  Args:
    terminal_width: Available terminal width

  Returns:
    Dictionary mapping column index to max width
  """
  # Custom column widths: ID (10), Status (12), Updated (10), rest for Title
  # Reserve space for borders/padding (~10 chars total)
  reserved = 10
  id_width = 10
  status_width = 12
  updated_width = 10
  title_width = max(
    terminal_width - id_width - status_width - updated_width - reserved,
    20,  # minimum title width
  )

  return {
    0: id_width,
    1: title_width,
    2: status_width,
    3: updated_width,
  }


def _prepare_decision_row(decision: Decision) -> list[str]:
  """Prepare a single decision row with styling.

  Args:
    decision: Decision to format

  Returns:
    List of formatted cell values [id, title, status, updated]
  """
  # Remove "ADR-XXX: " prefix from title for display
  title = re.sub(r"^ADR-\d+:\s*", "", decision.title)

  # Use em dash for missing dates in table format
  updated_date = decision.updated.strftime("%Y-%m-%d") if decision.updated else "—"

  # Apply styling with rich markup
  decision_id = f"[adr.id]{decision.id}[/adr.id]"
  status_style = get_adr_status_style(decision.status)
  status_styled = f"[{status_style}]{decision.status}[/{status_style}]"

  return [decision_id, title, status_styled, updated_date]


def _format_as_table(
  decisions: Sequence[Decision],
  truncate: bool,
) -> str:
  """Format decisions as a rich table.

  Args:
    decisions: Decisions to format
    truncate: Whether to truncate columns to fit terminal

  Returns:
    Rendered table string
  """
  table = create_table(
    columns=["ID", "Title", "Status", "Updated"],
    title="Architecture Decision Records",
  )

  max_widths = _calculate_column_widths(get_terminal_width()) if truncate else None

  for decision in decisions:
    row = _prepare_decision_row(decision)
    add_row_with_truncation(table, row, max_widths=max_widths)

  return render_table(table)


def format_decision_list_table(
  decisions: Sequence[Decision],
  format_type: str = "table",
  truncate: bool = False,
) -> str:
  """Format decisions as table, JSON, or TSV.

  Args:
    decisions: List of Decision objects to format
    format_type: Output format (table|json|tsv)
    truncate: If True, truncate long fields (default: False, show full content)

  Returns:
    Formatted string in requested format
  """
  if format_type == "json":
    return format_decision_list_json(decisions)

  if format_type == "tsv":
    rows = _format_decision_as_tsv_rows(decisions)
    return format_as_tsv(rows)

  return _format_as_table(decisions, truncate)


def format_decision_list_json(decisions: Sequence[Decision]) -> str:
  """Format decisions as JSON array.

  Args:
    decisions: List of Decision objects

  Returns:
    JSON string with structure: {"items": [...]}
  """
  items = []
  for decision in decisions:
    item = {
      "id": decision.id,
      "status": decision.status,
      "title": decision.title,
      "created": decision.created,
      "updated": decision.updated,
      "decided": decision.decided,
      "tags": decision.tags if decision.tags else [],
    }
    # Add optional fields
    if decision.specs:
      item["specs"] = decision.specs
    if decision.requirements:
      item["requirements"] = decision.requirements
    if decision.deltas:
      item["deltas"] = decision.deltas

    items.append(item)

  return format_as_json(items)
