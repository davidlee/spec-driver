"""Tests for cross-reference checks."""

from __future__ import annotations

import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from supekku.scripts.lib.diagnostics.checks.refs import CATEGORY, check_refs
from supekku.scripts.lib.validation.validator import ValidationIssue


@dataclass
class _FakeWorkspace:
  root: Path


class TestCheckRefs(unittest.TestCase):
  """Tests for check_refs function."""

  def setUp(self) -> None:
    self.ws = _FakeWorkspace(root=Path("/fake"))

  @patch("supekku.scripts.lib.diagnostics.checks.refs.validate_workspace")
  def test_no_issues_passes(self, mock_validate: object) -> None:
    """No validation issues should produce a single pass result."""
    mock_validate.return_value = []  # type: ignore[attr-defined]
    results = check_refs(self.ws)
    assert len(results) == 1
    assert results[0].status == "pass"
    assert results[0].name == "cross-references"

  @patch("supekku.scripts.lib.diagnostics.checks.refs.validate_workspace")
  def test_error_translates_to_fail(self, mock_validate: object) -> None:
    """Validator error level should translate to fail status."""
    mock_validate.return_value = [  # type: ignore[attr-defined]
      ValidationIssue(level="error", message="missing delta DE-999", artifact="FR-001"),
    ]
    results = check_refs(self.ws)
    assert len(results) == 1
    assert results[0].status == "fail"
    assert results[0].name == "FR-001"
    assert "DE-999" in results[0].message

  @patch("supekku.scripts.lib.diagnostics.checks.refs.validate_workspace")
  def test_warning_translates_to_warn(self, mock_validate: object) -> None:
    """Validator warning level should translate to warn status."""
    mock_validate.return_value = [  # type: ignore[attr-defined]
      ValidationIssue(level="warning", message="stale ref", artifact="SPEC-010"),
    ]
    results = check_refs(self.ws)
    assert len(results) == 1
    assert results[0].status == "warn"

  @patch("supekku.scripts.lib.diagnostics.checks.refs.validate_workspace")
  def test_info_translates_to_pass(self, mock_validate: object) -> None:
    """Validator info level should translate to pass status."""
    mock_validate.return_value = [  # type: ignore[attr-defined]
      ValidationIssue(level="info", message="planned verification", artifact="FR-002"),
    ]
    results = check_refs(self.ws)
    assert len(results) == 1
    assert results[0].status == "pass"

  @patch("supekku.scripts.lib.diagnostics.checks.refs.validate_workspace")
  def test_multiple_issues(self, mock_validate: object) -> None:
    """Multiple issues should produce one result per issue."""
    mock_validate.return_value = [  # type: ignore[attr-defined]
      ValidationIssue(level="error", message="bad ref", artifact="DE-001"),
      ValidationIssue(level="warning", message="stale", artifact="SPEC-002"),
      ValidationIssue(level="info", message="ok", artifact="FR-003"),
    ]
    results = check_refs(self.ws)
    assert len(results) == 3
    statuses = [r.status for r in results]
    assert statuses == ["fail", "warn", "pass"]

  @patch("supekku.scripts.lib.diagnostics.checks.refs.validate_workspace")
  def test_validator_exception_produces_fail(self, mock_validate: object) -> None:
    """If the validator raises, check_refs should return a fail result."""
    mock_validate.side_effect = RuntimeError("boom")  # type: ignore[attr-defined]
    results = check_refs(self.ws)
    assert len(results) == 1
    assert results[0].status == "fail"
    assert "boom" in results[0].message
    assert results[0].name == "validator"

  @patch("supekku.scripts.lib.diagnostics.checks.refs.validate_workspace")
  def test_all_results_have_refs_category(self, mock_validate: object) -> None:
    """Every result should use the refs category."""
    mock_validate.return_value = [  # type: ignore[attr-defined]
      ValidationIssue(level="error", message="bad", artifact="X-1"),
    ]
    results = check_refs(self.ws)
    assert all(r.category == CATEGORY for r in results)


if __name__ == "__main__":
  unittest.main()
