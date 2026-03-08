"""Standard display formatters.

Pure formatting functions with no business logic.
Formatters take StandardRecord objects and return formatted strings for display.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.column_defs import (
  EXT_ID_COLUMN,
  STANDARD_COLUMNS,
  column_labels,
)
from supekku.scripts.lib.formatters.table_utils import (
  format_as_json,
  format_list_table,
)
from supekku.scripts.lib.formatters.theme import get_standard_status_style

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.scripts.lib.standards.registry import StandardRecord


def _format_basic_fields(standard: StandardRecord) -> list[str]:
  """Format basic standard fields (id, title, status)."""
  lines = [
    f"ID: {standard.id}",
    f"Title: {standard.title}",
    f"Status: {standard.status}",
  ]
  if standard.ext_id:
    ext_line = f"External: {standard.ext_id}"
    if standard.ext_url:
      ext_line += f" ({standard.ext_url})"
    lines.append(ext_line)
  return lines


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


def _prepare_standard_tsv_row(standard: StandardRecord) -> list[str]:
  """Prepare a single standard as a plain TSV row (no markup)."""
  updated_date = standard.updated.strftime("%Y-%m-%d") if standard.updated else "N/A"
  return [standard.id, standard.status, standard.title, updated_date]


def _calculate_column_widths(terminal_width: int) -> dict[int, int]:
  """Calculate optimal column widths for standard table.

  Args:
    terminal_width: Available terminal width

  Returns:
    Dictionary mapping column index to max width
  """
  # Custom column widths: ID (10), Tags (20), Status (12), Updated (10), rest for Title
  # Reserve space for borders/padding (~10 chars total)
  reserved = 10
  id_width = 10
  tags_width = 20
  status_width = 12
  updated_width = 10
  title_width = max(
    terminal_width - id_width - tags_width - status_width - updated_width - reserved,
    20,  # minimum title width
  )

  return {
    0: id_width,
    1: title_width,
    2: tags_width,
    3: status_width,
    4: updated_width,
  }


def _prepare_standard_row(standard: StandardRecord) -> list[str]:
  """Prepare a single standard row with styling.

  Args:
    standard: StandardRecord to format

  Returns:
    List of formatted cell values [id, title, tags, status, updated]
  """
  # Remove "STD-XXX: " prefix from title for display
  title = re.sub(r"^STD-\d+:\s*", "", standard.title)

  # Format tags as comma-separated list with styling
  tags = ", ".join(standard.tags) if standard.tags else ""
  tags_styled = f"[#d79921]{tags}[/#d79921]" if tags else ""

  # Use em dash for missing dates in table format
  updated_date = standard.updated.strftime("%Y-%m-%d") if standard.updated else "—"

  # Apply styling with rich markup
  standard_id = f"[standard.id]{standard.id}[/standard.id]"
  status_style = get_standard_status_style(standard.status)
  status_styled = f"[{status_style}]{standard.status}[/{status_style}]"

  return [standard_id, title, tags_styled, status_styled, updated_date]


def format_standard_list_table(
  standards: Sequence[StandardRecord],
  format_type: str = "table",
  truncate: bool = False,
  *,
  show_external: bool = False,
) -> str:
  """Format standards as table, JSON, or TSV.

  Args:
    standards: List of StandardRecord objects to format
    format_type: Output format (table|json|tsv)
    truncate: If True, truncate long fields (default: False, show full content)
    show_external: If True, show ext_id column after ID

  Returns:
    Formatted string in requested format
  """
  col_defs = list(STANDARD_COLUMNS)
  if show_external:
    col_defs.insert(1, EXT_ID_COLUMN)

  def _row(standard: StandardRecord) -> list[str]:
    row = _prepare_standard_row(standard)
    if show_external:
      row.insert(1, standard.ext_id)
    return row

  def _tsv_row(standard: StandardRecord) -> list[str]:
    row = _prepare_standard_tsv_row(standard)
    if show_external:
      row.insert(1, standard.ext_id)
    return row

  return format_list_table(
    standards,
    columns=column_labels(col_defs),
    title="Standards",
    prepare_row=_row,
    prepare_tsv_row=_tsv_row,
    to_json=format_standard_list_json,
    format_type=format_type,
    truncate=truncate,
    column_widths=_calculate_column_widths if not show_external else None,
  )


def format_standard_list_json(standards: Sequence[StandardRecord]) -> str:
  """Format standards as JSON array.

  Args:
    standards: List of StandardRecord objects

  Returns:
    JSON string representation
  """
  standard_dicts = []
  for standard in standards:
    d: dict[str, object] = {
      "id": standard.id,
      "title": standard.title,
      "status": standard.status,
      "updated": standard.updated.strftime("%Y-%m-%d") if standard.updated else None,
      "summary": standard.summary,
      "path": standard.path,
    }
    if standard.ext_id:
      d["ext_id"] = standard.ext_id
    if standard.ext_url:
      d["ext_url"] = standard.ext_url
    standard_dicts.append(d)
  return format_as_json(standard_dicts)
