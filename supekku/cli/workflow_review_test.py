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
    from supekku.scripts.lib.core.version import get_package_version

    ver = get_package_version()
    (sd / "workflow.toml").write_text(
      f'ceremony = "pioneer"\nspec_driver_installed_version = "{ver}"\n',
    )
    os.chdir(self.root)

  def tearDown(self) -> None:
    os.chdir(self._cwd)
    self.tmpdir.cleanup()

  def _start_phase(self, delta_id: str = "DE-100") -> None:
    result = self.runner.invoke(app, ["phase", "start", delta_id])
    assert result.exit_code == 0, result.output

  def _create_handoff_and_accept_as_reviewer(
    self,
    delta_id: str = "DE-100",
  ) -> None:
    """Create handoff to reviewer and accept it."""
    with (
      patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40),
      patch("supekku.scripts.lib.core.git.get_branch", return_value="main"),
      patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False),
      patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False),
    ):
      self.runner.invoke(
        app,
        ["create", "handoff", delta_id, "--to", "reviewer"],
      )
    self.runner.invoke(
      app,
      ["accept", "handoff", delta_id, "--identity", "reviewer-1"],
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
      "supekku.scripts.lib.core.git.get_head_sha",
      return_value="a" * 40,
    ):
      self.runner.invoke(app, ["review", "prime", "DE-100"])

    data1 = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    assert data1["staleness"]["cache_key"]["head"] == "a" * 40

    # Second prime with new HEAD
    with patch(
      "supekku.scripts.lib.core.git.get_head_sha",
      return_value="b" * 40,
    ):
      self.runner.invoke(app, ["review", "prime", "DE-100"])

    data2 = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    assert data2["staleness"]["cache_key"]["head"] == "b" * 40

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
      app,
      ["review", "complete", "DE-100", "--status", "changes_requested"],
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
    assert findings["review"]["current_round"] == 1
    assert findings["rounds"][0]["status"] == "changes_requested"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_transitions_to_approved(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "approved"],
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
    assert findings["review"]["current_round"] == 1

    # Cycle back: create handoff → accept → review complete again
    with (
      patch("supekku.scripts.lib.core.git.get_head_sha", return_value="b" * 40),
      patch("supekku.scripts.lib.core.git.get_branch", return_value="main"),
      patch("supekku.scripts.lib.core.git.has_uncommitted_changes", return_value=False),
      patch("supekku.scripts.lib.core.git.has_staged_changes", return_value=False),
    ):
      self.runner.invoke(
        app,
        ["create", "handoff", "DE-100", "--to", "reviewer"],
      )
    self.runner.invoke(
      app,
      ["accept", "handoff", "DE-100", "--identity", "reviewer-2"],
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
    assert findings["review"]["current_round"] == 2

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
    assert findings["rounds"][0]["reviewer_role"] == "reviewer"

  def test_rejects_invalid_status(self) -> None:
    _create_delta_bundle(self.root)
    self._start_phase()
    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "invalid"],
    )
    assert result.exit_code == 1

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_fails_when_not_reviewing(self, *_mocks) -> None:
    """Cannot complete review when not in reviewing state."""
    _create_delta_bundle(self.root)
    self._start_phase()
    # Still implementing, not reviewing
    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "approved"],
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
        "review",
        "complete",
        "DE-100",
        "--status",
        "changes_requested",
        "--summary",
        "Needs revision",
      ],
    )
    assert result.exit_code == 0, result.output

    # Summary feature deferred to Phase 3 (DE-109) — v2 accumulative
    # model stores round-level data, not top-level history.
    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    assert findings["version"] == 2
    assert findings["rounds"][0]["status"] == "changes_requested"

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
      app,
      ["review", "complete", "DE-100", "--status", "approved"],
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
    self,
    *_mocks,
  ) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "changes_requested"],
    )

    assert (delta_dir / "workflow" / "review-findings.yaml").exists()
    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "changes_requested"


