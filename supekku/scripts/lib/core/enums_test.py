"""Tests for enum registry and status validation."""

import pytest

from .enums import get_enum_values, list_enum_paths, validate_status_for_entity


class TestGovernanceEnumValues:
  """Tests for governance artifact status enums (DE-075)."""

  def test_spec_statuses(self) -> None:
    values = get_enum_values("spec.status")
    assert values is not None
    assert set(values) == {"stub", "draft", "active", "deprecated", "archived"}

  def test_adr_statuses(self) -> None:
    values = get_enum_values("adr.status")
    assert values is not None
    assert set(values) == {
      "draft", "proposed", "accepted", "rejected",
      "deprecated", "superseded", "revision-required",
    }

  def test_policy_statuses(self) -> None:
    values = get_enum_values("policy.status")
    assert values is not None
    assert set(values) == {"draft", "required", "deprecated"}

  def test_standard_statuses(self) -> None:
    values = get_enum_values("standard.status")
    assert values is not None
    assert set(values) == {"draft", "required", "default", "deprecated"}

  def test_memory_statuses(self) -> None:
    values = get_enum_values("memory.status")
    assert values is not None
    assert set(values) == {"draft", "active", "review", "superseded", "archived"}

  def test_backlog_base_statuses(self) -> None:
    values = get_enum_values("backlog.status")
    assert values is not None
    assert set(values) == {"open", "triaged", "in-progress", "resolved"}

  def test_risk_statuses_include_extensions(self) -> None:
    values = get_enum_values("risk.status")
    assert values is not None
    assert "accepted" in values
    assert "expired" in values
    assert "open" in values  # base included

  def test_non_risk_backlog_kinds_share_base(self) -> None:
    base = get_enum_values("backlog.status")
    for kind in ("issue", "problem", "improvement"):
      assert get_enum_values(f"{kind}.status") == base, kind


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
    validate_status_for_entity("widget", "anything-goes")  # no enum → accept

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
    validate_status_for_entity("problem", "in-progress")
    validate_status_for_entity("improvement", "triaged")
    validate_status_for_entity("risk", "accepted")

  def test_rejects_invalid_backlog_status(self) -> None:
    with pytest.raises(ValueError, match="Invalid status.*issue"):
      validate_status_for_entity("issue", "bogus")

  def test_accepts_valid_governance_statuses(self) -> None:
    validate_status_for_entity("spec", "active")
    validate_status_for_entity("adr", "accepted")
    validate_status_for_entity("policy", "required")
    validate_status_for_entity("standard", "default")
    validate_status_for_entity("memory", "review")

  def test_rejects_invalid_governance_statuses(self) -> None:
    with pytest.raises(ValueError, match="Invalid status.*spec"):
      validate_status_for_entity("spec", "live")
    with pytest.raises(ValueError, match="Invalid status.*policy"):
      validate_status_for_entity("policy", "active")
    with pytest.raises(ValueError, match="Invalid status.*memory"):
      validate_status_for_entity("memory", "obsolete")


class TestListEnumPaths:
  """Tests for list_enum_paths()."""

  def test_returns_sorted_list(self) -> None:
    paths = list_enum_paths()
    assert paths == sorted(paths)

  def test_includes_expected_entries(self) -> None:
    paths = list_enum_paths()
    for expected in (
      "adr.status",
      "backlog.status",
      "delta.status",
      "drift.status",
      "issue.status",
      "improvement.status",
      "memory.status",
      "policy.status",
      "problem.status",
      "requirement.status",
      "revision.status",
      "risk.status",
      "spec.status",
      "standard.status",
    ):
      assert expected in paths, f"{expected} missing from enum paths"
