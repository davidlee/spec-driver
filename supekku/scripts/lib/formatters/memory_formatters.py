"""Memory display formatters.

Pure formatting functions with no business logic.
Formatters take MemoryRecord objects and return formatted strings for display.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.table_utils import (
  add_row_with_truncation,
  create_table,
  format_as_json,
  format_as_tsv,
  get_terminal_width,
  render_table,
)
from supekku.scripts.lib.formatters.theme import get_memory_status_style

if TYPE_CHECKING:
  from supekku.scripts.lib.memory.models import MemoryRecord


# --- Detail view ---


def _format_detail_lines(record: MemoryRecord) -> list[str]:
  """Build lines for a memory detail view, omitting empty optional fields."""
  lines = [
    f"ID: {record.id}",
    f"Name: {record.name}",
    f"Status: {record.status}",
    f"Type: {record.memory_type}",
  ]

  if record.confidence:
    lines.append(f"Confidence: {record.confidence}")

  if record.created:
    lines.append(f"Created: {record.created.isoformat()}")
  if record.updated:
    lines.append(f"Updated: {record.updated.isoformat()}")

  if record.summary:
    lines.append(f"Summary: {record.summary}")
  if record.tags:
    lines.append(f"Tags: {', '.join(record.tags)}")

  lines.append(f"Path: {record.path}")
  return lines


def format_memory_details(record: MemoryRecord) -> str:
  """Format a memory record as multi-line detail string.

  Args:
    record: MemoryRecord to format.

  Returns:
    Human-readable detail string.
  """
  return "\n".join(_format_detail_lines(record))


# --- List views ---


def _prepare_memory_row(record: MemoryRecord) -> list[str]:
  """Prepare a single row for the memory table."""
  mem_id = f"[memory.id]{record.id}[/memory.id]"
  status_style = get_memory_status_style(record.status)
  status = f"[{status_style}]{record.status}[/{status_style}]"
  confidence = record.confidence or ""
  tags = ", ".join(record.tags) if record.tags else ""
  tags_styled = f"[#d79921]{tags}[/#d79921]" if tags else ""
  updated = record.updated.strftime("%Y-%m-%d") if record.updated else "—"

  return [
    mem_id, status, record.memory_type, record.name,
    confidence, tags_styled, updated,
  ]


def _calculate_column_widths(terminal_width: int) -> dict[int, int]:
  """Calculate column widths for memory table based on terminal width."""
  # ID + Status + Type + Name(flex) + Confidence + Tags(flex) + Updated
  fixed = 8 + 10 + 10 + 10 + 10
  flex = max(terminal_width - fixed, 20)
  name_width = int(flex * 0.6)
  tags_width = flex - name_width
  return {3: name_width, 5: tags_width}


def _format_as_table(records: Sequence[MemoryRecord], truncate: bool) -> str:
  """Format memory records as a rich table."""
  table = create_table(
    columns=["ID", "Status", "Type", "Name", "Confidence", "Tags", "Updated"],
    title="Memory Records",
  )

  max_widths = _calculate_column_widths(get_terminal_width()) if truncate else None

  for record in records:
    row = _prepare_memory_row(record)
    add_row_with_truncation(table, row, max_widths=max_widths)

  return render_table(table)


def _format_memory_as_tsv_rows(
  records: Sequence[MemoryRecord],
) -> list[list[str]]:
  """Convert memory records to TSV row format."""
  rows = []
  for record in records:
    updated = record.updated.strftime("%Y-%m-%d") if record.updated else "N/A"
    rows.append([
      record.id, record.status, record.memory_type,
      record.name, record.confidence or "", updated,
    ])
  return rows


def format_memory_list_table(
  records: Sequence[MemoryRecord],
  format_type: str = "table",
  truncate: bool = False,
) -> str:
  """Format memory records as table, JSON, or TSV.

  Args:
    records: List of MemoryRecord objects.
    format_type: Output format (table|json|tsv).
    truncate: If True, truncate long fields.

  Returns:
    Formatted string in requested format.
  """
  if format_type == "json":
    return format_memory_list_json(records)

  if format_type == "tsv":
    rows = _format_memory_as_tsv_rows(records)
    return format_as_tsv(rows)

  return _format_as_table(records, truncate)


def format_memory_list_json(records: Sequence[MemoryRecord]) -> str:
  """Format memory records as JSON array.

  Args:
    records: List of MemoryRecord objects.

  Returns:
    JSON string with structure: {"items": [...]}.
  """
  items = []
  for record in records:
    item: dict = {
      "id": record.id,
      "name": record.name,
      "status": record.status,
      "memory_type": record.memory_type,
      "path": record.path,
      "created": record.created,
      "updated": record.updated,
    }
    if record.tags:
      item["tags"] = record.tags
    if record.confidence:
      item["confidence"] = record.confidence
    if record.summary:
      item["summary"] = record.summary

    items.append(item)

  return format_as_json(items)
