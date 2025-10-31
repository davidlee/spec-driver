"""Change artifact (delta/revision/audit) display formatters.

Pure formatting functions with no business logic.
Formatters take ChangeArtifact objects and return formatted strings for display.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
  from supekku.scripts.lib.changes.artifacts import ChangeArtifact


def format_change_list_item(artifact: "ChangeArtifact") -> str:
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


def format_change_with_context(artifact: "ChangeArtifact") -> str:
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
