"""Dual-validation tests for delta frontmatter metadata.

Tests that the new metadata-driven validator handles delta-specific fields
correctly while maintaining compatibility with base field validation.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .delta import DELTA_FRONTMATTER_METADATA


class DeltaFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for delta-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases (3 tests)

  def test_valid_minimal_delta(self) -> None:
    """Both validators accept minimal delta (base fields only)."""
    data = {
      "id": "DE-001",
      "name": "Example Delta",
      "slug": "delta-example",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_delta_with_all_fields(self) -> None:
    """Both validators accept delta with all optional fields."""
    data = {
      "id": "DE-021",
      "name": "Content Binding Migration",
      "slug": "delta-content-binding",
      "kind": "delta",
      "status": "approved",
      "created": "2024-06-08",
      "updated": "2025-01-15",
      "applies_to": {
        "specs": ["SPEC-101", "SPEC-102"],
        "prod": ["PROD-020"],
        "requirements": ["SPEC-101.FR-01"],
      },
      "context_inputs": [
        {"type": "research", "id": "RC-010"},
        {"type": "decision", "id": "SPEC-101.DEC-02"},
      ],
      "outcome_summary": "Target state description",
      "risk_register": [
        {
          "id": "RISK-DC-001",
          "title": "Data migration risk",
          "exposure": "change",
          "likelihood": "medium",
          "impact": "high",
          "mitigation": "Add validation step",
        }
      ],
    }
    self._assert_both_valid(data)

  def test_valid_delta_partial_applies_to(self) -> None:
    """Both validators accept applies_to with only some fields."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "applies_to": {
        "specs": ["SPEC-101"],
        # prod and requirements omitted
      },
    }
    self._assert_both_valid(data)

  # applies_to validation (5 tests)

  def test_valid_applies_to_all_categories(self) -> None:
    """Both validators accept applies_to with all categories."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "applies_to": {
        "specs": ["SPEC-101", "SPEC-102"],
        "prod": ["PROD-020", "PROD-021"],
        "requirements": ["SPEC-101.FR-01", "PROD-020.NF-03"],
      },
    }
    self._assert_both_valid(data)

  def test_valid_applies_to_empty_arrays(self) -> None:
    """Both validators accept applies_to with empty arrays."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "applies_to": {
        "specs": [],
        "prod": [],
        "requirements": [],
      },
    }
    self._assert_both_valid(data)

  def test_applies_to_specs_not_array(self) -> None:
    """New validator rejects applies_to.specs as non-array."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "applies_to": {
        "specs": "SPEC-101",  # Should be array
      },
    }
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject non-array specs")

  def test_applies_to_empty_string_in_array(self) -> None:
    """New validator rejects empty strings in applies_to arrays."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "applies_to": {
        "specs": ["SPEC-101", ""],  # Empty string
      },
    }
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in specs")

  def test_applies_to_not_object(self) -> None:
    """New validator rejects applies_to as non-object."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "applies_to": ["SPEC-101"],  # Should be object
    }
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject non-object applies_to")

  # context_inputs validation (5 tests)

  def test_valid_context_inputs_all_types(self) -> None:
    """Both validators accept all context_inputs types."""
    for ctx_type in ["research", "decision", "hypothesis", "issue"]:
      data = {
        "id": "DE-001",
        "name": "Test Delta",
        "slug": "test-delta",
        "kind": "delta",
        "status": "draft",
        "created": "2025-01-15",
        "updated": "2025-01-15",
        "context_inputs": [{"type": ctx_type, "id": "TEST-001"}],
      }
      self._assert_both_valid(data)

  def test_valid_context_inputs_multiple(self) -> None:
    """Both validators accept multiple context_inputs."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context_inputs": [
        {"type": "research", "id": "RC-010"},
        {"type": "decision", "id": "SPEC-101.DEC-02"},
        {"type": "hypothesis", "id": "SPEC-101.HYP-01"},
      ],
    }
    self._assert_both_valid(data)

  def test_context_input_missing_type(self) -> None:
    """New validator rejects context_input missing type."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context_inputs": [{"id": "RC-010"}],  # Missing type
    }
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject missing type")

  def test_context_input_invalid_type(self) -> None:
    """New validator rejects invalid context_input type."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context_inputs": [{"type": "unknown", "id": "TEST-001"}],
    }
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid type")

  def test_context_input_missing_id(self) -> None:
    """New validator rejects context_input missing id."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "context_inputs": [{"type": "research"}],  # Missing id
    }
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject missing id")

  # risk_register validation (8 tests)

  def test_valid_risk_register_complete(self) -> None:
    """Both validators accept complete risk entry."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "risk_register": [
        {
          "id": "RISK-DC-001",
          "title": "Data migration risk",
          "exposure": "change",
          "likelihood": "medium",
          "impact": "high",
          "mitigation": "Add validation step",
        }
      ],
    }
    self._assert_both_valid(data)

  def test_valid_risk_register_minimal(self) -> None:
    """Both validators accept risk without optional mitigation."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "risk_register": [
        {
          "id": "RISK-DC-001",
          "title": "Data migration risk",
          "exposure": "change",
          "likelihood": "low",
          "impact": "low",
          # mitigation is optional
        }
      ],
    }
    self._assert_both_valid(data)

  def test_risk_missing_required_fields(self) -> None:
    """New validator rejects risk missing required fields."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "risk_register": [
        {
          "id": "RISK-DC-001",
          # Missing title, exposure, likelihood, impact
        }
      ],
    }
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject missing required fields")

  def test_valid_risk_exposure_types(self) -> None:
    """New validator accepts all valid exposure types."""
    for exposure in ["change", "systemic", "operational", "delivery"]:
      data = {
        "id": "DE-001",
        "name": "Test Delta",
        "slug": "test-delta",
        "kind": "delta",
        "status": "draft",
        "created": "2025-01-15",
        "updated": "2025-01-15",
        "risk_register": [
          {
            "id": "RISK-001",
            "title": "Test risk",
            "exposure": exposure,
            "likelihood": "low",
            "impact": "low",
          }
        ],
      }
      self._assert_both_valid(data)

  def test_risk_invalid_exposure(self) -> None:
    """New validator rejects invalid exposure type."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "risk_register": [
        {
          "id": "RISK-001",
          "title": "Test risk",
          "exposure": "unknown",
          "likelihood": "low",
          "impact": "low",
        }
      ],
    }
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid exposure")

  def test_valid_risk_likelihood_values(self) -> None:
    """New validator accepts all valid likelihood values."""
    for likelihood in ["low", "medium", "high"]:
      data = {
        "id": "DE-001",
        "name": "Test Delta",
        "slug": "test-delta",
        "kind": "delta",
        "status": "draft",
        "created": "2025-01-15",
        "updated": "2025-01-15",
        "risk_register": [
          {
            "id": "RISK-001",
            "title": "Test risk",
            "exposure": "change",
            "likelihood": likelihood,
            "impact": "low",
          }
        ],
      }
      self._assert_both_valid(data)

  def test_risk_invalid_likelihood(self) -> None:
    """New validator rejects invalid likelihood."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "risk_register": [
        {
          "id": "RISK-001",
          "title": "Test risk",
          "exposure": "change",
          "likelihood": "unknown",
          "impact": "low",
        }
      ],
    }
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid likelihood")

  def test_risk_invalid_impact(self) -> None:
    """New validator rejects invalid impact."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "risk_register": [
        {
          "id": "RISK-001",
          "title": "Test risk",
          "exposure": "change",
          "likelihood": "low",
          "impact": "critical",  # Not in enum
        }
      ],
    }
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid impact")

  # outcome_summary validation (2 tests)

  def test_valid_outcome_summary(self) -> None:
    """Both validators accept outcome_summary as string."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "outcome_summary": (
        "Target state: System uses event sourcing with optimistic locking"
      ),
    }
    self._assert_both_valid(data)

  def test_outcome_summary_not_string(self) -> None:
    """New validator rejects outcome_summary as non-string."""
    data = {
      "id": "DE-001",
      "name": "Test Delta",
      "slug": "test-delta",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "outcome_summary": ["Target state description"],  # Should be string
    }
    new_validator = MetadataValidator(DELTA_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject non-string outcome_summary")


if __name__ == "__main__":
  unittest.main()
