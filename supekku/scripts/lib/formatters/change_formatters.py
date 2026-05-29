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

import frontmatter
from pydantic import ValidationError

from supekku.scripts.lib.blocks.plan import (
  extract_phase_overview,
  extract_phase_tracking,
)
from supekku.scripts.lib.changes.phase_model import PhaseSheet
from supekku.scripts.lib.changes.revision_check import RevisionChangeSummary
from supekku.scripts.lib.core.frontmatter_metadata.delta import AUDIT_GATE_AUTO
from supekku.scripts.lib.formatters.cell_helpers import format_tags_cell
from supekku.scripts.lib.formatters.column_defs import (
  AUDIT_COLUMNS,
  CHANGE_COLUMNS,
  DELTA_COLUMNS,
  DELTA_TAGS_COLUMN,
  EXT_ID_COLUMN,
  PHASE_COLUMNS,
  PLAN_COLUMNS,
  REFS_COLUMN,
  REVISION_COLUMNS,
  column_labels,
)
from supekku.scripts.lib.formatters.relation_formatters import (
  format_refs_count,
  format_refs_tsv,
)
from supekku.scripts.lib.formatters.table_utils import (
  create_table,
  format_as_json,
  format_list_table,
  render_table,
)
from supekku.scripts.lib.formatters.theme import get_change_status_style
from supekku.scripts.lib.relations.query import collect_references

if TYPE_CHECKING:
  from collections.abc import Mapping, Sequence

  from supekku.scripts.lib.changes.artifacts import ChangeArtifact
  from supekku.scripts.lib.changes.audit_check import AuditFindingsSummary


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


def _prepare_change_row(change: ChangeArtifact) -> list[str]:
  """Prepare a single change artifact row with styling."""
  styled_id = f"[change.id]{change.id}[/change.id]"
  display_name = change.name
  if change.kind == "delta" and display_name.startswith("Delta - "):
    display_name = display_name[8:]
  status_style = get_change_status_style(change.status)
  styled_status = f"[{status_style}]{change.status}[/{status_style}]"
  return [styled_id, display_name, format_tags_cell(change.tags), styled_status]


def _prepare_change_tsv_row(change: ChangeArtifact) -> list[str]:
  """Prepare a single change artifact as a plain TSV row."""
  return [change.id, change.status, change.name]


def format_change_list_table(
  changes: Sequence[ChangeArtifact],
  format_type: str = "table",
  truncate: bool = False,
  *,
  show_external: bool = False,
  show_refs: bool = False,
) -> str:
  """Format change artifacts as table, JSON, or TSV.

  Args:
    changes: List of ChangeArtifact objects to format
    format_type: Output format (table|json|tsv)
    truncate: If True, truncate long fields to fit terminal width
    show_external: If True, show ext_id column after ID
    show_refs: If True, show refs column (count in table, pairs in TSV)

  Returns:
    Formatted string in requested format
  """
  col_defs = list(CHANGE_COLUMNS)
  if show_external:
    col_defs.insert(1, EXT_ID_COLUMN)
  if show_refs:
    col_defs.append(REFS_COLUMN)

  def _row(change: ChangeArtifact) -> list[str]:
    row = _prepare_change_row(change)
    if show_external:
      row.insert(1, change.ext_id)
    if show_refs:
      row.append(format_refs_count(collect_references(change)))
    return row

  def _tsv_row(change: ChangeArtifact) -> list[str]:
    row = _prepare_change_tsv_row(change)
    if show_external:
      row.insert(1, change.ext_id)
    if show_refs:
      row.append(format_refs_tsv(collect_references(change)))
    return row

  return format_list_table(
    changes,
    columns=column_labels(col_defs),
    title="Change Artifacts",
    prepare_row=_row,
    prepare_tsv_row=_tsv_row,
    to_json=format_change_list_json,
    format_type=format_type,
    truncate=truncate,
  )


_EMPTY_CELL = "–"


def _format_specs_cell(applies_to: dict[str, Any]) -> str:
  """Render DR-138 §8.1 Specs column: ``N (first-id)`` or em-dash if empty."""
  specs = applies_to.get("specs", []) if applies_to else []
  if not specs:
    return _EMPTY_CELL
  return f"{len(specs)} ({specs[0]})"


def _format_audit_glyph(delta_id: str, audited_delta_ids: set[str]) -> str:
  """Render DR-138 §8.1 Audit column. Glyph keys on delta_id (DEC-138-13)."""
  return "✓" if delta_id in audited_delta_ids else _EMPTY_CELL


