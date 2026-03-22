"""Unit tests for spec_driver.orchestration.operations (DE-124 Phase 1).

Tests each composed operation independently using temp directory fixtures.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from spec_driver.orchestration.operations import (
  DeltaNotFoundError,
  DispositionValidationError,
  FindingNotFoundError,
  PrimeAction,
  ReviewApprovalGuardError,
  complete_review,
  disposition_finding,
  prime_review,
  resolve_delta_dir,
  summarize_review,
  teardown_review,
)
from supekku.scripts.lib.core.paths import DELTAS_SUBDIR, SPEC_DRIVER_DIR
from supekku.scripts.lib.workflow.review_io import (
  FindingsNotFoundError,
  build_findings,
  build_review_index,
  write_findings,
  write_review_index,
)
from supekku.scripts.lib.workflow.review_state_machine import (
  BootstrapStatus,
  FindingDispositionAction,
  FindingStatus,
  ReviewStatus,
)
from supekku.scripts.lib.workflow.state_io import (
  StateNotFoundError,
  init_state,
  update_state_workflow,
  write_state,
)
from supekku.scripts.lib.workflow.state_machine import (
  TransitionError,
  WorkflowState,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _create_delta_bundle(
  root: Path,
  delta_id: str = "DE-100",
  slug: str = "test-delta",
) -> Path:
  """Create a minimal delta bundle for testing."""
  bundle_name = f"{delta_id}-{slug}"
  delta_dir = root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / bundle_name
  delta_dir.mkdir(parents=True, exist_ok=True)
  (delta_dir / f"{delta_id}.md").write_text(
    f"---\nid: {delta_id}\nstatus: in-progress\nkind: delta\n---\n",
  )
  (delta_dir / "notes.md").write_text("# Notes\n")
  return delta_dir


def _init_workflow_state(
  delta_dir: Path,
  *,
  status: str = "reviewing",
  active_role: str = "reviewer",
) -> None:
  """Write a valid state.yaml via init_state, then patch status/role."""
  parts = delta_dir.name.split("-", 2)
  aid = f"{parts[0]}-{parts[1]}".upper()
  sd_root = delta_dir.parent.parent.parent
  artifact_path = str(delta_dir.relative_to(sd_root))

  state_data = init_state(
    artifact_id=aid,
    phase_id="IP-100.PHASE-01",
    plan_id="IP-100",
    artifact_path=artifact_path,
    notes_path=f"{artifact_path}/notes.md",
    plan_path=f"{artifact_path}/IP-100.md",
    phase_path=f"{artifact_path}/phases/phase-01.md",
  )
  update_state_workflow(
    state_data,
    status=status,
    active_role=active_role,
  )
  if active_role == "reviewer":
    state_data["workflow"]["claimed_by"] = "test-reviewer"
  write_state(delta_dir, state_data)


def _write_findings(
  delta_dir: Path,
  *,
  blocking: list[dict] | None = None,
  non_blocking: list[dict] | None = None,
  status: str = "changes_requested",
  round_number: int = 1,
) -> None:
  """Write a review-findings.yaml with one round."""
  data = build_findings(
    artifact_id="DE-100",
    round_number=round_number,
    status=status,
    blocking=blocking,
    non_blocking=non_blocking,
  )
  write_findings(delta_dir, data)


def _make_finding(
  fid: str,
  title: str = "Test finding",
) -> dict:
  return {"id": fid, "title": title, "status": "open"}


class _OperationsTestBase(unittest.TestCase):
  """Base class with temp directory and workflow setup."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()
    self.tmpdir = tempfile.TemporaryDirectory()
    self.root = Path(self.tmpdir.name)
    (self.root / ".git").mkdir()
    sd = self.root / SPEC_DRIVER_DIR
    sd.mkdir(parents=True, exist_ok=True)
    from supekku.scripts.lib.core.version import (  # noqa: PLC0415
      get_package_version,
    )

    ver = get_package_version()
    (sd / "workflow.toml").write_text(
      f'ceremony = "pioneer"\nspec_driver_installed_version = "{ver}"\n',
    )
    os.chdir(self.root)

  def tearDown(self) -> None:
    os.chdir(self._cwd)
    self.tmpdir.cleanup()


