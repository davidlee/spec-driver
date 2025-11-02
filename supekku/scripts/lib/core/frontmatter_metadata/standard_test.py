"""Dual-validation tests for standard frontmatter metadata."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .standard import STANDARD_FRONTMATTER_METADATA


class StandardFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for standard-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(STANDARD_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases
  def test_valid_minimal_standard(self) -> None:
    """Both validators accept minimal standard (base fields only)."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_standard_with_all_fields(self) -> None:
    """Both validators accept standard with all optional fields."""
    data = {
      "id": "STD-015",
      "name": "Python Coding Standards",
      "slug": "standard-python-coding",
      "kind": "standard",
      "status": "default",
      "lifecycle": "maintenance",
      "created": "2024-02-15",
      "updated": "2025-01-15",
      "reviewed": "2025-01-05",
      "owners": ["engineering-standards"],
      "auditers": ["quality-team"],
      "summary": "Defines code style and testing practices",
      "tags": ["python", "code-quality"],
      "supersedes": ["STD-008"],
      "policies": ["POL-042"],
      "specs": ["SPEC-101"],
      "requirements": ["SPEC-101.NF-02"],
      "deltas": ["DE-050"],
      "related_policies": ["POL-043"],
      "related_standards": ["STD-016"],
    }
    self._assert_both_valid(data)

  def test_valid_reviewed_date(self) -> None:
    """Both validators accept valid reviewed date."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "reviewed": "2025-01-10",
    }
    self._assert_both_valid(data)

  def test_valid_empty_arrays(self) -> None:
    """Both validators accept empty arrays for standard-specific fields."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "supersedes": [],
      "superseded_by": [],
      "policies": [],
      "specs": [],
      "requirements": [],
      "deltas": [],
      "related_policies": [],
      "related_standards": [],
    }
    self._assert_both_valid(data)

  def test_valid_status_default(self) -> None:
    """Both validators accept status=default for standards."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "default",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_status_required(self) -> None:
    """Both validators accept status=required for standards."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "required",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  # Invalid cases (new validator only)
  def test_invalid_reviewed_date_format(self) -> None:
    """New validator rejects invalid reviewed date format."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "reviewed": "2025/01/10",  # Wrong format
    }
    new_validator = MetadataValidator(STANDARD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid date format")

  def test_invalid_supersedes_id_format(self) -> None:
    """New validator rejects invalid supersedes ID format."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "supersedes": ["STANDARD-001"],  # Wrong format, should be STD-001
    }
    new_validator = MetadataValidator(STANDARD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid standard ID format")

  def test_invalid_superseded_by_id_format(self) -> None:
    """New validator rejects invalid superseded_by ID format."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "superseded_by": ["STD-1"],  # Missing leading zeros
    }
    new_validator = MetadataValidator(STANDARD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid superseded_by ID format")

  def test_invalid_policies_id_format(self) -> None:
    """New validator rejects invalid policies ID format."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "policies": ["POLICY-001"],  # Wrong format, should be POL-001
    }
    new_validator = MetadataValidator(STANDARD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid policy ID format")

  def test_invalid_related_policies_id_format(self) -> None:
    """New validator rejects invalid related_policies ID format."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "related_policies": ["POL-1234"],  # Too many digits
    }
    new_validator = MetadataValidator(STANDARD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject invalid related_policies ID format"
    )

  def test_invalid_related_standards_id_format(self) -> None:
    """New validator rejects invalid related_standards ID format."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "related_standards": ["STD-12"],  # Missing one digit
    }
    new_validator = MetadataValidator(STANDARD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject invalid related_standards ID format"
    )

  def test_supersedes_not_array(self) -> None:
    """New validator rejects supersedes when not an array."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "supersedes": "STD-002",  # Should be array
    }
    new_validator = MetadataValidator(STANDARD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject supersedes as non-array")

  def test_empty_string_in_specs_array(self) -> None:
    """New validator rejects empty strings in specs array."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "specs": ["SPEC-001", ""],  # Empty string
    }
    new_validator = MetadataValidator(STANDARD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in specs")

  def test_empty_string_in_requirements_array(self) -> None:
    """New validator rejects empty strings in requirements array."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "requirements": [""],
    }
    new_validator = MetadataValidator(STANDARD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in requirements")

  def test_empty_string_in_deltas_array(self) -> None:
    """New validator rejects empty strings in deltas array."""
    data = {
      "id": "STD-001",
      "name": "Test Standard",
      "slug": "test-standard",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "deltas": ["DE-001", "", "DE-002"],
    }
    new_validator = MetadataValidator(STANDARD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in deltas")


if __name__ == "__main__":
  unittest.main()
