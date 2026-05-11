"""Tests for verification coverage metadata-driven validation.

Captures hand-rolled ``VerificationCoverageValidator`` behaviour as of
DE-118 (IP-118-P03 C1 retirement); tightening or relaxing rules is an
*intended* drift event handled in the delta that introduces it.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import (
  MetadataValidator,
  metadata_to_json_schema,
)

from .verification_metadata import VERIFICATION_COVERAGE_METADATA


def _validate(data: dict) -> list[str]:
  """Validate ``data`` against the verification.coverage metadata in strict mode."""
  validator = MetadataValidator(
    VERIFICATION_COVERAGE_METADATA, strict_unknown_keys=True
  )
  return [str(err) for err in validator.validate(data)]


class TopLevelValidationTest(unittest.TestCase):
  """Cover top-level field validation (schema, version, subject, entries shape)."""

  def test_valid_minimal_block(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        }
      ],
    }
    assert _validate(data) == []

  def test_valid_complete_block(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "PROD-200",
      "entries": [
        {
          "artefact": "VA-002",
          "kind": "VA",
          "requirement": "PROD-200.NFR-PERF",
          "phase": "IP-001.PHASE-01",
          "status": "in-progress",
          "notes": "Performance analysis ongoing",
        }
      ],
    }
    assert _validate(data) == []

  def test_missing_schema_field(self):
    data = {
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        }
      ],
    }
    assert any("schema" in err.lower() for err in _validate(data))

  def test_wrong_schema_value(self):
    data = {
      "schema": "wrong.schema",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        }
      ],
    }
    assert any("schema" in err.lower() for err in _validate(data))

  def test_wrong_version(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 999,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        }
      ],
    }
    assert any("version" in err.lower() for err in _validate(data))

  def test_missing_subject(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        }
      ],
    }
    assert any("subject" in err.lower() for err in _validate(data))

  def test_invalid_subject_pattern(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "INVALID-123",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        }
      ],
    }
    assert any("subject" in err.lower() for err in _validate(data))

  def test_missing_entries(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
    }
    assert any("entries" in err.lower() for err in _validate(data))

  def test_empty_entries_array(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [],
    }
    assert any("entries" in err.lower() for err in _validate(data))

  def test_entries_not_array(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": "not-array",
    }
    errors = _validate(data)
    assert any("entries" in err.lower() or "array" in err.lower() for err in errors)


class EntryValidationTest(unittest.TestCase):
  """Cover per-entry validation (artefact / kind / requirement / phase / status)."""

  def test_entry_not_object(self):
    """The retired validator rejected non-dict entries; metadata does the same."""
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": ["not-an-object"],
    }
    assert _validate(data) != []

  def test_entry_missing_artefact(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        }
      ],
    }
    assert any("artefact" in err.lower() for err in _validate(data))

  def test_entry_invalid_artefact_pattern(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "INVALID-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        }
      ],
    }
    assert any("artefact" in err.lower() for err in _validate(data))

  def test_entry_missing_kind(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        }
      ],
    }
    assert any("kind" in err.lower() for err in _validate(data))

  def test_entry_invalid_kind(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "INVALID",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        }
      ],
    }
    assert any("kind" in err.lower() for err in _validate(data))

  def test_entry_missing_requirement(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "status": "verified",
        }
      ],
    }
    assert any("requirement" in err.lower() for err in _validate(data))

  def test_entry_invalid_requirement_pattern(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "INVALID",
          "status": "verified",
        }
      ],
    }
    assert any("requirement" in err.lower() for err in _validate(data))

  def test_entry_invalid_phase_pattern(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "phase": "INVALID-PHASE",
          "status": "verified",
        }
      ],
    }
    assert any("phase" in err.lower() for err in _validate(data))

  def test_entry_missing_status(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
        }
      ],
    }
    assert any("status" in err.lower() for err in _validate(data))

  def test_entry_invalid_status(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "invalid-status",
        }
      ],
    }
    assert any("status" in err.lower() for err in _validate(data))

  def test_multiple_entries_with_errors(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        },
        {
          "artefact": "INVALID",
          "kind": "INVALID_KIND",
          "requirement": "INVALID_REQ",
          "status": "invalid-status",
        },
      ],
    }
    assert len(_validate(data)) >= 3

  def test_all_verification_kinds(self):
    for kind in ["VT", "VA", "VH"]:
      data = {
        "schema": "supekku.verification.coverage",
        "version": 1,
        "subject": "SPEC-100",
        "entries": [
          {
            "artefact": f"{kind}-001",
            "kind": kind,
            "requirement": "SPEC-100.FR-001",
            "status": "verified",
          }
        ],
      }
      assert _validate(data) == [], f"Rejected valid kind {kind}"

  def test_all_verification_statuses(self):
    for status in ["planned", "in-progress", "verified", "failed", "blocked"]:
      data = {
        "schema": "supekku.verification.coverage",
        "version": 1,
        "subject": "SPEC-100",
        "entries": [
          {
            "artefact": "VT-001",
            "kind": "VT",
            "requirement": "SPEC-100.FR-001",
            "status": status,
          }
        ],
      }
      assert _validate(data) == [], f"Rejected valid status {status}"


class StrictModeBehaviourTest(unittest.TestCase):
  """New enforcement introduced at C1: unknown keys rejected under strict mode."""

  def test_unknown_top_level_key_rejected(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "unexpected": "value",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
        }
      ],
    }
    assert _validate(data) != []

  def test_unknown_entry_key_rejected(self):
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [
        {
          "artefact": "VT-001",
          "kind": "VT",
          "requirement": "SPEC-100.FR-001",
          "status": "verified",
          "rogue": "extra",
        }
      ],
    }
    assert _validate(data) != []


class MetadataDescriptorTest(unittest.TestCase):
  """JSON Schema generation and example presence."""

  def test_json_schema_generation(self):
    schema = metadata_to_json_schema(VERIFICATION_COVERAGE_METADATA)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert "supekku-verification-coverage" in schema["$id"]

    assert set(schema["required"]) == {"schema", "version", "subject", "entries"}

    assert schema["properties"]["schema"]["const"] == "supekku.verification.coverage"
    assert schema["properties"]["version"]["const"] == 1
    assert schema["properties"]["subject"]["type"] == "string"
    assert schema["properties"]["subject"]["pattern"]

    assert schema["properties"]["entries"]["type"] == "array"
    assert schema["properties"]["entries"]["minItems"] == 1
    assert "items" in schema["properties"]["entries"]

    entry_schema = schema["properties"]["entries"]["items"]
    assert entry_schema["type"] == "object"
    assert set(entry_schema["required"]) == {
      "artefact",
      "kind",
      "requirement",
      "status",
    }

  def test_examples_included(self):
    assert len(VERIFICATION_COVERAGE_METADATA.examples) > 0
    example = VERIFICATION_COVERAGE_METADATA.examples[0]
    assert example["schema"] == "supekku.verification.coverage"
    assert example["version"] == 1
    assert "entries" in example


if __name__ == "__main__":
  unittest.main()
