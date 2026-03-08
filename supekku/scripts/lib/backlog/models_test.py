"""Tests for backlog models and status vocabulary (VT-057 + VT-075)."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.backlog.models import (
  ALL_VALID_STATUSES,
  BACKLOG_BASE_STATUSES,
  BACKLOG_STATUSES,
  DEFAULT_HIDDEN_STATUSES,
  RISK_EXTRA_STATUSES,
  RISK_STATUSES,
  is_valid_status,
)


class UnifiedStatusSetsTest(unittest.TestCase):
  """Test unified backlog status sets (DEC-075-05)."""

  def test_base_statuses(self) -> None:
    assert (
      frozenset(
        {
          "open",
          "triaged",
          "in-progress",
          "resolved",
        }
      )
      == BACKLOG_BASE_STATUSES
    )

  def test_risk_extra_statuses(self) -> None:
    assert frozenset({"accepted", "expired"}) == RISK_EXTRA_STATUSES

  def test_risk_statuses_is_superset_of_base(self) -> None:
    assert RISK_STATUSES == BACKLOG_BASE_STATUSES | RISK_EXTRA_STATUSES

  def test_backlog_statuses_covers_all_kinds(self) -> None:
    assert set(BACKLOG_STATUSES.keys()) == {"issue", "problem", "improvement", "risk"}

  def test_non_risk_kinds_share_base(self) -> None:
    for kind in ("issue", "problem", "improvement"):
      assert BACKLOG_STATUSES[kind] is BACKLOG_BASE_STATUSES, kind

  def test_risk_kind_has_extensions(self) -> None:
    assert BACKLOG_STATUSES["risk"] is RISK_STATUSES

  def test_default_hidden_statuses(self) -> None:
    assert frozenset({"resolved"}) == DEFAULT_HIDDEN_STATUSES

  def test_all_valid_statuses(self) -> None:
    assert ALL_VALID_STATUSES == BACKLOG_BASE_STATUSES | RISK_EXTRA_STATUSES

  def test_sets_are_frozen(self) -> None:
    for s in (BACKLOG_BASE_STATUSES, RISK_EXTRA_STATUSES, RISK_STATUSES):
      assert isinstance(s, frozenset)


class IsValidStatusTest(unittest.TestCase):
  """Test is_valid_status() helper."""

  def test_base_status_valid_for_all_kinds(self) -> None:
    for kind in ("issue", "problem", "improvement", "risk"):
      assert is_valid_status(kind, "open") is True

  def test_risk_extra_valid_for_risk(self) -> None:
    assert is_valid_status("risk", "accepted") is True
    assert is_valid_status("risk", "expired") is True

  def test_risk_extra_invalid_for_non_risk(self) -> None:
    with self.assertLogs("supekku.scripts.lib.backlog.models", level="WARNING"):
      result = is_valid_status("issue", "accepted")
    assert result is False

  def test_unknown_status_returns_false(self) -> None:
    with self.assertLogs("supekku.scripts.lib.backlog.models", level="WARNING"):
      result = is_valid_status("issue", "xyzzy")
    assert result is False

  def test_unknown_kind_returns_false(self) -> None:
    with self.assertLogs("supekku.scripts.lib.backlog.models", level="WARNING"):
      result = is_valid_status("nonsense", "open")
    assert result is False

  def test_terminal_statuses_are_valid(self) -> None:
    for status in DEFAULT_HIDDEN_STATUSES:
      assert status in ALL_VALID_STATUSES, f"{status} not in any kind's status set"


class BacklogItemExtFieldsTest(unittest.TestCase):
  """VT-067-001: BacklogItem supports ext_id and ext_url fields."""

  def test_ext_fields_default_to_empty(self) -> None:
    from pathlib import Path  # noqa: PLC0415

    from supekku.scripts.lib.backlog.models import BacklogItem  # noqa: PLC0415

    item = BacklogItem(
      id="ISSUE-001", kind="issue", status="open", title="Test", path=Path()
    )
    assert item.ext_id == ""
    assert item.ext_url == ""

  def test_ext_fields_populated(self) -> None:
    from pathlib import Path  # noqa: PLC0415

    from supekku.scripts.lib.backlog.models import BacklogItem  # noqa: PLC0415

    item = BacklogItem(
      id="ISSUE-002",
      kind="issue",
      status="open",
      title="Test",
      path=Path(),
      ext_id="JIRA-999",
      ext_url="https://jira.example.com/JIRA-999",
    )
    assert item.ext_id == "JIRA-999"
    assert item.ext_url == "https://jira.example.com/JIRA-999"


if __name__ == "__main__":
  unittest.main()