# ---------------------------------------------------------------------------
# resolve_delta_dir
# ---------------------------------------------------------------------------


class ResolveDeltaDirTest(_OperationsTestBase):
  """Test resolve_delta_dir operation."""

  def test_resolves_by_id(self) -> None:
    _create_delta_bundle(self.root)
    result = resolve_delta_dir("DE-100", self.root)
    assert result.name.startswith("DE-100")

  def test_case_insensitive(self) -> None:
    _create_delta_bundle(self.root)
    result = resolve_delta_dir("de-100", self.root)
    assert result.name.startswith("DE-100")

  def test_not_found_raises(self) -> None:
    with self.assertRaises(DeltaNotFoundError) as ctx:
      resolve_delta_dir("DE-999", self.root)
    assert ctx.exception.delta_id == "DE-999"

  def test_no_deltas_dir_raises(self) -> None:
    empty = Path(self.tmpdir.name) / "empty"
    empty.mkdir()
    (empty / ".git").mkdir()
    (empty / SPEC_DRIVER_DIR).mkdir(parents=True)

    with self.assertRaises(DeltaNotFoundError):
      resolve_delta_dir("DE-100", empty)


# ---------------------------------------------------------------------------
# prime_review
# ---------------------------------------------------------------------------


class PrimeReviewTest(_OperationsTestBase):
  """Test prime_review operation."""

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_cold_start_creates_files(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir)

    result = prime_review(delta_dir, self.root)

    assert result.action == PrimeAction.CREATED
    assert result.bootstrap_status == BootstrapStatus.WARM
    assert result.judgment_status == ReviewStatus.IN_PROGRESS
    assert result.index_path.exists()
    assert result.bootstrap_path.exists()
    assert result.review_round == 1

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_reprime_same_head(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir)

    prime_review(delta_dir, self.root)
    # Same HEAD, same phase → warm (no triggers) → CREATED
    result = prime_review(delta_dir, self.root)
    assert result.action == PrimeAction.CREATED

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="b" * 40,
  )
  @patch(
    "supekku.scripts.lib.core.git.get_changed_files",
    return_value=["some/file.py"],
  )
  def test_reprime_with_changes_rebuilds(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir)

    idx = build_review_index(
      artifact_id="DE-100",
      phase_id="IP-100.PHASE-01",
      git_head="a" * 40,
      domain_map=[
        {
          "area": "test",
          "purpose": "test",
          "files": ["x.py"],
        }
      ],
    )
    write_review_index(delta_dir, idx)

    result = prime_review(delta_dir, self.root)
    assert result.action.value in ("rebuilt", "refreshed")

  def test_no_state_raises(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    with self.assertRaises(StateNotFoundError):
      prime_review(delta_dir, self.root)

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_delta_id_extracted_correctly(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir)
    result = prime_review(delta_dir, self.root)
    assert result.delta_id == "DE-100"

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_bootstrap_markdown_content(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir)
    result = prime_review(delta_dir, self.root)
    content = result.bootstrap_path.read_text()
    assert "Review Bootstrap" in content
    assert "DE-100" in content


# ---------------------------------------------------------------------------
# complete_review
# ---------------------------------------------------------------------------


class CompleteReviewTest(_OperationsTestBase):
  """Test complete_review operation."""

  def _setup_reviewing_state(self) -> Path:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir, status="reviewing")
    return delta_dir

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_changes_requested(self, *_mocks) -> None:
    delta_dir = self._setup_reviewing_state()
    result = complete_review(
      delta_dir,
      self.root,
      status=ReviewStatus.CHANGES_REQUESTED,
    )
    assert result.outcome == ReviewStatus.CHANGES_REQUESTED
    assert result.previous_state == WorkflowState.REVIEWING
    assert result.new_state == WorkflowState.CHANGES_REQUESTED
    assert result.findings_path.exists()
    assert result.round_number == 1

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_approved_with_no_findings(self, *_mocks) -> None:
    delta_dir = self._setup_reviewing_state()
    result = complete_review(
      delta_dir,
      self.root,
      status=ReviewStatus.APPROVED,
    )
    assert result.outcome == ReviewStatus.APPROVED
    assert result.teardown_performed is True

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_approved_no_auto_teardown(self, *_mocks) -> None:
    delta_dir = self._setup_reviewing_state()
    result = complete_review(
      delta_dir,
      self.root,
      status=ReviewStatus.APPROVED,
      auto_teardown=False,
    )
    assert result.outcome == ReviewStatus.APPROVED
    assert result.teardown_performed is False

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_approval_guard_blocks(self, *_mocks) -> None:
    delta_dir = self._setup_reviewing_state()
    _write_findings(
      delta_dir,
      blocking=[_make_finding("R1-001")],
    )
    with self.assertRaises(ReviewApprovalGuardError) as ctx:
      complete_review(
        delta_dir,
        self.root,
        status=ReviewStatus.APPROVED,
      )
    assert "R1-001" in str(ctx.exception)

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_wrong_state_raises(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir, status="implementing")
    with self.assertRaises(TransitionError):
      complete_review(
        delta_dir,
        self.root,
        status=ReviewStatus.APPROVED,
      )

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_with_summary(self, *_mocks) -> None:
    delta_dir = self._setup_reviewing_state()
    complete_review(
      delta_dir,
      self.root,
      status=ReviewStatus.CHANGES_REQUESTED,
      summary="Needs rework",
    )
    findings = yaml.safe_load(
      (delta_dir / "workflow" / "review-findings.yaml").read_text(),
    )
    assert findings["rounds"][0]["summary"] == "Needs rework"

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_increments_round_number(self, *_mocks) -> None:
    delta_dir = self._setup_reviewing_state()

    complete_review(
      delta_dir,
      self.root,
      status=ReviewStatus.CHANGES_REQUESTED,
    )

    # Back to reviewing for second round
    _init_workflow_state(delta_dir, status="reviewing")
    result = complete_review(
      delta_dir,
      self.root,
      status=ReviewStatus.CHANGES_REQUESTED,
    )
    assert result.round_number == 2


