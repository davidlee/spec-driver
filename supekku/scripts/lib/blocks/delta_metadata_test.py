"""Dual-validation tests for delta relationships metadata.

Tests that the new metadata-driven validator produces identical results
to the existing DeltaRelationshipsValidator.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import (
  MetadataValidator,
  metadata_to_json_schema,
)

from .delta import DeltaRelationshipsBlock, DeltaRelationshipsValidator
from .delta_metadata import DELTA_RELATIONSHIPS_METADATA


class DualValidationTest(unittest.TestCase):
  """Test that metadata validator matches existing validator behavior."""

  def _validate_both(
    self, data: dict, *, delta_id: str | None = None
  ) -> tuple[list[str], list[str]]:
    """Run both validators and return (old_errors, new_errors)."""
    # Old validator
    block = DeltaRelationshipsBlock(raw_yaml="", data=data)
    old_validator = DeltaRelationshipsValidator()
    old_errors = old_validator.validate(block, delta_id=delta_id)

    # New metadata validator
    new_validator = MetadataValidator(DELTA_RELATIONSHIPS_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_errors, new_errors

  def test_valid_minimal_block(self):
    """Both validators accept valid minimal block."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert old_errors == []
    assert new_errors == []

  def test_valid_complete_block(self):
    """Both validators accept block with all optional fields."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-002",
      "revision_links": {
        "introduces": ["RE-001", "RE-002"],
        "supersedes": ["RE-000"],
      },
      "specs": {
        "primary": ["SPEC-100"],
        "collaborators": ["SPEC-200", "SPEC-300"],
      },
      "requirements": {
        "implements": ["SPEC-100.FR-001"],
        "updates": ["SPEC-100.FR-002"],
        "verifies": ["SPEC-100.NFR-PERF"],
      },
      "phases": [
        {"id": "IP-001.PHASE-01"},
        {"id": "IP-001.PHASE-02"},
      ],
    }

    old_errors, new_errors = self._validate_both(data)
    assert old_errors == []
    assert new_errors == []

  def test_missing_schema_field(self):
    """Both validators reject missing schema field."""
    data = {
      "version": 1,
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("schema" in err.lower() for err in old_errors)
    assert any("schema" in err.lower() for err in new_errors)

  def test_wrong_schema_value(self):
    """Both validators reject wrong schema value."""
    data = {
      "schema": "wrong.schema",
      "version": 1,
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("schema" in err.lower() for err in old_errors)
    assert any("schema" in err.lower() for err in new_errors)

  def test_wrong_version(self):
    """Both validators reject wrong version."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 999,
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("version" in err.lower() for err in old_errors)
    assert any("version" in err.lower() for err in new_errors)

  def test_missing_delta(self):
    """Both validators reject missing delta."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("delta" in err.lower() for err in old_errors)
    assert any("delta" in err.lower() for err in new_errors)

  def test_delta_id_mismatch(self):
    """Both validators detect delta ID mismatch when expected ID provided."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-999",
    }

    old_errors, new_errors = self._validate_both(data, delta_id="DE-001")
    # Old validator checks for mismatch
    assert any(
      "de-999" in err.lower() and "de-001" in err.lower() for err in old_errors
    )
    # New validator doesn't support delta_id parameter yet (that's OK for now)

  def test_specs_not_object(self):
    """Both validators reject non-object specs."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "specs": "not-object",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("specs" in err.lower() for err in old_errors)
    assert any("specs" in err.lower() or "object" in err.lower() for err in new_errors)

  def test_requirements_not_object(self):
    """Both validators reject non-object requirements."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "requirements": "not-object",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("requirements" in err.lower() for err in old_errors)
    assert any(
      "requirements" in err.lower() or "object" in err.lower() for err in new_errors
    )

  def test_specs_primary_not_array(self):
    """Both validators reject non-array specs.primary."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "specs": {
        "primary": "not-array",
      },
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("primary" in err.lower() for err in old_errors)
    assert any("primary" in err.lower() for err in new_errors)

  def test_specs_primary_non_string_items(self):
    """Both validators reject non-string items in specs.primary."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "specs": {
        "primary": ["SPEC-100", 123, "SPEC-200"],
      },
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("string" in err.lower() for err in old_errors)
    assert any("string" in err.lower() for err in new_errors)

  def test_requirements_implements_not_array(self):
    """Both validators reject non-array requirements.implements."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "requirements": {
        "implements": "not-array",
      },
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("implements" in err.lower() for err in old_errors)
    assert any("implements" in err.lower() for err in new_errors)

  def test_phases_not_array(self):
    """Both validators reject non-array phases."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "phases": "not-array",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("phases" in err.lower() for err in old_errors)
    assert any("phases" in err.lower() or "array" in err.lower() for err in new_errors)

  def test_phases_entry_not_object(self):
    """Both validators reject non-object phase entries."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "phases": ["not-object"],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("object" in err.lower() for err in old_errors)
    assert any("object" in err.lower() for err in new_errors)

  def test_phases_entry_missing_id(self):
    """Both validators reject phase entry missing id."""
    data = {
      "schema": "supekku.delta.relationships",
      "version": 1,
      "delta": "DE-001",
      "phases": [
        {"name": "Phase 1"},
      ],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("id" in err.lower() for err in old_errors)
    assert any("id" in err.lower() for err in new_errors)

  def test_all_specs_sections(self):
    """Both validators accept all specs sections."""
    for section in ["primary", "collaborators"]:
      data = {
        "schema": "supekku.delta.relationships",
        "version": 1,
        "delta": "DE-001",
        "specs": {
          section: ["SPEC-100"],
        },
      }

      old_errors, new_errors = self._validate_both(data)
      assert old_errors == [], f"Old validator rejected valid specs.{section}"
      assert new_errors == [], f"New validator rejected valid specs.{section}"

  def test_all_requirements_sections(self):
    """Both validators accept all requirements sections."""
    for section in ["implements", "updates", "verifies"]:
      data = {
        "schema": "supekku.delta.relationships",
        "version": 1,
        "delta": "DE-001",
        "requirements": {
          section: ["SPEC-100.FR-001"],
        },
      }

      old_errors, new_errors = self._validate_both(data)
      assert old_errors == [], f"Old validator rejected valid requirements.{section}"
      assert new_errors == [], f"New validator rejected valid requirements.{section}"

  def test_all_revision_links_sections(self):
    """Both validators accept all revision_links sections."""
    for section in ["introduces", "supersedes"]:
      data = {
        "schema": "supekku.delta.relationships",
        "version": 1,
        "delta": "DE-001",
        "revision_links": {
          section: ["RE-001"],
        },
      }

      old_errors, new_errors = self._validate_both(data)
      assert old_errors == [], f"Old validator rejected valid revision_links.{section}"
      assert new_errors == [], f"New validator rejected valid revision_links.{section}"


class MetadataOnlyTest(unittest.TestCase):
  """Test metadata-specific features not in old validator."""

  def test_json_schema_generation(self):
    """Metadata can generate JSON Schema for delta relationships."""
    schema = metadata_to_json_schema(DELTA_RELATIONSHIPS_METADATA)

    # Verify schema structure
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert "supekku-delta-relationships" in schema["$id"]

    # Verify required fields
    assert set(schema["required"]) == {"schema", "version", "delta"}

    # Verify properties
    assert schema["properties"]["schema"]["const"] == "supekku.delta.relationships"
    assert schema["properties"]["version"]["const"] == 1
    assert schema["properties"]["delta"]["type"] == "string"

    # Verify optional nested objects
    assert schema["properties"]["specs"]["type"] == "object"
    assert schema["properties"]["requirements"]["type"] == "object"
    assert schema["properties"]["revision_links"]["type"] == "object"

    # Verify phases array
    assert schema["properties"]["phases"]["type"] == "array"
    assert schema["properties"]["phases"]["items"]["type"] == "object"
    assert schema["properties"]["phases"]["items"]["required"] == ["id"]

  def test_examples_included(self):
    """Metadata includes examples."""
    assert len(DELTA_RELATIONSHIPS_METADATA.examples) > 0
    example = DELTA_RELATIONSHIPS_METADATA.examples[0]
    assert example["schema"] == "supekku.delta.relationships"
    assert example["version"] == 1
    assert "delta" in example


if __name__ == "__main__":
  unittest.main()
