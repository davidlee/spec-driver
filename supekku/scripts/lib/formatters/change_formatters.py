"""Change artifact (delta/revision/audit) display formatters.

Pure formatting functions with no business logic.
Formatters take ChangeArtifact objects and return formatted strings for display.
"""

from __future__ import annotations

import contextlib
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from supekku.scripts.lib.blocks.plan import extract_phase_tracking
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
  # Handle phase 0 explicitly since 0 is falsy
  if "phase" in phase:
    phase_id = str(phase["phase"])
  elif "id" in phase:
    phase_id = str(phase["id"])
  else:
    phase_id = "?"

  # Strip IP-XXX. prefix for cleaner display
  if "." in phase_id and phase_id.count(".") == 1:
    phase_id = phase_id.split(".", 1)[1]

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
    columns=["ID", "Name", "Tags", "Status"],
    title="Change Artifacts",
  )

  terminal_width = get_terminal_width()
  max_widths = calculate_column_widths(terminal_width, num_columns=4)

  for change in changes:
    # Apply styling
    styled_id = f"[change.id]{change.id}[/change.id]"

    # Format tags as comma-separated list with styling
    tags = ", ".join(change.tags) if change.tags else ""
    tags_styled = f"[#d79921]{tags}[/#d79921]" if tags else ""

    status_style = get_change_status_style(change.status)
    styled_status = f"[{status_style}]{change.status}[/{status_style}]"

    add_row_with_truncation(
      table,
      [styled_id, change.name, tags_styled, styled_status],
      max_widths=max_widths if not no_truncate else None,
    )

  return render_table(table)


def _format_change_basic_fields(artifact: ChangeArtifact) -> list[str]:
  """Format basic change artifact fields."""
  return [
    f"Delta: {artifact.id}",
    f"Name: {artifact.name}",
    f"Status: {artifact.status}",
    f"Kind: {artifact.kind}",
  ]


def _format_applies_to(artifact: ChangeArtifact) -> list[str]:
  """Format applies_to section if present."""
  if not artifact.applies_to:
    return []

  specs = artifact.applies_to.get("specs", [])
  requirements = artifact.applies_to.get("requirements", [])

  # Only show section if there's actual content
  if not specs and not requirements:
    return []

  lines = ["", "Applies To:"]

  if specs:
    specs_str = ", ".join(str(s) for s in specs)
    lines.append(f"  Specs: {specs_str}")

  if requirements:
    lines.append("  Requirements:")
    for req in requirements:
      lines.append(f"    - {req}")

  return lines


