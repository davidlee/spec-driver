"""Dual-validation tests for problem frontmatter metadata."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .problem import PROBLEM_FRONTMATTER_METADATA


class ProblemFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for problem-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(PROBLEM_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases
  def test_valid_minimal_problem(self) -> None:
    """Both validators accept minimal problem (base fields only)."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_problem_with_all_fields(self) -> None:
    """Both validators accept problem with all optional fields."""
    data = {
      "id": "PROB-012",
      "name": "Slow Sync Performance",
      "slug": "problem-slow-sync",
      "kind": "problem",
      "status": "validated",
      "lifecycle": "discovery",
      "created": "2024-09-10",
      "updated": "2025-01-15",
      "owners": ["product-team"],
      "summary": "Users experience unacceptable sync latency",
      "tags": ["performance", "sync"],
      "problem_statement": "Sync operations take over 15 seconds during peak usage",
      "context": [
        {"type": "research", "id": "UX-023"},
        {"type": "metric", "id": "sync_latency_p99"},
      ],
      "success_criteria": [
        "Users report sync completes within 5s in interviews",
        "P99 latency < 7s for two consecutive releases",
      ],
      "related_requirements": ["PROD-005.FR-02", "SPEC-101.NF-01"],
    }
    self._assert_both_valid(data)

  def test_valid_problem_statement(self) -> None:
    """Both validators accept problem_statement as text."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "problem_statement": "This is a description of the problem",
    }
    self._assert_both_valid(data)

  def test_valid_context_research(self) -> None:
    """Both validators accept context with type=research."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context": [{"type": "research", "id": "UX-023"}],
    }
    self._assert_both_valid(data)

  def test_valid_context_metric(self) -> None:
    """Both validators accept context with type=metric."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context": [{"type": "metric", "id": "sync_latency_p99"}],
    }
    self._assert_both_valid(data)

  def test_valid_context_feedback(self) -> None:
    """Both validators accept context with type=feedback."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context": [{"type": "feedback", "id": "support-ticket-4521"}],
    }
    self._assert_both_valid(data)

  def test_valid_context_observation(self) -> None:
    """Both validators accept context with type=observation."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context": [{"type": "observation", "id": "field-note-12"}],
    }
    self._assert_both_valid(data)

  def test_valid_success_criteria(self) -> None:
    """Both validators accept success_criteria as array of strings."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "success_criteria": [
        "Criterion 1",
        "Criterion 2",
      ],
    }
    self._assert_both_valid(data)

  def test_valid_empty_arrays(self) -> None:
    """Both validators accept empty arrays for problem-specific fields."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context": [],
      "success_criteria": [],
      "related_requirements": [],
    }
    self._assert_both_valid(data)

  # Invalid cases (new validator only)
  def test_invalid_context_type(self) -> None:
    """New validator rejects invalid context type."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context": [{"type": "invalid", "id": "UX-023"}],  # Invalid type
    }
    new_validator = MetadataValidator(PROBLEM_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid context type")

  def test_context_missing_type(self) -> None:
    """New validator rejects context missing type field."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context": [{"id": "UX-023"}],  # Missing type
    }
    new_validator = MetadataValidator(PROBLEM_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject context missing type")

  def test_context_missing_id(self) -> None:
    """New validator rejects context missing id field."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context": [{"type": "research"}],  # Missing id
    }
    new_validator = MetadataValidator(PROBLEM_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject context missing id")

  def test_context_empty_id(self) -> None:
    """New validator rejects context with empty id."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context": [{"type": "research", "id": ""}],  # Empty id
    }
    new_validator = MetadataValidator(PROBLEM_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject context with empty id")

  def test_empty_string_in_success_criteria(self) -> None:
    """New validator rejects empty strings in success_criteria."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "success_criteria": ["Valid criterion", ""],  # Empty string
    }
    new_validator = MetadataValidator(PROBLEM_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty string in success_criteria"
    )

  def test_empty_string_in_related_requirements(self) -> None:
    """New validator rejects empty strings in related_requirements."""
    data = {
      "id": "PROB-001",
      "name": "Test Problem",
      "slug": "test-problem",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "related_requirements": [""],
    }
    new_validator = MetadataValidator(PROBLEM_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty string in related_requirements"
    )


if __name__ == "__main__":
  unittest.main()
