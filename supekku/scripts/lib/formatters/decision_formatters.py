"""Decision/ADR display formatters.

Pure formatting functions with no business logic.
Formatters take DecisionRecord objects and return formatted strings for display.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.cell_helpers import (
  format_date_cell,
  format_tags_cell,
)
from supekku.scripts.lib.formatters.column_defs import ADR_COLUMNS, column_labels
from supekku.scripts.lib.formatters.table_utils import (
  format_as_json,
  format_list_table,
  governance_5col_widths,
)
from supekku.scripts.lib.formatters.theme import get_adr_status_style

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.scripts.lib.decisions.registry import DecisionRecord as Decision


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
    ("Policies", decision.policies),
    ("Standards", decision.standards),
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


def _prepare_decision_tsv_row(decision: Decision) -> list[str]:
  """Prepare a single decision as a plain TSV row (no markup)."""
  updated = format_date_cell(decision.updated, missing="N/A")
  return [decision.id, decision.status, decision.title, updated]


def _prepare_decision_row(decision: Decision) -> list[str]:
  """Prepare a single decision row with styling.

  Returns:
    List of formatted cell values [id, title, tags, status, updated]
  """
  title = re.sub(r"^ADR-\d+:\s*", "", decision.title)
  decision_id = f"[adr.id]{decision.id}[/adr.id]"
  status_style = get_adr_status_style(decision.status)
  status_styled = f"[{status_style}]{decision.status}[/{status_style}]"

  return [
    decision_id,
    title,
    format_tags_cell(decision.tags),
    status_styled,
    format_date_cell(decision.updated),
  ]


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
  return format_list_table(
    decisions,
    columns=column_labels(ADR_COLUMNS),
    title="Architecture Decision Records",
    prepare_row=_prepare_decision_row,
    prepare_tsv_row=_prepare_decision_tsv_row,
    to_json=format_decision_list_json,
    format_type=format_type,
    truncate=truncate,
    column_widths=governance_5col_widths,
  )


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
      "path": decision.path,
      "created": decision.created,
      "updated": decision.updated,
      "decided": decision.decided,
      "tags": decision.tags if decision.tags else [],
    }
    # Add optional fields
    if decision.policies:
      item["policies"] = decision.policies
    if decision.standards:
      item["standards"] = decision.standards
    if decision.specs:
      item["specs"] = decision.specs
    if decision.requirements:
      item["requirements"] = decision.requirements
    if decision.deltas:
      item["deltas"] = decision.deltas

    items.append(item)

  return format_as_json(items)
