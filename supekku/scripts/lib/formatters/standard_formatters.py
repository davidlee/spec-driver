"""Standard display formatters.

Pure formatting functions with no business logic.
Formatters take StandardRecord objects and return formatted strings for display.
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
from supekku.scripts.lib.formatters.theme import get_standard_status_style

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.scripts.lib.standards.registry import StandardRecord


def _format_basic_fields(standard: StandardRecord) -> list[str]:
  """Format basic standard fields (id, title, status)."""
  return [
    f"ID: {standard.id}",
    f"Title: {standard.title}",
    f"Status: {standard.status}",
  ]


def _format_timestamps(standard: StandardRecord) -> list[str]:
  """Format timestamp fields if present."""
  lines = []
  timestamp_fields = [
    ("Created", standard.created),
    ("Updated", standard.updated),
    ("Reviewed", standard.reviewed),
  ]
  for label, value in timestamp_fields:
    if value:
      lines.append(f"{label}: {value}")
  return lines


def _format_people(standard: StandardRecord) -> list[str]:
  """Format people-related fields (owners)."""
  lines = []
  if standard.owners:
    lines.append(f"Owners: {', '.join(str(o) for o in standard.owners)}")
  return lines


def _format_relationships(standard: StandardRecord) -> list[str]:
  """Format standard relationship fields (supersedes, superseded_by)."""
  lines = []
  if standard.supersedes:
    lines.append(f"Supersedes: {', '.join(standard.supersedes)}")
  if standard.superseded_by:
    lines.append(f"Superseded by: {', '.join(standard.superseded_by)}")
  return lines


def _format_artifact_references(standard: StandardRecord) -> list[str]:
  """Format references to other artifacts (specs, requirements, etc)."""
  lines = []
  artifact_refs = [
    ("Related specs", standard.specs),
    ("Requirements", standard.requirements),
    ("Deltas", standard.deltas),
    ("Policies", standard.policies),
  ]
  for label, refs in artifact_refs:
    if refs:
      lines.append(f"{label}: {', '.join(refs)}")
  return lines


def _format_related_items(standard: StandardRecord) -> list[str]:
  """Format related policies and standards."""
  lines = []
  if standard.related_policies:
    lines.append(f"Related policies: {', '.join(standard.related_policies)}")
  if standard.related_standards:
    lines.append(f"Related standards: {', '.join(standard.related_standards)}")
  return lines


def _format_tags_and_backlinks(standard: StandardRecord) -> list[str]:
  """Format tags and backlinks."""
  lines = []
  if standard.tags:
    lines.append(f"Tags: {', '.join(standard.tags)}")

  if standard.backlinks:
    lines.append("\nBacklinks:")
    for link_type, refs in standard.backlinks.items():
      lines.append(f"  {link_type}: {', '.join(refs)}")
  return lines


def format_standard_details(standard: StandardRecord) -> str:
  """Format standard details as multi-line string for display.

  Args:
    standard: StandardRecord object to format

  Returns:
    Formatted string with all standard details
  """
  sections = [
    _format_basic_fields(standard),
    _format_timestamps(standard),
    _format_people(standard),
    _format_relationships(standard),
    _format_artifact_references(standard),
    _format_related_items(standard),
    _format_tags_and_backlinks(standard),
  ]

  # Flatten all non-empty sections
  lines = [line for section in sections for line in section]
  return "\n".join(lines)


def _format_standard_as_tsv_rows(
  standards: Sequence[StandardRecord],
) -> list[list[str]]:
  """Convert standards to TSV row format."""
  rows = []
  for standard in standards:
    updated_date = standard.updated.strftime("%Y-%m-%d") if standard.updated else "N/A"
    rows.append([standard.id, standard.status, standard.title, updated_date])
  return rows


def _calculate_column_widths(terminal_width: int) -> dict[int, int]:
  """Calculate optimal column widths for standard table.

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


def _prepare_standard_row(standard: StandardRecord) -> list[str]:
  """Prepare a single standard row with styling.

  Args:
    standard: StandardRecord to format

  Returns:
    List of formatted cell values [id, title, status, updated]
  """
  # Remove "STD-XXX: " prefix from title for display
  title = re.sub(r"^STD-\d+:\s*", "", standard.title)

  # Use em dash for missing dates in table format
  updated_date = standard.updated.strftime("%Y-%m-%d") if standard.updated else "—"

  # Apply styling with rich markup
  standard_id = f"[standard.id]{standard.id}[/standard.id]"
  status_style = get_standard_status_style(standard.status)
  status_styled = f"[{status_style}]{standard.status}[/{status_style}]"

  return [standard_id, title, status_styled, updated_date]


def _format_as_table(
  standards: Sequence[StandardRecord],
  truncate: bool,
) -> str:
  """Format standards as a rich table.

  Args:
    standards: Standards to format
    truncate: Whether to truncate columns to fit terminal

  Returns:
    Rendered table string
  """
  table = create_table(
    columns=["ID", "Title", "Status", "Updated"],
    title="Standards",
  )

  max_widths = _calculate_column_widths(get_terminal_width()) if truncate else None

  for standard in standards:
    row = _prepare_standard_row(standard)
    add_row_with_truncation(table, row, max_widths=max_widths)

  return render_table(table)


def format_standard_list_table(
  standards: Sequence[StandardRecord],
  format_type: str = "table",
  truncate: bool = False,
) -> str:
  """Format standards as table, JSON, or TSV.

  Args:
    standards: List of StandardRecord objects to format
    format_type: Output format (table|json|tsv)
    truncate: If True, truncate long fields (default: False, show full content)

  Returns:
    Formatted string in requested format
  """
  if format_type == "json":
    return format_standard_list_json(standards)

  if format_type == "tsv":
    rows = _format_standard_as_tsv_rows(standards)
    return format_as_tsv(rows)

  return _format_as_table(standards, truncate)


def format_standard_list_json(standards: Sequence[StandardRecord]) -> str:
  """Format standards as JSON array.

  Args:
    standards: List of StandardRecord objects

  Returns:
    JSON string representation
  """
  standard_dicts = [
    {
      "id": standard.id,
      "title": standard.title,
      "status": standard.status,
      "updated": standard.updated.strftime("%Y-%m-%d") if standard.updated else None,
      "summary": standard.summary,
      "path": standard.path,
    }
    for standard in standards
  ]
  return format_as_json(standard_dicts)
