"""Dual-validation tests for product frontmatter metadata.

This module tests the metadata validator for product-specific fields,
comparing behavior against the legacy imperative validator.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .prod import PROD_FRONTMATTER_METADATA


class ProdFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for product-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases
  def test_valid_minimal_prod(self) -> None:
    """Both validators accept minimal product spec (base fields only)."""
    data = {
      "id": "PROD-001",
      "name": "Test Product Spec",
      "slug": "test-product",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_prod_with_all_fields(self) -> None:
    """Both validators accept product spec with all optional fields."""
    data = {
      "id": "PROD-020",
      "name": "Sync Performance Product Spec",
      "slug": "prod-sync-performance",
      "kind": "prod",
      "status": "approved",
      "lifecycle": "implementation",
      "created": "2024-06-01",
      "updated": "2025-01-15",
      "owners": ["product-team"],
      "summary": "Improve sync speed to reduce user churn",
      "scope": "Reduce sync latency for all sync operations",
      "problems": ["PROB-012"],
      "value_proposition": "Faster sync improves user retention",
      "guiding_principles": ["Resolve user pain without sacrificing offline mode"],
      "assumptions": ["Users are comfortable with 5s sync delays"],
      "hypotheses": [
        {
          "id": "PROD-020.HYP-01",
          "statement": "Improving sync speed will reduce churn",
          "status": "proposed",
        }
      ],
      "decisions": [
        {
          "id": "PROD-020.DEC-01",
          "summary": "Prioritise sync speed over new features this quarter",
        }
      ],
      "product_requirements": [
        {
          "code": "PROD-020.FR-01",
          "statement": "Sync completes within 5s",
        },
        {
          "code": "PROD-020.NF-01",
          "statement": "Sync success rate ≥ 99%",
        },
      ],
      "verification_strategy": [
        {"research": "UX-023"},
        {"metric": "sync_latency_p99"},
      ],
      "relations": [
        {"type": "relates_to", "target": "PROB-012"},
      ],
    }
    self._assert_both_valid(data)

  def test_valid_hypothesis_statuses(self) -> None:
    """Both validators accept all valid hypothesis status enum values."""
    for status in ["proposed", "validated", "invalid"]:
      data = {
        "id": "PROD-002",
        "name": "Test Product",
        "slug": "test-product-2",
        "kind": "prod",
        "status": "draft",
        "created": "2025-01-15",
        "updated": "2025-01-15",
        "hypotheses": [
          {
            "id": "PROD-002.HYP-01",
            "statement": "Test hypothesis",
            "status": status,
          }
        ],
      }
      self._assert_both_valid(data)

  # Invalid cases (new validator only)
  def test_invalid_hypothesis_status(self) -> None:
    """New validator rejects invalid hypothesis status enum value."""
    data = {
      "id": "PROD-003",
      "name": "Test Product",
      "slug": "test-product-3",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "hypotheses": [
        {
          "id": "PROD-003.HYP-01",
          "statement": "Test hypothesis",
          "status": "unknown-status",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid hypothesis status")

  def test_hypothesis_missing_id(self) -> None:
    """New validator rejects hypothesis missing required id field."""
    data = {
      "id": "PROD-004",
      "name": "Test Product",
      "slug": "test-product-4",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "hypotheses": [
        {
          "statement": "Test hypothesis",
          "status": "proposed",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject hypothesis missing id")

  def test_hypothesis_missing_statement(self) -> None:
    """New validator rejects hypothesis missing required statement field."""
    data = {
      "id": "PROD-005",
      "name": "Test Product",
      "slug": "test-product-5",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "hypotheses": [
        {
          "id": "PROD-005.HYP-01",
          "status": "proposed",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject hypothesis missing statement")

  def test_hypothesis_missing_status(self) -> None:
    """New validator rejects hypothesis missing required status field."""
    data = {
      "id": "PROD-006",
      "name": "Test Product",
      "slug": "test-product-6",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "hypotheses": [
        {
          "id": "PROD-006.HYP-01",
          "statement": "Test hypothesis",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject hypothesis missing status")

  def test_decision_missing_id(self) -> None:
    """New validator rejects decision missing required id field."""
    data = {
      "id": "PROD-007",
      "name": "Test Product",
      "slug": "test-product-7",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "decisions": [
        {
          "summary": "Test decision",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject decision missing id")

  def test_decision_missing_summary(self) -> None:
    """New validator rejects decision missing required summary field."""
    data = {
      "id": "PROD-008",
      "name": "Test Product",
      "slug": "test-product-8",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "decisions": [
        {
          "id": "PROD-008.DEC-01",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject decision missing summary")

  def test_product_requirement_missing_code(self) -> None:
    """New validator rejects product requirement missing required code field."""
    data = {
      "id": "PROD-009",
      "name": "Test Product",
      "slug": "test-product-9",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "product_requirements": [
        {
          "statement": "Test requirement",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject product requirement missing code"
    )

  def test_product_requirement_missing_statement(self) -> None:
    """New validator rejects product requirement missing statement field."""
    data = {
      "id": "PROD-010",
      "name": "Test Product",
      "slug": "test-product-10",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "product_requirements": [
        {
          "code": "PROD-010.FR-01",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject product requirement missing statement"
    )

  def test_empty_string_in_problems_array(self) -> None:
    """New validator rejects empty string in problems array."""
    data = {
      "id": "PROD-011",
      "name": "Test Product",
      "slug": "test-product-11",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "problems": ["PROB-001", ""],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in problems")

  def test_empty_string_in_guiding_principles_array(self) -> None:
    """New validator rejects empty string in guiding_principles array."""
    data = {
      "id": "PROD-012",
      "name": "Test Product",
      "slug": "test-product-12",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "guiding_principles": ["Valid principle", ""],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty string in guiding_principles"
    )

  def test_empty_string_in_assumptions_array(self) -> None:
    """New validator rejects empty string in assumptions array."""
    data = {
      "id": "PROD-013",
      "name": "Test Product",
      "slug": "test-product-13",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "assumptions": ["Valid assumption", ""],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in assumptions")

  def test_verification_strategy_with_empty_research(self) -> None:
    """New validator rejects verification_strategy with empty research."""
    data = {
      "id": "PROD-014",
      "name": "Test Product",
      "slug": "test-product-14",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_strategy": [
        {"research": ""},
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty research in verification_strategy"
    )

  def test_verification_strategy_with_empty_metric(self) -> None:
    """New validator rejects verification_strategy with empty metric."""
    data = {
      "id": "PROD-015",
      "name": "Test Product",
      "slug": "test-product-15",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_strategy": [
        {"metric": ""},
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty metric in verification_strategy"
    )

  def test_empty_arrays_are_valid(self) -> None:
    """Both validators accept empty arrays for optional array fields."""
    data = {
      "id": "PROD-016",
      "name": "Test Product",
      "slug": "test-product-16",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "problems": [],
      "guiding_principles": [],
      "assumptions": [],
      "hypotheses": [],
      "decisions": [],
      "product_requirements": [],
      "verification_strategy": [],
    }
    self._assert_both_valid(data)

  def test_hypothesis_with_empty_id(self) -> None:
    """New validator rejects hypothesis with empty id string."""
    data = {
      "id": "PROD-017",
      "name": "Test Product",
      "slug": "test-product-17",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "hypotheses": [
        {
          "id": "",
          "statement": "Test hypothesis",
          "status": "proposed",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject hypothesis with empty id")

  def test_hypothesis_with_empty_statement(self) -> None:
    """New validator rejects hypothesis with empty statement string."""
    data = {
      "id": "PROD-018",
      "name": "Test Product",
      "slug": "test-product-18",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "hypotheses": [
        {
          "id": "PROD-018.HYP-01",
          "statement": "",
          "status": "proposed",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject hypothesis with empty statement")

  def test_decision_with_empty_id(self) -> None:
    """New validator rejects decision with empty id string."""
    data = {
      "id": "PROD-019",
      "name": "Test Product",
      "slug": "test-product-19",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "decisions": [
        {
          "id": "",
          "summary": "Test decision",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject decision with empty id")

  def test_decision_with_empty_summary(self) -> None:
    """New validator rejects decision with empty summary string."""
    data = {
      "id": "PROD-020",
      "name": "Test Product",
      "slug": "test-product-20",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "decisions": [
        {
          "id": "PROD-020.DEC-01",
          "summary": "",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject decision with empty summary")

  def test_product_requirement_with_empty_code(self) -> None:
    """New validator rejects product requirement with empty code string."""
    data = {
      "id": "PROD-021",
      "name": "Test Product",
      "slug": "test-product-21",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "product_requirements": [
        {
          "code": "",
          "statement": "Test requirement",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject product requirement with empty code"
    )

  def test_product_requirement_with_empty_statement(self) -> None:
    """New validator rejects product requirement with empty statement string."""
    data = {
      "id": "PROD-022",
      "name": "Test Product",
      "slug": "test-product-22",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "product_requirements": [
        {
          "code": "PROD-022.FR-01",
          "statement": "",
        }
      ],
    }
    new_validator = MetadataValidator(PROD_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject product requirement with empty statement"
    )


if __name__ == "__main__":
  unittest.main()
