"""Backlog item display formatters.

Pure formatting functions with no business logic.
Formatters take BacklogItem objects and return formatted strings for display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

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
) -> str:
  """Format backlog items as table, JSON, or TSV.

  Args:
    items: List of BacklogItem objects to format
    format_type: Output format (table|json|tsv)
    truncate: If True, truncate long fields (default: False, show full content)

  Returns:
    Formatted string in requested format
  """
  if format_type == "json":
    return format_backlog_list_json(items)

  if format_type == "tsv":
    rows = []
    for item in items:
      severity = getattr(item, "severity", "") or ""
      rows.append([item.id, item.kind, item.status, item.title, severity])
    return format_as_tsv(rows)

  # table format - columns: ID, Kind, Title, Tags, Status, Severity
  table = create_table(
    columns=["ID", "Kind", "Title", "Tags", "Status", "Severity"],
    title="Backlog Items",
  )

  terminal_width = get_terminal_width()

  # Custom column widths: ID (12), Kind (12), Tags (20), Status (12),
  # Severity (10), rest for Title
  # Reserve space for borders/padding (~10 chars total)
  reserved = 10
  id_width = 12
  kind_width = 12
  tags_width = 20
  status_width = 12
  severity_width = 10
  title_width = max(
    terminal_width
    - id_width
    - kind_width
    - tags_width
    - status_width
    - severity_width
    - reserved,
    20,  # minimum title width
  )

  max_widths = {
    0: id_width,
    1: kind_width,
    2: title_width,
    3: tags_width,
    4: status_width,
    5: severity_width,
  }

  for item in items:
    # Apply styling with rich markup
    item_id = f"[backlog.id]{item.id}[/backlog.id]"

    # Format tags as comma-separated list with styling
    tags = ", ".join(item.tags) if item.tags else ""
    tags_styled = f"[#d79921]{tags}[/#d79921]" if tags else ""

    status_style = get_backlog_status_style(item.kind, item.status)
    status_styled = f"[{status_style}]{item.status}[/{status_style}]"

    # Get severity/priority if available (issues and risks have it)
    severity = getattr(item, "severity", "—")

    add_row_with_truncation(
      table,
      [item_id, item.kind, item.title, tags_styled, status_styled, severity],
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

  # Timestamps (only if not empty)
  if hasattr(item, "created") and item.created:
    lines.append(f"Created: {item.created}")
  if hasattr(item, "updated") and item.updated:
    lines.append(f"Updated: {item.updated}")

  return "\n".join(lines)
