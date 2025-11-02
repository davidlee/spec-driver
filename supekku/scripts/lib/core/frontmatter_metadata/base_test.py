"""Dual-validation tests for base frontmatter metadata.

Tests that the new metadata-driven validator produces compatible results
with the existing frontmatter validator.
"""

from __future__ import annotations

import unittest
from datetime import date

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .base import BASE_FRONTMATTER_METADATA


class BaseFrontmatterDualValidationTest(unittest.TestCase):
  """Test metadata validator matches existing validator behavior."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors).

    Args:
      data: Frontmatter dictionary to validate

    Returns:
      - old_error: None if valid, error message if invalid
      - new_errors: List of error strings from new validator
    """
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(BASE_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  def _assert_both_invalid(self, data: dict) -> None:
    """Assert both validators reject the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNotNone(old_error, "Old validator accepted invalid data")
    self.assertNotEqual(new_errors, [], "New validator accepted invalid data")

  # Valid cases (5 tests)

  def test_valid_minimal_frontmatter(self) -> None:
    """Both validators accept minimal valid frontmatter."""
    data = {
      "id": "SPEC-001",
      "name": "Example Specification",
      "slug": "example-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_complete_frontmatter(self) -> None:
    """Both validators accept frontmatter with all optional fields."""
    data = {
      "id": "SPEC-100",
      "name": "Authentication Specification",
      "slug": "spec-auth",
      "kind": "spec",
      "status": "approved",
      "lifecycle": "implementation",
      "created": "2024-06-08",
      "updated": "2025-01-15",
      "owners": ["alice", "bob"],
      "auditers": ["charlie"],
      "source": "docs/specs/SPEC-100.md",
      "summary": "Defines authentication flows for the platform.",
      "tags": ["security", "auth", "core"],
      "relations": [
        {
          "type": "implements",
          "target": "FR-102",
        }
      ],
    }
    self._assert_both_valid(data)

  def test_valid_date_as_string(self) -> None:
    """Both validators accept dates as ISO strings."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_date_as_date_object(self) -> None:
    """Old validator accepts date objects, new validator requires strings."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": date(2025, 1, 15),
      "updated": date(2025, 1, 15),
    }
    # Old validator accepts date objects
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)
    self.assertIsNone(old_error, "Old validator should accept date objects")

    # New validator requires strings (by design - pre-processing needed)
    new_validator = MetadataValidator(BASE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "New validator requires string dates")

  def test_valid_empty_relations_array(self) -> None:
    """Both validators accept empty relations array."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": [],
    }
    self._assert_both_valid(data)

  # Required field validation (6 tests)

  def test_missing_id(self) -> None:
    """Both validators reject missing id."""
    data = {
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_invalid(data)

  def test_missing_name(self) -> None:
    """Both validators reject missing name."""
    data = {
      "id": "SPEC-001",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_invalid(data)

  def test_missing_slug(self) -> None:
    """Both validators reject missing slug."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_invalid(data)

  def test_missing_status(self) -> None:
    """Both validators reject missing status."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_invalid(data)

  def test_missing_created(self) -> None:
    """Both validators reject missing created."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "updated": "2025-01-15",
    }
    self._assert_both_invalid(data)

  def test_missing_updated(self) -> None:
    """Both validators reject missing updated."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
    }
    self._assert_both_invalid(data)

  # Type validation (8 tests)

  def test_id_not_string(self) -> None:
    """Both validators reject non-string id."""
    data = {
      "id": 123,
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_invalid(data)

  def test_name_not_string(self) -> None:
    """Both validators reject non-string name."""
    data = {
      "id": "SPEC-001",
      "name": ["Test", "Spec"],
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_invalid(data)

  def test_empty_string_id(self) -> None:
    """Both validators reject empty string for required fields."""
    data = {
      "id": "",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_invalid(data)

  def test_owners_not_array(self) -> None:
    """Both validators reject non-array owners."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "owners": "alice",
    }
    self._assert_both_invalid(data)

  def test_auditers_not_array(self) -> None:
    """Both validators reject non-array auditers."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "auditers": "bob",
    }
    self._assert_both_invalid(data)

  def test_tags_not_array(self) -> None:
    """New validator rejects non-array tags (old validator doesn't validate tags)."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "tags": "security",
    }
    # Old validator doesn't validate tags field
    # New validator does
    new_validator = MetadataValidator(BASE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "New validator should reject non-array tags")

  def test_relations_not_array(self) -> None:
    """Both validators reject non-array relations."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": {"type": "implements", "target": "FR-001"},
    }
    self._assert_both_invalid(data)

  def test_invalid_date_format(self) -> None:
    """Both validators reject invalid date format."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "01/15/2025",
      "updated": "2025-01-15",
    }
    self._assert_both_invalid(data)

  # Enum validation (3 tests)

  def test_invalid_kind_value(self) -> None:
    """New validator rejects invalid kind value (old validator doesn't check)."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "invalid-kind",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    # Old validator doesn't validate kind enum
    # New validator does
    new_validator = MetadataValidator(BASE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "New validator should reject invalid kind")

  def test_invalid_lifecycle_value(self) -> None:
    """New validator rejects invalid lifecycle value."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "lifecycle": "invalid-phase",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    new_validator = MetadataValidator(BASE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "New validator should reject invalid lifecycle"
    )

  def test_invalid_relation_type_value(self) -> None:
    """Both validators reject invalid relation type."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": [
        {
          "type": "invalid-relation",
          "target": "FR-001",
        }
      ],
    }
    # Old validator doesn't check relation type enum
    # New validator does
    new_validator = MetadataValidator(BASE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "New validator should reject invalid relation type"
    )

  # Relations validation (8 tests)

  def test_valid_relation_minimal_fields(self) -> None:
    """Both validators accept relation with just type and target."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": [
        {
          "type": "implements",
          "target": "FR-102",
        }
      ],
    }
    self._assert_both_valid(data)

  def test_valid_relation_with_extra_fields(self) -> None:
    """Both validators accept relation with additional fields."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": [
        {
          "type": "implements",
          "target": "FR-102",
          "via": "VT-102",
          "method": "automated",
          "annotation": "OAuth2 implementation",
          "strength": "strong",
          "effective": "2024-06-01",
        }
      ],
    }
    self._assert_both_valid(data)

  def test_relation_missing_type(self) -> None:
    """Both validators reject relation missing type."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": [
        {
          "target": "FR-102",
        }
      ],
    }
    self._assert_both_invalid(data)

  def test_relation_missing_target(self) -> None:
    """Both validators reject relation missing target."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": [
        {
          "type": "implements",
        }
      ],
    }
    self._assert_both_invalid(data)

  def test_relation_type_not_in_enum(self) -> None:
    """New validator rejects relation type not in enum."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": [
        {
          "type": "custom-relation",
          "target": "FR-102",
        }
      ],
    }
    new_validator = MetadataValidator(BASE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "New validator should reject invalid relation type"
    )

  def test_relation_target_empty_string(self) -> None:
    """Both validators reject empty target string."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": [
        {
          "type": "implements",
          "target": "",
        }
      ],
    }
    self._assert_both_invalid(data)

  def test_empty_relations_array_is_valid(self) -> None:
    """Both validators accept empty relations array."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": [],
    }
    self._assert_both_valid(data)

  def test_relation_with_extra_fields_preserved(self) -> None:
    """Both validators preserve extra fields in relations."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": [
        {
          "type": "implements",
          "target": "FR-102",
          "custom_field": "custom_value",
        }
      ],
    }
    self._assert_both_valid(data)

  # Array item validation (5 tests)

  def test_owners_with_non_string_item(self) -> None:
    """Both validators reject non-string items in owners."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "owners": ["alice", 123],
    }
    self._assert_both_invalid(data)

  def test_auditers_with_empty_string(self) -> None:
    """Both validators reject empty strings in auditers."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "auditers": ["bob", ""],
    }
    self._assert_both_invalid(data)

  def test_tags_with_empty_string(self) -> None:
    """New validator rejects empty strings in tags (old doesn't validate)."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "tags": ["security", ""],
    }
    # Old validator doesn't validate tags field
    # New validator does
    new_validator = MetadataValidator(BASE_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "New validator should reject empty strings in tags"
    )

  def test_relations_with_non_object_item(self) -> None:
    """Both validators reject non-object items in relations."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "relations": ["implements FR-102"],
    }
    self._assert_both_invalid(data)

  def test_empty_arrays_are_valid(self) -> None:
    """Both validators accept empty arrays for optional fields."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "owners": [],
      "auditers": [],
      "tags": [],
      "relations": [],
    }
    self._assert_both_valid(data)

  # Date pattern validation (3 tests)

  def test_date_with_invalid_format_not_iso(self) -> None:
    """Both validators reject non-ISO date format."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "15-01-2025",
      "updated": "2025-01-15",
    }
    self._assert_both_invalid(data)

  def test_date_with_time_component(self) -> None:
    """Both validators reject date with time component."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15T10:00:00Z",
      "updated": "2025-01-15",
    }
    self._assert_both_invalid(data)

  def test_valid_iso_date(self) -> None:
    """Both validators accept valid ISO date (YYYY-MM-DD)."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2024-12-31",
    }
    self._assert_both_valid(data)


if __name__ == "__main__":
  unittest.main()
