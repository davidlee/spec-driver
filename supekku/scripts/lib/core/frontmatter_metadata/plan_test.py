"""Dual-validation tests for plan frontmatter metadata."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .plan import PLAN_FRONTMATTER_METADATA


class PlanFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for plan/phase/task-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(PLAN_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases
  def test_valid_minimal_plan(self) -> None:
    """Both validators accept minimal plan (base fields only)."""
    data = {
      "id": "PLAN-001",
      "name": "Test Plan",
      "slug": "test-plan",
      "kind": "plan",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_minimal_phase(self) -> None:
    """Both validators accept minimal phase (base fields only)."""
    data = {
      "id": "PHASE-001",
      "name": "Test Phase",
      "slug": "test-phase",
      "kind": "phase",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_minimal_task(self) -> None:
    """Both validators accept minimal task (base fields only)."""
    data = {
      "id": "TASK-001",
      "name": "Test Task",
      "slug": "test-task",
      "kind": "task",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_plan_with_all_fields(self) -> None:
    """Both validators accept plan with all optional fields."""
    data = {
      "id": "PLAN-042",
      "name": "Authentication Implementation Plan",
      "slug": "plan-auth-implementation",
      "kind": "plan",
      "status": "active",
      "lifecycle": "implementation",
      "created": "2024-08-01",
      "updated": "2025-01-15",
      "owners": ["auth-team"],
      "summary": "Plan for implementing OAuth2 authentication",
      "tags": ["auth", "implementation"],
      "objective": "Implement OAuth2 authentication with token refresh",
      "entrance_criteria": [
        "SPEC-101 status == approved",
        "Test infrastructure available",
      ],
      "exit_criteria": ["VT-210 executed and passing", "Security audit completed"],
    }
    self._assert_both_valid(data)

  def test_valid_objective(self) -> None:
    """Both validators accept objective as text."""
    data = {
      "id": "PLAN-001",
      "name": "Test Plan",
      "slug": "test-plan",
      "kind": "plan",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "objective": "This is the objective of the plan",
    }
    self._assert_both_valid(data)

  def test_valid_entrance_criteria(self) -> None:
    """Both validators accept entrance_criteria as array."""
    data = {
      "id": "PLAN-001",
      "name": "Test Plan",
      "slug": "test-plan",
      "kind": "plan",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "entrance_criteria": [
        "SPEC-101 approved",
        "Resources allocated",
      ],
    }
    self._assert_both_valid(data)

  def test_valid_exit_criteria(self) -> None:
    """Both validators accept exit_criteria as array."""
    data = {
      "id": "PLAN-001",
      "name": "Test Plan",
      "slug": "test-plan",
      "kind": "plan",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "exit_criteria": [
        "All tests passing",
        "Documentation complete",
      ],
    }
    self._assert_both_valid(data)

  def test_valid_empty_arrays(self) -> None:
    """Both validators accept empty arrays."""
    data = {
      "id": "PLAN-001",
      "name": "Test Plan",
      "slug": "test-plan",
      "kind": "plan",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "entrance_criteria": [],
      "exit_criteria": [],
    }
    self._assert_both_valid(data)

  # Invalid cases (new validator only)
  def test_empty_string_in_entrance_criteria(self) -> None:
    """New validator rejects empty strings in entrance_criteria."""
    data = {
      "id": "PLAN-001",
      "name": "Test Plan",
      "slug": "test-plan",
      "kind": "plan",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "entrance_criteria": ["Valid criterion", ""],
    }
    new_validator = MetadataValidator(PLAN_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject empty string in entrance_criteria"
    )

  def test_empty_string_in_exit_criteria(self) -> None:
    """New validator rejects empty strings in exit_criteria."""
    data = {
      "id": "PLAN-001",
      "name": "Test Plan",
      "slug": "test-plan",
      "kind": "plan",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "exit_criteria": [""],
    }
    new_validator = MetadataValidator(PLAN_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in exit_criteria")


if __name__ == "__main__":
  unittest.main()