class _FindingTestBase(_ReviewTestBase):
  """Base for tests needing findings with blocking/non-blocking items."""

  @staticmethod
  def _finding(
    finding_id: str,
    title: str,
    summary: str = "",
  ) -> dict:
    """Build a minimal finding dict that passes schema validation."""
    return {"id": finding_id, "title": title, "summary": summary, "status": "open"}

  def _setup_review_with_findings(
    self,
    delta_id: str = "DE-100",
    blocking: list[dict] | None = None,
    non_blocking: list[dict] | None = None,
  ) -> Path:
    """Set up a delta in reviewing state with v2 findings."""
    from supekku.scripts.lib.workflow.review_io import (
      build_findings,
      write_findings,
    )

    delta_dir = _create_delta_bundle(self.root, delta_id=delta_id)
    self._start_phase(delta_id)
    self._create_handoff_and_accept_as_reviewer(delta_id)

    findings_data = build_findings(
      artifact_id=delta_id.upper(),
      round_number=1,
      status="in_progress",
      reviewer_role="reviewer",
      blocking=blocking or [],
      non_blocking=non_blocking or [],
    )
    write_findings(delta_dir, findings_data)
    return delta_dir


# ---------------------------------------------------------------------------
# VT-109-008: Disposition command tests (DR-109 §5.3)
# ---------------------------------------------------------------------------


class ReviewFindingResolveTest(_FindingTestBase):
  """Test `spec-driver review finding resolve`."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_resolve_blocking_finding(self, *_mocks) -> None:
    delta_dir = self._setup_review_with_findings(
      blocking=[self._finding("R1-001", "Bug", "A bug")],
    )

    result = self.runner.invoke(
      app,
      [
        "review", "finding", "resolve", "DE-100", "R1-001",
        "--resolved-at", "abc123",
      ],
    )
    assert result.exit_code == 0, result.output
    assert "fix" in result.output.lower()

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    finding = findings["rounds"][0]["blocking"][0]
    assert finding["disposition"]["action"] == "fix"
    assert finding["disposition"]["resolved_at"] == "abc123"
    assert finding["status"] == "resolved"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_resolve_non_blocking_without_resolved_at(self, *_mocks) -> None:
    """Non-blocking findings can be resolved without --resolved-at."""
    delta_dir = self._setup_review_with_findings(
      non_blocking=[self._finding("R1-002", "Nit", "A nit")],
    )

    result = self.runner.invoke(
      app,
      ["review", "finding", "resolve", "DE-100", "R1-002"],
    )
    assert result.exit_code == 0, result.output

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    finding = findings["rounds"][0]["non_blocking"][0]
    assert finding["disposition"]["action"] == "fix"
    assert finding["status"] == "resolved"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_finding_not_found_shows_available_ids(self, *_mocks) -> None:
    self._setup_review_with_findings(
      blocking=[self._finding("R1-001", "Bug", "A bug")],
    )

    result = self.runner.invoke(
      app,
      ["review", "finding", "resolve", "DE-100", "R1-999"],
    )
    assert result.exit_code == 1
    assert "R1-001" in result.output  # suggests available IDs

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_overwrites_existing_disposition(self, *_mocks) -> None:
    """Re-dispositioning overwrites previous (latest wins)."""
    delta_dir = self._setup_review_with_findings(
      non_blocking=[self._finding("R1-001", "Nit", "A nit")],
    )

    # First disposition: defer
    self.runner.invoke(
      app,
      [
        "review", "finding", "defer", "DE-100", "R1-001",
        "--rationale", "Later",
      ],
    )
    # Second disposition: resolve (overwrites)
    self.runner.invoke(
      app,
      ["review", "finding", "resolve", "DE-100", "R1-001"],
    )

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    finding = findings["rounds"][0]["non_blocking"][0]
    assert finding["disposition"]["action"] == "fix"
    assert finding["status"] == "resolved"


class ReviewFindingDeferTest(_FindingTestBase):
  """Test `spec-driver review finding defer`."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_defer_with_rationale(self, *_mocks) -> None:
    delta_dir = self._setup_review_with_findings(
      non_blocking=[self._finding("R1-001", "Nit", "A nit")],
    )

    result = self.runner.invoke(
      app,
      [
        "review", "finding", "defer", "DE-100", "R1-001",
        "--rationale", "Not critical now",
      ],
    )
    assert result.exit_code == 0, result.output

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    finding = findings["rounds"][0]["non_blocking"][0]
    assert finding["disposition"]["action"] == "defer"
    assert finding["disposition"]["rationale"] == "Not critical now"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_defer_without_rationale_fails(self, *_mocks) -> None:
    self._setup_review_with_findings(
      non_blocking=[self._finding("R1-001", "Nit", "A nit")],
    )

    result = self.runner.invoke(
      app,
      ["review", "finding", "defer", "DE-100", "R1-001"],
    )
    assert result.exit_code != 0

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_defer_blocking_with_backlog_ref(self, *_mocks) -> None:
    delta_dir = self._setup_review_with_findings(
      blocking=[self._finding("R1-001", "Bug", "A bug")],
    )

    result = self.runner.invoke(
      app,
      [
        "review", "finding", "defer", "DE-100", "R1-001",
        "--rationale", "Tracked in backlog",
        "--backlog-ref", "ISSUE-042",
      ],
    )
    assert result.exit_code == 0, result.output

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    finding = findings["rounds"][0]["blocking"][0]
    assert finding["disposition"]["backlog_ref"] == "ISSUE-042"


