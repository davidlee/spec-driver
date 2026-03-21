"""Tests for handoff I/O (DR-102 §3.2, §5)."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from supekku.scripts.lib.workflow.handoff_io import (
  HandoffNotFoundError,
  HandoffValidationError,
  build_handoff,
  handoff_path,
  read_handoff,
  write_handoff,
)


def _minimal_handoff() -> dict:
  """Return minimal valid handoff dict."""
  return {
    "schema": "supekku.workflow.handoff",
    "version": 1,
    "artifact": {"id": "DE-090", "kind": "delta"},
    "transition": {
      "from_role": "implementer",
      "to_role": "reviewer",
      "status": "pending",
    },
    "phase": {"id": "IP-090.PHASE-01"},
    "required_reading": [".spec-driver/deltas/DE-090/notes.md"],
    "next_activity": {"kind": "review"},
    "timestamps": {"emitted_at": "2026-03-21T10:00:00+00:00"},
  }


class HandoffPathTest(unittest.TestCase):
  def test_default(self) -> None:
    p = handoff_path(Path("/tmp/delta"))
    assert p == Path("/tmp/delta/workflow/handoff.current.yaml")


class WriteHandoffTest(unittest.TestCase):
  def test_write_valid(self) -> None:
    with TemporaryDirectory() as tmp:
      path = write_handoff(Path(tmp), _minimal_handoff())
      assert path.exists()
      loaded = yaml.safe_load(path.read_text())
      assert loaded["transition"]["to_role"] == "reviewer"

  def test_write_rejects_invalid(self) -> None:
    with TemporaryDirectory() as tmp, self.assertRaises(HandoffValidationError):
      write_handoff(Path(tmp), {"schema": "supekku.workflow.handoff"})

  def test_atomic_no_temp_files(self) -> None:
    with TemporaryDirectory() as tmp:
      write_handoff(Path(tmp), _minimal_handoff())
      files = list((Path(tmp) / "workflow").iterdir())
      assert len(files) == 1
      assert files[0].name == "handoff.current.yaml"


class ReadHandoffTest(unittest.TestCase):
  def test_read_valid(self) -> None:
    with TemporaryDirectory() as tmp:
      write_handoff(Path(tmp), _minimal_handoff())
      data = read_handoff(Path(tmp))
      assert data["artifact"]["id"] == "DE-090"

  def test_read_missing_raises(self) -> None:
    with TemporaryDirectory() as tmp, self.assertRaises(HandoffNotFoundError):
      read_handoff(Path(tmp))


class BuildHandoffTest(unittest.TestCase):
  def test_minimal_build(self) -> None:
    data = build_handoff(
      artifact_id="DE-100",
      artifact_kind="delta",
      from_role="implementer",
      to_role="reviewer",
      phase_id="IP-100.PHASE-01",
      required_reading=[".spec-driver/deltas/DE-100/notes.md"],
    )
    assert data["schema"] == "supekku.workflow.handoff"
    assert data["transition"]["status"] == "pending"
    assert data["next_activity"]["kind"] == "implementation"
    assert "timestamps" in data

  def test_build_validates_on_write(self) -> None:
    """Built handoff must be writable."""
    with TemporaryDirectory() as tmp:
      data = build_handoff(
        artifact_id="DE-100",
        artifact_kind="delta",
        from_role="implementer",
        to_role="reviewer",
        phase_id="IP-100.PHASE-01",
        required_reading=["notes.md"],
      )
      path = write_handoff(Path(tmp), data)
      assert path.exists()

  def test_build_with_git_state(self) -> None:
    data = build_handoff(
      artifact_id="DE-100",
      artifact_kind="delta",
      from_role="implementer",
      to_role="reviewer",
      phase_id="IP-100.PHASE-01",
      required_reading=["notes.md"],
      git_head="abc1234",
      git_branch="main",
      has_uncommitted=True,
      has_staged=False,
    )
    assert data["git"]["head"] == "abc1234"
    assert data["git"]["branch"] == "main"
    assert data["git"]["worktree"]["has_uncommitted_changes"] is True

  def test_build_with_verification(self) -> None:
    data = build_handoff(
      artifact_id="DE-100",
      artifact_kind="delta",
      from_role="implementer",
      to_role="reviewer",
      phase_id="IP-100.PHASE-01",
      required_reading=["notes.md"],
      verification_status="pass",
      verification_summary="All tests green",
    )
    assert data["verification"]["status"] == "pass"

  def test_build_with_open_items(self) -> None:
    items = [
      {"id": "OI-001", "kind": "next_step",
       "summary": "Do phase 04", "blocking": False},
    ]
    data = build_handoff(
      artifact_id="DE-100",
      artifact_kind="delta",
      from_role="implementer",
      to_role="reviewer",
      phase_id="IP-100.PHASE-01",
      required_reading=["notes.md"],
      open_items=items,
    )
    assert len(data["open_items"]) == 1

  def test_build_with_boundary(self) -> None:
    data = build_handoff(
      artifact_id="DE-100",
      artifact_kind="delta",
      from_role="implementer",
      to_role="reviewer",
      phase_id="IP-100.PHASE-01",
      required_reading=["notes.md"],
      boundary="phase",
    )
    assert data["transition"]["boundary"] == "phase"

  def test_build_omits_empty_optionals(self) -> None:
    data = build_handoff(
      artifact_id="DE-100",
      artifact_kind="delta",
      from_role="implementer",
      to_role="reviewer",
      phase_id="IP-100.PHASE-01",
      required_reading=["notes.md"],
    )
    assert "git" not in data
    assert "verification" not in data
    assert "open_items" not in data
    assert "design_tensions" not in data

  def test_next_activity_kind_for_reviewer(self) -> None:
    data = build_handoff(
      artifact_id="DE-100",
      artifact_kind="delta",
      from_role="implementer",
      to_role="reviewer",
      phase_id="IP-100.PHASE-01",
      required_reading=["notes.md"],
      next_activity_kind="review",
      next_activity_summary="Assess phase output",
    )
    assert data["next_activity"]["kind"] == "review"
    assert data["next_activity"]["summary"] == "Assess phase output"


if __name__ == "__main__":
  unittest.main()
