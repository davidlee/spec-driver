"""Tests for workflow CLI commands (DR-102 §5).

Tests phase start, workflow status, block/unblock via CliRunner.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

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

  # Delta file
  (delta_dir / f"{delta_id}.md").write_text(
    f"---\nid: {delta_id}\nstatus: in-progress\nkind: delta\n---\n# {delta_id}\n",
  )

  # Plan file
  (delta_dir / f"{plan_id}.md").write_text(
    f"---\nid: {plan_id}\nstatus: draft\nkind: plan\n---\n# {plan_id}\n",
  )

  # Notes file
  (delta_dir / "notes.md").write_text("# Notes\n")

  # Phase files
  phases_dir = delta_dir / "phases"
  phases_dir.mkdir(exist_ok=True)
  for i in range(1, phases + 1):
    phase_id = f"{plan_id}.PHASE-{i:02d}"
    (phases_dir / f"phase-{i:02d}.md").write_text(
      f"---\nid: {phase_id}\nstatus: draft\nkind: phase\n---\n# Phase {i:02d}\n",
    )

  return delta_dir


class PhaseStartTest(unittest.TestCase):
  """Test `spec-driver phase start`."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self._cwd = Path.cwd()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    # Minimal workflow.toml so config loads
    sd = self.root / SPEC_DRIVER_DIR
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "workflow.toml").write_text('ceremony = "pioneer"\n')
    os.chdir(self.root)

  def tearDown(self) -> None:
    os.chdir(self._cwd)
    self.tmpdir.cleanup()

  def test_creates_state_yaml(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    result = self.runner.invoke(app, ["phase", "start", "DE-100"])
    assert result.exit_code == 0, result.output
    assert "Phase started" in result.output

    state_file = delta_dir / "workflow" / "state.yaml"
    assert state_file.exists()
    data = yaml.safe_load(state_file.read_text())
    assert data["workflow"]["status"] == "implementing"
    assert data["workflow"]["active_role"] == "implementer"
    assert data["artifact"]["id"] == "DE-100"

  def test_auto_discovers_latest_phase(self) -> None:
    delta_dir = _create_delta_bundle(self.root, phases=3)
    result = self.runner.invoke(app, ["phase", "start", "DE-100"])
    assert result.exit_code == 0, result.output

    data = yaml.safe_load((delta_dir / "workflow" / "state.yaml").read_text())
    assert data["phase"]["id"] == "IP-100.PHASE-03"

  def test_explicit_phase_override(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    result = self.runner.invoke(
      app, ["phase", "start", "DE-100", "--phase", "IP-100.PHASE-01"],
    )
    assert result.exit_code == 0, result.output

    data = yaml.safe_load((delta_dir / "workflow" / "state.yaml").read_text())
    assert data["phase"]["id"] == "IP-100.PHASE-01"

  def test_idempotent_when_already_implementing(self) -> None:
    _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    result = self.runner.invoke(app, ["phase", "start", "DE-100"])
    assert result.exit_code == 0
    assert "Already implementing" in result.output

  def test_unknown_delta_fails(self) -> None:
    result = self.runner.invoke(app, ["phase", "start", "DE-999"])
    assert result.exit_code == 1

  def test_no_phases_dir_with_explicit_phase(self) -> None:
    """phase start works with --phase even if phases/ is empty."""
    delta_dir = _create_delta_bundle(self.root, phases=0)
    # Remove phases dir
    phases_dir = delta_dir / "phases"
    if phases_dir.exists():
      import shutil
      shutil.rmtree(phases_dir)
    result = self.runner.invoke(
      app, ["phase", "start", "DE-100", "--phase", "IP-100.PHASE-01"],
    )
    assert result.exit_code == 0, result.output

  def test_records_plan_info(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    data = yaml.safe_load((delta_dir / "workflow" / "state.yaml").read_text())
    assert data["plan"]["id"] == "IP-100"

  def test_updates_phase_frontmatter_to_in_progress(self) -> None:
    """phase start writes 'in-progress' to phase sheet frontmatter (DE-104)."""
    from supekku.scripts.lib.core.spec_utils import load_markdown_file

    delta_dir = _create_delta_bundle(self.root)
    phase_file = delta_dir / "phases" / "phase-02.md"

    # Verify starts as draft
    fm, _ = load_markdown_file(phase_file)
    assert fm["status"] == "draft"

    result = self.runner.invoke(app, ["phase", "start", "DE-100"])
    assert result.exit_code == 0, result.output

    fm, _ = load_markdown_file(phase_file)
    assert fm["status"] == "in-progress"

  def test_frontmatter_tolerates_no_status_field(self) -> None:
    """phase start succeeds when phase file lacks frontmatter status."""
    delta_dir = _create_delta_bundle(self.root, phases=0)
    phases_dir = delta_dir / "phases"
    phases_dir.mkdir(exist_ok=True)
    # Phase file without frontmatter
    (phases_dir / "phase-01.md").write_text("# Phase 01\n\nContent.\n")

    result = self.runner.invoke(app, ["phase", "start", "DE-100"])
    assert result.exit_code == 0, result.output


class WorkflowStatusTest(unittest.TestCase):
  """Test `spec-driver workflow status`."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self._cwd = Path.cwd()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    sd = self.root / SPEC_DRIVER_DIR
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "workflow.toml").write_text('ceremony = "pioneer"\n')
    os.chdir(self.root)

  def tearDown(self) -> None:
    os.chdir(self._cwd)
    self.tmpdir.cleanup()

  def test_displays_status(self) -> None:
    _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    result = self.runner.invoke(app, ["workflow", "status", "DE-100"])
    assert result.exit_code == 0, result.output
    assert "implementing" in result.output
    assert "DE-100" in result.output
    assert "implementer" in result.output

  def test_no_state_reports_gracefully(self) -> None:
    _create_delta_bundle(self.root)
    result = self.runner.invoke(app, ["workflow", "status", "DE-100"])
    assert result.exit_code == 0
    assert "not found" in result.output

  def test_displays_phase_info(self) -> None:
    _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    result = self.runner.invoke(app, ["workflow", "status", "DE-100"])
    assert "IP-100.PHASE-02" in result.output


class BlockUnblockTest(unittest.TestCase):
  """Test `spec-driver block` / `spec-driver unblock`."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self._cwd = Path.cwd()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    sd = self.root / SPEC_DRIVER_DIR
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "workflow.toml").write_text('ceremony = "pioneer"\n')
    os.chdir(self.root)

  def tearDown(self) -> None:
    os.chdir(self._cwd)
    self.tmpdir.cleanup()

  def test_block_transitions_to_blocked(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    result = self.runner.invoke(app, ["block", "DE-100"])
    assert result.exit_code == 0, result.output
    assert "Blocked" in result.output

    data = yaml.safe_load((delta_dir / "workflow" / "state.yaml").read_text())
    assert data["workflow"]["status"] == "blocked"
    assert data["workflow"]["previous_state"] == "implementing"

  def test_block_with_reason(self) -> None:
    _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    result = self.runner.invoke(
      app, ["block", "DE-100", "--reason", "waiting on review"],
    )
    assert result.exit_code == 0
    assert "waiting on review" in result.output

  def test_unblock_restores_previous_state(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    self.runner.invoke(app, ["block", "DE-100"])
    result = self.runner.invoke(app, ["unblock", "DE-100"])
    assert result.exit_code == 0, result.output
    assert "Unblocked" in result.output
    assert "implementing" in result.output

    data = yaml.safe_load((delta_dir / "workflow" / "state.yaml").read_text())
    assert data["workflow"]["status"] == "implementing"
    assert "previous_state" not in data["workflow"]

  def test_block_already_blocked_fails(self) -> None:
    _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    self.runner.invoke(app, ["block", "DE-100"])
    result = self.runner.invoke(app, ["block", "DE-100"])
    assert result.exit_code == 1

  def test_unblock_not_blocked_fails(self) -> None:
    _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    result = self.runner.invoke(app, ["unblock", "DE-100"])
    assert result.exit_code == 1

  def test_block_without_state_fails(self) -> None:
    _create_delta_bundle(self.root)
    result = self.runner.invoke(app, ["block", "DE-100"])
    assert result.exit_code == 1

  def test_workflow_status_shows_blocked(self) -> None:
    _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    self.runner.invoke(app, ["block", "DE-100"])
    result = self.runner.invoke(app, ["workflow", "status", "DE-100"])
    assert result.exit_code == 0
    assert "blocked" in result.output
    assert "previous_state" in result.output


class TopLevelBlockTest(unittest.TestCase):
  """Verify block/unblock work as top-level commands."""

  def setUp(self) -> None:
    self.runner = CliRunner()
    self._cwd = Path.cwd()
    self.tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    sd = self.root / SPEC_DRIVER_DIR
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "workflow.toml").write_text('ceremony = "pioneer"\n')
    os.chdir(self.root)

  def tearDown(self) -> None:
    os.chdir(self._cwd)
    self.tmpdir.cleanup()

  def test_block_is_top_level(self) -> None:
    """block is accessible as `spec-driver block`, not `spec-driver workflow block`."""
    _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    # Top-level
    result = self.runner.invoke(app, ["block", "DE-100"])
    assert result.exit_code == 0, result.output

  def test_unblock_is_top_level(self) -> None:
    _create_delta_bundle(self.root)
    self.runner.invoke(app, ["phase", "start", "DE-100"])
    self.runner.invoke(app, ["block", "DE-100"])
    result = self.runner.invoke(app, ["unblock", "DE-100"])
    assert result.exit_code == 0, result.output


if __name__ == "__main__":
  unittest.main()
