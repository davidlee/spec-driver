"""Validation tests for revision change metadata.

P03 C5 retires ``RevisionBlockValidator``; these tests capture the
positive paths and negative branches the legacy class enforced plus
the four ``REVISION_BLOCK_JSON_SCHEMA`` regex-bug cases that the
metadata-driven validator now handles correctly (DR-118 §5).

DEC-007 header note: tightening or relaxing rules here is an
*intended* drift event handled in the delta that introduces it.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import (
  MetadataValidator,
  metadata_to_json_schema,
)

from .revision_metadata import (
  REVISION_CHANGE_METADATA,
  validate_revision_change,
)


class RevisionChangeValidationTest(unittest.TestCase):
  """Test wrapper + metadata validator against retired class semantics."""

  def _validate_both(self, data: dict) -> tuple[list[str], list[str]]:
    """Run wrapper and metadata validator; return (wrapper, metadata)."""
    wrapper_errors = validate_revision_change(data)
    direct_validator = MetadataValidator(REVISION_CHANGE_METADATA)
    direct_errors = [
      str(err) for err in direct_validator.validate(data, strict=True)
    ]
    return wrapper_errors, direct_errors

  # Root level tests

  def test_valid_minimal_block(self):
    """Both paths accept valid minimal block."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {
        "revision": "RE-001",
      },
      "specs": [],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_valid_complete_block(self):
    """Both paths accept block with all optional fields."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {
        "revision": "RE-001",
        "prepared_by": "system",
        "generated_at": "2025-01-15T10:00:00Z",
      },
      "specs": [
        {
          "spec_id": "SPEC-100",
          "action": "created",
          "summary": "New spec",
          "requirement_flow": {
            "added": ["SPEC-100.FR-001"],
            "removed": [],
            "moved_in": [],
            "moved_out": [],
          },
          "section_changes": [
            {
              "section": "Introduction",
              "change": "added",
              "notes": "Added intro section",
            }
          ],
        }
      ],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "introduce",
          "summary": "New requirement",
          "destination": {
            "spec": "SPEC-100",
            "path": "/section/intro",
            "additional_specs": ["SPEC-200"],
          },
          "lifecycle": {
            "status": "pending",
            "introduced_by": "RE-001",
            "implemented_by": ["DE-001"],
            "verified_by": ["AUD-001"],
          },
          "text_changes": {
            "before_excerpt": "Before text",
            "after_excerpt": "After text",
            "diff_ref": "diff-001",
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_missing_schema_field(self):
    """Both paths reject missing schema field."""
    data = {
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("schema" in err.lower() for err in wrapper_errors)
    assert any("schema" in err.lower() for err in direct_errors)

  def test_wrong_schema_value(self):
    """Both paths reject wrong schema value."""
    data = {
      "schema": "wrong.schema",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("schema" in err.lower() for err in wrapper_errors)
    assert any("schema" in err.lower() for err in direct_errors)

  def test_missing_version_field(self):
    """Both paths reject missing version field."""
    data = {
      "schema": "supekku.revision.change",
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("version" in err.lower() for err in wrapper_errors)
    assert any("version" in err.lower() for err in direct_errors)

  # Metadata tests

  def test_valid_metadata_with_all_fields(self):
    """Both paths accept metadata with all optional fields."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {
        "revision": "RE-123",
        "prepared_by": "alice",
        "generated_at": "2025-01-15",
      },
      "specs": [],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_missing_revision_field(self):
    """Both paths reject missing revision field in metadata."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {
        "prepared_by": "alice",
      },
      "specs": [],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("revision" in err.lower() for err in wrapper_errors)
    assert any("revision" in err.lower() for err in direct_errors)

  def test_invalid_revision_pattern(self):
    """Both paths reject invalid revision ID pattern."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {
        "revision": "INVALID-001",
      },
      "specs": [],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("revision" in err.lower() for err in wrapper_errors)
    assert any("revision" in err.lower() for err in direct_errors)

  def test_prepared_by_wrong_type(self):
    """Both paths reject wrong type for prepared_by."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {
        "revision": "RE-001",
        "prepared_by": 123,
      },
      "specs": [],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("prepared_by" in err.lower() for err in wrapper_errors)
    assert any("prepared_by" in err.lower() for err in direct_errors)

  def test_generated_at_wrong_type(self):
    """Both paths reject wrong type for generated_at."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {
        "revision": "RE-001",
        "generated_at": 12345,
      },
      "specs": [],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("generated_at" in err.lower() for err in wrapper_errors)
    assert any("generated_at" in err.lower() for err in direct_errors)

  # Specs tests

  def test_valid_spec_entry(self):
    """Both paths accept valid spec entry."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [
        {
          "spec_id": "SPEC-100",
          "action": "created",
        }
      ],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_missing_specs_array(self):
    """Both paths reject missing specs array."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("specs" in err.lower() for err in wrapper_errors)
    assert any("specs" in err.lower() for err in direct_errors)

  def test_specs_wrong_type(self):
    """Both paths reject specs as non-array."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": "not-an-array",
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("specs" in err.lower() for err in wrapper_errors)
    assert any("specs" in err.lower() for err in direct_errors)

  def test_spec_missing_spec_id(self):
    """Both paths reject spec without spec_id."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [
        {
          "action": "created",
        }
      ],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("spec_id" in err.lower() for err in wrapper_errors)
    assert any("spec_id" in err.lower() for err in direct_errors)

  def test_spec_missing_action(self):
    """Both paths reject spec without action."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [
        {
          "spec_id": "SPEC-100",
        }
      ],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("action" in err.lower() for err in wrapper_errors)
    assert any("action" in err.lower() for err in direct_errors)

  def test_spec_id_wrong_pattern(self):
    """Both paths reject invalid spec_id pattern."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [
        {
          "spec_id": "INVALID",
          "action": "created",
        }
      ],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("spec_id" in err.lower() for err in wrapper_errors)
    assert any("spec_id" in err.lower() for err in direct_errors)

  def test_spec_action_invalid_enum(self):
    """Both paths reject invalid action enum value."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [
        {
          "spec_id": "SPEC-100",
          "action": "invalid",
        }
      ],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("action" in err.lower() for err in wrapper_errors)
    assert any("action" in err.lower() for err in direct_errors)

  def test_requirement_flow_structure(self):
    """Both paths accept valid requirement_flow structure."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [
        {
          "spec_id": "SPEC-100",
          "action": "updated",
          "requirement_flow": {
            "added": ["SPEC-100.FR-001"],
            "removed": ["SPEC-100.FR-002"],
          },
        }
      ],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_requirement_flow_invalid_pattern(self):
    """Both paths reject invalid requirement ID in flow."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [
        {
          "spec_id": "SPEC-100",
          "action": "updated",
          "requirement_flow": {
            "added": ["INVALID-ID"],
          },
        }
      ],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert len(wrapper_errors) > 0
    assert len(direct_errors) > 0

  def test_section_changes_structure(self):
    """Both paths accept valid section_changes structure."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [
        {
          "spec_id": "SPEC-100",
          "action": "updated",
          "section_changes": [
            {
              "section": "Overview",
              "change": "added",
              "notes": "Added overview section",
            }
          ],
        }
      ],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  # Requirements tests

  def test_valid_requirement_introduce(self):
    """Both paths accept valid requirement with introduce action."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "introduce",
          "destination": {
            "spec": "SPEC-100",
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_valid_requirement_move(self):
    """Both paths accept valid requirement with move action and origin."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "move",
          "origin": [
            {
              "kind": "spec",
              "ref": "SPEC-200",
            }
          ],
          "destination": {
            "spec": "SPEC-100",
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_valid_requirement_modify(self):
    """Both paths accept valid requirement with modify action."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "modify",
          "destination": {
            "spec": "SPEC-100",
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_valid_requirement_retire(self):
    """Both paths accept valid requirement with retire action."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "retire",
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_requirement_missing_requirement_id(self):
    """Both paths reject requirement without requirement_id."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "kind": "functional",
          "action": "retire",
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("requirement_id" in err.lower() for err in wrapper_errors)
    assert any("requirement_id" in err.lower() for err in direct_errors)

  def test_requirement_invalid_requirement_id_pattern(self):
    """Both paths reject invalid requirement_id pattern."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "INVALID",
          "kind": "functional",
          "action": "retire",
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("requirement_id" in err.lower() for err in wrapper_errors)
    assert any("requirement_id" in err.lower() for err in direct_errors)

  def test_requirement_invalid_kind(self):
    """Both paths reject invalid kind enum."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "invalid",
          "action": "retire",
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("kind" in err.lower() for err in wrapper_errors)
    assert any("kind" in err.lower() for err in direct_errors)

  def test_requirement_invalid_action(self):
    """Both paths reject invalid action enum."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "invalid",
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("action" in err.lower() for err in wrapper_errors)
    assert any("action" in err.lower() for err in direct_errors)

  def test_requirement_destination_structure(self):
    """Both paths accept valid destination structure."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "introduce",
          "destination": {
            "spec": "SPEC-100",
            "requirement_id": "SPEC-100.FR-001",
            "path": "/section/intro",
            "additional_specs": ["SPEC-200", "SPEC-300"],
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_requirement_additional_specs_invalid_pattern(self):
    """Both paths reject invalid SPEC id inside additional_specs."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "introduce",
          "destination": {
            "spec": "SPEC-100",
            "additional_specs": ["SPEC-FOO", "SPEC-200"],
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert any("additional_specs" in err.lower() for err in wrapper_errors)
    assert any("additional_specs" in err.lower() for err in direct_errors)

  def test_requirement_destination_spec_invalid_pattern(self):
    """Both paths reject invalid spec pattern in destination."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "introduce",
          "destination": {
            "spec": "INVALID",
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert len(wrapper_errors) > 0
    assert len(direct_errors) > 0

  def test_requirement_lifecycle_structure(self):
    """Both paths accept valid lifecycle structure."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "retire",
          "lifecycle": {
            "status": "pending",
            "introduced_by": "RE-001",
            "implemented_by": ["DE-001", "DE-002"],
            "verified_by": ["AUD-001"],
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_requirement_lifecycle_invalid_status(self):
    """Both paths reject invalid lifecycle status."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "retire",
          "lifecycle": {
            "status": "invalid-status",
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert len(wrapper_errors) > 0
    assert len(direct_errors) > 0

  def test_requirement_implemented_by_pattern(self):
    """Both paths reject invalid delta ID in implemented_by."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "retire",
          "lifecycle": {
            "implemented_by": ["INVALID"],
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert len(wrapper_errors) > 0
    assert len(direct_errors) > 0

  def test_requirement_verified_by_pattern(self):
    """Both paths reject invalid audit ID in verified_by."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "retire",
          "lifecycle": {
            "verified_by": ["INVALID"],
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert len(wrapper_errors) > 0
    assert len(direct_errors) > 0

  def test_requirement_text_changes_structure(self):
    """Both paths accept valid text_changes structure."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "retire",
          "text_changes": {
            "before_excerpt": "Old text",
            "after_excerpt": "New text",
            "diff_ref": "diff-001",
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  # Regex-bug regression tests (DR-118 §5)
  #
  # REVISION_BLOCK_JSON_SCHEMA carried four double-escaped regex patterns
  # (e.g. ``r"^RE-\\d{3,}$"``) that would have rejected canonical RE/DE/AUD
  # identifiers had any consumer evaluated them. The hand-rolled
  # ``RevisionBlockValidator`` ignored those JSON Schema patterns and used
  # ``is_kind`` instead; the metadata-driven validator uses the correctly
  # escaped patterns. These tests pin the metadata behaviour to the canonical
  # IDs so a regression that reintroduces the double-backslash slips earlier.

  def test_regex_bug_metadata_revision_accepts_canonical_re_id(self):
    """Canonical RE-### accepted in metadata.revision (was buggy in JSON schema)."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_regex_bug_lifecycle_introduced_by_accepts_canonical_re_id(self):
    """RE-### accepted in lifecycle.introduced_by (was buggy in JSON schema)."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "retire",
          "lifecycle": {
            "introduced_by": "RE-042",
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_regex_bug_lifecycle_implemented_by_accepts_canonical_de_id(self):
    """DE-### accepted in lifecycle.implemented_by (was buggy in JSON schema)."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "retire",
          "lifecycle": {
            "implemented_by": ["DE-118", "DE-001"],
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  def test_regex_bug_lifecycle_verified_by_accepts_canonical_aud_id(self):
    """AUD-### accepted in lifecycle.verified_by (was buggy in JSON schema)."""
    data = {
      "schema": "supekku.revision.change",
      "version": 1,
      "metadata": {"revision": "RE-001"},
      "specs": [],
      "requirements": [
        {
          "requirement_id": "SPEC-100.FR-001",
          "kind": "functional",
          "action": "retire",
          "lifecycle": {
            "verified_by": ["AUD-001", "AUD-042"],
          },
        }
      ],
    }

    wrapper_errors, direct_errors = self._validate_both(data)
    assert wrapper_errors == []
    assert direct_errors == []

  # JSON Schema generation test

  def test_metadata_generates_json_schema(self):
    """Metadata can be converted to valid JSON Schema."""
    schema = metadata_to_json_schema(REVISION_CHANGE_METADATA)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "required" in schema

    assert "schema" in schema["properties"]
    assert "version" in schema["properties"]
    assert "metadata" in schema["properties"]
    assert "specs" in schema["properties"]
    assert "requirements" in schema["properties"]

    assert "schema" in schema["required"]
    assert "version" in schema["required"]
    assert "metadata" in schema["required"]
    assert "specs" in schema["required"]
    assert "requirements" in schema["required"]


if __name__ == "__main__":
  unittest.main()
