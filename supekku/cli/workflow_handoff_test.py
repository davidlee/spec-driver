"""Tests for create handoff / accept handoff CLI commands (DR-102 §4/§5).

Tests handoff creation, payload assembly, claim guard,
write ordering, and re-run safety.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from typer.testing import CliRunner

from supekku.cli.main import app
from supekku.scripts.lib.core.paths import DELTAS_SUBDIR, SPEC_DRIVER_DIR


def _create_delta_bundle(
  root: Path,
  delta_id: str = "DE-100",
  slug: str = "test-delta",
  plan_id: str = "IP-100",
  phases: int = 2,
) -> Path:
  """Create a minimal delta bundle for testing."""
  bundle_name = f"{delta_id}-{slug}"
  delta_dir = root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / bundle_name
  delta_dir.mkdir(parents=True, exist_ok=True)

  (delta_dir / f"{delta_id}.md").write_text(
    f"---\nid: {delta_id}\nstatus: in-progress\nkind: delta\n---\n",
  )
  (delta_dir / f"{plan_id}.md").write_text(
    f"---\nid: {plan_id}\nstatus: draft\nkind: plan\n---\n",
  )
  (delta_dir / "notes.md").write_text("# Notes\n")

  phases_dir = delta_dir / "phases"
  phases_dir.mkdir(exist_ok=True)
  for i in range(1, phases + 1):
    phase_id = f"{plan_id}.PHASE-{i:02d}"
    (phases_dir / f"phase-{i:02d}.md").write_text(
      f"---\nid: {phase_id}\nstatus: draft\nkind: phase\n---\n",
    )

  return delta_dir


class _HandoffTestBase(unittest.TestCase):
  """Common setup for handoff tests."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self._cwd = Path.cwd()
    self.tmpdir = tempfile.TemporaryDirectory()
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    sd = self.root / SPEC_DRIVER_DIR
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "workflow.toml").write_text('ceremony = "pioneer"\n')
    os.chdir(self.root)

  def tearDown(self) -> None:
    os.chdir(self._cwd)
    self.tmpdir.cleanup()

  def _start_phase(self, delta_id: str = "DE-100") -> None:
    result = self.runner.invoke(app, ["phase", "start", delta_id])
    assert result.exit_code == 0, result.output


