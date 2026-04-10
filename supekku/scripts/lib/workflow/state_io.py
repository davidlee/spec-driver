"""Read and write workflow state.yaml with schema validation.

All mutations to state.yaml go through ``write_state``, which validates
the output against the schema before writing.  Writes are atomic
(write-to-temp + rename) per DR-102 §5.

Design authority: DR-102 §3.1, §5.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from supekku.scripts.lib.blocks.metadata.validator import MetadataValidator
from supekku.scripts.lib.blocks.workflow_metadata import WORKFLOW_STATE_METADATA
from supekku.scripts.lib.core.io import atomic_write
from supekku.scripts.lib.workflow.state_machine import WorkflowState


class StateValidationError(Exception):
  """Raised when state.yaml data fails schema validation."""

  def __init__(self, errors: list) -> None:
    self.errors = errors
    details = "; ".join(str(e) for e in errors[:5])
    super().__init__(f"state.yaml validation failed: {details}")


class StateNotFoundError(Exception):
  """Raised when workflow/state.yaml does not exist."""


_VALIDATOR = MetadataValidator(WORKFLOW_STATE_METADATA)

# Default workflow subdirectory within a delta bundle
DEFAULT_STATE_DIR = "workflow"


def _now_iso() -> str:
  """Current UTC timestamp in ISO 8601 format."""
  return datetime.now(tz=UTC).isoformat(timespec="seconds")


def state_path(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> Path:
  """Return the path to workflow/state.yaml within a delta bundle."""
  return delta_dir / state_dir / "state.yaml"


def read_state(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> dict[str, Any]:
  """Read and validate workflow/state.yaml.

  Args:
    delta_dir: Path to the delta bundle directory.
    state_dir: Subdirectory for workflow files.

  Returns:
    Parsed and validated state dict.

  Raises:
    StateNotFoundError: If the file does not exist.
    StateValidationError: If the content fails schema validation.
  """
  path = state_path(delta_dir, state_dir)
  if not path.exists():
    raise StateNotFoundError(f"workflow state not found: {path}")

  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  errors = _VALIDATOR.validate(data)
  if errors:
    raise StateValidationError(errors)
  return data


def write_state(
  delta_dir: Path,
  data: dict[str, Any],
  state_dir: str = DEFAULT_STATE_DIR,
) -> Path:
  """Validate and atomically write workflow/state.yaml.

  Args:
    delta_dir: Path to the delta bundle directory.
    data: State dict to write.
    state_dir: Subdirectory for workflow files.

  Returns:
    Path to the written file.

  Raises:
    StateValidationError: If the data fails schema validation.
  """
  errors = _VALIDATOR.validate(data)
  if errors:
    raise StateValidationError(errors)

  path = state_path(delta_dir, state_dir)
  content = yaml.dump(data, default_flow_style=False, sort_keys=False)
  return atomic_write(path, content)


def init_state(
  *,
  artifact_id: str,
  artifact_kind: str = "delta",
  phase_id: str,
  plan_id: str | None = None,
  artifact_path: str | None = None,
  notes_path: str | None = None,
  plan_path: str | None = None,
  phase_path: str | None = None,
  config: dict[str, Any] | None = None,
) -> dict[str, Any]:
  """Create initial state.yaml data for ``planned → implementing``.

  Does NOT write the file — call ``write_state`` after transition.

  Returns:
    State dict ready for write_state.
  """
  wf_config = (config or {}).get("workflow", {})

  now = _now_iso()

  artifact: dict[str, Any] = {
    "id": artifact_id,
    "kind": artifact_kind,
  }
  if artifact_path:
    artifact["path"] = artifact_path
  if notes_path:
    artifact["notes_path"] = notes_path

  phase: dict[str, Any] = {
    "id": phase_id,
    "status": "in_progress",
  }
  if phase_path:
    phase["path"] = phase_path

  workflow: dict[str, Any] = {
    "status": WorkflowState.IMPLEMENTING.value,
    "active_role": "implementer",
    "handoff_boundary": wf_config.get("handoff_boundary", "phase"),
  }

  data: dict[str, Any] = {
    "schema": "supekku.workflow.state",
    "version": 1,
    "artifact": artifact,
    "phase": phase,
    "workflow": workflow,
    "timestamps": {
      "created": now,
      "updated": now,
    },
  }

  if plan_id:
    plan: dict[str, Any] = {"id": plan_id}
    if plan_path:
      plan["path"] = plan_path
    data["plan"] = plan

  return data


def update_state_workflow(
  data: dict[str, Any],
  *,
  status: str | None = None,
  active_role: str | None = None,
  next_role: str | None = None,
  claimed_by: str | None | type[...] = ...,
  previous_state: str | None | type[...] = ...,
) -> dict[str, Any]:
  """Update workflow fields in a state dict (in-place).

  Uses ``...`` (Ellipsis) as sentinel to distinguish "not provided"
  from "set to None".  Pass ``claimed_by=None`` to clear the claim.

  Returns the mutated dict for convenience.
  """
  wf = data["workflow"]
  if status is not None:
    wf["status"] = status
  if active_role is not None:
    wf["active_role"] = active_role
  if next_role is not None:
    wf["next_role"] = next_role
  if claimed_by is not ...:
    if claimed_by is None:
      wf.pop("claimed_by", None)
    else:
      wf["claimed_by"] = claimed_by
  if previous_state is not ...:
    if previous_state is None:
      wf.pop("previous_state", None)
    else:
      wf["previous_state"] = previous_state
  data["timestamps"]["updated"] = _now_iso()
  return data
