"""Dual-validation tests for issue frontmatter metadata."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .issue import ISSUE_FRONTMATTER_METADATA


class IssueFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for issue-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(ISSUE_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases
  def test_valid_minimal_issue(self) -> None:
    """Both validators accept minimal issue (base fields only)."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_issue_with_all_fields(self) -> None:
    """Both validators accept issue with all optional fields."""
    data = {
      "id": "ISSUE-234",
      "name": "Token Refresh Fails on Slow Networks",
      "slug": "issue-token-refresh-slow-network",
      "kind": "issue",
      "status": "triaged",
      "lifecycle": "implementation",
      "created": "2024-11-05",
      "updated": "2025-01-15",
      "owners": ["auth-team"],
      "summary": "OAuth2 token refresh fails when network latency exceeds 5 seconds",
      "tags": ["auth", "reliability"],
      "categories": ["regression", "verification_gap"],
      "severity": "p2",
      "impact": "user",
      "problem_refs": ["PROB-012"],
      "related_requirements": ["SPEC-101.FR-01"],
      "affected_verifications": ["VT-210"],
      "linked_deltas": ["DE-021"],
    }
    self._assert_both_valid(data)

  def test_valid_categories_array(self) -> None:
    """Both validators accept categories as array."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "categories": ["regression", "verification_gap", "enhancement"],
    }
    self._assert_both_valid(data)

  def test_valid_severity_values(self) -> None:
    """Both validators accept all severity enum values."""
    for severity in ["p1", "p2", "p3", "p4"]:
      with self.subTest(severity=severity):
        data = {
          "id": "ISSUE-001",
          "name": "Test Issue",
          "slug": "test-issue",
          "kind": "issue",
          "status": "open",
          "created": "2025-01-15",
          "updated": "2025-01-15",
          "severity": severity,
        }
        self._assert_both_valid(data)

  def test_valid_impact_user(self) -> None:
    """Both validators accept impact=user."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "impact": "user",
    }
    self._assert_both_valid(data)

  def test_valid_impact_systemic(self) -> None:
    """Both validators accept impact=systemic."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "impact": "systemic",
    }
    self._assert_both_valid(data)

  def test_valid_impact_process(self) -> None:
    """Both validators accept impact=process."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "impact": "process",
    }
    self._assert_both_valid(data)

  def test_valid_empty_arrays(self) -> None:
    """Both validators accept empty arrays for issue-specific fields."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "categories": [],
      "problem_refs": [],
      "related_requirements": [],
      "affected_verifications": [],
      "linked_deltas": [],
    }
    self._assert_both_valid(data)

  # Invalid cases (new validator only)
  def test_invalid_severity(self) -> None:
    """New validator rejects invalid severity."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "severity": "critical",  # Not in enum
    }
    new_validator = MetadataValidator(ISSUE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid severity")

  def test_invalid_impact(self) -> None:
    """New validator rejects invalid impact."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "impact": "business",  # Not in enum
    }
    new_validator = MetadataValidator(ISSUE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid impact")

  def test_empty_string_in_categories(self) -> None:
    """New validator rejects empty strings in categories."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "categories": ["regression", ""],
    }
    new_validator = MetadataValidator(ISSUE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty string in categories"
    )

  def test_empty_string_in_problem_refs(self) -> None:
    """New validator rejects empty strings in problem_refs."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "problem_refs": [""],
    }
    new_validator = MetadataValidator(ISSUE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty string in problem_refs"
    )

  def test_empty_string_in_related_requirements(self) -> None:
    """New validator rejects empty strings in related_requirements."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "related_requirements": ["SPEC-101.FR-01", ""],
    }
    new_validator = MetadataValidator(ISSUE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty string in related_requirements"
    )

  def test_empty_string_in_affected_verifications(self) -> None:
    """New validator rejects empty strings in affected_verifications."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "affected_verifications": ["VT-210", ""],
    }
    new_validator = MetadataValidator(ISSUE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty string in affected_verifications"
    )

  def test_empty_string_in_linked_deltas(self) -> None:
    """New validator rejects empty strings in linked_deltas."""
    data = {
      "id": "ISSUE-001",
      "name": "Test Issue",
      "slug": "test-issue",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "linked_deltas": [""],
    }
    new_validator = MetadataValidator(ISSUE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty string in linked_deltas"
    )


if __name__ == "__main__":
  unittest.main()
