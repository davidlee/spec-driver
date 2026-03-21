"""Tests for phase complete CLI command (DR-102 §5, §6, §7).

Tests phase completion, auto-handoff emission, bridge block integration.
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
  *,
  phase_frontmatter: bool = False,
) -> Path:
  """Create a minimal delta bundle for testing.

  Args:
    phase_frontmatter: If True, generate phase files with proper frontmatter
      (status: draft) so update_frontmatter_status can operate on them.
  """
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
    if phase_frontmatter:
      content = (
        f"---\nid: {plan_id}.PHASE-{i:02d}\nstatus: draft\nkind: phase\n---\n"
        f"\n# Phase {i:02d}\n\nContent.\n"
      )
    else:
      content = f"# Phase {i:02d}\n\nContent.\n"
    (phases_dir / f"phase-{i:02d}.md").write_text(content)

  return delta_dir


class _PhaseCompleteTestBase(unittest.TestCase):
  """Common setup."""

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


class PhaseCompleteBasicTest(_PhaseCompleteTestBase):
  """Test basic phase complete behaviour."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_marks_phase_complete(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    result = self.runner.invoke(app, ["phase", "complete", "DE-100"])
    assert result.exit_code == 0, result.output
    assert "Phase complete" in result.output

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["phase"]["status"] == "complete"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_auto_handoff_by_default(self, *_mocks) -> None:
    """Default policy emits handoff on phase complete."""
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    result = self.runner.invoke(app, ["phase", "complete", "DE-100"])
    assert result.exit_code == 0, result.output
    assert "handoff emitted" in result.output

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "awaiting_handoff"

    handoff_file = delta_dir / "workflow" / "handoff.current.yaml"
    assert handoff_file.exists()

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_no_handoff_flag(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    result = self.runner.invoke(
      app, ["phase", "complete", "DE-100", "--no-handoff"],
    )
    assert result.exit_code == 0, result.output
    assert "handoff emitted" not in result.output

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    # Still implementing (not awaiting_handoff), phase marked complete
    assert state["workflow"]["status"] == "implementing"
    assert state["phase"]["status"] == "complete"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_to_role_override(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    result = self.runner.invoke(
      app, ["phase", "complete", "DE-100", "--to", "reviewer"],
    )
    assert result.exit_code == 0, result.output
    assert "reviewer" in result.output

    handoff = yaml.safe_load(
      (delta_dir / "workflow" / "handoff.current.yaml").read_text(),
    )
    assert handoff["transition"]["to_role"] == "reviewer"

  def test_fails_when_not_implementing(self) -> None:
    _create_delta_bundle(self.root)
    # Don't start phase — still planned (no state)
    result = self.runner.invoke(app, ["phase", "complete", "DE-100"])
    assert result.exit_code == 1


class PhaseBridgeIntegrationTest(_PhaseCompleteTestBase):
  """Test phase-bridge block integration with phase complete."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_bridge_handoff_ready_true(self, *_mocks) -> None:
    """Phase-bridge with handoff_ready triggers handoff."""
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    # Write phase-bridge block into phase sheet
    phase_file = delta_dir / "phases" / "phase-02.md"
    phase_file.write_text("""# Phase 02

## Workflow

```yaml supekku:workflow.phase-bridge@v1
schema: supekku.workflow.phase-bridge
version: 1
phase: IP-100.PHASE-02
status: complete
handoff_ready: true
review_required: true
```
""")

    result = self.runner.invoke(app, ["phase", "complete", "DE-100"])
    assert result.exit_code == 0, result.output
    assert "reviewer" in result.output  # review_required → reviewer

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_bridge_handoff_ready_false_suppresses(self, *_mocks) -> None:
    """Phase-bridge with handoff_ready: false suppresses auto-handoff."""
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    phase_file = delta_dir / "phases" / "phase-02.md"
    phase_file.write_text("""# Phase 02

## Workflow

```yaml supekku:workflow.phase-bridge@v1
schema: supekku.workflow.phase-bridge
version: 1
phase: IP-100.PHASE-02
status: complete
handoff_ready: false
```
""")

    result = self.runner.invoke(app, ["phase", "complete", "DE-100"])
    assert result.exit_code == 0, result.output
    assert "handoff emitted" not in result.output

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    # No handoff emitted — stays implementing
    assert state["workflow"]["status"] == "implementing"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_idempotent_rerun(self, *_mocks) -> None:
    """Re-running phase complete with already-complete phase still works."""
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    # First complete
    self.runner.invoke(app, ["phase", "complete", "DE-100", "--no-handoff"])

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["phase"]["status"] == "complete"

    # Idempotent second run (still implementing since --no-handoff)
    result = self.runner.invoke(
      app, ["phase", "complete", "DE-100", "--no-handoff"],
    )
    assert result.exit_code == 0, result.output


class PhaseFrontmatterTest(_PhaseCompleteTestBase):
  """Test that phase complete updates phase sheet frontmatter (DE-104)."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_phase_complete_updates_frontmatter_to_completed(self, *_mocks) -> None:
    """Phase complete writes 'completed' to phase sheet frontmatter (DEC-104-08)."""
    delta_dir = _create_delta_bundle(self.root, phase_frontmatter=True)
    self._start_phase()

    # Verify frontmatter starts as draft (phase start changes it to in-progress)
    phase_file = delta_dir / "phases" / "phase-02.md"
    from supekku.scripts.lib.core.spec_utils import load_markdown_file
    fm, _ = load_markdown_file(phase_file)
    assert fm["status"] == "in-progress"

    result = self.runner.invoke(
      app, ["phase", "complete", "DE-100", "--no-handoff"],
    )
    assert result.exit_code == 0, result.output

    fm, _ = load_markdown_file(phase_file)
    assert fm["status"] == "completed"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_phase_complete_tolerates_missing_frontmatter(self, *_mocks) -> None:
    """Phase complete succeeds when phase file has no frontmatter status."""
    delta_dir = _create_delta_bundle(self.root, phase_frontmatter=False)
    self._start_phase()

    result = self.runner.invoke(
      app, ["phase", "complete", "DE-100", "--no-handoff"],
    )
    assert result.exit_code == 0, result.output
    assert "Phase complete" in result.output

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  @patch("supekku.scripts.lib.core.git.get_branch", return_value="main")
  @patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False)
  @patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False)
  def test_state_yaml_still_uses_complete(self, *_mocks) -> None:
    """state.yaml uses control-plane vocabulary ('complete'), not lifecycle."""
    delta_dir = _create_delta_bundle(self.root, phase_frontmatter=True)
    self._start_phase()

    self.runner.invoke(
      app, ["phase", "complete", "DE-100", "--no-handoff"],
    )

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["phase"]["status"] == "complete"


if __name__ == "__main__":
  unittest.main()
