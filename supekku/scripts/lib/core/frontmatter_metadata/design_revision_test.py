"""Dual-validation tests for design revision frontmatter metadata.

This module tests the metadata validator for design revision-specific fields,
comparing behavior against the legacy imperative validator.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .design_revision import DESIGN_REVISION_FRONTMATTER_METADATA


class DesignRevisionFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for design revision-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    # Old validator
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    # New metadata validator
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases
  def test_valid_minimal_design_revision(self) -> None:
    """Both validators accept minimal design revision (base fields only)."""
    data = {
      "id": "REV-001",
      "name": "Test Design Revision",
      "slug": "test-revision",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    }
    self._assert_both_valid(data)

  def test_valid_design_revision_with_all_fields(self) -> None:
    """Both validators accept design revision with all optional fields."""
    data = {
      "id": "REV-021",
      "name": "Schema Update Design Revision",
      "slug": "rev-schema-update",
      "kind": "design_revision",
      "status": "approved",
      "lifecycle": "design",
      "created": "2024-06-08",
      "updated": "2025-01-15",
      "owners": ["dev-team"],
      "summary": "Design for implementing optimistic locking in schema updates",
      "delta_ref": "DE-021",
      "source_context": [
        {"type": "research", "id": "RC-010"},
        {"type": "hypothesis", "id": "PROD-020.HYP-03"},
      ],
      "code_impacts": [
        {
          "path": "internal/content/reconciler.go",
          "current_state": "Direct schema updates without locking",
          "target_state": "Optimistic locking with version checks",
        },
        {
          "path": "internal/content/schema_repo.go",
          "current_state": "Single transaction per update",
          "target_state": "Retry logic with exponential backoff",
        }
      ],
      "verification_alignment": [
        {"verification": "VT-210", "impact": "regression"},
        {"verification": "VA-044", "impact": "new"},
      ],
      "design_decisions": [
        {
          "id": "SPEC-101.DEC-04",
          "summary": "Adopt optimistic locking for schema updates",
        }
      ],
      "open_questions": [
        {
          "description": "Do we need a background repair job?",
          "owner": "david",
          "due": "2024-06-12",
        }
      ],
      "relations": [
        {"type": "implements", "target": "DE-021"},
      ],
    }
    self._assert_both_valid(data)

  def test_valid_source_context_types(self) -> None:
    """Both validators accept all valid source_context type enum values."""
    for context_type in ["research", "hypothesis"]:
      data = {
        "id": "REV-002",
        "name": "Test Revision",
        "slug": "test-revision-2",
        "kind": "design_revision",
        "status": "draft",
        "created": "2025-01-15",
        "updated": "2025-01-15",
        "source_context": [
          {"type": context_type, "id": "TEST-001"},
        ],
      }
      self._assert_both_valid(data)

  def test_valid_verification_impact_types(self) -> None:
    """Both validators accept all valid verification impact enum values."""
    for impact in ["regression", "new"]:
      data = {
        "id": "REV-003",
        "name": "Test Revision",
        "slug": "test-revision-3",
        "kind": "design_revision",
        "status": "draft",
        "created": "2025-01-15",
        "updated": "2025-01-15",
        "verification_alignment": [
          {"verification": "VT-001", "impact": impact},
        ],
      }
      self._assert_both_valid(data)

  # Invalid cases (new validator only)
  def test_invalid_source_context_type(self) -> None:
    """New validator rejects invalid source_context type enum value."""
    data = {
      "id": "REV-004",
      "name": "Test Revision",
      "slug": "test-revision-4",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "source_context": [
        {"type": "unknown-type", "id": "TEST-001"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject invalid source_context type"
    )

  def test_source_context_missing_id(self) -> None:
    """New validator rejects source_context missing required id field."""
    data = {
      "id": "REV-005",
      "name": "Test Revision",
      "slug": "test-revision-5",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "source_context": [
        {"type": "research"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject source_context missing id"
    )

  def test_source_context_missing_type(self) -> None:
    """New validator rejects source_context missing required type field."""
    data = {
      "id": "REV-006",
      "name": "Test Revision",
      "slug": "test-revision-6",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "source_context": [
        {"id": "TEST-001"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject source_context missing type"
    )

  def test_code_impact_missing_path(self) -> None:
    """New validator rejects code_impact missing required path field."""
    data = {
      "id": "REV-007",
      "name": "Test Revision",
      "slug": "test-revision-7",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "code_impacts": [
        {
          "current_state": "Current",
          "target_state": "Target",
        }
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject code_impact missing path"
    )

  def test_code_impact_missing_current_state(self) -> None:
    """New validator rejects code_impact missing current_state field."""
    data = {
      "id": "REV-008",
      "name": "Test Revision",
      "slug": "test-revision-8",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "code_impacts": [
        {
          "path": "internal/test.go",
          "target_state": "Target",
        }
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject code_impact missing current_state"
    )

  def test_code_impact_missing_target_state(self) -> None:
    """New validator rejects code_impact missing target_state field."""
    data = {
      "id": "REV-009",
      "name": "Test Revision",
      "slug": "test-revision-9",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "code_impacts": [
        {
          "path": "internal/test.go",
          "current_state": "Current",
        }
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject code_impact missing target_state"
    )

  def test_verification_alignment_missing_verification(self) -> None:
    """New validator rejects verification_alignment missing verification."""
    data = {
      "id": "REV-010",
      "name": "Test Revision",
      "slug": "test-revision-10",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_alignment": [
        {"impact": "regression"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [],
      "Should reject verification_alignment missing verification"
    )

  def test_verification_alignment_missing_impact(self) -> None:
    """New validator rejects verification_alignment missing impact field."""
    data = {
      "id": "REV-011",
      "name": "Test Revision",
      "slug": "test-revision-11",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_alignment": [
        {"verification": "VT-001"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject verification_alignment missing impact"
    )

  def test_invalid_verification_alignment_impact(self) -> None:
    """New validator rejects invalid verification_alignment impact enum."""
    data = {
      "id": "REV-012",
      "name": "Test Revision",
      "slug": "test-revision-12",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_alignment": [
        {"verification": "VT-001", "impact": "unknown-impact"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject invalid verification_alignment impact"
    )

  def test_design_decision_missing_id(self) -> None:
    """New validator rejects design_decision missing required id field."""
    data = {
      "id": "REV-013",
      "name": "Test Revision",
      "slug": "test-revision-13",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "design_decisions": [
        {"summary": "Test decision"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject design_decision missing id"
    )

  def test_design_decision_missing_summary(self) -> None:
    """New validator rejects design_decision missing required summary field."""
    data = {
      "id": "REV-014",
      "name": "Test Revision",
      "slug": "test-revision-14",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "design_decisions": [
        {"id": "SPEC-001.DEC-01"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject design_decision missing summary"
    )

  def test_open_question_missing_description(self) -> None:
    """New validator rejects open_question missing required description."""
    data = {
      "id": "REV-015",
      "name": "Test Revision",
      "slug": "test-revision-15",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "open_questions": [
        {"owner": "alice", "due": "2025-02-01"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject open_question missing description"
    )

  def test_open_question_missing_owner(self) -> None:
    """New validator rejects open_question missing required owner field."""
    data = {
      "id": "REV-016",
      "name": "Test Revision",
      "slug": "test-revision-16",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "open_questions": [
        {"description": "Test question", "due": "2025-02-01"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject open_question missing owner"
    )

  def test_open_question_missing_due(self) -> None:
    """New validator rejects open_question missing required due field."""
    data = {
      "id": "REV-017",
      "name": "Test Revision",
      "slug": "test-revision-17",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "open_questions": [
        {"description": "Test question", "owner": "alice"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject open_question missing due"
    )

  def test_open_question_invalid_due_format(self) -> None:
    """New validator rejects open_question with invalid due date format."""
    data = {
      "id": "REV-018",
      "name": "Test Revision",
      "slug": "test-revision-18",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "open_questions": [
        {
          "description": "Test question",
          "owner": "alice",
          "due": "tomorrow",
        }
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject open_question with invalid due format"
    )

  def test_empty_string_in_code_impact_path(self) -> None:
    """New validator rejects code_impact with empty path string."""
    data = {
      "id": "REV-019",
      "name": "Test Revision",
      "slug": "test-revision-19",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "code_impacts": [
        {
          "path": "",
          "current_state": "Current",
          "target_state": "Target",
        }
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject code_impact with empty path"
    )

  def test_empty_string_in_verification(self) -> None:
    """New validator rejects verification_alignment with empty verification."""
    data = {
      "id": "REV-020",
      "name": "Test Revision",
      "slug": "test-revision-20",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_alignment": [
        {"verification": "", "impact": "regression"},
      ],
    }
    new_validator = MetadataValidator(DESIGN_REVISION_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject verification_alignment with empty verification"
    )

  def test_empty_arrays_are_valid(self) -> None:
    """Both validators accept empty arrays for optional array fields."""
    data = {
      "id": "REV-021",
      "name": "Test Revision",
      "slug": "test-revision-21",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "source_context": [],
      "code_impacts": [],
      "verification_alignment": [],
      "design_decisions": [],
      "open_questions": [],
    }
    self._assert_both_valid(data)


if __name__ == "__main__":
  unittest.main()
