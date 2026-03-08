"""Requirement display formatters.

Pure formatting functions with no business logic.
Formatters take RequirementRecord objects and return formatted strings for display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.column_defs import (
  EXT_ID_COLUMN,
  REQUIREMENT_COLUMNS,
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
from supekku.scripts.lib.formatters.theme import get_requirement_status_style

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.scripts.lib.requirements.registry import RequirementRecord


def format_requirement_list_table(
  requirements: Sequence[RequirementRecord],
  format_type: str = "table",
  truncate: bool = False,
  *,
  show_external: bool = False,
) -> str:
  """Format requirements as table, JSON, or TSV.

  Args:
    requirements: List of RequirementRecord objects to format
    format_type: Output format (table|json|tsv)
    truncate: If True, truncate long fields (default: False, show full content)
    show_external: If True, show ext_id column after Label

  Returns:
    Formatted string in requested format
  """
  if format_type == "json":
    return format_requirement_list_json(requirements)

  if format_type == "tsv":
    rows = []
    for req in requirements:
      spec = req.primary_spec or (req.specs[0] if req.specs else "")
      category = req.category or "-"
      row = [spec, req.label]
      if show_external:
        row.append(req.ext_id)
      row.extend([category, req.title, req.status])
      rows.append(row)
    return format_as_tsv(rows)

  # table format
  col_defs = list(REQUIREMENT_COLUMNS)
  if show_external:
    col_defs.insert(2, EXT_ID_COLUMN)  # After Label
  table = create_table(
    columns=column_labels(col_defs),
    title="Requirements",
  )

  terminal_width = get_terminal_width()

  reserved = 10
  spec_width = 10
  label_width = 8
  ext_id_width = 14 if show_external else 0
  category_width = 12
  tags_width = 20
  status_width = 12
  title_width = max(
    terminal_width
    - spec_width
    - label_width
    - ext_id_width
    - category_width
    - tags_width
    - status_width
    - reserved,
    20,
  )

  col_idx = 0
  max_widths: dict[int, int] = {}
  for w in [spec_width, label_width]:
    max_widths[col_idx] = w
    col_idx += 1
  if show_external:
    max_widths[col_idx] = ext_id_width
    col_idx += 1
  for w in [category_width, title_width, tags_width, status_width]:
    max_widths[col_idx] = w
    col_idx += 1

  for req in requirements:
    spec = req.primary_spec or (req.specs[0] if req.specs else "—")
    spec_styled = f"[spec.id]{spec}[/spec.id]"
    label_styled = f"[requirement.id]{req.label}[/requirement.id]"
    category = req.category or "—"
    category_styled = f"[requirement.category]{category}[/requirement.category]"

    tags = ", ".join(req.tags) if req.tags else ""
    tags_styled = f"[#d79921]{tags}[/#d79921]" if tags else ""

    status_style = get_requirement_status_style(req.status)
    status_styled = f"[{status_style}]{req.status}[/{status_style}]"

    row = [spec_styled, label_styled]
    if show_external:
      row.append(req.ext_id)
    row.extend([category_styled, req.title, tags_styled, status_styled])

    add_row_with_truncation(
      table,
      row,
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
      "category": req.category,
      "primary_spec": req.primary_spec,
      "specs": req.specs,
    }
    # Add optional fields
    if req.introduced:
      item["introduced"] = req.introduced
    if req.implemented_by:
      item["implemented_by"] = req.implemented_by
    if req.coverage_evidence:
      item["coverage_evidence"] = req.coverage_evidence
    if req.coverage_entries:
      item["coverage_entries"] = req.coverage_entries
    if req.verified_by:
      item["verified_by"] = req.verified_by
    if req.path:
      item["path"] = req.path
    if req.ext_id:
      item["ext_id"] = req.ext_id
    if req.ext_url:
      item["ext_url"] = req.ext_url

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
  if requirement.category:
    lines.append(f"Category: {requirement.category}")
  lines.append(f"Status: {requirement.status}")

  # Specs
  if requirement.primary_spec:
    lines.append(f"Primary Spec: {requirement.primary_spec}")
  if requirement.specs:
    lines.append(f"Specs: {', '.join(requirement.specs)}")

  # External references
  if requirement.ext_id:
    ext_line = f"External: {requirement.ext_id}"
    if requirement.ext_url:
      ext_line += f" ({requirement.ext_url})"
    lines.append(ext_line)

  # Lifecycle
  if requirement.introduced:
    lines.append(f"Introduced: {requirement.introduced}")
  if requirement.implemented_by:
    lines.append(f"Implemented by: {', '.join(requirement.implemented_by)}")
  if requirement.coverage_evidence:
    lines.append(f"Coverage evidence: {', '.join(requirement.coverage_evidence)}")
  if requirement.verified_by:
    lines.append(f"Verified by: {', '.join(requirement.verified_by)}")

  # Path
  if requirement.path:
    lines.append(f"Path: {requirement.path}")

  return "\n".join(lines)