class CreateHandoffTest(_HandoffTestBase):
  """Test `spec-driver create handoff`."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_creates_handoff_yaml(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    result = self.runner.invoke(
      app, ["create", "handoff", "DE-100", "--to", "reviewer"],
    )
    assert result.exit_code == 0, result.output
    assert "Handoff created" in result.output
    assert "reviewer" in result.output

    handoff_file = delta_dir / "workflow" / "handoff.current.yaml"
    assert handoff_file.exists()
    data = yaml.safe_load(handoff_file.read_text())
    assert data["transition"]["to_role"] == "reviewer"
    assert data["transition"]["status"] == "pending"
    assert data["transition"]["from_role"] == "implementer"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="b" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_transitions_to_awaiting_handoff(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    self.runner.invoke(
      app, ["create", "handoff", "DE-100", "--to", "reviewer"],
    )

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "awaiting_handoff"
    assert state["workflow"].get("next_role") == "reviewer"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="c" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_clears_claimed_by(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    # Manually set claimed_by
    state_file = delta_dir / "workflow" / "state.yaml"
    state = yaml.safe_load(state_file.read_text())
    state["workflow"]["claimed_by"] = "old-agent"
    state_file.write_text(yaml.dump(state, sort_keys=False))

    self.runner.invoke(
      app, ["create", "handoff", "DE-100", "--to", "implementer"],
    )

    state = yaml.safe_load(state_file.read_text())
    assert "claimed_by" not in state["workflow"]

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="d" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="feat-x")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=True)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=True)
  def test_captures_git_state(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    self.runner.invoke(
      app, ["create", "handoff", "DE-100", "--to", "reviewer"],
    )

    data = yaml.safe_load(
      (delta_dir / "workflow" / "handoff.current.yaml").read_text(),
    )
    assert data["git"]["head"] == "d" * 8  # short_sha
    assert data["git"]["branch"] == "feat-x"
    assert data["git"]["worktree"]["has_uncommitted_changes"] is True
    assert data["git"]["worktree"]["has_staged_changes"] is True

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="e" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_assembles_required_reading(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    self.runner.invoke(
      app, ["create", "handoff", "DE-100", "--to", "reviewer"],
    )

    data = yaml.safe_load(
      (delta_dir / "workflow" / "handoff.current.yaml").read_text(),
    )
    rr = data["required_reading"]
    assert len(rr) >= 3  # DE, IP, phase, notes
    assert any("DE-100" in r for r in rr)
    assert any("IP-100" in r for r in rr)

  def test_fails_from_planned_state(self) -> None:
    """Cannot create handoff before phase start."""
    _create_delta_bundle(self.root)
    result = self.runner.invoke(
      app, ["create", "handoff", "DE-100", "--to", "reviewer"],
    )
    assert result.exit_code == 1

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="f" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_rerun_is_idempotent(self, *_mocks) -> None:
    """Re-running create handoff overwrites cleanly."""
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    # First handoff to implementer
    self.runner.invoke(
      app, ["create", "handoff", "DE-100", "--to", "implementer"],
    )
    # Accept it — goes back to implementing (non-reviewer)
    self.runner.invoke(
      app,
      ["accept", "handoff", "DE-100", "--identity", "agent-1"],
    )
    # Second handoff (from implementing again)
    result = self.runner.invoke(
      app, ["create", "handoff", "DE-100", "--to", "architect"],
    )
    assert result.exit_code == 0, result.output

    data = yaml.safe_load(
      (delta_dir / "workflow" / "handoff.current.yaml").read_text(),
    )
    assert data["transition"]["to_role"] == "architect"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="0" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_infers_review_activity_for_reviewer(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    self.runner.invoke(
      app, ["create", "handoff", "DE-100", "--to", "reviewer"],
    )

    data = yaml.safe_load(
      (delta_dir / "workflow" / "handoff.current.yaml").read_text(),
    )
    assert data["next_activity"]["kind"] == "review"


class AcceptHandoffTest(_HandoffTestBase):
  """Test `spec-driver accept handoff`."""

  def _create_handoff(
    self,
    to_role: str = "reviewer",
    delta_id: str = "DE-100",
  ) -> None:
    with (
      patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40),
      patch("supekku.scripts.lib.core.git.get_branch", return_value="main"),
      patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False),
      patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False),
    ):
      self.runner.invoke(
        app,
        ["create", "handoff", delta_id, "--to", to_role],
      )

  def test_accept_transitions_to_reviewing(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff(to_role="reviewer")

    result = self.runner.invoke(
      app,
      ["accept", "handoff", "DE-100", "--identity", "reviewer-1"],
    )
    assert result.exit_code == 0, result.output
    assert "accepted" in result.output.lower()

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "reviewing"
    assert state["workflow"]["active_role"] == "reviewer"
    assert state["workflow"]["claimed_by"] == "reviewer-1"

  def test_accept_transitions_to_implementing(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff(to_role="implementer")

    result = self.runner.invoke(
      app,
      ["accept", "handoff", "DE-100", "--identity", "agent-2"],
    )
    assert result.exit_code == 0, result.output

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "implementing"
    assert state["workflow"]["active_role"] == "implementer"

  def test_claim_guard_rejects_different_identity(self) -> None:
    _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff()

    # First claim
    self.runner.invoke(
      app,
      ["accept", "handoff", "DE-100", "--identity", "agent-1"],
    )
    # Re-create handoff to get back to awaiting
    self._create_handoff()

    # Manually set claimed_by to simulate prior claim
    delta_dir = (
      self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / "DE-100-test-delta"
    )
    state_file = delta_dir / "workflow" / "state.yaml"
    state = yaml.safe_load(state_file.read_text())
    state["workflow"]["claimed_by"] = "agent-1"
    state_file.write_text(yaml.dump(state, sort_keys=False))

    result = self.runner.invoke(
      app,
      ["accept", "handoff", "DE-100", "--identity", "agent-2"],
    )
    assert result.exit_code == 1
    assert "agent-1" in result.output

  def test_claim_guard_idempotent_same_identity(self) -> None:
    _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff()

    # First accept
    self.runner.invoke(
      app,
      ["accept", "handoff", "DE-100", "--identity", "agent-1"],
    )

    # Re-create handoff
    self._create_handoff()

    # Accept again with same identity
    result = self.runner.invoke(
      app,
      ["accept", "handoff", "DE-100", "--identity", "agent-1"],
    )
    assert result.exit_code == 0, result.output

  def test_accept_without_handoff_fails(self) -> None:
    _create_delta_bundle(self.root)
    self._start_phase()

    result = self.runner.invoke(
      app,
      ["accept", "handoff", "DE-100", "--identity", "agent-1"],
    )
    assert result.exit_code == 1

  def test_accept_defaults_identity_to_user(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff()

    with patch.dict(os.environ, {"USER": "test-user"}):
      result = self.runner.invoke(
        app, ["accept", "handoff", "DE-100"],
      )
    assert result.exit_code == 0, result.output

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["claimed_by"] == "test-user"

  def test_accept_not_awaiting_fails(self) -> None:
    """Cannot accept handoff when not in awaiting_handoff state."""
    _create_delta_bundle(self.root)
    self._start_phase()
    # No handoff created, still implementing

    # Manually create handoff file without transitioning state
    delta_dir = (
      self.root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / "DE-100-test-delta"
    )
    wf_dir = delta_dir / "workflow"
    handoff = {
      "schema": "supekku.workflow.handoff",
      "version": 1,
      "artifact": {"id": "DE-100", "kind": "delta"},
      "transition": {
        "from_role": "implementer",
        "to_role": "reviewer",
        "status": "pending",
      },
      "phase": {"id": "IP-100.PHASE-02"},
      "required_reading": ["notes.md"],
      "next_activity": {"kind": "review"},
      "timestamps": {"emitted_at": "2026-03-21T10:00:00+00:00"},
    }
    (wf_dir / "handoff.current.yaml").write_text(
      yaml.dump(handoff, sort_keys=False),
    )

    result = self.runner.invoke(
      app,
      ["accept", "handoff", "DE-100", "--identity", "agent-1"],
    )
    assert result.exit_code == 1
    assert "not awaiting" in result.output.lower()


class WriteOrderTest(_HandoffTestBase):
  """Test write ordering per DR-102 §5."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_handoff_written_before_state(self, *_mocks) -> None:
    """handoff.current.yaml must be written before state.yaml."""
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    # Get timestamps before
    self.runner.invoke(
      app, ["create", "handoff", "DE-100", "--to", "reviewer"],
    )

    # Both files exist
    handoff_file = delta_dir / "workflow" / "handoff.current.yaml"
    state_file = delta_dir / "workflow" / "state.yaml"
    assert handoff_file.exists()
    assert state_file.exists()

    # State reflects the transition
    state = yaml.safe_load(state_file.read_text())
    assert state["workflow"]["status"] == "awaiting_handoff"


if __name__ == "__main__":
  unittest.main()
