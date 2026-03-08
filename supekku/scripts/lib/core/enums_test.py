"""Tests for enum registry and status validation."""

import pytest

from .enums import get_enum_values, list_enum_paths, validate_status_for_entity


class TestGetEnumValues:
  """Tests for get_enum_values()."""

  def test_returns_sorted_list_for_known_path(self) -> None:
    values = get_enum_values("delta.status")
    assert isinstance(values, list)
    assert values == sorted(values)
    assert "draft" in values
    assert "in-progress" in values

  def test_returns_none_for_unknown_path(self) -> None:
    assert get_enum_values("nonexistent.field") is None

  def test_revision_status_matches_delta_status(self) -> None:
    assert get_enum_values("revision.status") == get_enum_values("delta.status")

  def test_audit_status_matches_delta_status(self) -> None:
    assert get_enum_values("audit.status") == get_enum_values("delta.status")

  def test_backlog_kind_statuses_registered(self) -> None:
    for kind in ("issue", "problem", "improvement", "risk"):
      values = get_enum_values(f"{kind}.status")
      assert values is not None, f"{kind}.status not registered"
      assert len(values) > 0

  def test_drift_status_registered(self) -> None:
    values = get_enum_values("drift.status")
    assert values is not None
    assert "open" in values
    assert "closed" in values

  def test_change_statuses_exclude_legacy_complete(self) -> None:
    for path in ("delta.status", "revision.status", "audit.status"):
      values = get_enum_values(path)
      assert "complete" not in values, f"'complete' should be excluded from {path}"
      assert "completed" in values


class TestValidateStatusForEntity:
  """Tests for validate_status_for_entity()."""

  def test_accepts_valid_delta_status(self) -> None:
    validate_status_for_entity("delta", "in-progress")  # should not raise

  def test_rejects_invalid_delta_status(self) -> None:
    with pytest.raises(ValueError, match="Invalid status.*delta"):
      validate_status_for_entity("delta", "bogus")

  def test_error_message_lists_valid_values(self) -> None:
    with pytest.raises(ValueError, match="Valid values:"):
      validate_status_for_entity("issue", "nonexistent")

  def test_accepts_any_status_for_unknown_entity(self) -> None:
    validate_status_for_entity("spec", "anything-goes")  # no enum → accept

  def test_rejects_empty_status(self) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
      validate_status_for_entity("delta", "")

  def test_rejects_whitespace_only_status(self) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
      validate_status_for_entity("delta", "  ")

  def test_accepts_valid_drift_status(self) -> None:
    validate_status_for_entity("drift", "open")

  def test_rejects_invalid_drift_status(self) -> None:
    with pytest.raises(ValueError, match="Invalid status.*drift"):
      validate_status_for_entity("drift", "bogus")

  def test_accepts_valid_backlog_statuses(self) -> None:
    validate_status_for_entity("issue", "open")
    validate_status_for_entity("problem", "captured")
    validate_status_for_entity("improvement", "idea")
    validate_status_for_entity("risk", "suspected")


class TestListEnumPaths:
  """Tests for list_enum_paths()."""

  def test_returns_sorted_list(self) -> None:
    paths = list_enum_paths()
    assert paths == sorted(paths)

  def test_includes_new_entries(self) -> None:
    paths = list_enum_paths()
    for expected in (
      "issue.status",
      "problem.status",
      "improvement.status",
      "risk.status",
      "drift.status",
      "revision.status",
      "audit.status",
    ):
      assert expected in paths, f"{expected} missing from enum paths"
