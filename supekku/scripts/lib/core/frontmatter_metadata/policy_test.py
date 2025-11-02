"""Dual-validation tests for policy frontmatter metadata."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .policy import POLICY_FRONTMATTER_METADATA


class PolicyFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for policy-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(POLICY_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases
  def test_valid_minimal_policy(self) -> None:
    """Both validators accept minimal policy (base fields only)."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_policy_with_all_fields(self) -> None:
    """Both validators accept policy with all optional fields."""
    data = {
      "id": "POL-042",
      "name": "Code Review and Approval Policy",
      "slug": "policy-code-review",
      "kind": "policy",
      "status": "required",
      "lifecycle": "maintenance",
      "created": "2024-03-10",
      "updated": "2025-01-15",
      "reviewed": "2025-01-10",
      "owners": ["engineering-leads"],
      "auditers": ["quality-team"],
      "summary": "Mandates peer review for all production code changes",
      "tags": ["quality", "governance"],
      "supersedes": ["POL-012", "POL-023"],
      "standards": ["STD-001", "STD-015"],
      "specs": ["SPEC-101"],
      "requirements": ["SPEC-101.FR-05"],
      "deltas": ["DE-042"],
      "related_policies": ["POL-043"],
      "related_standards": ["STD-002"],
    }
    self._assert_both_valid(data)

  def test_valid_reviewed_date(self) -> None:
    """Both validators accept valid reviewed date."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "reviewed": "2025-01-10",
    }
    self._assert_both_valid(data)

  def test_valid_empty_arrays(self) -> None:
    """Both validators accept empty arrays for policy-specific fields."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "supersedes": [],
      "superseded_by": [],
      "standards": [],
      "specs": [],
      "requirements": [],
      "deltas": [],
      "related_policies": [],
      "related_standards": [],
    }
    self._assert_both_valid(data)

  # Invalid cases (new validator only)
  def test_invalid_reviewed_date_format(self) -> None:
    """New validator rejects invalid reviewed date format."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "reviewed": "2025/01/10",  # Wrong format
    }
    new_validator = MetadataValidator(POLICY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid date format")

  def test_invalid_supersedes_id_format(self) -> None:
    """New validator rejects invalid supersedes ID format."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "supersedes": ["POLICY-001"],  # Wrong format, should be POL-001
    }
    new_validator = MetadataValidator(POLICY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid policy ID format")

  def test_invalid_superseded_by_id_format(self) -> None:
    """New validator rejects invalid superseded_by ID format."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "superseded_by": ["POL-1"],  # Missing leading zeros
    }
    new_validator = MetadataValidator(POLICY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid superseded_by ID format")

  def test_invalid_standards_id_format(self) -> None:
    """New validator rejects invalid standards ID format."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "standards": ["STANDARD-001"],  # Wrong format, should be STD-001
    }
    new_validator = MetadataValidator(POLICY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid standard ID format")

  def test_invalid_related_policies_id_format(self) -> None:
    """New validator rejects invalid related_policies ID format."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "related_policies": ["POL-1234"],  # Too many digits
    }
    new_validator = MetadataValidator(POLICY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject invalid related_policies ID format"
    )

  def test_invalid_related_standards_id_format(self) -> None:
    """New validator rejects invalid related_standards ID format."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "related_standards": ["STD-12"],  # Missing one digit
    }
    new_validator = MetadataValidator(POLICY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject invalid related_standards ID format"
    )

  def test_supersedes_not_array(self) -> None:
    """New validator rejects supersedes when not an array."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "supersedes": "POL-002",  # Should be array
    }
    new_validator = MetadataValidator(POLICY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject supersedes as non-array")

  def test_empty_string_in_specs_array(self) -> None:
    """New validator rejects empty strings in specs array."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "specs": ["SPEC-001", ""],  # Empty string
    }
    new_validator = MetadataValidator(POLICY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in specs")

  def test_empty_string_in_requirements_array(self) -> None:
    """New validator rejects empty strings in requirements array."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "requirements": [""],
    }
    new_validator = MetadataValidator(POLICY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in requirements")

  def test_empty_string_in_deltas_array(self) -> None:
    """New validator rejects empty strings in deltas array."""
    data = {
      "id": "POL-001",
      "name": "Test Policy",
      "slug": "test-policy",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "deltas": ["DE-001", "", "DE-002"],
    }
    new_validator = MetadataValidator(POLICY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in deltas")


if __name__ == "__main__":
  unittest.main()
