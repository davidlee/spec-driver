"""Requirement display formatters.

Pure formatting functions with no business logic.
Formatters take RequirementRecord objects and return formatted strings for display.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from supekku.scripts.lib.formatters.cell_helpers import format_tags_cell
from supekku.scripts.lib.formatters.column_defs import (
  EXT_ID_COLUMN,
  REQUIREMENT_COLUMNS,
  column_labels,
)
from supekku.scripts.lib.formatters.table_utils import (
  format_as_json,
  format_list_table,
)
from supekku.scripts.lib.formatters.theme import get_requirement_status_style

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.scripts.lib.requirements.registry import RequirementRecord


def _prepare_requirement_row(req: RequirementRecord) -> list[str]:
  """Prepare a single requirement row with styling."""
  spec = req.primary_spec or (req.specs[0] if req.specs else "—")
  spec_styled = f"[spec.id]{spec}[/spec.id]"
  label_styled = f"[requirement.id]{req.label}[/requirement.id]"
  category = req.category or "—"
  category_styled = f"[requirement.category]{category}[/requirement.category]"
  status_style = get_requirement_status_style(req.status)
  status_styled = f"[{status_style}]{req.status}[/{status_style}]"
  source = req.source_kind or "—"
  return [
    spec_styled,
    label_styled,
    source,
    category_styled,
    req.title,
    format_tags_cell(req.tags),
    status_styled,
  ]


def _prepare_requirement_tsv_row(req: RequirementRecord) -> list[str]:
  """Prepare a single requirement as a plain TSV row."""
  spec = req.primary_spec or (req.specs[0] if req.specs else "")
  category = req.category or "-"
  source = req.source_kind or "-"
  return [spec, req.label, source, category, req.title, req.status]


def _requirement_column_widths(
  show_external: bool = False,
) -> Callable[[int], dict[int, int]]:
  """Return a column-width calculator for the requirement table layout."""

  def _calc(terminal_width: int) -> dict[int, int]:
    reserved = 10
    spec_width = 10
    label_width = 8
    source_width = 12
    ext_id_width = 14 if show_external else 0
    category_width = 12
    tags_width = 20
    status_width = 12
    title_width = max(
      terminal_width
      - spec_width
      - label_width
      - source_width
      - ext_id_width
      - category_width
      - tags_width
      - status_width
      - reserved,
      20,
    )
    col_idx = 0
    widths: dict[int, int] = {}
    for w in [spec_width, label_width, source_width]:
      widths[col_idx] = w
      col_idx += 1
    if show_external:
      widths[col_idx] = ext_id_width
      col_idx += 1
    for w in [category_width, title_width, tags_width, status_width]:
      widths[col_idx] = w
      col_idx += 1
    return widths

  return _calc


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
  col_defs = list(REQUIREMENT_COLUMNS)
  if show_external:
    col_defs.insert(3, EXT_ID_COLUMN)

  def _row(req: RequirementRecord) -> list[str]:
    row = _prepare_requirement_row(req)
    if show_external:
      row.insert(3, req.ext_id)
    return row

  def _tsv_row(req: RequirementRecord) -> list[str]:
    row = _prepare_requirement_tsv_row(req)
    if show_external:
      row.insert(3, req.ext_id)
    return row

  return format_list_table(
    requirements,
    columns=column_labels(col_defs),
    title="Requirements",
    prepare_row=_row,
    prepare_tsv_row=_tsv_row,
    to_json=format_requirement_list_json,
    format_type=format_type,
    truncate=truncate,
    column_widths=_requirement_column_widths(show_external),
  )


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
    if req.source_kind:
      item["source_kind"] = req.source_kind
    if req.source_type:
      item["source_type"] = req.source_type

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

  # Source provenance
  if requirement.source_kind:
    lines.append(f"Source: {requirement.source_kind}")
  if requirement.source_type:
    lines.append(f"Source Type: {requirement.source_type}")

  # Path
  if requirement.path:
    lines.append(f"Path: {requirement.path}")

  return "\n".join(lines)