class ReviewFindingWaiveTest(_FindingTestBase):
  """Test `spec-driver review finding waive`."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_waive_with_rationale(self, *_mocks) -> None:
    delta_dir = self._setup_review_with_findings(
      non_blocking=[self._finding("R1-001", "Nit", "A nit")],
    )

    result = self.runner.invoke(
      app,
      [
        "review", "finding", "waive", "DE-100", "R1-001",
        "--rationale", "Acceptable risk",
      ],
    )
    assert result.exit_code == 0, result.output

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    finding = findings["rounds"][0]["non_blocking"][0]
    assert finding["disposition"]["action"] == "waive"
    assert finding["disposition"]["rationale"] == "Acceptable risk"
    assert finding["status"] == "waived"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_waive_without_rationale_fails(self, *_mocks) -> None:
    self._setup_review_with_findings(
      non_blocking=[self._finding("R1-001", "Nit", "A nit")],
    )

    result = self.runner.invoke(
      app,
      ["review", "finding", "waive", "DE-100", "R1-001"],
    )
    assert result.exit_code != 0

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_waive_blocking_requires_authority_user(self, *_mocks) -> None:
    """Waiving a blocking finding requires --authority user."""
    self._setup_review_with_findings(
      blocking=[self._finding("R1-001", "Bug", "A bug")],
    )

    result = self.runner.invoke(
      app,
      [
        "review", "finding", "waive", "DE-100", "R1-001",
        "--rationale", "Acceptable",
        "--authority", "agent",
      ],
    )
    # Command succeeds (writes disposition), but guard will catch it later
    assert result.exit_code == 0, result.output

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_waive_with_authority_user(self, *_mocks) -> None:
    delta_dir = self._setup_review_with_findings(
      blocking=[self._finding("R1-001", "Bug", "A bug")],
    )

    result = self.runner.invoke(
      app,
      [
        "review", "finding", "waive", "DE-100", "R1-001",
        "--rationale", "Accepted by user",
        "--authority", "user",
      ],
    )
    assert result.exit_code == 0, result.output

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    finding = findings["rounds"][0]["blocking"][0]
    assert finding["disposition"]["authority"] == "user"


class ReviewFindingSupersedeTest(_FindingTestBase):
  """Test `spec-driver review finding supersede`."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_supersede_finding(self, *_mocks) -> None:
    delta_dir = self._setup_review_with_findings(
      non_blocking=[
        self._finding("R1-001", "Old", "Old finding"),
        self._finding("R1-002", "New", "New finding"),
      ],
    )

    result = self.runner.invoke(
      app,
      [
        "review", "finding", "supersede", "DE-100", "R1-001",
        "--superseded-by", "R1-002",
      ],
    )
    assert result.exit_code == 0, result.output

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    finding = findings["rounds"][0]["non_blocking"][0]
    assert finding["disposition"]["action"] == "supersede"
    assert finding["disposition"]["superseded_by"] == "R1-002"
    assert finding["status"] == "superseded"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_supersede_without_superseded_by_fails(self, *_mocks) -> None:
    self._setup_review_with_findings(
      non_blocking=[self._finding("R1-001", "Old", "Old finding")],
    )

    result = self.runner.invoke(
      app,
      ["review", "finding", "supersede", "DE-100", "R1-001"],
    )
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# VT-109-005: CLI guard enforcement (DR-109 §5.4)
# ---------------------------------------------------------------------------


