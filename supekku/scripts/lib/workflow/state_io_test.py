"""Tests for workflow state.yaml reading/writing (DR-102 §3.1, §5).

Validates schema validation on read/write, atomic writes,
init_state construction, and update_state_workflow mutations.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from supekku.scripts.lib.workflow.state_io import (
  StateNotFoundError,
  StateValidationError,
  init_state,
  read_state,
  state_path,
  update_state_workflow,
  write_state,
)
from supekku.scripts.lib.workflow.state_machine import WorkflowState


def _minimal_state() -> dict:
  """Return minimal valid state dict."""
  return {
    "schema": "supekku.workflow.state",
    "version": 1,
    "artifact": {"id": "DE-090", "kind": "delta"},
    "phase": {"id": "IP-090.PHASE-01", "status": "in_progress"},
    "workflow": {
      "status": "implementing",
      "active_role": "implementer",
    },
    "timestamps": {
      "created": "2026-03-21T10:00:00+00:00",
      "updated": "2026-03-21T10:00:00+00:00",
    },
  }


class StatePathTest(unittest.TestCase):
  """state_path returns expected path."""

  def test_default_dir(self) -> None:
    p = state_path(Path("/tmp/delta"))
    assert p == Path("/tmp/delta/workflow/state.yaml")

  def test_custom_dir(self) -> None:
    p = state_path(Path("/tmp/delta"), state_dir="custom")
    assert p == Path("/tmp/delta/custom/state.yaml")


class WriteStateTest(unittest.TestCase):
  """Atomic write with schema validation."""

  def test_write_valid_state(self) -> None:
    with TemporaryDirectory() as tmp:
      delta = Path(tmp)
      data = _minimal_state()
      path = write_state(delta, data)
      assert path.exists()
      loaded = yaml.safe_load(path.read_text())
      assert loaded["artifact"]["id"] == "DE-090"

  def test_write_creates_directory(self) -> None:
    with TemporaryDirectory() as tmp:
      delta = Path(tmp) / "nested" / "delta"
      data = _minimal_state()
      path = write_state(delta, data)
      assert path.exists()

  def test_write_rejects_invalid_data(self) -> None:
    with TemporaryDirectory() as tmp:
      delta = Path(tmp)
      data = {"schema": "supekku.workflow.state", "version": 1}  # missing required
      with self.assertRaises(StateValidationError):
        write_state(delta, data)

  def test_write_is_atomic_no_partial_file(self) -> None:
    with TemporaryDirectory() as tmp:
      delta = Path(tmp)
      data = _minimal_state()
      write_state(delta, data)
      # Verify only state.yaml exists — no temp files left behind
      wf_dir = delta / "workflow"
      files = list(wf_dir.iterdir())
      assert len(files) == 1
      assert files[0].name == "state.yaml"


class ReadStateTest(unittest.TestCase):
  """Read with validation."""

  def test_read_valid_state(self) -> None:
    with TemporaryDirectory() as tmp:
      delta = Path(tmp)
      data = _minimal_state()
      write_state(delta, data)
      loaded = read_state(delta)
      assert loaded["artifact"]["id"] == "DE-090"

  def test_read_missing_file_raises(self) -> None:
    with TemporaryDirectory() as tmp:
      delta = Path(tmp)
      with self.assertRaises(StateNotFoundError):
        read_state(delta)

  def test_read_invalid_file_raises(self) -> None:
    with TemporaryDirectory() as tmp:
      delta = Path(tmp)
      wf_dir = delta / "workflow"
      wf_dir.mkdir(parents=True)
      (wf_dir / "state.yaml").write_text(
        yaml.dump({"schema": "supekku.workflow.state", "version": 1}),
      )
      with self.assertRaises(StateValidationError):
        read_state(delta)


class InitStateTest(unittest.TestCase):
  """init_state constructs valid state dicts."""

  def test_minimal_init(self) -> None:
    data = init_state(artifact_id="DE-100", phase_id="IP-100.PHASE-01")
    assert data["schema"] == "supekku.workflow.state"
    assert data["version"] == 1
    assert data["artifact"]["id"] == "DE-100"
    assert data["artifact"]["kind"] == "delta"
    assert data["phase"]["id"] == "IP-100.PHASE-01"
    assert data["phase"]["status"] == "in_progress"
    assert data["workflow"]["status"] == WorkflowState.IMPLEMENTING.value
    assert data["workflow"]["active_role"] == "implementer"
    assert "timestamps" in data

  def test_full_init(self) -> None:
    data = init_state(
      artifact_id="DE-100",
      artifact_kind="delta",
      phase_id="IP-100.PHASE-01",
      plan_id="IP-100",
      artifact_path=".spec-driver/deltas/DE-100-slug",
      notes_path=".spec-driver/deltas/DE-100-slug/notes.md",
      plan_path=".spec-driver/deltas/DE-100-slug/IP-100.md",
      phase_path=".spec-driver/deltas/DE-100-slug/phases/phase-01.md",
    )
    assert data["artifact"]["path"] == ".spec-driver/deltas/DE-100-slug"
    assert data["artifact"]["notes_path"] == ".spec-driver/deltas/DE-100-slug/notes.md"
    assert data["plan"]["id"] == "IP-100"
    assert data["plan"]["path"] == ".spec-driver/deltas/DE-100-slug/IP-100.md"
    assert data["phase"]["path"] == ".spec-driver/deltas/DE-100-slug/phases/phase-01.md"

  def test_init_respects_config(self) -> None:
    config = {"workflow": {"handoff_boundary": "task"}}
    data = init_state(
      artifact_id="DE-100",
      phase_id="IP-100.PHASE-01",
      config=config,
    )
    assert data["workflow"]["handoff_boundary"] == "task"

  def test_init_validates_on_write(self) -> None:
    """init_state output must be writable (schema-valid)."""
    with TemporaryDirectory() as tmp:
      data = init_state(artifact_id="DE-100", phase_id="IP-100.PHASE-01")
      path = write_state(Path(tmp), data)
      assert path.exists()


class UpdateStateWorkflowTest(unittest.TestCase):
  """update_state_workflow mutations."""

  def test_update_status(self) -> None:
    data = _minimal_state()
    update_state_workflow(data, status="awaiting_handoff")
    assert data["workflow"]["status"] == "awaiting_handoff"

  def test_update_active_role(self) -> None:
    data = _minimal_state()
    update_state_workflow(data, active_role="reviewer")
    assert data["workflow"]["active_role"] == "reviewer"

  def test_update_next_role(self) -> None:
    data = _minimal_state()
    update_state_workflow(data, next_role="reviewer")
    assert data["workflow"]["next_role"] == "reviewer"

  def test_set_claimed_by(self) -> None:
    data = _minimal_state()
    update_state_workflow(data, claimed_by="agent-1")
    assert data["workflow"]["claimed_by"] == "agent-1"

  def test_clear_claimed_by(self) -> None:
    data = _minimal_state()
    data["workflow"]["claimed_by"] = "agent-1"
    update_state_workflow(data, claimed_by=None)
    assert "claimed_by" not in data["workflow"]

  def test_set_previous_state(self) -> None:
    data = _minimal_state()
    update_state_workflow(data, previous_state="implementing")
    assert data["workflow"]["previous_state"] == "implementing"

  def test_clear_previous_state(self) -> None:
    data = _minimal_state()
    data["workflow"]["previous_state"] = "implementing"
    update_state_workflow(data, previous_state=None)
    assert "previous_state" not in data["workflow"]

  def test_ellipsis_sentinel_preserves_existing(self) -> None:
    """Not passing claimed_by should not touch existing value."""
    data = _minimal_state()
    data["workflow"]["claimed_by"] = "agent-1"
    update_state_workflow(data, status="blocked")
    assert data["workflow"]["claimed_by"] == "agent-1"

  def test_updates_timestamp(self) -> None:
    import time  # noqa: PLC0415

    data = _minimal_state()
    old_ts = data["timestamps"]["updated"]
    time.sleep(0.01)  # Ensure timestamp differs
    update_state_workflow(data, status="blocked")
    assert data["timestamps"]["updated"] != old_ts


if __name__ == "__main__":
  unittest.main()
