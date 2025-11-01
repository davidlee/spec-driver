"""Dual-validation tests for verification coverage metadata.

Tests that the new metadata-driven validator produces identical results
to the existing VerificationCoverageValidator.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import (
  MetadataValidator,
  metadata_to_json_schema,
)

from .verification import VerificationCoverageBlock, VerificationCoverageValidator
from .verification_metadata import VERIFICATION_COVERAGE_METADATA


class DualValidationTest(unittest.TestCase):
  """Test that metadata validator matches existing validator behavior."""

  def _validate_both(
    self, data: dict, *, subject_id: str | None = None
  ) -> tuple[list[str], list[str]]:
    """Run both validators and return (old_errors, new_errors)."""
    # Old validator
    block = VerificationCoverageBlock(raw_yaml="", data=data)
    old_validator = VerificationCoverageValidator()
    old_errors = old_validator.validate(block, subject_id=subject_id)

    # New metadata validator
    new_validator = MetadataValidator(VERIFICATION_COVERAGE_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_errors, new_errors

  def test_valid_minimal_block(self):
    """Both validators accept valid minimal block."""
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

    old_errors, new_errors = self._validate_both(data)
    assert old_errors == []
    assert new_errors == []

  def test_valid_complete_block(self):
    """Both validators accept block with all optional fields."""
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

    old_errors, new_errors = self._validate_both(data)
    assert old_errors == []
    assert new_errors == []

  def test_missing_schema_field(self):
    """Both validators reject missing schema field."""
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

    old_errors, new_errors = self._validate_both(data)
    # Old validator checks for wrong value
    assert any("schema" in err.lower() for err in old_errors)
    # New validator checks for missing field
    assert any("schema" in err.lower() for err in new_errors)

  def test_wrong_schema_value(self):
    """Both validators reject wrong schema value."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("schema" in err.lower() for err in old_errors)
    assert any("schema" in err.lower() for err in new_errors)

  def test_wrong_version(self):
    """Both validators reject wrong version."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("version" in err.lower() for err in old_errors)
    assert any("version" in err.lower() for err in new_errors)

  def test_missing_subject(self):
    """Both validators reject missing subject."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("subject" in err.lower() for err in old_errors)
    assert any("subject" in err.lower() for err in new_errors)

  def test_invalid_subject_pattern(self):
    """Both validators reject invalid subject pattern."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("subject" in err.lower() for err in old_errors)
    assert any("subject" in err.lower() for err in new_errors)

  def test_missing_entries(self):
    """Both validators reject missing entries."""
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("entries" in err.lower() for err in old_errors)
    assert any("entries" in err.lower() for err in new_errors)

  def test_empty_entries_array(self):
    """Both validators reject empty entries array."""
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": [],
    }

    old_errors, new_errors = self._validate_both(data)
    # Old validator checks for falsy entries
    assert any("entries" in err.lower() for err in old_errors)
    # New validator checks min_items constraint
    assert any("entries" in err.lower() for err in new_errors)

  def test_entries_not_array(self):
    """Both validators reject non-array entries."""
    data = {
      "schema": "supekku.verification.coverage",
      "version": 1,
      "subject": "SPEC-100",
      "entries": "not-array",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("entries" in err.lower() for err in old_errors)
    assert any("entries" in err.lower() or "array" in err.lower() for err in new_errors)

  def test_entry_missing_artefact(self):
    """Both validators reject entry missing artefact."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("artefact" in err.lower() for err in old_errors)
    assert any("artefact" in err.lower() for err in new_errors)

  def test_entry_invalid_artefact_pattern(self):
    """Both validators reject invalid artefact pattern."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("artefact" in err.lower() for err in old_errors)
    assert any("artefact" in err.lower() for err in new_errors)

  def test_entry_missing_kind(self):
    """Both validators reject entry missing kind."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("kind" in err.lower() for err in old_errors)
    assert any("kind" in err.lower() for err in new_errors)

  def test_entry_invalid_kind(self):
    """Both validators reject invalid kind value."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("kind" in err.lower() for err in old_errors)
    assert any("kind" in err.lower() for err in new_errors)

  def test_entry_missing_requirement(self):
    """Both validators reject entry missing requirement."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("requirement" in err.lower() for err in old_errors)
    assert any("requirement" in err.lower() for err in new_errors)

  def test_entry_invalid_requirement_pattern(self):
    """Both validators reject invalid requirement pattern."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("requirement" in err.lower() for err in old_errors)
    assert any("requirement" in err.lower() for err in new_errors)

  def test_entry_invalid_phase_pattern(self):
    """Both validators reject invalid phase pattern."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("phase" in err.lower() for err in old_errors)
    assert any("phase" in err.lower() for err in new_errors)

  def test_entry_missing_status(self):
    """Both validators reject entry missing status."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("status" in err.lower() for err in old_errors)
    assert any("status" in err.lower() for err in new_errors)

  def test_entry_invalid_status(self):
    """Both validators reject invalid status value."""
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

    old_errors, new_errors = self._validate_both(data)
    assert any("status" in err.lower() for err in old_errors)
    assert any("status" in err.lower() for err in new_errors)

  def test_multiple_entries_with_errors(self):
    """Both validators detect errors in multiple entries."""
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

    old_errors, new_errors = self._validate_both(data)
    # Both should detect multiple errors in second entry
    assert len(old_errors) >= 3  # At least artefact, kind, requirement, status
    assert len(new_errors) >= 3

  def test_all_verification_kinds(self):
    """Both validators accept all valid verification kinds."""
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

      old_errors, new_errors = self._validate_both(data)
      assert old_errors == [], f"Old validator rejected valid kind {kind}"
      assert new_errors == [], f"New validator rejected valid kind {kind}"

  def test_all_verification_statuses(self):
    """Both validators accept all valid verification statuses."""
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

      old_errors, new_errors = self._validate_both(data)
      assert old_errors == [], f"Old validator rejected valid status {status}"
      assert new_errors == [], f"New validator rejected valid status {status}"


class MetadataOnlyTest(unittest.TestCase):
  """Test metadata-specific features not in old validator."""

  def test_json_schema_generation(self):
    """Metadata can generate JSON Schema for verification coverage."""
    schema = metadata_to_json_schema(VERIFICATION_COVERAGE_METADATA)

    # Verify schema structure
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert "supekku-verification-coverage" in schema["$id"]

    # Verify required fields
    assert set(schema["required"]) == {"schema", "version", "subject", "entries"}

    # Verify properties
    assert schema["properties"]["schema"]["const"] == "supekku.verification.coverage"
    assert schema["properties"]["version"]["const"] == 1
    assert schema["properties"]["subject"]["type"] == "string"
    assert schema["properties"]["subject"]["pattern"]

    # Verify entries array
    assert schema["properties"]["entries"]["type"] == "array"
    assert schema["properties"]["entries"]["minItems"] == 1
    assert "items" in schema["properties"]["entries"]

    # Verify entry item properties
    entry_schema = schema["properties"]["entries"]["items"]
    assert entry_schema["type"] == "object"
    assert set(entry_schema["required"]) == {
      "artefact",
      "kind",
      "requirement",
      "status",
    }

  def test_examples_included(self):
    """Metadata includes examples."""
    assert len(VERIFICATION_COVERAGE_METADATA.examples) > 0
    example = VERIFICATION_COVERAGE_METADATA.examples[0]
    assert example["schema"] == "supekku.verification.coverage"
    assert example["version"] == 1
    assert "entries" in example


if __name__ == "__main__":
  unittest.main()