def _format_phases_cell(plan: dict[str, Any] | None) -> str:
  """Render DR-138 §8.1 Phases column: completed/total or em-dash if no plan."""
  if not plan:
    return _EMPTY_CELL
  phases = plan.get("phases") or []
  if not phases:
    return _EMPTY_CELL
  total = len(phases)
  completed = sum(
    1
    for p in phases
    if isinstance(p, dict) and str(p.get("status", "")).strip() == "completed"
  )
  return f"{completed}/{total}"


def _format_audit_gate_cell(audit_gate: str | None) -> str:
  """Render DR-138 §8.1 Audit Gate column. Empty when default (``auto``)."""
  if not audit_gate or audit_gate == AUDIT_GATE_AUTO:
    return ""
  return audit_gate


def format_delta_list_row(
  artifact: ChangeArtifact,
  *,
  audited_delta_ids: set[str],
  show_tags: bool = False,
) -> dict[str, str]:
  """Render one delta as a column-keyed cell dict (DR-138 §8.2).

  Pure function — caller renders via Rich table, TSV, or JSON. POL-003
  boundary: takes primitive input (no registry access); the CLI orchestrator
  builds ``audited_delta_ids`` once per invocation.
  """
  row = {
    "id": artifact.id,
    "name": artifact.name,
    "status": artifact.status,
    "specs": _format_specs_cell(artifact.applies_to),
    "audit_gate": _format_audit_gate_cell(artifact.audit_gate),
    "audit": _format_audit_glyph(artifact.id, audited_delta_ids),
    "phases": _format_phases_cell(artifact.plan),
  }
  if show_tags:
    row["tags"] = format_tags_cell(artifact.tags)
  return row


def format_delta_list_json(
  deltas: Sequence[ChangeArtifact],
  *,
  audited_delta_ids: set[str],
) -> str:
  """JSON output per DR-138 §8.4 — full ``applies_to`` + full ``plan``."""
  items: list[dict[str, Any]] = []
  for d in deltas:
    item: dict[str, Any] = {
      "id": d.id,
      "kind": d.kind,
      "status": d.status,
      "name": d.name,
      "slug": d.slug,
      "path": d.path.as_posix(),
      "applies_to": d.applies_to,
      "plan": d.plan,
      "audit_gate": d.audit_gate,
      "audited": d.id in audited_delta_ids,
      "tags": d.tags,
    }
    if d.relations:
      item["relations"] = d.relations
    if d.ext_id:
      item["ext_id"] = d.ext_id
    if d.ext_url:
      item["ext_url"] = d.ext_url
    items.append(item)
  return format_as_json(items)


def format_delta_list_table(
  deltas: Sequence[ChangeArtifact],
  *,
  audited_delta_ids: set[str],
  format_type: str = "table",
  truncate: bool = False,
  show_tags: bool = False,
  show_external: bool = False,
  show_refs: bool = False,
) -> str:
  """Render the enriched delta list per DR-138 §8.1–§8.4.

  ``--external`` / ``--refs`` are preserved column flags (§8.3 flag
  preservation); ``--tags`` is the new opt-in for the legacy Tags column
  (§8.5).
  """
  col_defs = list(DELTA_COLUMNS)
  if show_external:
    col_defs.insert(1, EXT_ID_COLUMN)
  if show_refs:
    col_defs.append(REFS_COLUMN)
  if show_tags:
    col_defs.append(DELTA_TAGS_COLUMN)
  fields = [c.field for c in col_defs]

  def _table_row(d: ChangeArtifact) -> list[str]:
    row = format_delta_list_row(
      d, audited_delta_ids=audited_delta_ids, show_tags=show_tags
    )
    if show_external:
      row["ext_id"] = d.ext_id
    if show_refs:
      row["refs"] = format_refs_count(collect_references(d))
    cells: list[str] = []
    for field_name in fields:
      cell = row.get(field_name, "")
      if field_name == "id":
        cell = f"[change.id]{cell}[/change.id]"
      elif field_name == "status":
        style = get_change_status_style(d.status)
        cell = f"[{style}]{cell}[/{style}]"
      cells.append(cell)
    return cells

  def _tsv_row(d: ChangeArtifact) -> list[str]:
    row = format_delta_list_row(
      d, audited_delta_ids=audited_delta_ids, show_tags=show_tags
    )
    if show_external:
      row["ext_id"] = d.ext_id
    if show_refs:
      row["refs"] = format_refs_tsv(collect_references(d))
    return [row.get(field_name, "") for field_name in fields]

  def _to_json(items: Sequence[ChangeArtifact]) -> str:
    return format_delta_list_json(items, audited_delta_ids=audited_delta_ids)

  return format_list_table(
    deltas,
    columns=column_labels(col_defs),
    title="Deltas",
    prepare_row=_table_row,
    prepare_tsv_row=_tsv_row,
    to_json=_to_json,
    format_type=format_type,
    truncate=truncate,
  )


