"""Dual-validation tests for audit frontmatter metadata."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .audit import AUDIT_FRONTMATTER_METADATA


class AuditFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for audit-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(AUDIT_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases
  def test_valid_minimal_audit(self) -> None:
    """Both validators accept minimal audit (base fields only)."""
    data = {
      "id": "AUDIT-001",
      "name": "Test Audit",
      "slug": "test-audit",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_audit_with_all_fields(self) -> None:
    """Both validators accept audit with all optional fields."""
    data = {
      "id": "AUDIT-042",
      "name": "Content Binding Alignment Review",
      "slug": "audit-content-binding",
      "kind": "audit",
      "status": "approved",
      "created": "2024-06-01",
      "updated": "2024-06-08",
      "spec_refs": ["SPEC-101"],
      "prod_refs": ["PROD-020"],
      "code_scope": ["internal/content/**"],
      "audit_window": {"start": "2024-06-01", "end": "2024-06-08"},
      "findings": [
        {
          "id": "FIND-001",
          "description": "Content reconciler deviates from spec",
          "outcome": "drift",
        }
      ],
      "patch_level": [{"artefact": "SPEC-101", "status": "divergent"}],
      "next_actions": [{"type": "delta", "id": "DE-021"}],
    }
    self._assert_both_valid(data)

  def test_valid_audit_window(self) -> None:
    """Both validators accept audit_window with start and end."""
    data = {
      "id": "AUDIT-001",
      "name": "Test Audit",
      "slug": "test-audit",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "audit_window": {"start": "2024-06-01", "end": "2024-06-08"},
    }
    self._assert_both_valid(data)

  def test_valid_findings_array(self) -> None:
    """Both validators accept findings array."""
    data = {
      "id": "AUDIT-001",
      "name": "Test Audit",
      "slug": "test-audit",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "findings": [
        {
          "id": "FIND-001",
          "description": "Test finding",
          "outcome": "drift",
          "linked_issue": "ISSUE-018",
        }
      ],
    }
    self._assert_both_valid(data)

  def test_valid_patch_level_array(self) -> None:
    """Both validators accept patch_level array."""
    data = {
      "id": "AUDIT-001",
      "name": "Test Audit",
      "slug": "test-audit",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "patch_level": [
        {"artefact": "SPEC-101", "status": "aligned", "notes": "All good"}
      ],
    }
    self._assert_both_valid(data)

  def test_valid_next_actions_array(self) -> None:
    """Both validators accept next_actions array."""
    data = {
      "id": "AUDIT-001",
      "name": "Test Audit",
      "slug": "test-audit",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "next_actions": [{"type": "delta", "id": "DE-021"}],
    }
    self._assert_both_valid(data)

  # Invalid cases (new validator only)
  def test_audit_window_missing_start(self) -> None:
    """New validator rejects audit_window missing start."""
    data = {
      "id": "AUDIT-001",
      "name": "Test Audit",
      "slug": "test-audit",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "audit_window": {"end": "2024-06-08"},
    }
    new_validator = MetadataValidator(AUDIT_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject audit_window missing start"
    )

  def test_audit_window_missing_end(self) -> None:
    """New validator rejects audit_window missing end."""
    data = {
      "id": "AUDIT-001",
      "name": "Test Audit",
      "slug": "test-audit",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "audit_window": {"start": "2024-06-01"},
    }
    new_validator = MetadataValidator(AUDIT_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject audit_window missing end")

  def test_finding_missing_required_fields(self) -> None:
    """New validator rejects finding missing required fields."""
    data = {
      "id": "AUDIT-001",
      "name": "Test Audit",
      "slug": "test-audit",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "findings": [{"id": "FIND-001"}],  # Missing description, outcome
    }
    new_validator = MetadataValidator(AUDIT_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject finding missing fields")

  def test_finding_invalid_outcome(self) -> None:
    """New validator rejects finding with invalid outcome."""
    data = {
      "id": "AUDIT-001",
      "name": "Test Audit",
      "slug": "test-audit",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "findings": [
        {
          "id": "FIND-001",
          "description": "Test",
          "outcome": "invalid",  # Not in enum
        }
      ],
    }
    new_validator = MetadataValidator(AUDIT_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid outcome")

  def test_patch_level_missing_required_fields(self) -> None:
    """New validator rejects patch_level missing required fields."""
    data = {
      "id": "AUDIT-001",
      "name": "Test Audit",
      "slug": "test-audit",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "patch_level": [{"artefact": "SPEC-101"}],  # Missing status
    }
    new_validator = MetadataValidator(AUDIT_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject patch_level missing fields")

  def test_next_action_missing_required_fields(self) -> None:
    """New validator rejects next_action missing required fields."""
    data = {
      "id": "AUDIT-001",
      "name": "Test Audit",
      "slug": "test-audit",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "next_actions": [{"type": "delta"}],  # Missing id
    }
    new_validator = MetadataValidator(AUDIT_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject next_action missing id")


if __name__ == "__main__":
  unittest.main()