def _enrich_phase_data(
  phase: dict[str, Any],
  artifact: ChangeArtifact,
  root: Path | None = None,
) -> dict[str, Any]:
  """Enrich phase data with file path and task completion stats.

  Checks for phase.tracking@v1 block first (structured data), then falls back
  to regex-based checkbox parsing for backward compatibility.

  Args:
    phase: Phase dictionary
    artifact: Parent delta artifact
    root: Repository root for relative paths

  Returns:
    Enriched phase dictionary with tasks/criteria in checkbox format
  """
  enriched = phase.copy()

  # Try to find the phase file
  phase_id = phase.get("phase") or phase.get("id")
  if not phase_id:
    return enriched

  phases_dir = artifact.path.parent / "phases"
  if not phases_dir.exists():
    return enriched

  # Extract numeric part from phase ID (e.g., "IP-005.PHASE-01" -> "01")
  phase_num = None
  if isinstance(phase_id, str):
    parts = phase_id.split("-")
    if parts:
      phase_num = parts[-1]

  if not phase_num:
    return enriched

  phase_file = phases_dir / f"phase-{phase_num.zfill(2)}.md"
  if not phase_file.exists():
    return enriched

  # Add file path
  phase_path_str = phase_file.as_posix()
  if root:
    with contextlib.suppress(ValueError):
      phase_path_str = phase_file.relative_to(root).as_posix()
  enriched["path"] = phase_path_str

  # Extract task completion stats
  try:
    phase_content = phase_file.read_text(encoding="utf-8")

    # Try structured tracking block first
    tracking_block = extract_phase_tracking(phase_content, phase_file)
    if tracking_block:
      # Extract tasks with checkbox-style status
      tasks = tracking_block.data.get("tasks", [])
      if tasks:
        task_list = []
        status_counts = {
          "pending": 0,
          "in_progress": 0,
          "completed": 0,
          "blocked": 0,
          "total": len(tasks),
        }

        for task in tasks:
          status = task.get("status", "pending")
          description = task.get("description", "")

          # Map status to checkbox format:
          # [x]=completed, [/]=in_progress, [!]=blocked, [ ]=pending
          if status == "completed":
            checkbox = "[x]"
            status_counts["completed"] += 1
          elif status == "in_progress":
            checkbox = "[/]"
            status_counts["in_progress"] += 1
          elif status == "blocked":
            checkbox = "[!]"
            status_counts["blocked"] += 1
          else:  # pending
            checkbox = "[ ]"
            status_counts["pending"] += 1

          task_list.append(f"{checkbox} {description}")

        enriched["tasks"] = task_list
        enriched["task_status"] = status_counts

      # Extract entrance/exit criteria with completion status
      entrance = tracking_block.data.get("entrance_criteria", [])
      if entrance:
        enriched["entrance_criteria"] = [
          f"[{'x' if c.get('completed', False) else ' '}] {c.get('item', '')}"
          for c in entrance
        ]

      exit_crit = tracking_block.data.get("exit_criteria", [])
      if exit_crit:
        enriched["exit_criteria"] = [
          f"[{'x' if c.get('completed', False) else ' '}] {c.get('item', '')}"
          for c in exit_crit
        ]
    else:
      # Fallback to regex-based checkbox parsing (backward compat)
      completed = len(re.findall(r"^- \[x\]", phase_content, re.MULTILINE))
      total = len(re.findall(r"^- \[(x| )\]", phase_content, re.MULTILINE))
      if total > 0:
        enriched["tasks_completed"] = completed
        enriched["tasks_total"] = total
  except (OSError, UnicodeDecodeError):
    pass

  return enriched


def _format_plan_overview(
  artifact: ChangeArtifact,
  root: Path | None = None,
) -> list[str]:
  """Format plan overview section if present."""
  if not artifact.plan:
    return []

  plan_id = artifact.plan.get("id", "")
  phases = artifact.plan.get("phases", [])

  if not phases:
    return []

  # Format plan file path
  plan_path = artifact.path.parent / f"{plan_id}.md"
  plan_path_str = plan_path.as_posix()
  if root:
    with contextlib.suppress(ValueError):
      plan_path_str = plan_path.relative_to(root).as_posix()

  lines = ["", f"Plan: {plan_id} ({len(phases)} phases)", f"  File: {plan_path_str}"]

  # Sort phases by ID for consistent ordering
  sorted_phases = sorted(phases, key=lambda p: p.get("id", ""))

  # Enrich all phases
  enriched_phases = [
    _enrich_phase_data(phase, artifact, root) for phase in sorted_phases
  ]

  # Create Rich table for phases
  table = create_table(columns=["Phase", "Status", "Objective"], show_header=True)

  # Add each phase as table row
  for enriched_phase in enriched_phases:
    # Phase ID (stripped)
    phase_id = enriched_phase.get("phase") or enriched_phase.get("id", "?")
    phase_id = str(phase_id)  # Convert to string (might be int)
    if "." in phase_id and phase_id.count(".") == 1:
      phase_id = phase_id.split(".", 1)[1]

    # Status column
    status_parts = []

    # Phase status if available
    phase_status = enriched_phase.get("status")
    if phase_status:
      status_parts.append(phase_status)

    # Task breakdown if tracking block present
    task_status = enriched_phase.get("task_status")
    if task_status:
      total = task_status.get("total", 0)
      if total > 0:
        parts = []
        if task_status.get("completed", 0) > 0:
          parts.append(f"{task_status['completed']}✓")
        if task_status.get("in_progress", 0) > 0:
          parts.append(f"{task_status['in_progress']}→")
        if task_status.get("blocked", 0) > 0:
          parts.append(f"{task_status['blocked']}!")
        if task_status.get("pending", 0) > 0:
          parts.append(f"{task_status['pending']}○")

        if parts:
          status_parts.append(" ".join(parts))
    else:
      # Fallback to old format for backward compatibility
      tasks_completed = enriched_phase.get("tasks_completed")
      tasks_total = enriched_phase.get("tasks_total")
      if tasks_completed is not None and tasks_total is not None:
        pct = int((tasks_completed / tasks_total) * 100) if tasks_total > 0 else 0
        status_parts.append(f"{tasks_completed}/{tasks_total} ({pct}%)")

    status_str = ", ".join(status_parts) if status_parts else "-"

    # Objective (no truncation for now - rich will handle wrapping)
    objective = str(enriched_phase.get("objective", "")).strip()
    objective = objective.splitlines()[0] if objective else "-"

    table.add_row(phase_id, status_str, objective)

  # Render table to string and add to lines
  table_output = render_table(table)
  lines.append(table_output.rstrip())

  return lines


