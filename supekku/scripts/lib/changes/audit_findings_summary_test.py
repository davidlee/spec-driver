"""Tests for AuditFindingsSummary and collect_audited_delta_ids.

Covers VT-141-LIST-002, -003, -006.
"""

from __future__ import annotations

from unittest.mock import MagicMock

from supekku.scripts.lib.changes.audit_check import (
  AuditFindingsSummary,
  collect_audited_delta_ids,
)

# ---------------------------------------------------------------------------
# VT-141-LIST-002: Findings summary computation
# ---------------------------------------------------------------------------


class TestAuditFindingsSummary:
  """VT-141-LIST-002"""

  def test_findings_cell_with_data(self) -> None:
    s = AuditFindingsSummary(
      total=7, aligned=3, drift=2, risk=2, disposed=5,
    )
    assert s.findings_cell() == "7 (3a/2d/2r)"

  def test_disposed_cell_with_data(self) -> None:
    s = AuditFindingsSummary(
      total=7, aligned=3, drift=2, risk=2, disposed=5,
    )
    assert s.disposed_cell() == "5/7"

  def test_findings_cell_zero(self) -> None:
    s = AuditFindingsSummary(0, 0, 0, 0, 0)
    assert s.findings_cell() == "–"

  def test_disposed_cell_zero(self) -> None:
    s = AuditFindingsSummary(0, 0, 0, 0, 0)
    assert s.disposed_cell() == "–"

  def test_all_aligned(self) -> None:
    s = AuditFindingsSummary(3, 3, 0, 0, 3)
    assert s.findings_cell() == "3 (3a/0d/0r)"
    assert s.disposed_cell() == "3/3"


# ---------------------------------------------------------------------------
# VT-141-LIST-003: collect_audited_delta_ids
# ---------------------------------------------------------------------------


class TestCollectAuditedDeltaIds:
  """VT-141-LIST-003"""

  def _mock_artifact(
    self,
    *,
    status: str = "completed",
    delta_ref: str | None = "DE-090",
  ) -> MagicMock:
    a = MagicMock()
    a.status = status
    a.delta_ref = delta_ref
    return a

  def test_collects_completed_delta_refs(self) -> None:
    audits = {
      "AUD-001": self._mock_artifact(delta_ref="DE-090"),
      "AUD-002": self._mock_artifact(delta_ref="DE-091"),
    }
    result = collect_audited_delta_ids(audits)
    assert result == {"DE-090", "DE-091"}

  def test_excludes_non_completed(self) -> None:
    audits = {
      "AUD-001": self._mock_artifact(status="draft", delta_ref="DE-090"),
    }
    assert collect_audited_delta_ids(audits) == set()

  def test_excludes_no_delta_ref(self) -> None:
    audits = {
      "AUD-001": self._mock_artifact(delta_ref=None),
    }
    assert collect_audited_delta_ids(audits) == set()

  def test_empty_audits(self) -> None:
    assert collect_audited_delta_ids({}) == set()


# ---------------------------------------------------------------------------
# VT-141-LIST-006: Zero-findings em-dash rendering
# ---------------------------------------------------------------------------


class TestZeroFindingsEmDash:
  """VT-141-LIST-006"""

  def test_em_dash_for_empty(self) -> None:
    s = AuditFindingsSummary(0, 0, 0, 0, 0)
    assert s.findings_cell() == "–"
    assert s.disposed_cell() == "–"