def _format_change_basic_fields(artifact: ChangeArtifact) -> list[str]:
  """Format basic change artifact fields."""
  lines = [
    f"Delta: {artifact.id}",
    f"Name: {artifact.name}",
    f"Status: {artifact.status}",
    f"Kind: {artifact.kind}",
  ]
  if artifact.ext_id:
    ext_line = f"External: {artifact.ext_id}"
    if artifact.ext_url:
      ext_line += f" ({artifact.ext_url})"
    lines.append(ext_line)
  return lines


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


def _resolve_phase_objective_from_file_body(
  phase_content: str,
  *,
  source_path: Path | None = None,
) -> str | None:
  """Structured objective from phase file body: frontmatter first, then phase.overview.

  Display-time enrichment (DE-131 / DR-131): does not merge conflicting sources;
  returns the first non-empty value per canonical precedence.
  """
  try:
    post = frontmatter.loads(phase_content)
  except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
    # Corrupt phase markdown must not break show delta / list output.
    return None
  fm_data: dict[str, Any] = dict(post.metadata or {})
  try:
    sheet = PhaseSheet.model_validate(fm_data)
  except ValidationError:
    sheet = PhaseSheet()
  if sheet.objective is not None and str(sheet.objective).strip():
    return str(sheet.objective).strip()
  try:
    overview = extract_phase_overview(phase_content, source_path)
  except ValueError:
    overview = None
  if overview:
    raw = overview.data.get("objective")
    if isinstance(raw, str) and raw.strip():
      return raw.strip()
  return None


_PHASE_SEQ_FROM_ID = re.compile(r"(?:\.PHASE-|-P)(?P<num>\d{2})$")


def _phase_sequence_digits_from_id(phase_id: str) -> str | None:
  """Return two-digit sequence from phase id (hyphen or dotted spelling)."""
  if not isinstance(phase_id, str):
    return None
  stripped = phase_id.strip()
  match = _PHASE_SEQ_FROM_ID.search(stripped)
  if match:
    return match.group("num")
  parts = stripped.split("-")
  if parts and parts[-1].isdigit():
    return parts[-1]
  return None


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

  phase_num = _phase_sequence_digits_from_id(str(phase_id))
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

    # DE-131 / DR-131: fill objective from disk when plan dict omits it
    if not str(enriched.get("objective", "")).strip():
      resolved = _resolve_phase_objective_from_file_body(
        phase_content,
        source_path=phase_file,
      )
      if resolved:
        enriched["objective"] = resolved
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
  table = create_table(columns=column_labels(PHASE_COLUMNS), show_header=True)

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
    rel_type = relation.get("type", "")
    target = relation.get("target", "")
    lines.append(f"  - {rel_type}: {target}")

  return lines


def _format_delta_reverse_lookups(
  linked_audits: list[tuple[str, str]],
  linked_revisions: list[tuple[str, str]],
) -> list[str]:
  """Format reverse lookup section for delta details.

  Args:
    linked_audits: List of (id, name) tuples for audits referencing this delta.
    linked_revisions: List of (id, name) for revisions referencing this delta.

  Returns:
    Lines for the reverse lookup section, or empty if none.
  """
  lines: list[str] = []
  for audit_id, audit_name in linked_audits:
    lines.append(f"Audit: {audit_id} — {audit_name}")
  for rev_id, rev_name in linked_revisions:
    lines.append(f"Revision: {rev_id} — {rev_name}")
  if lines:
    lines.insert(0, "")
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
  *,
  linked_audits: list[tuple[str, str]] | None = None,
  linked_revisions: list[tuple[str, str]] | None = None,
) -> str:
  """Format delta details as multi-line string for display.

  Args:
    artifact: ChangeArtifact to format
    root: Repository root for relative path calculation (optional)
    linked_audits: List of (id, name) for audits referencing this delta.
    linked_revisions: List of (id, name) for revisions referencing this delta.

  Returns:
    Formatted string with all delta details
  """
  sections = [
    _format_change_basic_fields(artifact),
    _format_applies_to(artifact),
    _format_plan_overview(artifact, root),
    _format_relations(artifact),
    _format_delta_reverse_lookups(
      linked_audits or [],
      linked_revisions or [],
    ),
    _format_other_files(artifact, root),
    _format_file_path_for_change(artifact, root),
  ]

  # Flatten all non-empty sections
  lines = [line for section in sections for line in section]
  return "\n".join(lines)