class ReviewGuardEnforcementTest(_FindingTestBase):
  """Test review complete --status approved enforces can_approve() guard."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_approve_blocked_by_open_blocking_finding(self, *_mocks) -> None:
    """Cannot approve with undispositioned blocking findings."""
    self._setup_review_with_findings(
      blocking=[self._finding("R1-001", "Bug", "A bug")],
    )

    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "approved"],
    )
    assert result.exit_code == 1
    output = result.output.lower()
    assert "cannot approve" in output or "blocking" in output

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_approve_succeeds_after_resolving_blocking(self, *_mocks) -> None:
    """Approve succeeds when all blocking findings are resolved."""
    self._setup_review_with_findings(
      blocking=[self._finding("R1-001", "Bug", "A bug")],
    )

    # Resolve the blocking finding
    self.runner.invoke(
      app,
      [
        "review", "finding", "resolve", "DE-100", "R1-001",
        "--resolved-at", "abc123",
      ],
    )

    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "approved"],
    )
    assert result.exit_code == 0, result.output

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_changes_requested_ignores_guard(self, *_mocks) -> None:
    """changes_requested does not require guard to pass."""
    self._setup_review_with_findings(
      blocking=[self._finding("R1-001", "Bug", "A bug")],
    )

    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "changes_requested"],
    )
    assert result.exit_code == 0, result.output

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_approve_blocked_by_agent_waive(self, *_mocks) -> None:
    """Agent-waived blocking finding still blocks approval."""
    self._setup_review_with_findings(
      blocking=[self._finding("R1-001", "Bug", "A bug")],
    )

    self.runner.invoke(
      app,
      [
        "review", "finding", "waive", "DE-100", "R1-001",
        "--rationale", "Agent says ok",
        "--authority", "agent",
      ],
    )

    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "approved"],
    )
    assert result.exit_code == 1

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_approve_allowed_with_user_waive(self, *_mocks) -> None:
    """User-waived blocking finding with rationale allows approval."""
    self._setup_review_with_findings(
      blocking=[self._finding("R1-001", "Bug", "A bug")],
    )

    self.runner.invoke(
      app,
      [
        "review", "finding", "waive", "DE-100", "R1-001",
        "--rationale", "Accepted risk",
        "--authority", "user",
      ],
    )

    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "approved"],
    )
    assert result.exit_code == 0, result.output


class ReviewJudgmentStatusTest(_FindingTestBase):
  """Test judgment_status written to review-index."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_prime_sets_judgment_in_progress(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()

    self.runner.invoke(app, ["review", "prime", "DE-100"])

    data = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    assert data["review"]["judgment_status"] == "in_progress"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_complete_writes_judgment_to_index(self, *_mocks) -> None:
    delta_dir = self._setup_review_with_findings()

    # Prime first to create review-index
    self.runner.invoke(app, ["review", "prime", "DE-100"])

    self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "changes_requested"],
    )

    data = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    assert data["review"]["judgment_status"] == "changes_requested"