def _format_relations(artifact: ChangeArtifact) -> list[str]:
  """Format relations section if present."""
  if not artifact.relations:
    return []

  lines = ["", "Relations:"]
  for relation in artifact.relations:
    kind = relation.get("kind", "")
    target = relation.get("target", "")
    lines.append(f"  - {kind}: {target}")

  return lines


def _format_other_files(
  artifact: ChangeArtifact,
  root: Path | None = None,
) -> list[str]:
  """Format other files in delta bundle."""
  # Collect all other files (excluding delta, plan, and phase files)
  excluded_files = {artifact.path}
  if artifact.plan:
    plan_id = artifact.plan.get("id", "")
    plan_path = artifact.path.parent / f"{plan_id}.md"
    excluded_files.add(plan_path)

    # Add all phase files to exclusion set
    phases_dir = artifact.path.parent / "phases"
    if phases_dir.exists():
      for phase_file in phases_dir.glob("*.md"):
        excluded_files.add(phase_file)

  # Find all other files
  other_files = []
  delta_dir = artifact.path.parent
  for file_path in sorted(delta_dir.rglob("*")):
    if file_path.is_file() and file_path not in excluded_files:
      file_path_str = file_path.as_posix()
      if root:
        with contextlib.suppress(ValueError):
          file_path_str = file_path.relative_to(root).as_posix()
      other_files.append(file_path_str)

  if not other_files:
    return []

  lines = ["", "Other Files:"]
  for file_path in other_files:
    lines.append(f"  {file_path}")

  return lines


def _format_file_path_for_change(
  artifact: ChangeArtifact,
  root: Path | None = None,
) -> list[str]:
  """Format file path section for change artifact."""
  if root:
    try:
      rel_path = artifact.path.relative_to(root)
      return ["", f"File: {rel_path.as_posix()}"]
    except ValueError:
      pass
  return ["", f"File: {artifact.path.as_posix()}"]


def format_delta_details(
  artifact: ChangeArtifact,
  root: Path | None = None,
) -> str:
  """Format delta details as multi-line string for display.

  Args:
    artifact: ChangeArtifact to format
    root: Repository root for relative path calculation (optional)

  Returns:
    Formatted string with all delta details
  """
  sections = [
    _format_change_basic_fields(artifact),
    _format_applies_to(artifact),
    _format_plan_overview(artifact, root),
    _format_relations(artifact),
    _format_other_files(artifact, root),
    _format_file_path_for_change(artifact, root),
  ]

  # Flatten all non-empty sections
  lines = [line for section in sections for line in section]
  return "\n".join(lines)


def _format_revision_basic_fields(artifact: ChangeArtifact) -> list[str]:
  """Format basic revision artifact fields."""
  return [
    f"Revision: {artifact.id}",
    f"Name: {artifact.name}",
    f"Status: {artifact.status}",
    f"Kind: {artifact.kind}",
  ]


