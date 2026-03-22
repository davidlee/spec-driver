"""Tests for requirement data models."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.requirements.models import RequirementRecord


class TestRequirementRecordToDict(unittest.TestCase):
  """Tests for RequirementRecord.to_dict() serialization."""

  def test_to_dict_omits_ext_id_ext_url_when_empty(self) -> None:
    """Empty ext_id/ext_url should not appear in serialized dict."""
    record = RequirementRecord(uid="SPEC-100.FR-001", label="FR-001", title="Test")

    result = record.to_dict()

    assert "ext_id" not in result
    assert "ext_url" not in result

  def test_to_dict_includes_ext_id_ext_url_when_set(self) -> None:
    """Populated ext_id/ext_url should appear in serialized dict."""
    record = RequirementRecord(
      uid="SPEC-100.FR-002",
      label="FR-002",
      title="External Req",
      ext_id="JIRA-1234",
      ext_url="https://jira.example.com/JIRA-1234",
    )

    result = record.to_dict()

    assert result["ext_id"] == "JIRA-1234"
    assert result["ext_url"] == "https://jira.example.com/JIRA-1234"

  def test_to_dict_ext_id_only(self) -> None:
    """ext_id without ext_url — only ext_id appears."""
    record = RequirementRecord(
      uid="SPEC-100.FR-003",
      label="FR-003",
      title="ID-Only",
      ext_id="GH-99",
    )

    result = record.to_dict()

    assert result["ext_id"] == "GH-99"
    assert "ext_url" not in result


if __name__ == "__main__":
  unittest.main()
