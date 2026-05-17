"""Metadata-driven validation tests for plan and phase overview blocks.

Captures hand-rolled ``PlanOverviewValidator`` and ``PhaseOverviewValidator``
behaviour as of DE-118 (IP-118-P03 C2 retirement); tightening or relaxing
rules is an *intended* drift event handled in the delta that introduces it.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import (
  MetadataValidator,
  metadata_to_json_schema,
)

from .plan import PHASE_SCHEMA, PHASE_VERSION, PLAN_SCHEMA, PLAN_VERSION
from .plan_metadata import PHASE_OVERVIEW_METADATA, PLAN_OVERVIEW_METADATA


def _validate_plan(data: dict) -> list[str]:
  """Validate ``data`` against the plan.overview metadata in strict mode."""
  validator = MetadataValidator(PLAN_OVERVIEW_METADATA)
  return [str(err) for err in validator.validate(data, strict=True)]


def _validate_phase(data: dict) -> list[str]:
  """Validate ``data`` against the phase.overview metadata in strict mode."""
  validator = MetadataValidator(PHASE_OVERVIEW_METADATA)
  return [str(err) for err in validator.validate(data, strict=True)]


class PlanMetadataValidationTest(unittest.TestCase):
  """Cover plan.overview block validation (top-level, phases array)."""

  def test_valid_minimal_plan(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }
    assert _validate_plan(data) == []

  def test_valid_complete_plan(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-002",
      "delta": "DE-002",
      "revision_links": {
        "aligns_with": ["RE-001", "RE-002"],
      },
      "specs": {
        "primary": ["SPEC-100"],
        "collaborators": ["SPEC-200", "SPEC-300"],
      },
      "requirements": {
        "targets": ["SPEC-100.FR-001"],
        "dependencies": ["SPEC-200.FR-005"],
      },
      "phases": [
        {
          "id": "PLN-002-P01",
          "name": "Phase 01 - Initial delivery",
          "objective": "Deliver the foundational work.",
          "entrance_criteria": ["All requirements approved"],
          "exit_criteria": ["All tests passing"],
        },
        {
          "id": "PLN-002-P02",
          "name": "Phase 02 - Finalization",
        },
      ],
    }
    assert _validate_plan(data) == []

  def test_missing_schema_field(self):
    data = {
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }
    assert any("schema" in err.lower() for err in _validate_plan(data))

  def test_wrong_schema_value(self):
    data = {
      "schema": "wrong.schema",
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }
    assert any("schema" in err.lower() for err in _validate_plan(data))

  def test_missing_version_field(self):
    data = {
      "schema": PLAN_SCHEMA,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }
    assert any("version" in err.lower() for err in _validate_plan(data))

  def test_wrong_version_value(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": 999,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }
    assert any("version" in err.lower() for err in _validate_plan(data))

  def test_missing_plan_id(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }
    assert any("plan" in err.lower() for err in _validate_plan(data))

  def test_plan_id_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": 123,
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }
    assert any("plan" in err.lower() for err in _validate_plan(data))

  def test_missing_delta_id(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "phases": [{"id": "PLN-001-P01"}],
    }
    assert any("delta" in err.lower() for err in _validate_plan(data))

  def test_delta_id_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": None,
      "phases": [{"id": "PLN-001-P01"}],
    }
    assert any("delta" in err.lower() for err in _validate_plan(data))

  def test_missing_phases(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
    }
    assert any("phases" in err.lower() for err in _validate_plan(data))

  def test_empty_phases_array(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [],
    }
    errors = _validate_plan(data)
    assert any("phases" in err.lower() or "empty" in err.lower() for err in errors)

  def test_phases_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": "not-an-array",
    }
    errors = _validate_plan(data)
    assert any("phases" in err.lower() or "array" in err.lower() for err in errors)

  def test_phase_entry_missing_id(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"name": "Phase 01"}],
    }
    assert any("id" in err.lower() for err in _validate_plan(data))

  def test_phase_entry_id_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": 123}],
    }
    errors = _validate_plan(data)
    assert any("id" in err.lower() or "string" in err.lower() for err in errors)

  def test_revision_links_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "revision_links": "not-an-object",
      "phases": [{"id": "PLN-001-P01"}],
    }
    errors = _validate_plan(data)
    assert any(
      "revision_links" in err.lower() or "object" in err.lower() for err in errors
    )

  def test_revision_links_aligns_with_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "revision_links": {"aligns_with": "not-an-array"},
      "phases": [{"id": "PLN-001-P01"}],
    }
    errors = _validate_plan(data)
    assert any("aligns_with" in err.lower() or "array" in err.lower() for err in errors)

  def test_specs_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "specs": "not-an-object",
      "phases": [{"id": "PLN-001-P01"}],
    }
    errors = _validate_plan(data)
    assert any("specs" in err.lower() or "object" in err.lower() for err in errors)

  def test_requirements_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "requirements": "not-an-object",
      "phases": [{"id": "PLN-001-P01"}],
    }
    errors = _validate_plan(data)
    assert any(
      "requirements" in err.lower() or "object" in err.lower() for err in errors
    )


class PhaseMetadataValidationTest(unittest.TestCase):
  """Cover phase.overview block validation."""

  def test_valid_minimal_phase(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
    }
    assert _validate_phase(data) == []

  def test_valid_complete_phase(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-002-P01",
      "plan": "PLN-002",
      "delta": "DE-002",
      "objective": "Deliver foundational work for this phase.",
      "entrance_criteria": ["All requirements approved", "Design complete"],
      "exit_criteria": ["All tests passing", "Documentation updated"],
      "verification": {
        "tests": ["VT-001", "VT-002"],
        "evidence": ["Test report", "Code review"],
      },
      "tasks": ["Implement feature A", "Write tests"],
      "risks": ["Timeline risk", "Integration complexity"],
    }
    assert _validate_phase(data) == []

  def test_missing_schema_field(self):
    data = {
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
    }
    assert any("schema" in err.lower() for err in _validate_phase(data))

  def test_wrong_schema_value(self):
    data = {
      "schema": "wrong.schema",
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
    }
    assert any("schema" in err.lower() for err in _validate_phase(data))

  def test_missing_version_field(self):
    data = {
      "schema": PHASE_SCHEMA,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
    }
    assert any("version" in err.lower() for err in _validate_phase(data))

  def test_missing_phase_id(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
    }
    assert any("phase" in err.lower() for err in _validate_phase(data))

  def test_phase_id_wrong_type(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": 123,
      "plan": "PLN-001",
      "delta": "DE-001",
    }
    errors = _validate_phase(data)
    assert any("phase" in err.lower() or "string" in err.lower() for err in errors)

  def test_missing_plan_id(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "delta": "DE-001",
    }
    assert any("plan" in err.lower() for err in _validate_phase(data))

  def test_plan_id_wrong_type(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": None,
      "delta": "DE-001",
    }
    assert any("plan" in err.lower() for err in _validate_phase(data))

  def test_missing_delta_id(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
    }
    assert any("delta" in err.lower() for err in _validate_phase(data))

  def test_delta_id_wrong_type(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": 123,
    }
    errors = _validate_phase(data)
    assert any("delta" in err.lower() or "string" in err.lower() for err in errors)

  def test_objective_wrong_type(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "objective": 123,
    }
    errors = _validate_phase(data)
    assert any("objective" in err.lower() or "string" in err.lower() for err in errors)

  def test_entrance_criteria_wrong_type(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "entrance_criteria": "not-an-array",
    }
    errors = _validate_phase(data)
    assert any(
      "entrance_criteria" in err.lower() or "array" in err.lower() for err in errors
    )

  def test_exit_criteria_wrong_type(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "exit_criteria": "not-an-array",
    }
    errors = _validate_phase(data)
    assert any(
      "exit_criteria" in err.lower() or "array" in err.lower() for err in errors
    )

  def test_verification_wrong_type(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "verification": "not-an-object",
    }
    errors = _validate_phase(data)
    assert any(
      "verification" in err.lower() or "object" in err.lower() for err in errors
    )

  def test_verification_tests_wrong_type(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "verification": {"tests": "not-an-array"},
    }
    errors = _validate_phase(data)
    assert any("tests" in err.lower() or "array" in err.lower() for err in errors)

  def test_tasks_wrong_type(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "tasks": "not-an-array",
    }
    errors = _validate_phase(data)
    assert any("tasks" in err.lower() or "array" in err.lower() for err in errors)

  def test_risks_wrong_type(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "risks": "not-an-array",
    }
    errors = _validate_phase(data)
    assert any("risks" in err.lower() or "array" in err.lower() for err in errors)


class PlanPhasesMetadataTest(unittest.TestCase):
  """VT-SCHEMA-013-001: Test phase metadata fields in plan.overview (DE-012)."""

  def test_plan_with_full_phase_metadata(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "name": "Schema Restoration",
          "objective": "Restore entry/exit criteria to plan.overview schema",
          "entrance_criteria": ["DE-012 approved", "ISSUE-013 understood"],
          "exit_criteria": ["Schema updated", "Tests passing"],
        }
      ],
    }
    assert _validate_plan(data) == []

  def test_plan_with_id_only_phases(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {"id": "IP-012.PHASE-01"},
        {"id": "IP-012.PHASE-02"},
      ],
    }
    assert _validate_plan(data) == []

  def test_plan_with_mixed_phase_formats(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "name": "Full metadata phase",
          "objective": "Has all fields",
          "entrance_criteria": ["Entry 1"],
          "exit_criteria": ["Exit 1"],
        },
        {"id": "IP-012.PHASE-02"},
        {
          "id": "IP-012.PHASE-03",
          "name": "Partial metadata",
          "entrance_criteria": ["Entry 3"],
        },
      ],
    }
    assert _validate_plan(data) == []

  def test_plan_with_empty_criteria_arrays(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "name": "Empty criteria",
          "objective": "Test empty arrays",
          "entrance_criteria": [],
          "exit_criteria": [],
        }
      ],
    }
    assert _validate_plan(data) == []

  def test_plan_phase_name_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "name": 123,
        }
      ],
    }
    errors = _validate_plan(data)
    assert any("name" in err.lower() for err in errors)

  def test_plan_phase_objective_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "objective": ["not", "a", "string"],
        }
      ],
    }
    errors = _validate_plan(data)
    assert any("objective" in err.lower() for err in errors)

  def test_plan_phase_entrance_criteria_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "entrance_criteria": "not an array",
        }
      ],
    }
    errors = _validate_plan(data)
    assert any("entrance_criteria" in err.lower() for err in errors)

  def test_plan_phase_exit_criteria_wrong_type(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "exit_criteria": {"key": "value"},
        }
      ],
    }
    errors = _validate_plan(data)
    assert any("exit_criteria" in err.lower() for err in errors)

  def test_plan_phase_criteria_items_must_be_strings(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "entrance_criteria": ["Valid string", 123, "Another string"],
        }
      ],
    }
    assert _validate_plan(data) != []


class StrictModeBehaviourTest(unittest.TestCase):
  """Strict-mode-only rejection paths (unknown keys) for plan and phase blocks."""

  def test_plan_rejects_unknown_top_level_key(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
      "unexpected_field": "value",
    }
    errors = _validate_plan(data)
    assert any("unexpected_field" in err for err in errors)

  def test_plan_rejects_unknown_phase_entry_key(self):
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01", "bogus_key": True}],
    }
    errors = _validate_plan(data)
    assert any("bogus_key" in err for err in errors)

  def test_phase_rejects_unknown_top_level_key(self):
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "extra_field": "value",
    }
    errors = _validate_phase(data)
    assert any("extra_field" in err for err in errors)


class JSONSchemaGenerationTest(unittest.TestCase):
  """Test JSON Schema generation for plan and phase metadata."""

  def test_plan_metadata_generates_json_schema(self):
    schema = metadata_to_json_schema(PLAN_OVERVIEW_METADATA)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "required" in schema

    assert "schema" in schema["required"]
    assert "version" in schema["required"]
    assert "plan" in schema["required"]
    assert "delta" in schema["required"]
    assert "phases" in schema["required"]

    assert schema["properties"]["phases"]["type"] == "array"
    assert schema["properties"]["phases"]["minItems"] == 1

  def test_plan_phases_optional_fields_in_json_schema(self):
    schema = metadata_to_json_schema(PLAN_OVERVIEW_METADATA)

    phase_items = schema["properties"]["phases"]["items"]
    phase_props = phase_items["properties"]

    assert "name" in phase_props
    assert "objective" in phase_props
    assert "entrance_criteria" in phase_props
    assert "exit_criteria" in phase_props

    assert phase_props["name"]["type"] == "string"
    assert phase_props["objective"]["type"] == "string"
    assert phase_props["entrance_criteria"]["type"] == "array"
    assert phase_props["exit_criteria"]["type"] == "array"

    assert "id" in phase_items["required"]
    assert "name" not in phase_items.get("required", [])
    assert "objective" not in phase_items.get("required", [])
    assert "entrance_criteria" not in phase_items.get("required", [])
    assert "exit_criteria" not in phase_items.get("required", [])

  def test_phase_metadata_generates_json_schema(self):
    schema = metadata_to_json_schema(PHASE_OVERVIEW_METADATA)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "required" in schema

    assert "schema" in schema["required"]
    assert "version" in schema["required"]
    assert "phase" in schema["required"]
    assert "plan" in schema["required"]
    assert "delta" in schema["required"]

    assert schema["properties"]["verification"]["type"] == "object"