def _format_revision_basic_fields(artifact: ChangeArtifact) -> list[str]:
  """Format basic revision artifact fields."""
  lines = [
    f"Revision: {artifact.id}",
    f"Name: {artifact.name}",
    f"Status: {artifact.status}",
    f"Kind: {artifact.kind}",
  ]
  if artifact.ext_id:
    ext_line = f"External: {artifact.ext_id}"
    if artifact.ext_url:
      ext_line += f" ({artifact.ext_url})"
    lines.append(ext_line)
  return lines


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


def _format_audit_basic_fields(artifact: ChangeArtifact) -> list[str]:
  """Format basic audit artifact fields."""
  return [
    f"Audit: {artifact.id}",
    f"Name: {artifact.name}",
    f"Status: {artifact.status}",
    f"Kind: {artifact.kind}",
  ]


def format_audit_details(
  artifact: ChangeArtifact,
  root: Path | None = None,
) -> str:
  """Format audit details as multi-line string for display.

  Args:
    artifact: ChangeArtifact to format (must be kind='audit')
    root: Repository root for relative path calculation (optional)

  Returns:
    Formatted string with all audit details
  """
  sections = [
    _format_audit_basic_fields(artifact),
    _format_affects(artifact),
    _format_relations(artifact),
    _format_file_path_for_change(artifact, root),
  ]

  lines = [line for section in sections for line in section]
  return "\n".join(lines)


_MODE_GLYPHS = {"conformance": "C", "discovery": "D"}


def _format_mode_glyph(artifact: ChangeArtifact) -> str:
  return _MODE_GLYPHS.get(artifact.mode or "", artifact.mode or _EMPTY_CELL)


def _format_delta_ref(artifact: ChangeArtifact) -> str:
  return artifact.delta_ref or _EMPTY_CELL


def format_audit_list_row(
  artifact: ChangeArtifact,
  summary: AuditFindingsSummary,
) -> dict[str, str]:
  """Render one audit as a column-keyed cell dict (DR-141 §5.4)."""
  display_name = artifact.name
  if display_name.startswith("Audit - "):
    display_name = display_name[8:]
  return {
    "id": artifact.id,
    "name": display_name,
    "status": artifact.status,
    "mode": _format_mode_glyph(artifact),
    "delta_ref": _format_delta_ref(artifact),
    "findings": summary.findings_cell(),
    "disposed": summary.disposed_cell(),
  }


def format_audit_list_json(
  audits: Sequence[ChangeArtifact],
  summaries: Mapping[str, AuditFindingsSummary],
) -> str:
  """JSON output for audit list — includes enriched fields."""
  items: list[dict[str, Any]] = []
  for a in audits:
    s = summaries.get(a.id)
    item: dict[str, Any] = {
      "id": a.id,
      "kind": a.kind,
      "status": a.status,
      "name": a.name,
      "slug": a.slug,
      "path": a.path.as_posix(),
      "mode": a.mode,
      "delta_ref": a.delta_ref,
    }
    if s:
      item["findings_total"] = s.total
      item["findings_aligned"] = s.aligned
      item["findings_drift"] = s.drift
      item["findings_risk"] = s.risk
      item["findings_disposed"] = s.disposed
    if a.applies_to:
      item["applies_to"] = a.applies_to
    if a.tags:
      item["tags"] = a.tags
    items.append(item)
  return format_as_json(items)


