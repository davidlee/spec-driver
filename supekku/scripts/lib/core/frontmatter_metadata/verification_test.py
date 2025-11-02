"""Dual-validation tests for verification frontmatter metadata."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .verification import VERIFICATION_FRONTMATTER_METADATA


class VerificationFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for verification-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(VERIFICATION_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases
  def test_valid_minimal_verification(self) -> None:
    """Both validators accept minimal verification (base fields only)."""
    data = {
      "id": "VT-001",
      "name": "Test Verification",
      "slug": "test-verification",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_verification_with_all_fields(self) -> None:
    """Both validators accept verification with all optional fields."""
    data = {
      "id": "VT-102",
      "name": "OAuth2 Authentication Flow Verification",
      "slug": "verification-oauth2-auth",
      "kind": "verification",
      "status": "approved",
      "lifecycle": "verification",
      "created": "2024-08-15",
      "updated": "2025-01-15",
      "owners": ["qa-team"],
      "summary": "Automated verification of OAuth2 authentication flow",
      "tags": ["security", "auth"],
      "verification_kind": "automated",
      "covers": ["FR-102", "NF-020"],
      "procedure": "Run integration test suite auth_flow_test.py",
    }
    self._assert_both_valid(data)

  def test_valid_verification_kind_automated(self) -> None:
    """Both validators accept verification_kind=automated."""
    data = {
      "id": "VT-001",
      "name": "Test Verification",
      "slug": "test-verification",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_kind": "automated",
    }
    self._assert_both_valid(data)

  def test_valid_verification_kind_agent(self) -> None:
    """Both validators accept verification_kind=agent."""
    data = {
      "id": "VT-001",
      "name": "Test Verification",
      "slug": "test-verification",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_kind": "agent",
    }
    self._assert_both_valid(data)

  def test_valid_verification_kind_manual(self) -> None:
    """Both validators accept verification_kind=manual."""
    data = {
      "id": "VT-001",
      "name": "Test Verification",
      "slug": "test-verification",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_kind": "manual",
    }
    self._assert_both_valid(data)

  def test_valid_covers_array(self) -> None:
    """Both validators accept covers as array of requirement IDs."""
    data = {
      "id": "VT-001",
      "name": "Test Verification",
      "slug": "test-verification",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "covers": ["FR-102", "NF-020", "SPEC-100.FR-05"],
    }
    self._assert_both_valid(data)

  def test_valid_empty_covers_array(self) -> None:
    """Both validators accept empty covers array."""
    data = {
      "id": "VT-001",
      "name": "Test Verification",
      "slug": "test-verification",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "covers": [],
    }
    self._assert_both_valid(data)

  def test_valid_procedure_text(self) -> None:
    """Both validators accept procedure as text."""
    data = {
      "id": "VT-001",
      "name": "Test Verification",
      "slug": "test-verification",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "procedure": "Run test suite with assertions on expected behavior",
    }
    self._assert_both_valid(data)

  # Invalid cases (new validator only)
  def test_invalid_verification_kind(self) -> None:
    """New validator rejects invalid verification_kind."""
    data = {
      "id": "VT-001",
      "name": "Test Verification",
      "slug": "test-verification",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_kind": "invalid",  # Not in enum
    }
    new_validator = MetadataValidator(VERIFICATION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid verification_kind")

  def test_covers_not_array(self) -> None:
    """New validator rejects covers when not an array."""
    data = {
      "id": "VT-001",
      "name": "Test Verification",
      "slug": "test-verification",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "covers": "FR-102",  # Should be array
    }
    new_validator = MetadataValidator(VERIFICATION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject covers as non-array")

  def test_empty_string_in_covers_array(self) -> None:
    """New validator rejects empty strings in covers array."""
    data = {
      "id": "VT-001",
      "name": "Test Verification",
      "slug": "test-verification",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "covers": ["FR-102", ""],  # Empty string
    }
    new_validator = MetadataValidator(VERIFICATION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in covers")

  def test_procedure_not_string(self) -> None:
    """New validator rejects procedure when not a string."""
    data = {
      "id": "VT-001",
      "name": "Test Verification",
      "slug": "test-verification",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "procedure": 123,  # Should be string
    }
    new_validator = MetadataValidator(VERIFICATION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject procedure as non-string")


if __name__ == "__main__":
  unittest.main()