# ---------------------------------------------------------------------------
# disposition_finding
# ---------------------------------------------------------------------------


class DispositionFindingTest(_OperationsTestBase):
  """Test disposition_finding operation."""

  def _setup_with_findings(
    self,
    blocking: list[dict] | None = None,
    non_blocking: list[dict] | None = None,
  ) -> Path:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir)
    _write_findings(
      delta_dir,
      blocking=blocking,
      non_blocking=non_blocking,
    )
    return delta_dir

  def test_fix_blocking(self) -> None:
    delta_dir = self._setup_with_findings(
      blocking=[_make_finding("R1-001")],
    )
    result = disposition_finding(
      delta_dir,
      "R1-001",
      action=FindingDispositionAction.FIX,
      resolved_at="abc123",
    )
    assert result.previous_status == FindingStatus.OPEN
    assert result.new_status == FindingStatus.RESOLVED
    assert result.action == FindingDispositionAction.FIX

  def test_waive_with_rationale(self) -> None:
    delta_dir = self._setup_with_findings(
      non_blocking=[_make_finding("R1-001")],
    )
    result = disposition_finding(
      delta_dir,
      "R1-001",
      action=FindingDispositionAction.WAIVE,
      rationale="Acceptable risk",
    )
    assert result.new_status == FindingStatus.WAIVED

  def test_waive_without_rationale_raises(self) -> None:
    delta_dir = self._setup_with_findings(
      non_blocking=[_make_finding("R1-001")],
    )
    with self.assertRaises(DispositionValidationError):
      disposition_finding(
        delta_dir,
        "R1-001",
        action=FindingDispositionAction.WAIVE,
      )

  def test_defer_with_rationale(self) -> None:
    delta_dir = self._setup_with_findings(
      blocking=[_make_finding("R1-001")],
    )
    result = disposition_finding(
      delta_dir,
      "R1-001",
      action=FindingDispositionAction.DEFER,
      rationale="Later",
    )
    assert result.action == FindingDispositionAction.DEFER

  def test_defer_without_rationale_raises(self) -> None:
    delta_dir = self._setup_with_findings(
      blocking=[_make_finding("R1-001")],
    )
    with self.assertRaises(DispositionValidationError):
      disposition_finding(
        delta_dir,
        "R1-001",
        action=FindingDispositionAction.DEFER,
      )

  def test_supersede(self) -> None:
    delta_dir = self._setup_with_findings(
      blocking=[_make_finding("R1-001")],
    )
    result = disposition_finding(
      delta_dir,
      "R1-001",
      action=FindingDispositionAction.SUPERSEDE,
      superseded_by="R2-001",
    )
    assert result.new_status == FindingStatus.SUPERSEDED

  def test_supersede_without_ref_raises(self) -> None:
    delta_dir = self._setup_with_findings(
      blocking=[_make_finding("R1-001")],
    )
    with self.assertRaises(DispositionValidationError):
      disposition_finding(
        delta_dir,
        "R1-001",
        action=FindingDispositionAction.SUPERSEDE,
      )

  def test_finding_not_found_raises(self) -> None:
    delta_dir = self._setup_with_findings(
      blocking=[_make_finding("R1-001")],
    )
    with self.assertRaises(FindingNotFoundError) as ctx:
      disposition_finding(
        delta_dir,
        "R1-999",
        action=FindingDispositionAction.FIX,
      )
    assert "R1-001" in ctx.exception.available

  def test_overwrites_existing_disposition(self) -> None:
    delta_dir = self._setup_with_findings(
      non_blocking=[_make_finding("R1-001")],
    )
    disposition_finding(
      delta_dir,
      "R1-001",
      action=FindingDispositionAction.WAIVE,
      rationale="Accept",
    )
    result = disposition_finding(
      delta_dir,
      "R1-001",
      action=FindingDispositionAction.FIX,
    )
    assert result.previous_status == FindingStatus.WAIVED
    assert result.new_status == FindingStatus.RESOLVED


