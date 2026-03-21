"""Tests for review CLI commands (DR-102 §3.3, §3.4, §5, §8).

Tests review prime, review complete, and review teardown.
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


class _ReviewTestBase(unittest.TestCase):
  """Common setup for review tests."""

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

  def _create_handoff_and_accept_as_reviewer(
    self, delta_id: str = "DE-100",
  ) -> None:
    """Create handoff to reviewer and accept it."""
    with (
      patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40),
      patch("supekku.scripts.lib.core.git.get_branch", return_value="main"),
      patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False),
      patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False),
    ):
      self.runner.invoke(
        app, ["create", "handoff", delta_id, "--to", "reviewer"],
      )
    self.runner.invoke(
      app, ["accept", "handoff", delta_id, "--identity", "reviewer-1"],
    )


class ReviewPrimeTest(_ReviewTestBase):
  """Test `spec-driver review prime`."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_creates_review_index(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    result = self.runner.invoke(app, ["review", "prime", "DE-100"])
    assert result.exit_code == 0, result.output
    assert "Review primed" in result.output

    idx_file = delta_dir / "workflow" / "review-index.yaml"
    assert idx_file.exists()
    data = yaml.safe_load(idx_file.read_text())
    assert data["schema"] == "supekku.workflow.review-index"
    assert data["review"]["bootstrap_status"] == "warm"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_creates_bootstrap_markdown(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    self.runner.invoke(app, ["review", "prime", "DE-100"])

    bp = delta_dir / "workflow" / "review-bootstrap.md"
    assert bp.exists()
    content = bp.read_text()
    assert "Review Bootstrap" in content
    assert "DE-100" in content

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_domain_map_includes_delta_docs(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    self.runner.invoke(app, ["review", "prime", "DE-100"])

    data = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    areas = [e["area"] for e in data["domain_map"]]
    assert "delta_docs" in areas

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_domain_map_includes_phase_sheets(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    self.runner.invoke(app, ["review", "prime", "DE-100"])

    data = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    areas = [e["area"] for e in data["domain_map"]]
    assert "phase_sheets" in areas

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="b" * 40)
  def test_rerun_updates_cache_key(self, *_mocks) -> None:
    """Re-running review prime updates the cache key."""
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    # First prime
    with patch(
      "supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40,
    ):
      self.runner.invoke(app, ["review", "prime", "DE-100"])

    data1 = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    assert data1["staleness"]["cache_key"]["head"] == "a" * 8

    # Second prime with new HEAD
    with patch(
      "supekku.scripts.lib.core.git.get_head_sha", return_value="b" * 40,
    ):
      self.runner.invoke(app, ["review", "prime", "DE-100"])

    data2 = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    assert data2["staleness"]["cache_key"]["head"] == "b" * 8

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_records_source_handoff(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    self.runner.invoke(app, ["review", "prime", "DE-100"])

    data = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    assert data["review"].get("source_handoff") == "workflow/handoff.current.yaml"

  def test_fails_without_state(self) -> None:
    _create_delta_bundle(self.root)
    result = self.runner.invoke(app, ["review", "prime", "DE-100"])
    assert result.exit_code == 1


class ReviewCompleteTest(_ReviewTestBase):
  """Test `spec-driver review complete`."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_transitions_to_changes_requested(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    result = self.runner.invoke(
      app, ["review", "complete", "DE-100", "--status", "changes_requested"],
    )
    assert result.exit_code == 0, result.output
    assert "changes_requested" in result.output

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "changes_requested"

    findings_file = delta_dir / "workflow" / "review-findings.yaml"
    assert findings_file.exists()
    findings = yaml.safe_load(findings_file.read_text())
    assert findings["review"]["round"] == 1
    assert findings["review"]["status"] == "changes_requested"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_transitions_to_approved(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    result = self.runner.invoke(
      app, ["review", "complete", "DE-100", "--status", "approved"],
    )
    assert result.exit_code == 0, result.output
    assert "approved" in result.output

    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "approved"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_increments_round_number(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    # Round 1
    self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "changes_requested"],
    )

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    assert findings["review"]["round"] == 1

    # Cycle back: create handoff → accept → review complete again
    with (
      patch("supekku.scripts.lib.core.git.get_head_sha", return_value="b" * 40),
      patch("supekku.scripts.lib.core.git.get_branch", return_value="main"),
      patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False),
      patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False),
    ):
      self.runner.invoke(
        app, ["create", "handoff", "DE-100", "--to", "reviewer"],
      )
    self.runner.invoke(
      app, ["accept", "handoff", "DE-100", "--identity", "reviewer-2"],
    )

    # Round 2 — use changes_requested to avoid auto-teardown deleting findings
    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "changes_requested"],
    )
    assert result.exit_code == 0, result.output

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    assert findings["review"]["round"] == 2

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_records_reviewer_role(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "changes_requested"],
    )

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    assert findings["review"]["reviewer_role"] == "reviewer"

  def test_rejects_invalid_status(self) -> None:
    _create_delta_bundle(self.root)
    self._start_phase()
    result = self.runner.invoke(
      app, ["review", "complete", "DE-100", "--status", "invalid"],
    )
    assert result.exit_code == 1

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_fails_when_not_reviewing(self, *_mocks) -> None:
    """Cannot complete review when not in reviewing state."""
    _create_delta_bundle(self.root)
    self._start_phase()
    # Still implementing, not reviewing
    result = self.runner.invoke(
      app, ["review", "complete", "DE-100", "--status", "approved"],
    )
    assert result.exit_code == 1

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_with_summary(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    # Use changes_requested to avoid auto-teardown deleting findings
    result = self.runner.invoke(
      app,
      [
        "review", "complete", "DE-100",
        "--status", "changes_requested",
        "--summary", "Needs revision",
      ],
    )
    assert result.exit_code == 0, result.output

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    assert findings["history"][0]["summary"] == "Needs revision"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_auto_teardown_on_approved(self, *_mocks) -> None:
    """Default policy tears down reviewer state on approved."""
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    # Create reviewer state first
    self.runner.invoke(app, ["review", "prime", "DE-100"])
    assert (delta_dir / "workflow" / "review-index.yaml").exists()

    self.runner.invoke(
      app, ["review", "complete", "DE-100", "--status", "approved"],
    )

    # Teardown should have deleted review-index and bootstrap
    assert not (delta_dir / "workflow" / "review-index.yaml").exists()
    assert not (delta_dir / "workflow" / "review-bootstrap.md").exists()


class ReviewTeardownTest(_ReviewTestBase):
  """Test `spec-driver review teardown`."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_deletes_reviewer_state(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    # Create reviewer state
    self.runner.invoke(app, ["review", "prime", "DE-100"])
    assert (delta_dir / "workflow" / "review-index.yaml").exists()
    assert (delta_dir / "workflow" / "review-bootstrap.md").exists()

    result = self.runner.invoke(app, ["review", "teardown", "DE-100"])
    assert result.exit_code == 0, result.output
    assert "deleted" in result.output.lower()

    assert not (delta_dir / "workflow" / "review-index.yaml").exists()
    assert not (delta_dir / "workflow" / "review-bootstrap.md").exists()

  def test_teardown_with_no_state(self) -> None:
    _create_delta_bundle(self.root)
    self._start_phase()

    result = self.runner.invoke(app, ["review", "teardown", "DE-100"])
    assert result.exit_code == 0
    assert "no reviewer state" in result.output.lower()

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_deletes_findings_too(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    # Create both review-index and findings
    self.runner.invoke(app, ["review", "prime", "DE-100"])
    self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "changes_requested"],
    )
    assert (delta_dir / "workflow" / "review-findings.yaml").exists()

    self.runner.invoke(app, ["review", "teardown", "DE-100"])

    assert not (delta_dir / "workflow" / "review-index.yaml").exists()
    assert not (delta_dir / "workflow" / "review-findings.yaml").exists()
    assert not (delta_dir / "workflow" / "review-bootstrap.md").exists()

  def test_teardown_without_delta_fails(self) -> None:
    result = self.runner.invoke(app, ["review", "teardown", "DE-999"])
    assert result.exit_code == 1


class WriteOrderTest(_ReviewTestBase):
  """Test write ordering per DR-102 §5."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_review_prime_creates_both_files(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    self.runner.invoke(app, ["review", "prime", "DE-100"])

    assert (delta_dir / "workflow" / "review-index.yaml").exists()
    assert (delta_dir / "workflow" / "review-bootstrap.md").exists()

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_review_complete_creates_findings_and_updates_state(
    self, *_mocks,
  ) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    self.runner.invoke(
      app, ["review", "complete", "DE-100", "--status", "changes_requested"],
    )

    assert (delta_dir / "workflow" / "review-findings.yaml").exists()
    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "changes_requested"


if __name__ == "__main__":
  unittest.main()