def format_audit_list_table(
  audits: Sequence[ChangeArtifact],
  summaries: Mapping[str, AuditFindingsSummary],
  *,
  format_type: str = "table",
  truncate: bool = False,
  show_external: bool = False,
) -> str:
  """Render enriched audit list per DR-141 §5.5."""
  col_defs = list(AUDIT_COLUMNS)
  if show_external:
    col_defs.insert(1, EXT_ID_COLUMN)
  fields = [c.field for c in col_defs]

  def _get_summary(a: ChangeArtifact) -> AuditFindingsSummary:
    s = summaries.get(a.id)
    if s:
      return s
    from supekku.scripts.lib.changes.audit_check import (  # noqa: PLC0415
      AuditFindingsSummary as _Summary,
    )

    return _Summary(0, 0, 0, 0, 0)

  def _table_row(a: ChangeArtifact) -> list[str]:
    row = format_audit_list_row(a, _get_summary(a))
    if show_external:
      row["ext_id"] = a.ext_id
    cells: list[str] = []
    for field_name in fields:
      cell = row.get(field_name, "")
      if field_name == "id":
        cell = f"[change.id]{cell}[/change.id]"
      elif field_name == "status":
        style = get_change_status_style(a.status)
        cell = f"[{style}]{cell}[/{style}]"
      cells.append(cell)
    return cells

  def _tsv_row(a: ChangeArtifact) -> list[str]:
    row = format_audit_list_row(a, _get_summary(a))
    if show_external:
      row["ext_id"] = a.ext_id
    return [row.get(field_name, "") for field_name in fields]

  def _to_json(items: Sequence[ChangeArtifact]) -> str:
    return format_audit_list_json(items, summaries)

  return format_list_table(
    audits,
    columns=column_labels(col_defs),
    title="Audits",
    prepare_row=_table_row,
    prepare_tsv_row=_tsv_row,
    to_json=_to_json,
    format_type=format_type,
    truncate=truncate,
  )


def format_revision_list_row(
  artifact: ChangeArtifact,
  summary: RevisionChangeSummary,
) -> dict[str, str]:
  """Render one revision as a column-keyed cell dict (DR-142 §7.2)."""
  display_name = artifact.name
  prefix = "Spec Revision - "
  if display_name.startswith(prefix):
    display_name = display_name[len(prefix) :]
  return {
    "id": artifact.id,
    "name": display_name,
    "status": artifact.status,
    "source": summary.source_cell(),
    "destination": summary.destination_cell(),
    "requirements": summary.requirements_cell(),
  }


def format_revision_list_json(
  revisions: Sequence[ChangeArtifact],
  summaries: Mapping[str, RevisionChangeSummary],
) -> str:
  """JSON output for revision list — enriched fields, stable schema."""
  items: list[dict[str, Any]] = []
  for r in revisions:
    s = summaries.get(r.id)
    item: dict[str, Any] = {
      "id": r.id,
      "kind": r.kind,
      "status": r.status,
      "name": r.name,
      "slug": r.slug,
      "path": r.path.as_posix(),
    }
    if s:
      item["sources"] = s.sources
      item["destinations"] = s.destinations
      item["requirements"] = s.requirements
    if r.applies_to:
      item["applies_to"] = r.applies_to
    if r.tags:
      item["tags"] = r.tags
    items.append(item)
  return format_as_json(items)


def format_revision_list_table(
  revisions: Sequence[ChangeArtifact],
  summaries: Mapping[str, RevisionChangeSummary],
  *,
  format_type: str = "table",
  truncate: bool = False,
  show_external: bool = False,
) -> str:
  """Render enriched revision list per DR-142 §7.2.

  DEC-CONSULT-06: the ``Source`` column is dropped in the **table** view when no
  revision has an origin; TSV and JSON keep the full field set (stable schema).
  """

  def _get_summary(r: ChangeArtifact) -> RevisionChangeSummary:
    s = summaries.get(r.id)
    if s:
      return s
    return RevisionChangeSummary([], [], [])

  full_defs = list(REVISION_COLUMNS)
  if show_external:
    full_defs.insert(1, EXT_ID_COLUMN)
  full_fields = [c.field for c in full_defs]

  # Adaptive Source-hide (table view only). TSV/JSON keep the full schema.
  hide_source = not any(_get_summary(r).sources for r in revisions)
  table_defs = (
    [c for c in full_defs if c.field != "source"] if hide_source else full_defs
  )
  table_fields = [c.field for c in table_defs]

  def _table_row(r: ChangeArtifact) -> list[str]:
    row = format_revision_list_row(r, _get_summary(r))
    if show_external:
      row["ext_id"] = r.ext_id
    cells: list[str] = []
    for field_name in table_fields:
      cell = row.get(field_name, "")
      if field_name == "id":
        cell = f"[change.id]{cell}[/change.id]"
      elif field_name == "status":
        style = get_change_status_style(r.status)
        cell = f"[{style}]{cell}[/{style}]"
      cells.append(cell)
    return cells

  def _tsv_row(r: ChangeArtifact) -> list[str]:
    row = format_revision_list_row(r, _get_summary(r))
    if show_external:
      row["ext_id"] = r.ext_id
    return [row.get(field_name, "") for field_name in full_fields]

  def _to_json(items: Sequence[ChangeArtifact]) -> str:
    return format_revision_list_json(items, summaries)

  return format_list_table(
    revisions,
    columns=column_labels(table_defs),
    title="Revisions",
    prepare_row=_table_row,
    prepare_tsv_row=_tsv_row,
    to_json=_to_json,
    format_type=format_type,
    truncate=truncate,
  )


