"""Dual-validation tests for spec frontmatter metadata.

Tests that the new metadata-driven validator handles spec-specific fields
correctly while maintaining compatibility with base field validation.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .spec import SPEC_FRONTMATTER_METADATA


class SpecFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for spec-specific fields."""

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
    new_validator = MetadataValidator(SPEC_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # Valid cases (3 tests)

  def test_valid_minimal_spec(self) -> None:
    """Both validators accept minimal spec (base fields only)."""
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

  def test_valid_spec_with_all_fields(self) -> None:
    """Both validators accept spec with all optional fields."""
    data = {
      "id": "SPEC-101",
      "name": "Content Binding Spec",
      "slug": "spec-content-binding",
      "kind": "spec",
      "status": "approved",
      "created": "2024-06-08",
      "updated": "2025-01-15",
      "c4_level": "container",
      "scope": "Maintain canonical content binding state",
      "concerns": [
        {
          "name": "content synchronisation",
          "description": "Maintain canonical content binding state",
        }
      ],
      "responsibilities": ["canonical content binding lifecycle"],
      "guiding_principles": ["Maintain block identity end-to-end"],
      "assumptions": ["Agents will reconcile markdown without manual edits"],
      "hypotheses": [
        {
          "id": "SPEC-101.HYP-01",
          "statement": "Rich diffing will reduce merge conflicts",
          "status": "proposed",
        }
      ],
      "decisions": [
        {
          "id": "SPEC-101.DEC-01",
          "summary": "Adopt optimistic locking for schema updates",
          "rationale": "Based on RC-010 findings",
        }
      ],
      "constraints": ["Must preserve block UUIDs during edits"],
      "verification_strategy": [
        {"type": "VT-210", "description": "End-to-end sync tests remain green"}
      ],
      "sources": [
        {
          "language": "python",
          "identifier": "supekku/scripts/lib/workspace.py",
          "module": "supekku.scripts.lib.workspace",
          "variants": [
            {"name": "api", "path": "contracts/python/workspace-api.md"},
          ],
        }
      ],
      "packages": ["internal/application/services/git"],
    }
    self._assert_both_valid(data)

  def test_valid_real_world_spec(self) -> None:
    """Both validators accept real-world SPEC-090 style frontmatter."""
    data = {
      "id": "SPEC-090",
      "slug": "supekku-scripts-lib-blocks-metadata-validator",
      "name": "supekku/scripts/lib/blocks/metadata/validator.py Specification",
      "created": "2025-11-02",
      "updated": "2025-11-02",
      "status": "draft",
      "kind": "spec",
      "responsibilities": [],
      "sources": [
        {
          "language": "python",
          "identifier": "supekku/scripts/lib/blocks/metadata/validator.py",
          "module": "supekku.scripts.lib.blocks.metadata.validator",
          "variants": [
            {"name": "api", "path": "contracts/api.md"},
            {"name": "implementation", "path": "contracts/implementation.md"},
            {"name": "tests", "path": "contracts/tests.md"},
          ],
        }
      ],
    }
    self._assert_both_valid(data)

  # Enum validation (4 tests)

  def test_valid_c4_levels(self) -> None:
    """New validator accepts all valid c4_level values."""
    for level in ["system", "container", "component", "code", "interaction"]:
      data = {
        "id": "SPEC-001",
        "name": "Test Spec",
        "slug": "test-spec",
        "kind": "spec",
        "status": "draft",
        "created": "2025-01-15",
        "updated": "2025-01-15",
        "c4_level": level,
      }
      self._assert_both_valid(data)

  def test_invalid_c4_level(self) -> None:
    """New validator rejects invalid c4_level."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "c4_level": "invalid-level",
    }
    # Old validator doesn't validate c4_level
    # New validator does
    new_validator = MetadataValidator(SPEC_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid c4_level")

  def test_valid_hypothesis_statuses(self) -> None:
    """New validator accepts all valid hypothesis status values."""
    for status in ["proposed", "validated", "invalid"]:
      data = {
        "id": "SPEC-001",
        "name": "Test Spec",
        "slug": "test-spec",
        "kind": "spec",
        "status": "draft",
        "created": "2025-01-15",
        "updated": "2025-01-15",
        "hypotheses": [
          {
            "id": "SPEC-001.HYP-01",
            "statement": "Test hypothesis",
            "status": status,
          }
        ],
      }
      self._assert_both_valid(data)

  def test_invalid_hypothesis_status(self) -> None:
    """New validator rejects invalid hypothesis status."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "hypotheses": [
        {
          "id": "SPEC-001.HYP-01",
          "statement": "Test hypothesis",
          "status": "unknown-status",
        }
      ],
    }
    new_validator = MetadataValidator(SPEC_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid hypothesis status")

  # Nested object validation (8 tests)

  def test_valid_concerns_array(self) -> None:
    """Both validators accept valid concerns array."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "concerns": [
        {
          "name": "performance",
          "description": "Ensure sub-100ms response times",
        },
        {
          "name": "security",
          "description": "Prevent unauthorized access",
        },
      ],
    }
    self._assert_both_valid(data)

  def test_concern_missing_required_field(self) -> None:
    """New validator rejects concern missing name or description."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "concerns": [
        {
          "name": "performance",
          # Missing description
        }
      ],
    }
    new_validator = MetadataValidator(SPEC_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject concern missing description")

  def test_valid_decisions_array(self) -> None:
    """Both validators accept valid decisions array."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "decisions": [
        {
          "id": "SPEC-001.DEC-01",
          "summary": "Use PostgreSQL for persistence",
          "rationale": "Better JSON support than MySQL",
        },
        {
          "id": "SPEC-001.DEC-02",
          "summary": "Adopt event sourcing",
          # rationale is optional
        },
      ],
    }
    self._assert_both_valid(data)

  def test_decision_missing_required_fields(self) -> None:
    """New validator rejects decision missing id or summary."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "decisions": [
        {
          "summary": "Use PostgreSQL",
          # Missing id
        }
      ],
    }
    new_validator = MetadataValidator(SPEC_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject decision missing id")

  def test_valid_verification_strategy(self) -> None:
    """Both validators accept valid verification_strategy."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_strategy": [
        {"type": "VT-100", "description": "Unit tests cover core logic"},
        {"type": "VT-101", "description": "Integration tests verify API"},
      ],
    }
    self._assert_both_valid(data)

  def test_verification_missing_required_fields(self) -> None:
    """New validator rejects verification missing type or description."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "verification_strategy": [
        {
          "type": "VT-100",
          # Missing description
        }
      ],
    }
    new_validator = MetadataValidator(SPEC_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors, [], "Should reject verification missing description"
    )

  def test_empty_hypotheses_array(self) -> None:
    """Both validators accept empty hypotheses array."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "hypotheses": [],
    }
    self._assert_both_valid(data)

  def test_hypothesis_with_all_fields(self) -> None:
    """Both validators accept hypothesis with all fields."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "hypotheses": [
        {
          "id": "SPEC-001.HYP-01",
          "statement": "Caching will improve response times by 50%",
          "status": "validated",
        }
      ],
    }
    self._assert_both_valid(data)

  # Sources validation (8 tests)

  def test_valid_python_source(self) -> None:
    """Both validators accept valid Python source."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "sources": [
        {
          "language": "python",
          "identifier": "supekku/scripts/lib/workspace.py",
          "module": "supekku.scripts.lib.workspace",
          "variants": [
            {"name": "api", "path": "contracts/api.md"},
          ],
        }
      ],
    }
    self._assert_both_valid(data)

  def test_valid_go_source(self) -> None:
    """Both validators accept valid Go source."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "sources": [
        {
          "language": "go",
          "identifier": "internal/application/services/git",
          "variants": [
            {"name": "public", "path": "contracts/go/git-public.md"},
            {"name": "internal", "path": "contracts/go/git-internal.md"},
          ],
        }
      ],
    }
    self._assert_both_valid(data)

  def test_valid_multiple_sources(self) -> None:
    """Both validators accept multiple sources."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "sources": [
        {
          "language": "python",
          "identifier": "supekku/main.py",
          "module": "supekku.main",
          "variants": [{"name": "api", "path": "contracts/main-api.md"}],
        },
        {
          "language": "go",
          "identifier": "cmd/vice/main.go",
          "variants": [{"name": "public", "path": "contracts/vice-api.md"}],
        },
      ],
    }
    self._assert_both_valid(data)

  def test_source_missing_language(self) -> None:
    """New validator rejects source missing language."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "sources": [
        {
          # Missing language
          "identifier": "supekku/main.py",
          "variants": [{"name": "api", "path": "contracts/api.md"}],
        }
      ],
    }
    new_validator = MetadataValidator(SPEC_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject source missing language")

  def test_source_invalid_language(self) -> None:
    """New validator rejects source with invalid language."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "sources": [
        {
          "language": "rust",  # Not in enum
          "identifier": "src/main.rs",
          "variants": [{"name": "api", "path": "contracts/api.md"}],
        }
      ],
    }
    new_validator = MetadataValidator(SPEC_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid language")

  def test_source_missing_variants(self) -> None:
    """New validator rejects source missing variants."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "sources": [
        {
          "language": "python",
          "identifier": "supekku/main.py",
          # Missing variants
        }
      ],
    }
    new_validator = MetadataValidator(SPEC_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject source missing variants")

  def test_source_empty_variants_array(self) -> None:
    """New validator rejects source with empty variants array."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "sources": [
        {
          "language": "python",
          "identifier": "supekku/main.py",
          "variants": [],  # Empty array
        }
      ],
    }
    new_validator = MetadataValidator(SPEC_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty variants array")

  def test_variant_missing_required_fields(self) -> None:
    """New validator rejects variant missing name or path."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "sources": [
        {
          "language": "python",
          "identifier": "supekku/main.py",
          "variants": [
            {
              "name": "api",
              # Missing path
            }
          ],
        }
      ],
    }
    new_validator = MetadataValidator(SPEC_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject variant missing path")

  # Array validation (4 tests)

  def test_empty_spec_arrays_valid(self) -> None:
    """Both validators accept empty arrays for spec fields."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "responsibilities": [],
      "guiding_principles": [],
      "assumptions": [],
      "constraints": [],
      "packages": [],
    }
    self._assert_both_valid(data)

  def test_valid_responsibilities_array(self) -> None:
    """Both validators accept valid responsibilities."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "responsibilities": [
        "Process user authentication requests",
        "Maintain session state",
        "Enforce authorization policies",
      ],
    }
    self._assert_both_valid(data)

  def test_valid_guiding_principles_array(self) -> None:
    """Both validators accept valid guiding_principles."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "guiding_principles": [
        "Fail fast and loudly",
        "Prefer composition over inheritance",
        "Write tests first",
      ],
    }
    self._assert_both_valid(data)

  def test_valid_constraints_array(self) -> None:
    """Both validators accept valid constraints."""
    data = {
      "id": "SPEC-001",
      "name": "Test Spec",
      "slug": "test-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
      "constraints": [
        "Must run on Python 3.12+",
        "Response time must be under 100ms",
        "Must support 1000 concurrent users",
      ],
    }
    self._assert_both_valid(data)


if __name__ == "__main__":
  unittest.main()
