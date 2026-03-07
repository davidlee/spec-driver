"""Tests for backlog models and status vocabulary (VT-057-status-enums)."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.backlog.models import (
  BACKLOG_STATUSES,
  DEFAULT_HIDDEN_STATUSES,
  IMPROVEMENT_STATUSES,
  ISSUE_STATUSES,
  PROBLEM_STATUSES,
  RISK_STATUSES,
  is_valid_status,
)


class StatusSetsTest(unittest.TestCase):
  """Test per-kind status frozensets."""

  def test_issue_default_in_set(self) -> None:
    assert "open" in ISSUE_STATUSES

  def test_problem_default_in_set(self) -> None:
    assert "captured" in PROBLEM_STATUSES

  def test_improvement_default_in_set(self) -> None:
    assert "idea" in IMPROVEMENT_STATUSES

  def test_risk_default_in_set(self) -> None:
    assert "suspected" in RISK_STATUSES

  def test_backlog_statuses_covers_all_kinds(self) -> None:
    assert set(BACKLOG_STATUSES.keys()) == {"issue", "problem", "improvement", "risk"}

  def test_default_hidden_matches_current_behaviour(self) -> None:
    """DEFAULT_HIDDEN_STATUSES must match current list_backlog() exclusion."""
    assert frozenset({"resolved", "implemented"}) == DEFAULT_HIDDEN_STATUSES


class IsValidStatusTest(unittest.TestCase):
  """Test is_valid_status() helper."""

  def test_known_status_returns_true(self) -> None:
    assert is_valid_status("issue", "open") is True
    assert is_valid_status("problem", "captured") is True
    assert is_valid_status("improvement", "idea") is True
    assert is_valid_status("risk", "suspected") is True

  def test_unknown_status_returns_false(self) -> None:
    with self.assertLogs("supekku.scripts.lib.backlog.models", level="WARNING"):
      result = is_valid_status("issue", "xyzzy")
    assert result is False

  def test_unknown_kind_returns_false(self) -> None:
    with self.assertLogs("supekku.scripts.lib.backlog.models", level="WARNING"):
      result = is_valid_status("nonsense", "open")
    assert result is False

  def test_terminal_statuses_are_valid(self) -> None:
    """All DEFAULT_HIDDEN_STATUSES must be valid for at least one kind."""
    from supekku.scripts.lib.backlog.models import ALL_VALID_STATUSES  # noqa: PLC0415

    for status in DEFAULT_HIDDEN_STATUSES:
      assert status in ALL_VALID_STATUSES, f"{status} not in any kind's status set"


if __name__ == "__main__":
  unittest.main()