class ReviewSummaryTest(_FindingTestBase):
  """Test --summary wired into round metadata."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_summary_stored_in_round(self, *_mocks) -> None:
    delta_dir = self._setup_review_with_findings()

    # Use changes_requested to avoid auto-teardown
    result = self.runner.invoke(
      app,
      [
        "review", "complete", "DE-100",
        "--status", "changes_requested",
        "--summary", "Needs work on error handling",
      ],
    )
    assert result.exit_code == 0, result.output

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    # Summary appears in the latest round
    latest_round = findings["rounds"][-1]
    assert latest_round["summary"] == "Needs work on error handling"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_no_summary_omits_key(self, *_mocks) -> None:
    delta_dir = self._setup_review_with_findings()

    self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "changes_requested"],
    )

    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    latest_round = findings["rounds"][-1]
    assert "summary" not in latest_round


# ---------------------------------------------------------------------------
# VT-109-009: End-to-end multi-round review (DR-109 §5.4)
# ---------------------------------------------------------------------------


class ReviewEndToEndTest(_ReviewTestBase):
  """End-to-end: prime → complete(changes_requested) → resolve → re-prime → approve."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_multi_round_with_disposition_and_approval(self, *_mocks) -> None:
    """VT-109-009: Full multi-round review lifecycle."""
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    # --- Round 1: prime + complete with changes_requested ---
    self.runner.invoke(app, ["review", "prime", "DE-100"])

    # Verify judgment_status set to in_progress
    idx = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    assert idx["review"]["judgment_status"] == "in_progress"

    # Complete round 1 with a blocking finding
    from supekku.scripts.lib.workflow.review_io import (
      build_findings,
      write_findings,
    )

    findings_data = build_findings(
      artifact_id="DE-100",
      round_number=1,
      status="changes_requested",
      reviewer_role="reviewer",
      summary="Found a blocking issue",
      blocking=[{
        "id": "R1-001",
        "title": "Security flaw",
        "summary": "Input not sanitised",
        "status": "open",
      }],
      non_blocking=[{
        "id": "R1-002",
        "title": "Style nit",
        "summary": "Inconsistent naming",
        "status": "open",
      }],
    )
    write_findings(delta_dir, findings_data)

    result = self.runner.invoke(
      app,
      [
        "review", "complete", "DE-100",
        "--status", "changes_requested",
        "--summary", "Blocking security issue",
      ],
    )
    assert result.exit_code == 0, result.output

    # Verify round 1 recorded
    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    assert len(findings["rounds"]) == 2  # initial + appended
    assert findings["rounds"][-1]["status"] == "changes_requested"

    # --- Attempt to approve with open blocking finding → fails ---
    # Re-enter reviewing state for round 2
    with (
      patch("supekku.scripts.lib.core.git.get_head_sha", return_value="b" * 40),
      patch("supekku.scripts.lib.core.git.get_branch", return_value="main"),
      patch(
        "supekku.scripts.lib.core.git.has_uncommitted_changes",
        return_value=False,
      ),
      patch(
        "supekku.scripts.lib.core.git.has_staged_changes",
        return_value=False,
      ),
    ):
      self.runner.invoke(
        app,
        ["create", "handoff", "DE-100", "--to", "reviewer"],
      )
    self.runner.invoke(
      app,
      ["accept", "handoff", "DE-100", "--identity", "reviewer-2"],
    )

    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "approved"],
    )
    assert result.exit_code == 1, (
      "Should fail: blocking finding R1-001 is still open"
    )

    # --- Resolve the blocking finding ---
    result = self.runner.invoke(
      app,
      [
        "review", "finding", "resolve", "DE-100", "R1-001",
        "--resolved-at", "b" * 8,
      ],
    )
    assert result.exit_code == 0, result.output

    # Verify finding is now resolved
    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    r1_blocking = findings["rounds"][0]["blocking"][0]
    assert r1_blocking["status"] == "resolved"
    assert r1_blocking["disposition"]["action"] == "fix"

    # --- Round 2: re-prime + approve (guard passes) ---
    with patch(
      "supekku.scripts.lib.core.git.get_head_sha",
      return_value="b" * 40,
    ):
      self.runner.invoke(app, ["review", "prime", "DE-100"])

    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "--status", "approved"],
    )
    assert result.exit_code == 0, result.output
    assert "approved" in result.output

    # --- Verify final state ---
    state = yaml.safe_load(
      (delta_dir / "workflow" / "state.yaml").read_text(),
    )
    assert state["workflow"]["status"] == "approved"

    # Review-index should be torn down on approval
    assert not (delta_dir / "workflow" / "review-index.yaml").exists()


# ---------------------------------------------------------------------------
# JSON output tests (DE-108 P02)
# ---------------------------------------------------------------------------

import json


