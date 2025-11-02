"""Dual-validation tests for risk frontmatter metadata."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .risk import RISK_FRONTMATTER_METADATA


class RiskFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for risk-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(RISK_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases
  def test_valid_minimal_risk(self) -> None:
    """Both validators accept minimal risk (base fields only)."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_risk_with_all_fields(self) -> None:
    """Both validators accept risk with all optional fields."""
    data = {
      "id": "RISK-SYS-042",
      "name": "Third-Party API Dependency Failure",
      "slug": "risk-api-dependency",
      "kind": "risk",
      "status": "mitigating",
      "lifecycle": "maintenance",
      "created": "2024-07-20",
      "updated": "2025-01-15",
      "owners": ["reliability-team"],
      "summary": "External payment API may become unavailable",
      "tags": ["availability", "dependencies"],
      "risk_kind": "systemic",
      "likelihood": "medium",
      "impact": "high",
      "origin": "ADR-012",
      "controls": ["TS-015", "SPEC-201.FR-08"],
    }
    self._assert_both_valid(data)

  def test_valid_risk_kind_systemic(self) -> None:
    """Both validators accept risk_kind=systemic."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "risk_kind": "systemic",
    }
    self._assert_both_valid(data)

  def test_valid_risk_kind_operational(self) -> None:
    """Both validators accept risk_kind=operational."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "risk_kind": "operational",
    }
    self._assert_both_valid(data)

  def test_valid_risk_kind_delivery(self) -> None:
    """Both validators accept risk_kind=delivery."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "risk_kind": "delivery",
    }
    self._assert_both_valid(data)

  def test_valid_likelihood_values(self) -> None:
    """Both validators accept all likelihood enum values."""
    for likelihood in ["low", "medium", "high"]:
      with self.subTest(likelihood=likelihood):
        data = {
          "id": "RISK-001",
          "name": "Test Risk",
          "slug": "test-risk",
          "kind": "risk",
          "status": "identified",
          "created": "2025-01-15",
          "updated": "2025-01-15",
          "likelihood": likelihood,
        }
        self._assert_both_valid(data)

  def test_valid_impact_values(self) -> None:
    """Both validators accept all impact enum values."""
    for impact in ["low", "medium", "high"]:
      with self.subTest(impact=impact):
        data = {
          "id": "RISK-001",
          "name": "Test Risk",
          "slug": "test-risk",
          "kind": "risk",
          "status": "identified",
          "created": "2025-01-15",
          "updated": "2025-01-15",
          "impact": impact,
        }
        self._assert_both_valid(data)

  def test_valid_origin(self) -> None:
    """Both validators accept origin as string."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "origin": "ADR-012",
    }
    self._assert_both_valid(data)

  def test_valid_controls(self) -> None:
    """Both validators accept controls as array."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "controls": ["TS-015", "SPEC-201.FR-08"],
    }
    self._assert_both_valid(data)

  def test_valid_empty_controls(self) -> None:
    """Both validators accept empty controls array."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "controls": [],
    }
    self._assert_both_valid(data)

  # Invalid cases (new validator only)
  def test_invalid_risk_kind(self) -> None:
    """New validator rejects invalid risk_kind."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "risk_kind": "invalid",  # Not in enum
    }
    new_validator = MetadataValidator(RISK_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid risk_kind")

  def test_invalid_likelihood(self) -> None:
    """New validator rejects invalid likelihood."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "likelihood": "critical",  # Not in enum
    }
    new_validator = MetadataValidator(RISK_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid likelihood")

  def test_invalid_impact(self) -> None:
    """New validator rejects invalid impact."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "impact": "severe",  # Not in enum
    }
    new_validator = MetadataValidator(RISK_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid impact")

  def test_empty_origin_string(self) -> None:
    """New validator rejects empty origin string."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "origin": "",  # Empty string
    }
    new_validator = MetadataValidator(RISK_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty origin string")

  def test_empty_string_in_controls(self) -> None:
    """New validator rejects empty strings in controls array."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "controls": ["TS-015", ""],  # Empty string
    }
    new_validator = MetadataValidator(RISK_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in controls")

  def test_controls_not_array(self) -> None:
    """New validator rejects controls when not an array."""
    data = {
      "id": "RISK-001",
      "name": "Test Risk",
      "slug": "test-risk",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "controls": "TS-015",  # Should be array
    }
    new_validator = MetadataValidator(RISK_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject controls as non-array")


if __name__ == "__main__":
  unittest.main()
