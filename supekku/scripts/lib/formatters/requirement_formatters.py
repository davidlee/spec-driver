"""Requirement display formatters.

Pure formatting functions with no business logic.
Formatters take RequirementRecord objects and return formatted strings for display.
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
from supekku.scripts.lib.formatters.theme import get_requirement_status_style

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.scripts.lib.requirements.registry import RequirementRecord


def format_requirement_list_table(
  requirements: Sequence[RequirementRecord],
  format_type: str = "table",
  truncate: bool = False,
) -> str:
  """Format requirements as table, JSON, or TSV.

  Args:
    requirements: List of RequirementRecord objects to format
    format_type: Output format (table|json|tsv)
    truncate: If True, truncate long fields (default: False, show full content)

  Returns:
    Formatted string in requested format
  """
  if format_type == "json":
    return format_requirement_list_json(requirements)

  if format_type == "tsv":
    rows = []
    for req in requirements:
      spec = req.primary_spec or (req.specs[0] if req.specs else "")
      rows.append([spec, req.label, req.title, req.status])
    return format_as_tsv(rows)

  # table format - columns: Spec, Label, Title, Status
  table = create_table(
    columns=["Spec", "Label", "Title", "Status"],
    title="Requirements",
  )

  terminal_width = get_terminal_width()

  # Custom column widths: Spec (10), Label (8), Status (12), rest for Title
  # Reserve space for borders/padding (~10 chars total)
  reserved = 10
  spec_width = 10
  label_width = 8
  status_width = 12
  title_width = max(
    terminal_width - spec_width - label_width - status_width - reserved,
    20,  # minimum title width
  )

  max_widths = {
    0: spec_width,
    1: label_width,
    2: title_width,
    3: status_width,
  }

  for req in requirements:
    # Apply styling with rich markup
    spec = req.primary_spec or (req.specs[0] if req.specs else "—")
    spec_styled = f"[spec.id]{spec}[/spec.id]"
    label_styled = f"[requirement.id]{req.label}[/requirement.id]"
    status_style = get_requirement_status_style(req.status)
    status_styled = f"[{status_style}]{req.status}[/{status_style}]"

    add_row_with_truncation(
      table,
      [spec_styled, label_styled, req.title, status_styled],
      max_widths=max_widths if truncate else None,
    )

  return render_table(table)


def format_requirement_list_json(requirements: Sequence[RequirementRecord]) -> str:
  """Format requirements as JSON array.

  Args:
    requirements: List of RequirementRecord objects

  Returns:
    JSON string with structure: {"items": [...]}
  """
  items = []
  for req in requirements:
    item = {
      "uid": req.uid,
      "label": req.label,
      "title": req.title,
      "status": req.status,
      "kind": req.kind,
      "primary_spec": req.primary_spec,
      "specs": req.specs,
    }
    # Add optional fields
    if req.introduced:
      item["introduced"] = req.introduced
    if req.implemented_by:
      item["implemented_by"] = req.implemented_by
    if req.verified_by:
      item["verified_by"] = req.verified_by
    if req.path:
      item["path"] = req.path

    items.append(item)

  return format_as_json(items)


def format_requirement_details(requirement: RequirementRecord) -> str:
  """Format single requirement with full details.

  Args:
    requirement: RequirementRecord to format

  Returns:
    Multi-line formatted string with all requirement details
  """
  lines = []

  # Basic fields
  lines.append(f"UID: {requirement.uid}")
  lines.append(f"Label: {requirement.label}")
  lines.append(f"Title: {requirement.title}")
  lines.append(f"Kind: {requirement.kind}")
  lines.append(f"Status: {requirement.status}")

  # Specs
  if requirement.primary_spec:
    lines.append(f"Primary Spec: {requirement.primary_spec}")
  if requirement.specs:
    lines.append(f"Specs: {', '.join(requirement.specs)}")

  # Lifecycle
  if requirement.introduced:
    lines.append(f"Introduced: {requirement.introduced}")
  if requirement.implemented_by:
    lines.append(f"Implemented by: {', '.join(requirement.implemented_by)}")
  if requirement.verified_by:
    lines.append(f"Verified by: {', '.join(requirement.verified_by)}")

  # Path
  if requirement.path:
    lines.append(f"Path: {requirement.path}")

  return "\n".join(lines)
