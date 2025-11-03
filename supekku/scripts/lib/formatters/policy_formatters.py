"""Policy display formatters.

Pure formatting functions with no business logic.
Formatters take PolicyRecord objects and return formatted strings for display.
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
from supekku.scripts.lib.formatters.theme import get_policy_status_style

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.scripts.lib.policies.registry import PolicyRecord


def _format_basic_fields(policy: PolicyRecord) -> list[str]:
  """Format basic policy fields (id, title, status)."""
  return [
    f"ID: {policy.id}",
    f"Title: {policy.title}",
    f"Status: {policy.status}",
  ]


def _format_timestamps(policy: PolicyRecord) -> list[str]:
  """Format timestamp fields if present."""
  lines = []
  timestamp_fields = [
    ("Created", policy.created),
    ("Updated", policy.updated),
    ("Reviewed", policy.reviewed),
  ]
  for label, value in timestamp_fields:
    if value:
      lines.append(f"{label}: {value}")
  return lines


def _format_people(policy: PolicyRecord) -> list[str]:
  """Format people-related fields (owners)."""
  lines = []
  if policy.owners:
    lines.append(f"Owners: {', '.join(str(o) for o in policy.owners)}")
  return lines


def _format_relationships(policy: PolicyRecord) -> list[str]:
  """Format policy relationship fields (supersedes, superseded_by)."""
  lines = []
  if policy.supersedes:
    lines.append(f"Supersedes: {', '.join(policy.supersedes)}")
  if policy.superseded_by:
    lines.append(f"Superseded by: {', '.join(policy.superseded_by)}")
  return lines


def _format_artifact_references(policy: PolicyRecord) -> list[str]:
  """Format references to other artifacts (specs, requirements, etc)."""
  lines = []
  artifact_refs = [
    ("Related specs", policy.specs),
    ("Requirements", policy.requirements),
    ("Deltas", policy.deltas),
    ("Standards", policy.standards),
  ]
  for label, refs in artifact_refs:
    if refs:
      lines.append(f"{label}: {', '.join(refs)}")
  return lines


def _format_related_items(policy: PolicyRecord) -> list[str]:
  """Format related policies and standards."""
  lines = []
  if policy.related_policies:
    lines.append(f"Related policies: {', '.join(policy.related_policies)}")
  if policy.related_standards:
    lines.append(f"Related standards: {', '.join(policy.related_standards)}")
  return lines


def _format_tags_and_backlinks(policy: PolicyRecord) -> list[str]:
  """Format tags and backlinks."""
  lines = []
  if policy.tags:
    lines.append(f"Tags: {', '.join(policy.tags)}")

  if policy.backlinks:
    lines.append("\nBacklinks:")
    for link_type, refs in policy.backlinks.items():
      lines.append(f"  {link_type}: {', '.join(refs)}")
  return lines


def format_policy_details(policy: PolicyRecord) -> str:
  """Format policy details as multi-line string for display.

  Args:
    policy: PolicyRecord object to format

  Returns:
    Formatted string with all policy details
  """
  sections = [
    _format_basic_fields(policy),
    _format_timestamps(policy),
    _format_people(policy),
    _format_relationships(policy),
    _format_artifact_references(policy),
    _format_related_items(policy),
    _format_tags_and_backlinks(policy),
  ]

  # Flatten all non-empty sections
  lines = [line for section in sections for line in section]
  return "\n".join(lines)


def _format_policy_as_tsv_rows(policies: Sequence[PolicyRecord]) -> list[list[str]]:
  """Convert policies to TSV row format."""
  rows = []
  for policy in policies:
    updated_date = policy.updated.strftime("%Y-%m-%d") if policy.updated else "N/A"
    rows.append([policy.id, policy.status, policy.title, updated_date])
  return rows


def _calculate_column_widths(terminal_width: int) -> dict[int, int]:
  """Calculate optimal column widths for policy table.

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


def _prepare_policy_row(policy: PolicyRecord) -> list[str]:
  """Prepare a single policy row with styling.

  Args:
    policy: PolicyRecord to format

  Returns:
    List of formatted cell values [id, title, status, updated]
  """
  # Remove "POL-XXX: " prefix from title for display
  title = re.sub(r"^POL-\d+:\s*", "", policy.title)

  # Use em dash for missing dates in table format
  updated_date = policy.updated.strftime("%Y-%m-%d") if policy.updated else "—"

  # Apply styling with rich markup
  policy_id = f"[policy.id]{policy.id}[/policy.id]"
  status_style = get_policy_status_style(policy.status)
  status_styled = f"[{status_style}]{policy.status}[/{status_style}]"

  return [policy_id, title, status_styled, updated_date]


def _format_as_table(
  policies: Sequence[PolicyRecord],
  truncate: bool,
) -> str:
  """Format policies as a rich table.

  Args:
    policies: Policies to format
    truncate: Whether to truncate columns to fit terminal

  Returns:
    Rendered table string
  """
  table = create_table(
    columns=["ID", "Title", "Status", "Updated"],
    title="Policies",
  )

  max_widths = _calculate_column_widths(get_terminal_width()) if truncate else None

  for policy in policies:
    row = _prepare_policy_row(policy)
    add_row_with_truncation(table, row, max_widths=max_widths)

  return render_table(table)


def format_policy_list_table(
  policies: Sequence[PolicyRecord],
  format_type: str = "table",
  truncate: bool = False,
) -> str:
  """Format policies as table, JSON, or TSV.

  Args:
    policies: List of PolicyRecord objects to format
    format_type: Output format (table|json|tsv)
    truncate: If True, truncate long fields (default: False, show full content)

  Returns:
    Formatted string in requested format
  """
  if format_type == "json":
    return format_policy_list_json(policies)

  if format_type == "tsv":
    rows = _format_policy_as_tsv_rows(policies)
    return format_as_tsv(rows)

  return _format_as_table(policies, truncate)


def format_policy_list_json(policies: Sequence[PolicyRecord]) -> str:
  """Format policies as JSON array.

  Args:
    policies: List of PolicyRecord objects

  Returns:
    JSON string representation
  """
  policy_dicts = [
    {
      "id": policy.id,
      "title": policy.title,
      "status": policy.status,
      "updated": policy.updated.strftime("%Y-%m-%d") if policy.updated else None,
      "summary": policy.summary,
      "path": policy.path,
    }
    for policy in policies
  ]
  return format_as_json(policy_dicts)