# ---------------------------------------------------------------------------
# teardown_review
# ---------------------------------------------------------------------------


class TeardownReviewTest(_OperationsTestBase):
  """Test teardown_review operation."""

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_removes_review_files(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir)
    prime_review(delta_dir, self.root)

    result = teardown_review(delta_dir)
    assert "review-index" in result.removed
    assert "review-bootstrap" in result.removed
    assert result.delta_id == "DE-100"

  def test_no_files_returns_empty(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    result = teardown_review(delta_dir)
    assert result.removed == []

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_removes_findings(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir)
    _write_findings(delta_dir, blocking=[_make_finding("R1-001")])

    result = teardown_review(delta_dir)
    assert "review-findings" in result.removed


# ---------------------------------------------------------------------------
# summarize_review
# ---------------------------------------------------------------------------


class SummarizeReviewTest(_OperationsTestBase):
  """Test summarize_review operation."""

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_counts_findings(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir)
    prime_review(delta_dir, self.root)
    _write_findings(
      delta_dir,
      blocking=[_make_finding("R1-001"), _make_finding("R1-002")],
      non_blocking=[_make_finding("R1-003")],
    )

    summary = summarize_review(delta_dir)
    assert summary.blocking_total == 2
    assert summary.blocking_dispositioned == 0
    assert summary.non_blocking_total == 1
    assert summary.all_blocking_resolved is False
    assert summary.current_round == 1

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_all_resolved(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir)
    prime_review(delta_dir, self.root)
    _write_findings(
      delta_dir,
      blocking=[_make_finding("R1-001")],
    )

    disposition_finding(
      delta_dir,
      "R1-001",
      action=FindingDispositionAction.FIX,
      resolved_at="abc123",
    )

    summary = summarize_review(delta_dir)
    assert summary.blocking_dispositioned == 1
    assert summary.all_blocking_resolved is True

  @patch(
    "supekku.scripts.lib.core.git.get_head_sha",
    return_value="a" * 40,
  )
  def test_judgment_status_from_index(self, *_mocks) -> None:
    delta_dir = _create_delta_bundle(self.root)
    _init_workflow_state(delta_dir)
    prime_review(delta_dir, self.root)
    _write_findings(delta_dir)

    summary = summarize_review(delta_dir)
    assert summary.judgment_status == ReviewStatus.IN_PROGRESS
    assert summary.outcome_ready is False

  def test_no_findings_raises(self) -> None:
    delta_dir = _create_delta_bundle(self.root)
    with self.assertRaises(FindingsNotFoundError):
      summarize_review(delta_dir)
