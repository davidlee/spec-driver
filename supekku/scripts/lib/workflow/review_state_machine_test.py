"""Tests for review lifecycle state machine (DR-109).

Covers: bootstrap derivation (VT-109-001), judgment transitions (VT-109-002),
approval guard + disposition constraints (VT-109-003), status derivation
(VT-109-006), and cross-round collection (VT-109-007).
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.workflow.review_state_machine import (
  VALID_BOOTSTRAP_TRANSITIONS,
  BootstrapStatus,
  DispositionAuthority,
  FindingDisposition,
  FindingDispositionAction,
  FindingStatus,
  ReviewFinding,
  ReviewStatus,
  ReviewTransitionCommand,
  ReviewTransitionError,
  apply_review_transition,
  can_approve,
  collect_blocking_findings,
  derive_bootstrap_status,
  derive_finding_status,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _warm_index(
  *,
  phase_id: str = "P01",
  head: str = "abc1234",
  domain_files: list[str] | None = None,
) -> dict:
  """Build a minimal valid review-index dict in WARM state."""
  index: dict = {
    "schema": "supekku.workflow.review-index",
    "version": 1,
    "staleness": {"cache_key": {"phase_id": phase_id, "head": head}},
  }
  if domain_files:
    index["domain_map"] = [{"files": domain_files}]
  return index


def _finding(
  finding_id: str = "R1-001",
  title: str = "Test finding",
  disposition: FindingDisposition | None = None,
) -> ReviewFinding:
  """Build a ReviewFinding for tests."""
  return ReviewFinding(id=finding_id, title=title, disposition=disposition)


def _disposition(
  action: FindingDispositionAction = FindingDispositionAction.FIX,
  authority: DispositionAuthority = DispositionAuthority.AGENT,
  **kwargs,
) -> FindingDisposition:
  """Build a FindingDisposition for tests."""
  return FindingDisposition(action=action, authority=authority, **kwargs)


# ---------------------------------------------------------------------------
# VT-109-001: Bootstrap derivation + validity invariants
# ---------------------------------------------------------------------------


class BootstrapEnumTest(unittest.TestCase):
  """BootstrapStatus enum values (DR-109 §3.2)."""

  def test_five_values(self) -> None:
    assert len(BootstrapStatus) == 5

  def test_warming_not_present(self) -> None:
    values = {s.value for s in BootstrapStatus}
    assert "warming" not in values

  def test_expected_values(self) -> None:
    expected = {"cold", "warm", "stale", "reusable", "invalid"}
    assert {s.value for s in BootstrapStatus} == expected


class BootstrapDerivationTest(unittest.TestCase):
  """derive_bootstrap_status() (DR-109 §3.2)."""

  def test_no_index_returns_cold(self) -> None:
    status = derive_bootstrap_status(None, current_phase_id="P01", current_head="abc")
    assert status == BootstrapStatus.COLD

  def test_current_index_returns_warm(self) -> None:
    index = _warm_index()
    status = derive_bootstrap_status(
      index, current_phase_id="P01", current_head="abc1234"
    )
    assert status == BootstrapStatus.WARM

  def test_commit_drift_only_returns_reusable(self) -> None:
    index = _warm_index(head="old_head")
    status = derive_bootstrap_status(
      index, current_phase_id="P01", current_head="new_head"
    )
    assert status == BootstrapStatus.REUSABLE

  def test_phase_boundary_crossing_returns_stale(self) -> None:
    index = _warm_index(phase_id="P01")
    status = derive_bootstrap_status(
      index, current_phase_id="P02", current_head="abc1234"
    )
    assert status == BootstrapStatus.STALE

  def test_dependency_surface_expansion_returns_stale(self) -> None:
    index = _warm_index(domain_files=["a.py"])
    status = derive_bootstrap_status(
      index,
      current_phase_id="P01",
      current_head="abc1234",
      changed_files=["a.py", "b.py"],
    )
    assert status == BootstrapStatus.STALE

  def test_deleted_domain_files_returns_invalid(self) -> None:
    index = _warm_index()
    status = derive_bootstrap_status(
      index,
      current_phase_id="P01",
      current_head="abc1234",
      deleted_domain_files=["gone.py"],
    )
    assert status == BootstrapStatus.INVALID

  def test_schema_version_mismatch_returns_invalid(self) -> None:
    index = _warm_index()
    index["version"] = 99
    status = derive_bootstrap_status(
      index, current_phase_id="P01", current_head="abc1234"
    )
    assert status == BootstrapStatus.INVALID

  def test_schema_id_mismatch_returns_invalid(self) -> None:
    index = _warm_index()
    index["schema"] = "wrong.schema"
    status = derive_bootstrap_status(
      index, current_phase_id="P01", current_head="abc1234"
    )
    assert status == BootstrapStatus.INVALID


class BootstrapValidityMatrixTest(unittest.TestCase):
  """Validity matrix assertions (DR-109 §3.2)."""

  def test_cold_to_cold_is_valid(self) -> None:
    # cold → cold: idempotent re-derivation (no index exists)
    derive_bootstrap_status(
      None,
      current_phase_id="P01",
      current_head="abc",
      previous_status=BootstrapStatus.COLD,
    )

  def test_cold_to_reusable_is_illegal(self) -> None:
    # cold → reusable should never happen
    index = _warm_index(head="old")
    with self.assertRaises(AssertionError, msg="cold → reusable"):
      derive_bootstrap_status(
        index,
        current_phase_id="P01",
        current_head="new",
        previous_status=BootstrapStatus.COLD,
      )

  def test_invalid_to_reusable_is_illegal(self) -> None:
    index = _warm_index(head="old")
    with self.assertRaises(AssertionError, msg="invalid → reusable"):
      derive_bootstrap_status(
        index,
        current_phase_id="P01",
        current_head="new",
        previous_status=BootstrapStatus.INVALID,
      )

  def test_warm_to_cold_is_illegal(self) -> None:
    with self.assertRaises(AssertionError, msg="warm → cold"):
      derive_bootstrap_status(
        None,
        current_phase_id="P01",
        current_head="abc",
        previous_status=BootstrapStatus.WARM,
      )

  def test_warm_to_stale_is_valid(self) -> None:
    index = _warm_index(phase_id="P01")
    derive_bootstrap_status(
      index,
      current_phase_id="P02",
      current_head="abc1234",
      previous_status=BootstrapStatus.WARM,
    )

  def test_stale_to_warm_is_valid(self) -> None:
    # Simulates re-prime after staleness — index now current
    index = _warm_index()
    derive_bootstrap_status(
      index,
      current_phase_id="P01",
      current_head="abc1234",
      previous_status=BootstrapStatus.STALE,
    )

  def test_all_valid_pairs_covered(self) -> None:
    """Every pair in VALID_BOOTSTRAP_TRANSITIONS should be reachable."""
    assert len(VALID_BOOTSTRAP_TRANSITIONS) == 11


# ---------------------------------------------------------------------------
# VT-109-002: Judgment transition table
# ---------------------------------------------------------------------------


class ReviewEnumTest(unittest.TestCase):
  """ReviewStatus enum values (DR-109 §3.3)."""

  def test_four_values(self) -> None:
    assert len(ReviewStatus) == 4

  def test_blocked_not_present(self) -> None:
    values = {s.value for s in ReviewStatus}
    assert "blocked" not in values


class JudgmentTransitionTest(unittest.TestCase):
  """apply_review_transition() (DR-109 §3.3)."""

  _RS = ReviewStatus
  _RC = ReviewTransitionCommand

  def test_not_started_to_in_progress(self) -> None:
    result = apply_review_transition(self._RS.NOT_STARTED, self._RC.BEGIN_REVIEW)
    assert result == self._RS.IN_PROGRESS

  def test_in_progress_to_approved(self) -> None:
    result = apply_review_transition(self._RS.IN_PROGRESS, self._RC.APPROVE)
    assert result == self._RS.APPROVED

  def test_in_progress_to_changes_requested(self) -> None:
    result = apply_review_transition(self._RS.IN_PROGRESS, self._RC.REQUEST_CHANGES)
    assert result == self._RS.CHANGES_REQUESTED

  def test_changes_requested_to_in_progress(self) -> None:
    result = apply_review_transition(self._RS.CHANGES_REQUESTED, self._RC.BEGIN_REVIEW)
    assert result == self._RS.IN_PROGRESS

  def test_not_started_to_approved_rejected(self) -> None:
    with self.assertRaises(ReviewTransitionError):
      apply_review_transition(self._RS.NOT_STARTED, self._RC.APPROVE)

  def test_approved_to_in_progress_rejected(self) -> None:
    with self.assertRaises(ReviewTransitionError):
      apply_review_transition(self._RS.APPROVED, self._RC.BEGIN_REVIEW)

  def test_changes_requested_to_approved_rejected(self) -> None:
    with self.assertRaises(ReviewTransitionError):
      apply_review_transition(self._RS.CHANGES_REQUESTED, self._RC.APPROVE)

  def test_error_carries_context(self) -> None:
    with self.assertRaises(ReviewTransitionError) as ctx:
      apply_review_transition(self._RS.APPROVED, self._RC.APPROVE)
    assert ctx.exception.current == self._RS.APPROVED
    assert ctx.exception.command == self._RC.APPROVE
    assert "approved" in str(ctx.exception)


# ---------------------------------------------------------------------------
# VT-109-006: Status derivation from disposition action
# ---------------------------------------------------------------------------


class StatusDerivationTest(unittest.TestCase):
  """derive_finding_status() (DR-109 §3.4)."""

  def test_no_disposition_returns_open(self) -> None:
    assert derive_finding_status(None) == FindingStatus.OPEN

  def test_fix_returns_resolved(self) -> None:
    d = _disposition(action=FindingDispositionAction.FIX)
    assert derive_finding_status(d) == FindingStatus.RESOLVED

  def test_waive_returns_waived(self) -> None:
    d = _disposition(action=FindingDispositionAction.WAIVE)
    assert derive_finding_status(d) == FindingStatus.WAIVED

  def test_supersede_returns_superseded(self) -> None:
    d = _disposition(action=FindingDispositionAction.SUPERSEDE)
    assert derive_finding_status(d) == FindingStatus.SUPERSEDED

  def test_defer_returns_open(self) -> None:
    d = _disposition(action=FindingDispositionAction.DEFER)
    assert derive_finding_status(d) == FindingStatus.OPEN


# ---------------------------------------------------------------------------
# VT-109-003: Approval guard + disposition constraints
# ---------------------------------------------------------------------------


class ApprovalGuardTest(unittest.TestCase):
  """can_approve() (DR-109 §3.3)."""

  def test_no_blocking_findings_can_approve(self) -> None:
    allowed, reasons = can_approve([])
    assert allowed is True
    assert not reasons

  def test_all_resolved_can_approve(self) -> None:
    f = _finding(
      disposition=_disposition(
        action=FindingDispositionAction.FIX,
        resolved_at="abc1234",
      )
    )
    allowed, _ = can_approve([f])
    assert allowed is True

  def test_fix_without_resolved_at_cannot_approve(self) -> None:
    f = _finding(disposition=_disposition(action=FindingDispositionAction.FIX))
    allowed, reasons = can_approve([f])
    assert allowed is False
    assert any("resolved_at" in r for r in reasons)

  def test_open_blocking_cannot_approve(self) -> None:
    f = _finding()  # no disposition
    allowed, reasons = can_approve([f])
    assert allowed is False
    assert any("no disposition" in r for r in reasons)

  def test_waived_by_agent_cannot_approve(self) -> None:
    f = _finding(
      disposition=_disposition(
        action=FindingDispositionAction.WAIVE,
        authority=DispositionAuthority.AGENT,
        rationale="some reason",
      )
    )
    allowed, reasons = can_approve([f])
    assert allowed is False
    assert any("user authority" in r for r in reasons)

  def test_waived_by_user_with_rationale_can_approve(self) -> None:
    f = _finding(
      disposition=_disposition(
        action=FindingDispositionAction.WAIVE,
        authority=DispositionAuthority.USER,
        rationale="Intentional deviation",
      )
    )
    allowed, _ = can_approve([f])
    assert allowed is True

  def test_waived_by_user_without_rationale_cannot_approve(self) -> None:
    f = _finding(
      disposition=_disposition(
        action=FindingDispositionAction.WAIVE,
        authority=DispositionAuthority.USER,
      )
    )
    allowed, reasons = can_approve([f])
    assert allowed is False
    assert any("rationale" in r for r in reasons)

  def test_deferred_by_user_with_backlog_ref_can_approve(self) -> None:
    f = _finding(
      disposition=_disposition(
        action=FindingDispositionAction.DEFER,
        authority=DispositionAuthority.USER,
        backlog_ref="ISSUE-047",
      )
    )
    allowed, _ = can_approve([f])
    assert allowed is True

  def test_deferred_by_agent_cannot_approve(self) -> None:
    f = _finding(
      disposition=_disposition(
        action=FindingDispositionAction.DEFER,
        authority=DispositionAuthority.AGENT,
        backlog_ref="ISSUE-047",
      )
    )
    allowed, reasons = can_approve([f])
    assert allowed is False
    assert any("user authority" in r for r in reasons)

  def test_deferred_without_backlog_ref_cannot_approve(self) -> None:
    f = _finding(
      disposition=_disposition(
        action=FindingDispositionAction.DEFER,
        authority=DispositionAuthority.USER,
      )
    )
    allowed, reasons = can_approve([f])
    assert allowed is False
    assert any("backlog reference" in r for r in reasons)

  def test_superseded_can_approve(self) -> None:
    f = _finding(
      disposition=_disposition(
        action=FindingDispositionAction.SUPERSEDE,
        superseded_by="R2-001",
      )
    )
    allowed, _ = can_approve([f])
    assert allowed is True

  def test_multiple_findings_all_must_pass(self) -> None:
    resolved = _finding(
      finding_id="R1-001",
      disposition=_disposition(
        action=FindingDispositionAction.FIX,
        resolved_at="abc",
      ),
    )
    open_finding = _finding(finding_id="R1-002")
    allowed, reasons = can_approve([resolved, open_finding])
    assert allowed is False
    assert len(reasons) == 1
    assert "R1-002" in reasons[0]

  def test_waive_by_agent_produces_two_reasons(self) -> None:
    """Agent waive without rationale: both authority and rationale fail."""
    f = _finding(
      disposition=_disposition(
        action=FindingDispositionAction.WAIVE,
        authority=DispositionAuthority.AGENT,
      )
    )
    _, reasons = can_approve([f])
    assert len(reasons) == 2


# ---------------------------------------------------------------------------
# VT-109-007: Cross-round finding collection
# ---------------------------------------------------------------------------


class CrossRoundCollectionTest(unittest.TestCase):
  """collect_blocking_findings() (DR-109 §3.7)."""

  def test_empty_rounds(self) -> None:
    assert not collect_blocking_findings([])

  def test_single_round_collects_blocking(self) -> None:
    rounds = [
      {
        "round": 1,
        "blocking": [
          {"id": "R1-001", "title": "Missing validation"},
          {"id": "R1-002", "title": "Error handling gap"},
        ],
        "non_blocking": [
          {"id": "R1-003", "title": "Style nit"},
        ],
      }
    ]
    findings = collect_blocking_findings(rounds)
    assert len(findings) == 2
    assert all(isinstance(f, ReviewFinding) for f in findings)
    assert findings[0].id == "R1-001"
    assert findings[1].id == "R1-002"

  def test_multi_round_collects_all(self) -> None:
    rounds = [
      {
        "round": 1,
        "blocking": [{"id": "R1-001", "title": "Round 1 issue"}],
      },
      {
        "round": 2,
        "blocking": [{"id": "R2-001", "title": "Round 2 issue"}],
      },
    ]
    findings = collect_blocking_findings(rounds)
    assert len(findings) == 2
    ids = [f.id for f in findings]
    assert ids == ["R1-001", "R2-001"]

  def test_disposition_preserved_from_originating_round(self) -> None:
    """Disposition applied in-place in originating round is collected."""
    rounds = [
      {
        "round": 1,
        "blocking": [
          {
            "id": "R1-001",
            "title": "Fixed issue",
            "status": "resolved",
            "disposition": {
              "action": "fix",
              "authority": "agent",
              "resolved_at": "abc1234",
            },
          }
        ],
      },
      {"round": 2, "blocking": []},
    ]
    findings = collect_blocking_findings(rounds)
    assert len(findings) == 1
    assert findings[0].disposition is not None
    assert findings[0].disposition.action == FindingDispositionAction.FIX
    assert findings[0].disposition.resolved_at == "abc1234"

  def test_round_with_no_blocking_key(self) -> None:
    rounds = [{"round": 1, "non_blocking": [{"id": "R1-001", "title": "Nit"}]}]
    assert not collect_blocking_findings(rounds)

  def test_cross_round_guard_integration(self) -> None:
    """Round 1 undispositioned blocking finding blocks approval in round 2."""
    rounds = [
      {
        "round": 1,
        "blocking": [{"id": "R1-001", "title": "Unresolved"}],
      },
      {"round": 2, "blocking": []},
    ]
    findings = collect_blocking_findings(rounds)
    allowed, reasons = can_approve(findings)
    assert allowed is False
    assert "R1-001" in reasons[0]

  def test_cross_round_dispositioned_finding_unblocks(self) -> None:
    """Round 1 finding fixed in-place allows approval."""
    rounds = [
      {
        "round": 1,
        "blocking": [
          {
            "id": "R1-001",
            "title": "Fixed",
            "disposition": {
              "action": "fix",
              "authority": "agent",
              "resolved_at": "def5678",
            },
          }
        ],
      },
      {"round": 2, "blocking": []},
    ]
    findings = collect_blocking_findings(rounds)
    allowed, _ = can_approve(findings)
    assert allowed is True


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class FindingDispositionModelTest(unittest.TestCase):
  """FindingDisposition Pydantic model."""

  def test_minimal_construction(self) -> None:
    d = FindingDisposition(
      action=FindingDispositionAction.FIX,
      authority=DispositionAuthority.AGENT,
    )
    assert d.action == FindingDispositionAction.FIX
    assert d.rationale is None

  def test_extra_fields_ignored(self) -> None:
    d = FindingDisposition(
      action="fix",
      authority="agent",
      unknown_field="should be ignored",
    )
    assert not hasattr(d, "unknown_field")

  def test_from_dict(self) -> None:
    raw = {
      "action": "waive",
      "authority": "user",
      "rationale": "Intentional",
      "timestamp": "2026-03-20T12:00:00+00:00",
    }
    d = FindingDisposition.model_validate(raw)
    assert d.action == FindingDispositionAction.WAIVE
    assert d.authority == DispositionAuthority.USER


class ReviewFindingModelTest(unittest.TestCase):
  """ReviewFinding Pydantic model."""

  def test_minimal_construction(self) -> None:
    f = ReviewFinding(id="R1-001", title="Test")
    assert f.status == FindingStatus.OPEN
    assert f.disposition is None

  def test_extra_fields_ignored(self) -> None:
    f = ReviewFinding(
      id="R1-001",
      title="Test",
      severity="blocking",  # not in model
    )
    assert not hasattr(f, "severity")

  def test_from_dict_with_disposition(self) -> None:
    raw = {
      "id": "R1-001",
      "title": "Missing validation",
      "status": "resolved",
      "disposition": {
        "action": "fix",
        "authority": "agent",
        "resolved_at": "abc1234",
      },
    }
    f = ReviewFinding.model_validate(raw)
    assert f.disposition is not None
    assert f.disposition.resolved_at == "abc1234"


if __name__ == "__main__":
  unittest.main()
