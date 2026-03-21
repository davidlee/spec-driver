"""Workflow orchestration operations (domain logic).

Each function implements one CLI command's business logic.  CLI modules
call these — they do not contain business logic themselves (skinny CLI).

Design authority: DR-102 §4, §5.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from supekku.scripts.lib.workflow.state_io import (
  init_state as _init_state,
)
from supekku.scripts.lib.workflow.state_io import (
  read_state,
  state_path,
  update_state_workflow,
  write_state,
)
from supekku.scripts.lib.workflow.state_machine import (
  TransitionCommand,
  TransitionError,
  WorkflowState,
  apply_transition,
)


class WorkflowAlreadyInitializedError(Exception):
  """Raised when phase start is called but state.yaml already exists."""


def phase_start(
  *,
  delta_dir: Path,
  artifact_id: str,
  artifact_kind: str = "delta",
  phase_id: str,
  plan_id: str | None = None,
  artifact_path: str | None = None,
  notes_path: str | None = None,
  plan_path: str | None = None,
  phase_path: str | None = None,
  state_dir: str = "workflow",
  config: dict[str, Any] | None = None,
) -> dict[str, Any]:
  """Initialize workflow state (planned → implementing).

  Creates ``workflow/state.yaml`` for a delta that has no workflow
  state yet.  If state already exists, raises an error.

  Returns:
    The written state dict.

  Raises:
    WorkflowAlreadyInitializedError: If state.yaml already exists.
  """
  path = state_path(delta_dir, state_dir)
  if path.exists():
    raise WorkflowAlreadyInitializedError(
      f"workflow already initialized: {path}"
    )

  data = _init_state(
    artifact_id=artifact_id,
    artifact_kind=artifact_kind,
    phase_id=phase_id,
    plan_id=plan_id,
    artifact_path=artifact_path,
    notes_path=notes_path,
    plan_path=plan_path,
    phase_path=phase_path,
    config=config,
  )
  write_state(delta_dir, data, state_dir)
  return data


def workflow_status(
  *,
  delta_dir: Path,
  state_dir: str = "workflow",
) -> dict[str, Any]:
  """Read workflow state for status display.

  Returns:
    Parsed state dict.

  Raises:
    StateNotFoundError: If state.yaml does not exist.
  """
  return read_state(delta_dir, state_dir)


def format_status(data: dict[str, Any]) -> str:
  """Format workflow state as human-readable summary.

  Returns multiline string suitable for terminal output.
  """
  artifact = data.get("artifact", {})
  phase = data.get("phase", {})
  wf = data.get("workflow", {})
  plan = data.get("plan", {})
  timestamps = data.get("timestamps", {})

  lines: list[str] = []
  lines.append(f"Artifact:  {artifact.get('id', '?')}")
  if plan.get("id"):
    lines.append(f"Plan:      {plan['id']}")
  lines.append(f"Phase:     {phase.get('id', '?')}")
  lines.append(f"Phase status: {phase.get('status', '?')}")
  lines.append("")
  lines.append(f"Workflow:  {wf.get('status', '?')}")
  lines.append(f"Role:      {wf.get('active_role', '?')}")
  if wf.get("next_role"):
    lines.append(f"Next role: {wf['next_role']}")
  if wf.get("claimed_by"):
    lines.append(f"Claimed by: {wf['claimed_by']}")
  if wf.get("previous_state"):
    lines.append(f"Previous:  {wf['previous_state']}")
  lines.append("")
  lines.append(f"Updated:   {timestamps.get('updated', '?')}")

  return "\n".join(lines)


def block_workflow(
  *,
  delta_dir: Path,
  state_dir: str = "workflow",
) -> dict[str, Any]:
  """Transition workflow to blocked state.

  Saves the current state as ``previous_state`` so unblock can restore it.

  Returns:
    Updated state dict.

  Raises:
    StateNotFoundError: If state.yaml does not exist.
    TransitionError: If already blocked.
  """
  data = read_state(delta_dir, state_dir)
  current = WorkflowState(data["workflow"]["status"])

  result = apply_transition(current, TransitionCommand.BLOCK)

  update_state_workflow(
    data,
    status=result.new_state.value,
    previous_state=result.previous_state.value,
  )
  write_state(delta_dir, data, state_dir)
  return data


def unblock_workflow(
  *,
  delta_dir: Path,
  state_dir: str = "workflow",
) -> dict[str, Any]:
  """Restore workflow from blocked state.

  Returns:
    Updated state dict.

  Raises:
    StateNotFoundError: If state.yaml does not exist.
    TransitionError: If not currently blocked or no previous_state.
  """
  data = read_state(delta_dir, state_dir)
  current = WorkflowState(data["workflow"]["status"])
  prev_raw = data["workflow"].get("previous_state")

  if prev_raw is None:
    raise TransitionError(
      current, TransitionCommand.UNBLOCK,
      "no previous_state recorded",
    )

  previous = WorkflowState(prev_raw)
  result = apply_transition(
    current, TransitionCommand.UNBLOCK, previous_state=previous,
  )

  update_state_workflow(
    data,
    status=result.new_state.value,
    active_role=data["workflow"].get("active_role"),
    previous_state=None,  # clear after restore
  )
  write_state(delta_dir, data, state_dir)
  return data
