"""Validation tests for spec relationships + capabilities metadata.

P03 C4 retires ``RelationshipsBlockValidator``; these tests capture
the negative branches of the retired class plus wrapper-specific
behaviour for ``validate_spec_relationships`` and the ergonomic
``validate_spec_capabilities``.

DEC-007 header note: tightening or relaxing rules here is an
*intended* drift event handled in the delta that introduces it.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import (
  MetadataValidator,
  metadata_to_json_schema,
)

from .relationships import RelationshipsBlock
from .spec_metadata import (
  SPEC_CAPABILITIES_METADATA,
  SPEC_RELATIONSHIPS_METADATA,
  validate_spec_capabilities,
  validate_spec_relationships,
)


def _block(data: dict) -> RelationshipsBlock:
  return RelationshipsBlock(raw_yaml="", data=data)


class SpecRelationshipsWrapperTest(unittest.TestCase):
  """validate_spec_relationships ID-equality + metadata composition."""

  def test_valid_minimal_block(self):
    block = _block(
      {
        "schema": "supekku.spec.relationships",
        "version": 1,
        "spec": "SPEC-001",
      }
    )
    assert validate_spec_relationships(block) == []

  def test_valid_complete_block(self):
    block = _block(
      {
        "schema": "supekku.spec.relationships",
        "version": 1,
        "spec": "SPEC-001",
        "requirements": {
          "primary": ["SPEC-001.FR-001"],
          "collaborators": ["SPEC-002.FR-010"],
        },
        "interactions": [
          {"type": "calls", "spec": "SPEC-002", "notes": "lookup"},
        ],
      }
    )
    assert validate_spec_relationships(block, spec_id="SPEC-001") == []

  def test_missing_schema_field(self):
    block = _block({"version": 1, "spec": "SPEC-001"})
    errors = validate_spec_relationships(block)
    assert any("schema" in err.lower() for err in errors)

  def test_wrong_schema_value(self):
    block = _block({"schema": "wrong.schema", "version": 1, "spec": "SPEC-001"})
    errors = validate_spec_relationships(block)
    assert any("schema" in err.lower() for err in errors)

  def test_wrong_version(self):
    block = _block(
      {"schema": "supekku.spec.relationships", "version": 999, "spec": "SPEC-001"}
    )
    errors = validate_spec_relationships(block)
    assert any("version" in err.lower() for err in errors)

  def test_missing_spec(self):
    block = _block({"schema": "supekku.spec.relationships", "version": 1})
    errors = validate_spec_relationships(block)
    assert any("spec" in err.lower() for err in errors)

  def test_spec_id_match_accepts(self):
    block = _block(
      {"schema": "supekku.spec.relationships", "version": 1, "spec": "SPEC-001"}
    )
    assert validate_spec_relationships(block, spec_id="SPEC-001") == []

  def test_spec_id_mismatch(self):
    block = _block(
      {"schema": "supekku.spec.relationships", "version": 1, "spec": "SPEC-999"}
    )
    errors = validate_spec_relationships(block, spec_id="SPEC-001")
    assert any(
      "spec-999" in err.lower() and "spec-001" in err.lower() for err in errors
    )

  def test_spec_id_none_skips_id_check(self):
    block = _block(
      {"schema": "supekku.spec.relationships", "version": 1, "spec": "SPEC-999"}
    )
    assert validate_spec_relationships(block, spec_id=None) == []

  def test_spec_id_empty_skips_id_check(self):
    block = _block(
      {"schema": "supekku.spec.relationships", "version": 1, "spec": "SPEC-999"}
    )
    assert validate_spec_relationships(block, spec_id="") == []

  def test_requirements_not_object(self):
    block = _block(
      {
        "schema": "supekku.spec.relationships",
        "version": 1,
        "spec": "SPEC-001",
        "requirements": "not-object",
      }
    )
    errors = validate_spec_relationships(block)
    assert any(
      "requirements" in err.lower() or "object" in err.lower() for err in errors
    )

  def test_requirements_primary_not_array(self):
    block = _block(
      {
        "schema": "supekku.spec.relationships",
        "version": 1,
        "spec": "SPEC-001",
        "requirements": {"primary": "not-array"},
      }
    )
    errors = validate_spec_relationships(block)
    assert any("primary" in err.lower() for err in errors)

  def test_requirements_primary_non_string_items(self):
    block = _block(
      {
        "schema": "supekku.spec.relationships",
        "version": 1,
        "spec": "SPEC-001",
        "requirements": {"primary": ["FR-001", 123]},
      }
    )
    errors = validate_spec_relationships(block)
    assert any("string" in err.lower() for err in errors)

  def test_interactions_not_array(self):
    block = _block(
      {
        "schema": "supekku.spec.relationships",
        "version": 1,
        "spec": "SPEC-001",
        "interactions": "not-array",
      }
    )
    errors = validate_spec_relationships(block)
    assert any(
      "interactions" in err.lower() or "array" in err.lower() for err in errors
    )

  def test_interaction_entry_not_object(self):
    block = _block(
      {
        "schema": "supekku.spec.relationships",
        "version": 1,
        "spec": "SPEC-001",
        "interactions": ["not-object"],
      }
    )
    errors = validate_spec_relationships(block)
    assert any("object" in err.lower() for err in errors)

  def test_interaction_missing_type(self):
    block = _block(
      {
        "schema": "supekku.spec.relationships",
        "version": 1,
        "spec": "SPEC-001",
        "interactions": [{"spec": "SPEC-002"}],
      }
    )
    errors = validate_spec_relationships(block)
    assert any("type" in err.lower() for err in errors)

  def test_interaction_missing_spec(self):
    block = _block(
      {
        "schema": "supekku.spec.relationships",
        "version": 1,
        "spec": "SPEC-001",
        "interactions": [{"type": "calls"}],
      }
    )
    errors = validate_spec_relationships(block)
    assert any("spec" in err.lower() for err in errors)

  def test_strict_unknown_keys_rejected(self):
    block = _block(
      {
        "schema": "supekku.spec.relationships",
        "version": 1,
        "spec": "SPEC-001",
        "unexpected_key": "value",
      }
    )
    errors = validate_spec_relationships(block)
    assert any("unexpected_key" in err for err in errors)

  def test_combined_metadata_and_id_errors(self):
    block = _block({"schema": "wrong.schema", "version": 1, "spec": "SPEC-999"})
    errors = validate_spec_relationships(block, spec_id="SPEC-001")
    assert any("schema" in err.lower() for err in errors)
    assert any(
      "spec-999" in err.lower() and "spec-001" in err.lower() for err in errors
    )


class SpecCapabilitiesWrapperTest(unittest.TestCase):
  """validate_spec_capabilities — ergonomic, no ID-equality enforcement."""

  def test_valid_minimal_block(self):
    block = _block(
      {
        "schema": "supekku.spec.capabilities",
        "version": 1,
        "spec": "PROD-001",
        "capabilities": [],
      }
    )
    assert validate_spec_capabilities(block) == []

  def test_valid_complete_block(self):
    block = _block(
      {
        "schema": "supekku.spec.capabilities",
        "version": 1,
        "spec": "PROD-001",
        "capabilities": [
          {
            "id": "auth",
            "name": "Authentication",
            "responsibilities": ["Validate credentials"],
            "requirements": ["PROD-001.FR-001"],
            "summary": "Handles identity verification.",
            "success_criteria": ["Valid creds return token"],
          }
        ],
      }
    )
    assert validate_spec_capabilities(block, spec_id="PROD-001") == []

  def test_missing_schema(self):
    block = _block({"version": 1, "spec": "PROD-001", "capabilities": []})
    errors = validate_spec_capabilities(block)
    assert any("schema" in err.lower() for err in errors)

  def test_missing_capabilities(self):
    block = _block(
      {"schema": "supekku.spec.capabilities", "version": 1, "spec": "PROD-001"}
    )
    errors = validate_spec_capabilities(block)
    assert any("capabilities" in err.lower() for err in errors)

  def test_capability_missing_id(self):
    block = _block(
      {
        "schema": "supekku.spec.capabilities",
        "version": 1,
        "spec": "PROD-001",
        "capabilities": [{"name": "Authentication"}],
      }
    )
    errors = validate_spec_capabilities(block)
    assert any("id" in err.lower() for err in errors)

  def test_capability_missing_name(self):
    block = _block(
      {
        "schema": "supekku.spec.capabilities",
        "version": 1,
        "spec": "PROD-001",
        "capabilities": [{"id": "auth"}],
      }
    )
    errors = validate_spec_capabilities(block)
    assert any("name" in err.lower() for err in errors)

  def test_spec_id_ignored_when_mismatched(self):
    """Ergonomic wrapper: spec_id is accepted but never enforced."""
    block = _block(
      {
        "schema": "supekku.spec.capabilities",
        "version": 1,
        "spec": "PROD-999",
        "capabilities": [],
      }
    )
    assert validate_spec_capabilities(block, spec_id="PROD-001") == []

  def test_strict_unknown_keys_rejected(self):
    block = _block(
      {
        "schema": "supekku.spec.capabilities",
        "version": 1,
        "spec": "PROD-001",
        "capabilities": [],
        "unexpected_key": "value",
      }
    )
    errors = validate_spec_capabilities(block)
    assert any("unexpected_key" in err for err in errors)


class MetadataOnlyTest(unittest.TestCase):
  """JSON Schema generation + examples for both metadata declarations."""

  def test_relationships_json_schema(self):
    schema = metadata_to_json_schema(SPEC_RELATIONSHIPS_METADATA)
    assert schema["type"] == "object"
    assert set(schema["required"]) == {"schema", "version", "spec"}
    assert schema["properties"]["schema"]["const"] == "supekku.spec.relationships"
    assert schema["properties"]["interactions"]["type"] == "array"

  def test_capabilities_json_schema(self):
    schema = metadata_to_json_schema(SPEC_CAPABILITIES_METADATA)
    assert schema["type"] == "object"
    assert set(schema["required"]) == {"schema", "version", "spec", "capabilities"}
    assert schema["properties"]["capabilities"]["type"] == "array"
    assert schema["properties"]["capabilities"]["items"]["required"] == ["id", "name"]

  def test_relationships_examples_included(self):
    assert len(SPEC_RELATIONSHIPS_METADATA.examples) > 0
    example = SPEC_RELATIONSHIPS_METADATA.examples[0]
    assert example["schema"] == "supekku.spec.relationships"

  def test_capabilities_examples_included(self):
    assert len(SPEC_CAPABILITIES_METADATA.examples) > 0
    example = SPEC_CAPABILITIES_METADATA.examples[0]
    assert example["schema"] == "supekku.spec.capabilities"

  def test_metadata_validator_directly(self):
    """MetadataValidator alone validates a known-good block (sanity)."""
    validator = MetadataValidator(SPEC_RELATIONSHIPS_METADATA)
    data = {
      "schema": "supekku.spec.relationships",
      "version": 1,
      "spec": "SPEC-001",
    }
    assert not list(validator.validate(data))


if __name__ == "__main__":
  unittest.main()
