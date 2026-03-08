"""Backlog item display formatters.

Pure formatting functions with no business logic.
Formatters take BacklogItem objects and return formatted strings for display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.column_defs import (
  BACKLOG_COLUMNS,
  EXT_ID_COLUMN,
  column_labels,
)
from supekku.scripts.lib.formatters.table_utils import (
  add_row_with_truncation,
  create_table,
  format_as_json,
  format_as_tsv,
  get_terminal_width,
  render_table,
)
from supekku.scripts.lib.formatters.theme import get_backlog_status_style

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.scripts.lib.backlog.models import BacklogItem


def format_backlog_list_table(
  items: Sequence[BacklogItem],
  format_type: str = "table",
  truncate: bool = False,
  *,
  show_external: bool = False,
) -> str:
  """Format backlog items as table, JSON, or TSV.

  Args:
    items: List of BacklogItem objects to format
    format_type: Output format (table|json|tsv)
    truncate: If True, truncate long fields (default: False, show full content)
    show_external: If True, show ext_id column after ID

  Returns:
    Formatted string in requested format
  """
  if format_type == "json":
    return format_backlog_list_json(items)

  if format_type == "tsv":
    rows = []
    for item in items:
      severity = getattr(item, "severity", "") or ""
      row = [item.id]
      if show_external:
        row.append(item.ext_id)
      row.extend([item.kind, item.status, item.title, severity])
      rows.append(row)
    return format_as_tsv(rows)

  # table format
  columns = list(BACKLOG_COLUMNS)
  if show_external:
    columns.insert(1, EXT_ID_COLUMN)
  table = create_table(
    columns=column_labels(columns),
    title="Backlog Items",
  )

  terminal_width = get_terminal_width()

  # Custom column widths
  reserved = 10
  id_width = 12
  ext_id_width = 14 if show_external else 0
  kind_width = 12
  tags_width = 20
  status_width = 12
  severity_width = 10
  title_width = max(
    terminal_width
    - id_width
    - ext_id_width
    - kind_width
    - tags_width
    - status_width
    - severity_width
    - reserved,
    20,
  )

  col_idx = 0
  max_widths = {col_idx: id_width}
  col_idx += 1
  if show_external:
    max_widths[col_idx] = ext_id_width
    col_idx += 1
  max_widths[col_idx] = kind_width
  col_idx += 1
  max_widths[col_idx] = title_width
  col_idx += 1
  max_widths[col_idx] = tags_width
  col_idx += 1
  max_widths[col_idx] = status_width
  col_idx += 1
  max_widths[col_idx] = severity_width

  for item in items:
    item_id = f"[backlog.id]{item.id}[/backlog.id]"

    tags = ", ".join(item.tags) if item.tags else ""
    tags_styled = f"[#d79921]{tags}[/#d79921]" if tags else ""

    status_style = get_backlog_status_style(item.kind, item.status)
    status_styled = f"[{status_style}]{item.status}[/{status_style}]"

    severity = getattr(item, "severity", "—")

    row = [item_id]
    if show_external:
      row.append(item.ext_id)
    row.extend([item.kind, item.title, tags_styled, status_styled, severity])

    add_row_with_truncation(
      table,
      row,
      max_widths=max_widths if truncate else None,
    )

  return render_table(table)


def format_backlog_list_json(items: Sequence[BacklogItem]) -> str:
  """Format backlog items as JSON array.

  Args:
    items: List of BacklogItem objects

  Returns:
    JSON string with structure: {"items": [...]}
  """
  json_items = []
  for item in items:
    json_item = {
      "id": item.id,
      "kind": item.kind,
      "status": item.status,
      "title": item.title,
    }
    # Add optional fields based on kind (only if not empty)
    if hasattr(item, "severity") and item.severity:
      json_item["severity"] = item.severity
    if hasattr(item, "categories") and item.categories:
      json_item["categories"] = item.categories
    if hasattr(item, "impact") and item.impact:
      json_item["impact"] = item.impact
    if hasattr(item, "likelihood") and item.likelihood:
      json_item["likelihood"] = item.likelihood
    if hasattr(item, "created") and item.created:
      json_item["created"] = item.created
    if hasattr(item, "updated") and item.updated:
      json_item["updated"] = item.updated
    if item.ext_id:
      json_item["ext_id"] = item.ext_id
    if item.ext_url:
      json_item["ext_url"] = item.ext_url

    json_items.append(json_item)

  return format_as_json(json_items)


def format_backlog_details(item: BacklogItem) -> str:
  """Format single backlog item with full details.

  Args:
    item: BacklogItem to format

  Returns:
    Multi-line formatted string with all backlog item details
  """
  lines = []

  # Basic fields
  lines.append(f"ID: {item.id}")
  lines.append(f"Kind: {item.kind}")
  lines.append(f"Status: {item.status}")
  lines.append(f"Title: {item.title}")

  # Kind-specific fields (only if not empty)
  if hasattr(item, "severity") and item.severity:
    lines.append(f"Severity: {item.severity}")
  if hasattr(item, "categories") and item.categories:
    lines.append(f"Categories: {', '.join(item.categories)}")
  if hasattr(item, "impact") and item.impact:
    lines.append(f"Impact: {item.impact}")
  if hasattr(item, "likelihood") and item.likelihood:
    lines.append(f"Likelihood: {item.likelihood}")

  # External references (only if not empty)
  if item.ext_id:
    ext_line = f"External: {item.ext_id}"
    if item.ext_url:
      ext_line += f" ({item.ext_url})"
    lines.append(ext_line)

  # Timestamps (only if not empty)
  if hasattr(item, "created") and item.created:
    lines.append(f"Created: {item.created}")
  if hasattr(item, "updated") and item.updated:
    lines.append(f"Updated: {item.updated}")

  return "\n".join(lines)
