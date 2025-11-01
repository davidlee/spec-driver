"""Change artifact (delta/revision/audit) display formatters.

Pure formatting functions with no business logic.
Formatters take ChangeArtifact objects and return formatted strings for display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from supekku.scripts.lib.formatters.table_utils import (
  add_row_with_truncation,
  calculate_column_widths,
  create_table,
  format_as_json,
  format_as_tsv,
  get_terminal_width,
  render_table,
)
from supekku.scripts.lib.formatters.theme import get_change_status_style

if TYPE_CHECKING:
  from collections.abc import Sequence

  from supekku.scripts.lib.changes.artifacts import ChangeArtifact


def format_change_list_item(artifact: ChangeArtifact) -> str:
  """Format change artifact as basic list item: id, kind, status, name.

  Args:
    artifact: Change artifact to format

  Returns:
    Tab-separated string: "{id}\\t{kind}\\t{status}\\t{name}"
  """
  return f"{artifact.id}\t{artifact.kind}\t{artifact.status}\t{artifact.name}"


def format_phase_summary(phase: dict[str, Any], max_objective_len: int = 60) -> str:
  """Format a single phase with truncated objective.

  Args:
    phase: Phase dictionary with 'phase'/'id' and 'objective' fields
    max_objective_len: Maximum length for objective before truncation

  Returns:
    Formatted string: "{phase_id}" or "{phase_id}: {objective}"
  """
  phase_id = phase.get("phase") or phase.get("id") or "?"
  objective = str(phase.get("objective", "")).strip()

  if not objective:
    return phase_id

  # Take first line only and truncate if needed
  objective = objective.splitlines()[0]
  if len(objective) > max_objective_len:
    objective = objective[: max_objective_len - 3] + "..."

  return f"{phase_id}: {objective}"


def format_change_with_context(artifact: ChangeArtifact) -> str:
  """Format change artifact with related specs, requirements, and phases.

  Provides detailed context including:
  - Basic info (id, kind, status, name)
  - Related specs
  - Requirements
  - Plan phases with objectives

  Args:
    artifact: Change artifact to format

  Returns:
    Multi-line formatted string with indented context
  """
  lines = [format_change_list_item(artifact)]

  # Related specs
  specs = artifact.applies_to.get("specs", []) if artifact.applies_to else []
  if specs:
    lines.append(f"  specs: {', '.join(str(s) for s in specs)}")

  # Requirements
  reqs = artifact.applies_to.get("requirements", []) if artifact.applies_to else []
  if reqs:
    lines.append(f"  requirements: {', '.join(str(r) for r in reqs)}")

  # Phases
  if artifact.plan and artifact.plan.get("phases"):
    phases = artifact.plan["phases"]
    phase_summaries = [format_phase_summary(phase) for phase in phases]

    if phase_summaries:
      lines.append("  phases:")
      for summary in phase_summaries:
        lines.append(f"    {summary}")

  return "\n".join(lines)


def format_change_list_table(
  changes: Sequence[ChangeArtifact],
  format_type: str = "table",
  no_truncate: bool = False,
) -> str:
  """Format change artifacts as table, JSON, or TSV.

  Args:
    changes: List of ChangeArtifact objects to format
    format_type: Output format (table|json|tsv)
    no_truncate: If True, don't truncate long fields

  Returns:
    Formatted string in requested format
  """
  if format_type == "json":
    return format_change_list_json(changes)

  if format_type == "tsv":
    rows = []
    for change in changes:
      rows.append([change.id, change.status, change.name])
    return format_as_tsv(rows)

  # table format
  table = create_table(
    columns=["ID", "Status", "Name"],
    title="Change Artifacts",
  )

  terminal_width = get_terminal_width()
  max_widths = calculate_column_widths(terminal_width, num_columns=3)

  for change in changes:
    # Apply styling
    styled_id = f"[change.id]{change.id}[/change.id]"
    status_style = get_change_status_style(change.status)
    styled_status = f"[{status_style}]{change.status}[/{status_style}]"

    add_row_with_truncation(
      table,
      [styled_id, styled_status, change.name],
      max_widths=max_widths if not no_truncate else None,
    )

  return render_table(table)


def format_change_list_json(changes: Sequence[ChangeArtifact]) -> str:
  """Format change artifacts as JSON array.

  Args:
    changes: List of ChangeArtifact objects

  Returns:
    JSON string with structure: {"items": [...]}
  """
  items = []
  for change in changes:
    item = {
      "id": change.id,
      "kind": change.kind,
      "status": change.status,
      "name": change.name,
      "slug": change.slug,
    }
    # Add optional fields
    if change.applies_to:
      item["applies_to"] = change.applies_to
    if change.relations:
      item["relations"] = change.relations

    items.append(item)

  return format_as_json(items)
