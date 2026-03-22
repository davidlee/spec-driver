"""Read and write workflow handoff.current.yaml with schema validation.

All mutations to handoff.current.yaml go through ``write_handoff``,
which validates output against the schema before writing.  Writes are
atomic (write-to-temp + rename) per DR-102 §5.

Design authority: DR-102 §3.2, §5.
"""

from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from supekku.scripts.lib.blocks.metadata.validator import MetadataValidator
from supekku.scripts.lib.blocks.workflow_metadata import (
  WORKFLOW_HANDOFF_METADATA,
)


class HandoffValidationError(Exception):
  """Raised when handoff data fails schema validation."""

  def __init__(self, errors: list) -> None:
    self.errors = errors
    details = "; ".join(str(e) for e in errors[:5])
    super().__init__(f"handoff validation failed: {details}")


class HandoffNotFoundError(Exception):
  """Raised when handoff.current.yaml does not exist."""


_VALIDATOR = MetadataValidator(WORKFLOW_HANDOFF_METADATA)

DEFAULT_STATE_DIR = "workflow"
HANDOFF_FILENAME = "handoff.current.yaml"


def _now_iso() -> str:
  """Current UTC timestamp in ISO 8601 format."""
  return datetime.now(tz=UTC).isoformat(timespec="seconds")


def handoff_path(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> Path:
  """Return the path to workflow/handoff.current.yaml."""
  return delta_dir / state_dir / HANDOFF_FILENAME


def read_handoff(
  delta_dir: Path,
  state_dir: str = DEFAULT_STATE_DIR,
) -> dict[str, Any]:
  """Read and validate handoff.current.yaml.

  Raises:
    HandoffNotFoundError: If the file does not exist.
    HandoffValidationError: If content fails schema validation.
  """
  path = handoff_path(delta_dir, state_dir)
  if not path.exists():
    raise HandoffNotFoundError(f"handoff not found: {path}")

  data = yaml.safe_load(path.read_text(encoding="utf-8"))
  errors = _VALIDATOR.validate(data)
  if errors:
    raise HandoffValidationError(errors)
  return data


def write_handoff(
  delta_dir: Path,
  data: dict[str, Any],
  state_dir: str = DEFAULT_STATE_DIR,
) -> Path:
  """Validate and atomically write handoff.current.yaml.

  Returns:
    Path to the written file.

  Raises:
    HandoffValidationError: If data fails schema validation.
  """
  errors = _VALIDATOR.validate(data)
  if errors:
    raise HandoffValidationError(errors)

  path = handoff_path(delta_dir, state_dir)
  path.parent.mkdir(parents=True, exist_ok=True)

  content = yaml.dump(data, default_flow_style=False, sort_keys=False)

  fd, tmp = tempfile.mkstemp(
    dir=path.parent,
    suffix=".tmp",
    prefix="handoff_",
  )
  closed = False
  try:
    os.write(fd, content.encode("utf-8"))
    os.close(fd)
    closed = True
    Path(tmp).replace(path)
  except BaseException:
    if not closed:
      os.close(fd)
    tmp_path = Path(tmp)
    if tmp_path.exists():
      tmp_path.unlink()
    raise

  return path


def build_handoff(
  *,
  artifact_id: str,
  artifact_kind: str,
  from_role: str,
  to_role: str,
  phase_id: str,
  phase_status: str | None = None,
  required_reading: list[str],
  boundary: str | None = None,
  next_activity_kind: str = "implementation",
  next_activity_summary: str | None = None,
  git_head: str | None = None,
  git_branch: str | None = None,
  has_uncommitted: bool | None = None,
  has_staged: bool | None = None,
  verification_status: str | None = None,
  verification_summary: str | None = None,
  verification_commands: list[str] | None = None,
  open_items: list[dict[str, Any]] | None = None,
  related_documents: list[str] | None = None,
  key_files: list[str] | None = None,
  design_tensions: list[str] | None = None,
  unresolved_assumptions: list[str] | None = None,
  decisions_to_preserve: list[str] | None = None,
) -> dict[str, Any]:
  """Build a handoff payload dict.

  Returns a dict ready for ``write_handoff``.
  """
  data: dict[str, Any] = {
    "schema": "supekku.workflow.handoff",
    "version": 1,
    "artifact": {
      "id": artifact_id,
      "kind": artifact_kind,
    },
    "transition": {
      "from_role": from_role,
      "to_role": to_role,
      "status": "pending",
    },
    "phase": {
      "id": phase_id,
    },
    "required_reading": required_reading,
    "next_activity": {
      "kind": next_activity_kind,
    },
    "timestamps": {
      "emitted_at": _now_iso(),
    },
  }

  if boundary:
    data["transition"]["boundary"] = boundary

  if phase_status:
    data["phase"]["status"] = phase_status

  if next_activity_summary:
    data["next_activity"]["summary"] = next_activity_summary

  # Git state
  if git_head is not None:
    git: dict[str, Any] = {"head": git_head}
    if git_branch is not None:
      git["branch"] = git_branch
    if has_uncommitted is not None or has_staged is not None:
      git["worktree"] = {
        "has_uncommitted_changes": has_uncommitted or False,
        "has_staged_changes": has_staged or False,
      }
    data["git"] = git

  # Verification
  if verification_status:
    verification: dict[str, Any] = {"status": verification_status}
    if verification_summary:
      verification["summary"] = verification_summary
    if verification_commands:
      verification["commands"] = verification_commands
    data["verification"] = verification

  # Optional lists — only include if non-empty
  if open_items:
    data["open_items"] = open_items
  if related_documents:
    data["related_documents"] = related_documents
  if key_files:
    data["key_files"] = key_files
  if design_tensions:
    data["design_tensions"] = design_tensions
  if unresolved_assumptions:
    data["unresolved_assumptions"] = unresolved_assumptions
  if decisions_to_preserve:
    data["decisions_to_preserve"] = decisions_to_preserve

  return data
