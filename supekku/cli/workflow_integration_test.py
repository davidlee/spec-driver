"""End-to-end integration tests for workflow orchestration (DR-102 §12).

Verifies the full workflow cycle and regression safety.
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
  delta_id: str = "DE-200",
  slug: str = "integration-test",
  plan_id: str = "IP-200",
) -> Path:
  """Create a delta bundle for integration testing."""
  bundle_name = f"{delta_id}-{slug}"
  delta_dir = root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / bundle_name
  delta_dir.mkdir(parents=True, exist_ok=True)

  (delta_dir / f"{delta_id}.md").write_text(
    f"---\nid: {delta_id}\nstatus: in-progress\nkind: delta\n---\n# {delta_id}\n",
  )
  (delta_dir / f"{plan_id}.md").write_text(
    f"---\nid: {plan_id}\nstatus: draft\nkind: plan\n---\n",
  )
  (delta_dir / "notes.md").write_text("# Notes\n")

  phases_dir = delta_dir / "phases"
  phases_dir.mkdir(exist_ok=True)
  for i in range(1, 4):
    (phases_dir / f"phase-{i:02d}.md").write_text(
      f"# Phase {i:02d}\n\nContent.\n",
    )

  return delta_dir


class _IntegrationTestBase(unittest.TestCase):
  """Common setup for integration tests."""

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

    # Default git mocks
    self._git_patches = [
      patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40),
      patch("supekku.scripts.lib.core.git.get_branch", return_value="main"),
      patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False),
      patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False),
      patch("supekku.scripts.lib.core.git.get_changed_files", return_value=[]),
    ]
    for p in self._git_patches:
      p.start()

  def tearDown(self) -> None:
    for p in self._git_patches:
      p.stop()
    os.chdir(self._cwd)
    self.tmpdir.cleanup()

  def _run(self, *args: str) -> str:
    result = self.runner.invoke(app, list(args))
    assert result.exit_code == 0, f"Command failed: {args}\n{result.output}"
    return result.output


class FullWorkflowCycleTest(_IntegrationTestBase):
  """VA-103-001: Full workflow cycle per DR-102 §12.

  Cycle: start → implement → handoff → review → changes_requested →
  handoff → review → approve.
  """

  def test_full_cycle(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    d = "DE-200"

    # 1. Phase start: planned → implementing
    out = self._run("phase", "start", d)
    assert "implementing" in out
    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "implementing"

    # 2. Workflow status readable
    out = self._run("workflow", "status", d)
    assert "implementing" in out

    # 3. Create handoff to reviewer
    out = self._run("create", "handoff", d, "--to", "reviewer")
    assert "awaiting_handoff" in out
    handoff = yaml.safe_load(
      (delta_dir / "workflow" / "handoff.current.yaml").read_text(),
    )
    assert handoff["transition"]["to_role"] == "reviewer"

    # 4. Accept handoff as reviewer
    out = self._run("accept", "handoff", d, "--identity", "reviewer-1")
    assert "reviewing" in out.lower() or "accepted" in out.lower()
    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "reviewing"

    # 5. Review prime — build bootstrap cache
    out = self._run("review", "prime", d)
    assert "primed" in out.lower()
    assert (delta_dir / "workflow" / "review-index.yaml").exists()
    assert (delta_dir / "workflow" / "review-bootstrap.md").exists()

    # 6. Review complete — changes_requested (round 1)
    out = self._run(
      "review",
      "complete",
      d,
      "--status",
      "changes_requested",
      "--summary",
      "Fix schema validation",
    )
    assert "changes_requested" in out
    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    assert findings["review"]["current_round"] == 1
    assert findings["rounds"][0]["status"] == "changes_requested"

    # 7. Handoff back to implementer
    out = self._run("create", "handoff", d, "--to", "implementer")
    assert "awaiting_handoff" in out

    # 8. Accept as implementer
    out = self._run("accept", "handoff", d, "--identity", "impl-2")
    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "implementing"

    # 9. Second handoff to reviewer (round 2)
    out = self._run("create", "handoff", d, "--to", "reviewer")
    assert "awaiting_handoff" in out

    # 10. Accept as reviewer again
    out = self._run("accept", "handoff", d, "--identity", "reviewer-2")
    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "reviewing"

    # 11. Review prime — cache should be reusable (same HEAD)
    out = self._run("review", "prime", d)
    idx = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    assert idx["review"]["bootstrap_status"] == "warm"

    # 12. Review complete — approved (round 2)
    out = self._run(
      "review",
      "complete",
      d,
      "--status",
      "approved",
    )
    assert "approved" in out
    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "approved"

    # 13. Auto-teardown on approved — reviewer state deleted
    assert not (delta_dir / "workflow" / "review-index.yaml").exists()
    assert not (delta_dir / "workflow" / "review-bootstrap.md").exists()


class PhaseCompleteCycleTest(_IntegrationTestBase):
  """Test phase complete with auto-handoff in a full cycle."""

  def test_phase_complete_auto_handoff(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    d = "DE-200"

    self._run("phase", "start", d)
    out = self._run("phase", "complete", d, "--to", "reviewer")
    assert "handoff emitted" in out
    assert "reviewer" in out

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "awaiting_handoff"
    assert state["phase"]["status"] == "complete"


class BlockUnblockCycleTest(_IntegrationTestBase):
  """Test block/unblock in a workflow cycle."""

  def test_block_and_unblock(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    d = "DE-200"

    self._run("phase", "start", d)

    # Block
    out = self._run("block", d, "--reason", "waiting for dependency")
    assert "Blocked" in out

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "blocked"
    assert state["workflow"]["previous_state"] == "implementing"

    # Unblock
    out = self._run("unblock", d)
    assert "Unblocked" in out

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "implementing"


class ExistingDeltasRegressionTest(_IntegrationTestBase):
  """VA-103-002: Existing deltas without workflow/ continue to work."""

  def test_status_without_workflow_dir(self) -> None:
    """workflow status for a delta without workflow/ shows no state."""
    _create_delta_bundle(self.root)

    result = self.runner.invoke(app, ["workflow", "status", "DE-200"])
    assert result.exit_code == 0
    assert "not found" in result.output.lower()

  def test_delta_files_untouched(self) -> None:
    """Starting workflow doesn't modify existing delta files."""
    delta_dir = _create_delta_bundle(self.root)

    # Record original contents
    de_content = (delta_dir / "DE-200.md").read_text()
    ip_content = (delta_dir / "IP-200.md").read_text()
    notes_content = (delta_dir / "notes.md").read_text()
    phase_content = (delta_dir / "phases" / "phase-01.md").read_text()

    # Run workflow commands
    self._run("phase", "start", "DE-200")
    self._run("phase", "complete", "DE-200", "--no-handoff")

    # Verify originals unchanged
    assert (delta_dir / "DE-200.md").read_text() == de_content
    assert (delta_dir / "IP-200.md").read_text() == ip_content
    assert (delta_dir / "notes.md").read_text() == notes_content
    assert (delta_dir / "phases" / "phase-01.md").read_text() == phase_content


class ClaimGuardCycleTest(_IntegrationTestBase):
  """Test claim guard in realistic scenarios."""

  def test_claim_guard_prevents_double_accept(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    d = "DE-200"

    self._run("phase", "start", d)
    self._run("create", "handoff", d, "--to", "reviewer")
    self._run("accept", "handoff", d, "--identity", "agent-A")

    # Complete review to cycle back, then create new handoff
    self._run("review", "complete", d, "--status", "changes_requested")
    self._run("create", "handoff", d, "--to", "reviewer")

    # Manually set claimed_by to simulate prior claim
    state_file = delta_dir / "workflow" / "state.yaml"
    state = yaml.safe_load(state_file.read_text())
    state["workflow"]["claimed_by"] = "agent-A"
    state_file.write_text(yaml.dump(state, sort_keys=False))

    # Different identity should fail
    result = self.runner.invoke(
      app,
      ["accept", "handoff", d, "--identity", "agent-B"],
    )
    assert result.exit_code == 1
    assert "agent-A" in result.output


if __name__ == "__main__":
  unittest.main()