def _format_affects(artifact: ChangeArtifact) -> list[str]:
  """Format affects section for revisions (similar to applies_to for deltas)."""
  if not artifact.applies_to:
    return []

  specs = artifact.applies_to.get("specs", [])
  requirements = artifact.applies_to.get("requirements", [])

  # Only show section if there's actual content
  if not specs and not requirements:
    return []

  lines = ["", "Affects:"]

  if specs:
    specs_str = ", ".join(str(s) for s in specs)
    lines.append(f"  Specs: {specs_str}")

  if requirements:
    lines.append("  Requirements:")
    for req in requirements:
      lines.append(f"    - {req}")

  return lines


def format_revision_details(
  artifact: ChangeArtifact,
  root: Path | None = None,
) -> str:
  """Format revision details as multi-line string for display.

  Args:
    artifact: ChangeArtifact to format (must be kind='revision')
    root: Repository root for relative path calculation (optional)

  Returns:
    Formatted string with all revision details
  """
  sections = [
    _format_revision_basic_fields(artifact),
    _format_affects(artifact),
    _format_relations(artifact),
    _format_file_path_for_change(artifact, root),
  ]

  # Flatten all non-empty sections
  lines = [line for section in sections for line in section]
  return "\n".join(lines)


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
      "path": change.path.as_posix(),
    }
    # Add optional fields
    if change.applies_to:
      item["applies_to"] = change.applies_to
    if change.relations:
      item["relations"] = change.relations

    items.append(item)

  return format_as_json(items)


def format_delta_details_json(
  artifact: ChangeArtifact,
  root: Path | None = None,
) -> str:
  """Format delta details as JSON with all file paths included.

  Args:
    artifact: ChangeArtifact to format
    root: Repository root for relative path calculation (optional)

  Returns:
    JSON string with complete delta information including all paths
  """
  # Calculate relative path for delta file
  delta_path = artifact.path.as_posix()
  if root:
    with contextlib.suppress(ValueError):
      delta_path = artifact.path.relative_to(root).as_posix()

  # Build base delta object
  delta_obj: dict[str, Any] = {
    "id": artifact.id,
    "kind": artifact.kind,
    "status": artifact.status,
    "name": artifact.name,
    "slug": artifact.slug,
    "path": delta_path,
  }

  # Add optional basic fields
  if artifact.updated:
    delta_obj["updated"] = artifact.updated

  # Add applies_to with spec/requirement details
  if artifact.applies_to:
    delta_obj["applies_to"] = artifact.applies_to

  # Add relations
  if artifact.relations:
    delta_obj["relations"] = artifact.relations

  # Add plan with all phase file paths
  if artifact.plan:
    plan_id = artifact.plan.get("id", "")
    plan_path = artifact.path.parent / f"{plan_id}.md"
    plan_path_str = plan_path.as_posix()
    if root:
      with contextlib.suppress(ValueError):
        plan_path_str = plan_path.relative_to(root).as_posix()

    plan_obj: dict[str, Any] = {
      "id": plan_id,
      "path": plan_path_str,
      "overview": artifact.plan.get("overview", {}),
      "phases": [],
    }

    # Add phases with enriched data (paths and task stats)
    for phase in artifact.plan.get("phases", []):
      enriched_phase = _enrich_phase_data(phase, artifact, root)
      plan_obj["phases"].append(enriched_phase)

    delta_obj["plan"] = plan_obj

  # Collect all other files in the delta bundle directory
  # Exclude: delta file, plan file, and phase files (already listed above)
  excluded_files = {artifact.path}
  if artifact.plan:
    plan_id = artifact.plan.get("id", "")
    plan_path = artifact.path.parent / f"{plan_id}.md"
    excluded_files.add(plan_path)

    # Add all phase files to exclusion set
    phases_dir = artifact.path.parent / "phases"
    if phases_dir.exists():
      for phase_file in phases_dir.glob("*.md"):
        excluded_files.add(phase_file)

  # Find all other files
  other_files = []
  delta_dir = artifact.path.parent
  for file_path in sorted(delta_dir.rglob("*")):
    if file_path.is_file() and file_path not in excluded_files:
      file_path_str = file_path.as_posix()
      if root:
        with contextlib.suppress(ValueError):
          file_path_str = file_path.relative_to(root).as_posix()
      other_files.append(file_path_str)

  if other_files:
    delta_obj["files"] = other_files

  return json.dumps(delta_obj, indent=2, default=str)