def format_plan_details(
  plan_data: dict,
  root: Path | None = None,
  path: Path | None = None,
) -> str:
  """Format plan details as multi-line string for display.

  Args:
    plan_data: Plan frontmatter dictionary.
    root: Repository root for relative path calculation (optional).
    path: Plan file path (optional).

  Returns:
    Formatted string with plan details.
  """
  lines = [
    f"Plan: {plan_data.get('id', 'unknown')}",
    f"Name: {plan_data.get('name', '')}",
    f"Status: {plan_data.get('status', '')}",
    f"Kind: {plan_data.get('kind', 'plan')}",
  ]
  if path:
    display_path = path
    if root:
      with contextlib.suppress(ValueError):
        display_path = path.relative_to(root)
    lines.extend(["", f"File: {display_path}"])
  return "\n".join(lines)


def _prepare_plan_row(plan: dict[str, Any]) -> list[str]:
  """Prepare a plan row with styling for rich table display."""
  plan_id = f"[change.id]{plan.get('id', '?')}[/change.id]"
  status = plan.get("status", "")
  status_style = get_change_status_style(status)
  styled_status = f"[{status_style}]{status}[/{status_style}]"
  name = plan.get("name", "")
  if name.startswith("Implementation Plan - "):
    name = name[21:]
  delta = plan.get("delta_ref", "")
  return [plan_id, styled_status, name, delta]


def _prepare_plan_tsv_row(plan: dict[str, Any]) -> list[str]:
  """Prepare a plan row for TSV output (no markup)."""
  name = plan.get("name", "")
  if name.startswith("Implementation Plan - "):
    name = name[21:]
  return [
    plan.get("id", ""),
    plan.get("status", ""),
    name,
    plan.get("delta_ref", ""),
  ]


def _plan_list_to_json(plans: Sequence[dict[str, Any]]) -> str:
  """Serialize plans to JSON."""
  items = []
  for plan in plans:
    item: dict[str, Any] = {
      "id": plan.get("id", ""),
      "status": plan.get("status", ""),
      "name": plan.get("name", ""),
    }
    if plan.get("delta_ref"):
      item["delta_ref"] = plan["delta_ref"]
    if plan.get("kind"):
      item["kind"] = plan["kind"]
    items.append(item)
  return format_as_json(items)


def format_plan_list_table(
  plans: Sequence[dict[str, Any]],
  format_type: str = "table",
  truncate: bool = False,
) -> str:
  """Format plans as table, JSON, or TSV.

  Args:
    plans: Plan frontmatter dictionaries.
    format_type: Output format (table|json|tsv).
    truncate: If True, truncate long fields.

  Returns:
    Formatted string in requested format.
  """
  return format_list_table(
    plans,
    columns=column_labels(PLAN_COLUMNS),
    title="Implementation Plans",
    prepare_row=_prepare_plan_row,
    prepare_tsv_row=_prepare_plan_tsv_row,
    to_json=_plan_list_to_json,
    format_type=format_type,
    truncate=truncate,
  )


def format_change_list_json(changes: Sequence[ChangeArtifact]) -> str:
  """Format change artifacts as JSON array.

  Args:
    changes: List of ChangeArtifact objects

  Returns:
    JSON string with structure: {"items": [...]}
  """
  items = []
  for change in changes:
    item: dict[str, Any] = {
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
    if change.ext_id:
      item["ext_id"] = change.ext_id
    if change.ext_url:
      item["ext_url"] = change.ext_url

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