class ReviewPrimeJsonTest(_ReviewTestBase):
  """Tests for review prime --format json."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_prime_json_success(self, *_mocks) -> None:
    _create_delta_bundle(self.root)
    self._start_phase()
    result = self.runner.invoke(
      app, ["review", "prime", "DE-100", "--format", "json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["version"] == 1
    assert data["command"] == "review.prime"
    assert data["status"] == "ok"
    assert data["exit_code"] == 0
    payload = data["data"]
    assert payload["delta_id"] == "DE-100"
    assert payload["action"] == "created"
    assert payload["bootstrap_status"] == "warm"
    assert payload["judgment_status"] == "in_progress"
    assert payload["review_round"] == 1
    assert "index_path" in payload
    assert "bootstrap_path" in payload

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_prime_json_full_sha(self, *_mocks) -> None:
    """JSON output uses full 40-char SHA (DEC-108-002)."""
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self.runner.invoke(
      app, ["review", "prime", "DE-100", "--format", "json"],
    )
    index = yaml.safe_load(
      (delta_dir / "workflow" / "review-index.yaml").read_text(),
    )
    assert index["staleness"]["cache_key"]["head"] == "a" * 40

  def test_prime_json_precondition_no_state(self) -> None:
    """No workflow state → exit 2, precondition error."""
    _create_delta_bundle(self.root)
    # Don't start phase — no state.yaml
    result = self.runner.invoke(
      app, ["review", "prime", "DE-100", "--format", "json"],
    )
    assert result.exit_code == 2
    data = json.loads(result.output)
    assert data["status"] == "error"
    assert data["error"]["kind"] == "precondition"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_prime_json_no_stderr(self, *_mocks) -> None:
    """JSON mode produces no stderr output."""
    _create_delta_bundle(self.root)
    self._start_phase()
    result = self.runner.invoke(
      app, ["review", "prime", "DE-100", "--format", "json"],
    )
    # CliRunner captures stderr separately if mix_stderr=False,
    # but by default mixes. The key check: output is valid JSON
    # (no interleaved text).
    data = json.loads(result.output)
    assert data["status"] == "ok"


class ReviewCompleteJsonTest(_ReviewTestBase):
  """Tests for review complete --format json."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_complete_json_changes_requested(self, *_mocks) -> None:
    _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()
    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "-s", "changes_requested",
       "--format", "json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["command"] == "review.complete"
    assert data["status"] == "ok"
    payload = data["data"]
    assert payload["delta_id"] == "DE-100"
    assert payload["outcome"] == "changes_requested"
    assert payload["round"] == 1
    assert "previous_state" in payload
    assert "new_state" in payload
    assert "findings_path" in payload
    assert isinstance(payload["teardown"], bool)

  def test_complete_json_precondition_no_state(self) -> None:
    _create_delta_bundle(self.root)
    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "-s", "approved", "--format", "json"],
    )
    assert result.exit_code == 2
    data = json.loads(result.output)
    assert data["error"]["kind"] == "precondition"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_complete_json_guard_violation(self, *_mocks) -> None:
    """Approve with open blocking finding → exit 3, guard_violation."""
    delta_dir = _create_delta_bundle(self.root)
    self._start_phase()
    self._create_handoff_and_accept_as_reviewer()

    # Create findings with an open blocking finding
    from supekku.scripts.lib.workflow.review_io import (
      build_findings,
      write_findings,
    )

    findings = build_findings(
      artifact_id="DE-100",
      round_number=1,
      status="changes_requested",
      blocking=[{"id": "R1-001", "title": "Bug", "status": "open"}],
    )
    write_findings(delta_dir, findings)

    # First do changes_requested to get back to a state where we can try approve
    self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "-s", "changes_requested"],
    )

    # Now start a new review cycle
    self._create_handoff_and_accept_as_reviewer()

    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "-s", "approved", "--format", "json"],
    )
    assert result.exit_code == 3
    data = json.loads(result.output)
    assert data["error"]["kind"] == "guard_violation"

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_complete_json_invalid_status(self, *_mocks) -> None:
    """Invalid status value → exit 2, precondition."""
    _create_delta_bundle(self.root)
    self._start_phase()
    result = self.runner.invoke(
      app,
      ["review", "complete", "DE-100", "-s", "bogus", "--format", "json"],
    )
    assert result.exit_code == 2
    data = json.loads(result.output)
    assert data["error"]["kind"] == "precondition"


class ReviewTeardownJsonTest(_ReviewTestBase):
  """Tests for review teardown --format json."""

  @patch("supekku.scripts.lib.core.git.get_head_sha", return_value="a" * 40)
  def test_teardown_json_success(self, *_mocks) -> None:
    _create_delta_bundle(self.root)
    self._start_phase()
    # Prime first to create review files
    self.runner.invoke(app, ["review", "prime", "DE-100"])

    result = self.runner.invoke(
      app, ["review", "teardown", "DE-100", "--format", "json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["command"] == "review.teardown"
    assert data["status"] == "ok"
    payload = data["data"]
    assert payload["delta_id"] == "DE-100"
    assert isinstance(payload["removed"], list)
    assert len(payload["removed"]) > 0

  def test_teardown_json_nothing_to_delete(self) -> None:
    _create_delta_bundle(self.root)
    self._start_phase()
    result = self.runner.invoke(
      app, ["review", "teardown", "DE-100", "--format", "json"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["data"]["removed"] == []


if __name__ == "__main__":
  unittest.main()
