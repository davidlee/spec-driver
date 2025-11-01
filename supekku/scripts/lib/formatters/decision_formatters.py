"""Decision/ADR display formatters.

Pure formatting functions with no business logic.
Formatters take DecisionRecord objects and return formatted strings for display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.table_utils import (
  add_row_with_truncation,
  calculate_column_widths,
  create_table,
  format_as_json,
  format_as_tsv,
  get_terminal_width,
  render_table,
)

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.models.decision import Decision


def format_decision_details(decision: Decision) -> str:
  """Format decision details as multi-line string for display.

  Args:
    decision: Decision object to format

  Returns:
    Formatted string with all decision details
  """
  lines = []

  # Basic fields
  lines.append(f"ID: {decision.id}")
  lines.append(f"Title: {decision.title}")
  lines.append(f"Status: {decision.status}")

  # Timestamps
  if decision.created:
    lines.append(f"Created: {decision.created}")
  if decision.decided:
    lines.append(f"Decided: {decision.decided}")
  if decision.updated:
    lines.append(f"Updated: {decision.updated}")
  if decision.reviewed:
    lines.append(f"Reviewed: {decision.reviewed}")

  # People
  if decision.authors:
    lines.append(f"Authors: {', '.join(str(a) for a in decision.authors)}")
  if decision.owners:
    lines.append(f"Owners: {', '.join(str(o) for o in decision.owners)}")

  # Relationships
  if decision.supersedes:
    lines.append(f"Supersedes: {', '.join(decision.supersedes)}")
  if decision.superseded_by:
    lines.append(f"Superseded by: {', '.join(decision.superseded_by)}")

  # References to other artifacts
  if decision.specs:
    lines.append(f"Related specs: {', '.join(decision.specs)}")
  if decision.requirements:
    lines.append(f"Requirements: {', '.join(decision.requirements)}")
  if decision.deltas:
    lines.append(f"Deltas: {', '.join(decision.deltas)}")
  if decision.revisions:
    lines.append(f"Revisions: {', '.join(decision.revisions)}")
  if decision.audits:
    lines.append(f"Audits: {', '.join(decision.audits)}")

  # Related items
  if decision.related_decisions:
    lines.append(f"Related decisions: {', '.join(decision.related_decisions)}")
  if decision.related_policies:
    lines.append(f"Related policies: {', '.join(decision.related_policies)}")

  # Tags
  if decision.tags:
    lines.append(f"Tags: {', '.join(decision.tags)}")

  # Backlinks
  if decision.backlinks:
    lines.append("\nBacklinks:")
    for link_type, refs in decision.backlinks.items():
      lines.append(f"  {link_type}: {', '.join(refs)}")

  return "\n".join(lines)


def format_decision_list_table(
  decisions: Sequence[Decision],
  format_type: str = "table",
  no_truncate: bool = False,
) -> str:
  """Format decisions as table, JSON, or TSV.

  Args:
    decisions: List of Decision objects to format
    format_type: Output format (table|json|tsv)
    no_truncate: If True, don't truncate long fields

  Returns:
    Formatted string in requested format
  """
  if format_type == "json":
    return format_decision_list_json(decisions)

  if format_type == "tsv":
    rows = []
    for decision in decisions:
      updated_date = (
        decision.updated.strftime("%Y-%m-%d") if decision.updated else "N/A"
      )
      rows.append([decision.id, decision.status, decision.title, updated_date])
    return format_as_tsv(rows)

  # table format
  table = create_table(
    columns=["ID", "Status", "Title", "Updated"],
    title="Architecture Decision Records",
  )

  terminal_width = get_terminal_width()
  max_widths = calculate_column_widths(terminal_width, num_columns=4)

  for decision in decisions:
    updated_date = decision.updated.strftime("%Y-%m-%d") if decision.updated else "N/A"
    add_row_with_truncation(
      table,
      [decision.id, decision.status, decision.title, updated_date],
      max_widths=max_widths if not no_truncate else None,
    )

  return render_table(table)


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
