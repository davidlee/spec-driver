"""Dual-validation tests for requirement frontmatter metadata."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .requirement import REQUIREMENT_FRONTMATTER_METADATA


class RequirementFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for requirement-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(REQUIREMENT_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases
  def test_valid_minimal_requirement(self) -> None:
    """Both validators accept minimal requirement (base fields only)."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_requirement_with_all_fields(self) -> None:
    """Both validators accept requirement with all optional fields."""
    data = {
      "id": "FR-102",
      "name": "OAuth2 Token Refresh",
      "slug": "requirement-oauth2-refresh",
      "kind": "requirement",
      "status": "approved",
      "lifecycle": "implementation",
      "created": "2024-06-15",
      "updated": "2025-01-15",
      "owners": ["auth-team"],
      "summary": "System must support automatic OAuth2 token refresh",
      "tags": ["auth", "security"],
      "requirement_kind": "functional",
      "rfc2119_level": "must",
      "value_driver": "user-capability",
      "acceptance_criteria": [
        "Given an expired access token",
        "When the system detects token expiration",
      ],
      "verification_refs": ["VT-210", "VH-044"],
    }
    self._assert_both_valid(data)

  def test_valid_requirement_kind_functional(self) -> None:
    """Both validators accept requirement_kind=functional."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "requirement_kind": "functional",
    }
    self._assert_both_valid(data)

  def test_valid_requirement_kind_non_functional(self) -> None:
    """Both validators accept requirement_kind=non-functional."""
    data = {
      "id": "NF-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "requirement_kind": "non-functional",
    }
    self._assert_both_valid(data)

  def test_valid_requirement_kind_policy(self) -> None:
    """Both validators accept requirement_kind=policy."""
    data = {
      "id": "PR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "requirement_kind": "policy",
    }
    self._assert_both_valid(data)

  def test_valid_requirement_kind_standard(self) -> None:
    """Both validators accept requirement_kind=standard."""
    data = {
      "id": "SR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "requirement_kind": "standard",
    }
    self._assert_both_valid(data)

  def test_valid_rfc2119_level_must(self) -> None:
    """Both validators accept rfc2119_level=must."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "rfc2119_level": "must",
    }
    self._assert_both_valid(data)

  def test_valid_rfc2119_level_should(self) -> None:
    """Both validators accept rfc2119_level=should."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "rfc2119_level": "should",
    }
    self._assert_both_valid(data)

  def test_valid_rfc2119_level_may(self) -> None:
    """Both validators accept rfc2119_level=may."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "rfc2119_level": "may",
    }
    self._assert_both_valid(data)

  def test_valid_value_driver_values(self) -> None:
    """Both validators accept all value_driver enum values."""
    for driver in [
      "user-capability",
      "operational-excellence",
      "compliance",
      "experience",
    ]:
      with self.subTest(driver=driver):
        data = {
          "id": "FR-001",
          "name": "Test Requirement",
          "slug": "test-requirement",
          "kind": "requirement",
          "status": "draft",
          "created": "2025-01-15",
          "updated": "2025-01-15",
          "value_driver": driver,
        }
        self._assert_both_valid(data)

  def test_valid_acceptance_criteria(self) -> None:
    """Both validators accept acceptance_criteria as array."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "acceptance_criteria": [
        "Given a condition",
        "When an action occurs",
        "Then an outcome is observed",
      ],
    }
    self._assert_both_valid(data)

  def test_valid_empty_arrays(self) -> None:
    """Both validators accept empty arrays."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "acceptance_criteria": [],
      "verification_refs": [],
    }
    self._assert_both_valid(data)

  # Invalid cases (new validator only)
  def test_invalid_requirement_kind(self) -> None:
    """New validator rejects invalid requirement_kind."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "requirement_kind": "invalid",
    }
    new_validator = MetadataValidator(REQUIREMENT_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject invalid requirement_kind"
    )

  def test_invalid_rfc2119_level(self) -> None:
    """New validator rejects invalid rfc2119_level."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "rfc2119_level": "could",
    }
    new_validator = MetadataValidator(REQUIREMENT_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid rfc2119_level")

  def test_invalid_value_driver(self) -> None:
    """New validator rejects invalid value_driver."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "value_driver": "profit",
    }
    new_validator = MetadataValidator(REQUIREMENT_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid value_driver")

  def test_empty_string_in_acceptance_criteria(self) -> None:
    """New validator rejects empty strings in acceptance_criteria."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "acceptance_criteria": ["Valid criterion", ""],
    }
    new_validator = MetadataValidator(REQUIREMENT_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty string in acceptance_criteria"
    )

  def test_empty_string_in_verification_refs(self) -> None:
    """New validator rejects empty strings in verification_refs."""
    data = {
      "id": "FR-001",
      "name": "Test Requirement",
      "slug": "test-requirement",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_refs": ["VT-210", ""],
    }
    new_validator = MetadataValidator(REQUIREMENT_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty string in verification_refs"
    )


if __name__ == "__main__":
  unittest.main()
