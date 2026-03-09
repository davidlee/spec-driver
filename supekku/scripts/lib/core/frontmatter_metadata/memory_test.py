"""Dual-validation tests for memory frontmatter metadata."""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator
from supekku.scripts.lib.core.frontmatter_schema import (
  FrontmatterValidationError,
  validate_frontmatter,
)

from .memory import MEMORY_FRONTMATTER_METADATA


def _minimal_memory(**overrides: object) -> dict:
  """Build a minimal valid memory record, with optional overrides."""
  data: dict = {
    "id": "mem.fact.test",
    "name": "Test Memory",
    "slug": "test-memory",
    "kind": "memory",
    "status": "active",
    "created": "2026-03-01",
    "updated": "2026-03-01",
    "memory_type": "fact",
    "confidence": "medium",
  }
  data.update(overrides)
  return data


class MemoryFrontmatterValidationTest(unittest.TestCase):
  """Test metadata validator for memory-specific fields."""

  def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    """Run both validators and return (old_error, new_errors)."""
    old_error = None
    try:
      validate_frontmatter(data)
    except FrontmatterValidationError as e:
      old_error = str(e)

    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_error, new_errors

  def _assert_both_valid(self, data: dict) -> None:
    """Assert both validators accept the data."""
    old_error, new_errors = self._validate_both(data)
    self.assertIsNone(old_error, f"Old validator rejected: {old_error}")
    self.assertEqual(new_errors, [], f"New validator rejected: {new_errors}")

  # ── Valid cases ──────────────────────────────────────────────

  def test_valid_minimal_memory(self) -> None:
    """Both validators accept minimal memory (base fields + memory_type)."""
    self._assert_both_valid(_minimal_memory())

  def test_valid_memory_with_all_fields(self) -> None:
    """Both validators accept memory with all optional fields."""
    data = {
      "id": "mem.signpost.auth.prereading",
      "name": "ADR-11 Required Pre-Reading for Auth Changes",
      "slug": "mem-adr11-required-for-auth",
      "kind": "memory",
      "status": "active",
      "lifecycle": "maintenance",
      "created": "2026-02-01",
      "updated": "2026-03-01",
      "memory_type": "signpost",
      "confidence": "high",
      "verified": "2026-03-01",
      "review_by": "2026-05-01",
      "owners": ["platform-team"],
      "summary": "Pre-read: ADR-11 before modifying auth flow",
      "tags": ["auth", "pre-read"],
      "requires_reading": [
        "specify/decisions/ADR-011-auth-flow.md",
        "memory/system/auth.md",
      ],
      "scope": {
        "globs": ["src/auth/**", "packages/auth/**"],
        "paths": ["src/auth/cache.ts"],
        "commands": ["test auth:integration"],
        "languages": ["ts"],
        "platforms": ["linux"],
      },
      "priority": {
        "severity": "high",
        "weight": 10,
      },
      "provenance": {
        "sources": [
          {"kind": "adr", "ref": "specify/decisions/ADR-011-auth-flow.md"},
        ],
      },
      "audience": ["human", "agent"],
      "visibility": ["pre"],
      "relations": [
        {"type": "relates_to", "target": "ADR-011"},
      ],
    }
    self._assert_both_valid(data)

  def test_valid_all_memory_types(self) -> None:
    """Both validators accept all memory_type enum values."""
    for memory_type in ["concept", "fact", "pattern", "signpost", "system", "thread"]:
      with self.subTest(memory_type=memory_type):
        self._assert_both_valid(_minimal_memory(memory_type=memory_type))

  def test_valid_all_confidence_values(self) -> None:
    """Both validators accept all confidence enum values."""
    for confidence in ["low", "medium", "high"]:
      with self.subTest(confidence=confidence):
        self._assert_both_valid(_minimal_memory(confidence=confidence))

  def test_valid_all_severity_values(self) -> None:
    """Both validators accept all priority.severity enum values."""
    for severity in ["none", "low", "medium", "high", "critical"]:
      with self.subTest(severity=severity):
        self._assert_both_valid(
          _minimal_memory(priority={"severity": severity}),
        )

  def test_valid_verified_date(self) -> None:
    """Both validators accept valid verified date."""
    self._assert_both_valid(_minimal_memory(verified="2026-03-01"))

  def test_valid_review_by_date(self) -> None:
    """Both validators accept valid review_by date."""
    self._assert_both_valid(_minimal_memory(review_by="2026-06-01"))

  def test_valid_empty_arrays(self) -> None:
    """Both validators accept empty arrays for memory-specific fields."""
    self._assert_both_valid(
      _minimal_memory(
        requires_reading=[],
        audience=[],
        visibility=[],
        tags=[],
      )
    )

  def test_valid_scope_partial(self) -> None:
    """Both validators accept scope with only some sub-fields."""
    self._assert_both_valid(
      _minimal_memory(scope={"globs": ["src/**"]}),
    )

  def test_valid_scope_empty(self) -> None:
    """Both validators accept empty scope object."""
    self._assert_both_valid(_minimal_memory(scope={}))

  def test_valid_provenance_empty_sources(self) -> None:
    """Both validators accept provenance with empty sources."""
    self._assert_both_valid(
      _minimal_memory(provenance={"sources": []}),
    )

  def test_valid_audience_single(self) -> None:
    """Both validators accept single audience value."""
    self._assert_both_valid(_minimal_memory(audience=["agent"]))

  def test_valid_visibility_both(self) -> None:
    """Both validators accept both visibility values."""
    self._assert_both_valid(
      _minimal_memory(visibility=["pre", "on_demand"]),
    )

  def test_valid_priority_weight_only(self) -> None:
    """Both validators accept priority with weight only."""
    self._assert_both_valid(_minimal_memory(priority={"weight": 5}))

  # ── Invalid cases (new validator only) ──────────────────────

  def test_invalid_memory_type(self) -> None:
    """New validator rejects invalid memory_type."""
    data = _minimal_memory(memory_type="note")  # Not in enum
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid memory_type")

  def test_missing_memory_type(self) -> None:
    """New validator rejects missing memory_type."""
    data = _minimal_memory()
    del data["memory_type"]
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject missing memory_type")

  def test_invalid_confidence(self) -> None:
    """New validator rejects invalid confidence."""
    data = _minimal_memory(confidence="very_high")  # Not in enum
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid confidence")

  def test_invalid_verified_date_format(self) -> None:
    """New validator rejects invalid verified date format."""
    data = _minimal_memory(verified="2026/03/01")  # Wrong format
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid verified date format")

  def test_invalid_review_by_date_format(self) -> None:
    """New validator rejects invalid review_by date format."""
    data = _minimal_memory(review_by="March 2026")  # Wrong format
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid review_by date format")

  def test_invalid_severity(self) -> None:
    """New validator rejects invalid priority.severity."""
    data = _minimal_memory(priority={"severity": "urgent"})  # Not in enum
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid severity")

  def test_invalid_audience_value(self) -> None:
    """New validator rejects invalid audience enum value."""
    data = _minimal_memory(audience=["bot"])  # Not in enum
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid audience value")

  def test_invalid_visibility_value(self) -> None:
    """New validator rejects invalid visibility enum value."""
    data = _minimal_memory(visibility=["always"])  # Not in enum
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject invalid visibility value")

  def test_empty_string_in_requires_reading(self) -> None:
    """New validator rejects empty strings in requires_reading."""
    data = _minimal_memory(requires_reading=["valid/path.md", ""])
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors,
      [],
      "Should reject empty string in requires_reading",
    )

  def test_empty_string_in_scope_globs(self) -> None:
    """New validator rejects empty strings in scope.globs."""
    data = _minimal_memory(scope={"globs": ["src/**", ""]})
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in scope.globs")

  def test_empty_string_in_scope_paths(self) -> None:
    """New validator rejects empty strings in scope.paths."""
    data = _minimal_memory(scope={"paths": [""]})
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject empty string in scope.paths")

  def test_empty_string_in_scope_commands(self) -> None:
    """New validator rejects empty strings in scope.commands."""
    data = _minimal_memory(scope={"commands": [""]})
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors,
      [],
      "Should reject empty string in scope.commands",
    )

  def test_requires_reading_not_array(self) -> None:
    """New validator rejects requires_reading when not an array."""
    data = _minimal_memory(requires_reading="single/path.md")
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(
      new_errors,
      [],
      "Should reject requires_reading as non-array",
    )

  def test_audience_not_array(self) -> None:
    """New validator rejects audience when not an array."""
    data = _minimal_memory(audience="human")
    new_validator = MetadataValidator(MEMORY_FRONTMATTER_METADATA)
    new_errors = new_validator.validate(data)
    self.assertNotEqual(new_errors, [], "Should reject audience as non-array")

  # ── Links field tests ──────────────────────────────────────

  def test_valid_links_with_out(self) -> None:
    """Both validators accept links with resolved out entries."""
    data = _minimal_memory(
      links={
        "out": [
          {"id": "ADR-001", "path": "decisions/ADR-001.md", "kind": "adr"},
        ],
      },
    )
    self._assert_both_valid(data)

  def test_valid_links_with_label(self) -> None:
    """Both validators accept links out entry with optional label."""
    data = _minimal_memory(
      links={
        "out": [
          {
            "id": "ADR-001",
            "path": "decisions/ADR-001.md",
            "kind": "adr",
            "label": "Auth Decision",
          },
        ],
      },
    )
    self._assert_both_valid(data)

  def test_valid_links_with_missing(self) -> None:
    """Both validators accept links with missing entries."""
    data = _minimal_memory(
      links={
        "missing": [{"raw": "ADR-999"}],
      },
    )
    self._assert_both_valid(data)

  def test_valid_links_mixed(self) -> None:
    """Both validators accept links with out and missing."""
    data = _minimal_memory(
      links={
        "out": [
          {"id": "SPEC-001", "path": "s.md", "kind": "spec"},
        ],
        "missing": [{"raw": "NOPE-999"}],
      },
    )
    self._assert_both_valid(data)

  def test_valid_links_empty(self) -> None:
    """Both validators accept empty links object."""
    self._assert_both_valid(_minimal_memory(links={}))


if __name__ == "__main__":
  unittest.main()
