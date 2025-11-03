"""Dual-validation tests for plan and phase overview metadata.

Tests that the new metadata-driven validators produce identical results
to the existing PlanOverviewValidator and PhaseOverviewValidator.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import (
  MetadataValidator,
  metadata_to_json_schema,
)

from .plan import (
  PHASE_SCHEMA,
  PHASE_VERSION,
  PLAN_SCHEMA,
  PLAN_VERSION,
  PhaseOverviewBlock,
  PhaseOverviewValidator,
  PlanOverviewBlock,
  PlanOverviewValidator,
)
from .plan_metadata import PHASE_OVERVIEW_METADATA, PLAN_OVERVIEW_METADATA


class PlanDualValidationTest(unittest.TestCase):
  """Test that plan overview metadata validator matches existing validator behavior."""

  def _validate_both(self, data: dict) -> tuple[list[str], list[str]]:
    """Run both validators and return (old_errors, new_errors)."""
    # Old validator
    block = PlanOverviewBlock(raw_yaml="", data=data)
    old_validator = PlanOverviewValidator()
    old_errors = old_validator.validate(block)

    # New metadata validator
    new_validator = MetadataValidator(PLAN_OVERVIEW_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_errors, new_errors

  def test_valid_minimal_plan(self):
    """Both validators accept valid minimal plan."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert old_errors == []
    assert new_errors == []

  def test_valid_complete_plan(self):
    """Both validators accept plan with all optional fields."""
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

    old_errors, new_errors = self._validate_both(data)
    assert old_errors == []
    assert new_errors == []

  def test_missing_schema_field(self):
    """Both validators reject missing schema field."""
    data = {
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("schema" in err.lower() for err in old_errors)
    assert any("schema" in err.lower() for err in new_errors)

  def test_wrong_schema_value(self):
    """Both validators reject wrong schema value."""
    data = {
      "schema": "wrong.schema",
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("schema" in err.lower() for err in old_errors)
    assert any("schema" in err.lower() for err in new_errors)

  def test_missing_version_field(self):
    """Both validators reject missing version field."""
    data = {
      "schema": PLAN_SCHEMA,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("version" in err.lower() for err in old_errors)
    assert any("version" in err.lower() for err in new_errors)

  def test_wrong_version_value(self):
    """Both validators reject wrong version value."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": 999,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("version" in err.lower() for err in old_errors)
    assert any("version" in err.lower() for err in new_errors)

  def test_missing_plan_id(self):
    """Both validators reject missing plan ID."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("plan" in err.lower() for err in old_errors)
    assert any("plan" in err.lower() for err in new_errors)

  def test_plan_id_wrong_type(self):
    """Both validators reject plan ID of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": 123,
      "delta": "DE-001",
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("plan" in err.lower() for err in old_errors)
    assert any("plan" in err.lower() for err in new_errors)

  def test_missing_delta_id(self):
    """Both validators reject missing delta ID."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("delta" in err.lower() for err in old_errors)
    assert any("delta" in err.lower() for err in new_errors)

  def test_delta_id_wrong_type(self):
    """Both validators reject delta ID of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": None,
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("delta" in err.lower() for err in old_errors)
    assert any("delta" in err.lower() for err in new_errors)

  def test_missing_phases(self):
    """Both validators reject missing phases."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("phases" in err.lower() for err in old_errors)
    assert any("phases" in err.lower() for err in new_errors)

  def test_empty_phases_array(self):
    """Both validators reject empty phases array."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("phases" in err.lower() or "empty" in err.lower() for err in old_errors)
    assert any("phases" in err.lower() or "empty" in err.lower() for err in new_errors)

  def test_phases_wrong_type(self):
    """Both validators reject phases of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": "not-an-array",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("phases" in err.lower() or "array" in err.lower() for err in old_errors)
    assert any("phases" in err.lower() or "array" in err.lower() for err in new_errors)

  def test_phase_entry_missing_id(self):
    """Both validators reject phase entry missing id."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"name": "Phase 01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("id" in err.lower() for err in old_errors)
    assert any("id" in err.lower() for err in new_errors)

  def test_phase_entry_id_wrong_type(self):
    """Both validators reject phase entry with id of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "phases": [{"id": 123}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("id" in err.lower() or "string" in err.lower() for err in old_errors)
    assert any("id" in err.lower() or "string" in err.lower() for err in new_errors)

  def test_revision_links_wrong_type(self):
    """Both validators reject revision_links of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "revision_links": "not-an-object",
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any(
      "revision_links" in err.lower() or "object" in err.lower() for err in old_errors
    )
    assert any(
      "revision_links" in err.lower() or "object" in err.lower() for err in new_errors
    )

  def test_revision_links_aligns_with_wrong_type(self):
    """Both validators reject aligns_with field of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "revision_links": {"aligns_with": "not-an-array"},
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any(
      "aligns_with" in err.lower() or "array" in err.lower() for err in old_errors
    )
    assert any(
      "aligns_with" in err.lower() or "array" in err.lower() for err in new_errors
    )

  def test_specs_wrong_type(self):
    """Both validators reject specs of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "specs": "not-an-object",
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("specs" in err.lower() or "object" in err.lower() for err in old_errors)
    assert any("specs" in err.lower() or "object" in err.lower() for err in new_errors)

  def test_requirements_wrong_type(self):
    """Both validators reject requirements of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
      "requirements": "not-an-object",
      "phases": [{"id": "PLN-001-P01"}],
    }

    old_errors, new_errors = self._validate_both(data)
    assert any(
      "requirements" in err.lower() or "object" in err.lower() for err in old_errors
    )
    assert any(
      "requirements" in err.lower() or "object" in err.lower() for err in new_errors
    )


class PhaseDualValidationTest(unittest.TestCase):
  """Test that phase overview metadata validator matches existing validator behavior."""

  def _validate_both(self, data: dict) -> tuple[list[str], list[str]]:
    """Run both validators and return (old_errors, new_errors)."""
    # Old validator
    block = PhaseOverviewBlock(raw_yaml="", data=data)
    old_validator = PhaseOverviewValidator()
    old_errors = old_validator.validate(block)

    # New metadata validator
    new_validator = MetadataValidator(PHASE_OVERVIEW_METADATA)
    new_validation_errors = new_validator.validate(data)
    new_errors = [str(err) for err in new_validation_errors]

    return old_errors, new_errors

  def test_valid_minimal_phase(self):
    """Both validators accept valid minimal phase."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert old_errors == []
    assert new_errors == []

  def test_valid_complete_phase(self):
    """Both validators accept phase with all optional fields."""
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

    old_errors, new_errors = self._validate_both(data)
    assert old_errors == []
    assert new_errors == []

  def test_missing_schema_field(self):
    """Both validators reject missing schema field."""
    data = {
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("schema" in err.lower() for err in old_errors)
    assert any("schema" in err.lower() for err in new_errors)

  def test_wrong_schema_value(self):
    """Both validators reject wrong schema value."""
    data = {
      "schema": "wrong.schema",
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("schema" in err.lower() for err in old_errors)
    assert any("schema" in err.lower() for err in new_errors)

  def test_missing_version_field(self):
    """Both validators reject missing version field."""
    data = {
      "schema": PHASE_SCHEMA,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("version" in err.lower() for err in old_errors)
    assert any("version" in err.lower() for err in new_errors)

  def test_missing_phase_id(self):
    """Both validators reject missing phase ID."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "plan": "PLN-001",
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("phase" in err.lower() for err in old_errors)
    assert any("phase" in err.lower() for err in new_errors)

  def test_phase_id_wrong_type(self):
    """Both validators reject phase ID of wrong type."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": 123,
      "plan": "PLN-001",
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("phase" in err.lower() or "string" in err.lower() for err in old_errors)
    assert any("phase" in err.lower() or "string" in err.lower() for err in new_errors)

  def test_missing_plan_id(self):
    """Both validators reject missing plan ID."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("plan" in err.lower() for err in old_errors)
    assert any("plan" in err.lower() for err in new_errors)

  def test_plan_id_wrong_type(self):
    """Both validators reject plan ID of wrong type."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": None,
      "delta": "DE-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("plan" in err.lower() for err in old_errors)
    assert any("plan" in err.lower() for err in new_errors)

  def test_missing_delta_id(self):
    """Both validators reject missing delta ID."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("delta" in err.lower() for err in old_errors)
    assert any("delta" in err.lower() for err in new_errors)

  def test_delta_id_wrong_type(self):
    """Both validators reject delta ID of wrong type."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": 123,
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("delta" in err.lower() or "string" in err.lower() for err in old_errors)
    assert any("delta" in err.lower() or "string" in err.lower() for err in new_errors)

  def test_objective_wrong_type(self):
    """Both validators reject objective of wrong type."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "objective": 123,
    }

    old_errors, new_errors = self._validate_both(data)
    assert any(
      "objective" in err.lower() or "string" in err.lower() for err in old_errors
    )
    assert any(
      "objective" in err.lower() or "string" in err.lower() for err in new_errors
    )

  def test_entrance_criteria_wrong_type(self):
    """Both validators reject entrance_criteria of wrong type."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "entrance_criteria": "not-an-array",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any(
      "entrance_criteria" in err.lower() or "array" in err.lower() for err in old_errors
    )
    assert any(
      "entrance_criteria" in err.lower() or "array" in err.lower() for err in new_errors
    )

  def test_exit_criteria_wrong_type(self):
    """Both validators reject exit_criteria of wrong type."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "exit_criteria": "not-an-array",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any(
      "exit_criteria" in err.lower() or "array" in err.lower() for err in old_errors
    )
    assert any(
      "exit_criteria" in err.lower() or "array" in err.lower() for err in new_errors
    )

  def test_verification_wrong_type(self):
    """Both validators reject verification of wrong type."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "verification": "not-an-object",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any(
      "verification" in err.lower() or "object" in err.lower() for err in old_errors
    )
    assert any(
      "verification" in err.lower() or "object" in err.lower() for err in new_errors
    )

  def test_verification_tests_wrong_type(self):
    """Both validators reject verification.tests of wrong type."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "verification": {"tests": "not-an-array"},
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("tests" in err.lower() or "array" in err.lower() for err in old_errors)
    assert any("tests" in err.lower() or "array" in err.lower() for err in new_errors)

  def test_tasks_wrong_type(self):
    """Both validators reject tasks of wrong type."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "tasks": "not-an-array",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("tasks" in err.lower() or "array" in err.lower() for err in old_errors)
    assert any("tasks" in err.lower() or "array" in err.lower() for err in new_errors)

  def test_risks_wrong_type(self):
    """Both validators reject risks of wrong type."""
    data = {
      "schema": PHASE_SCHEMA,
      "version": PHASE_VERSION,
      "phase": "PLN-001-P01",
      "plan": "PLN-001",
      "delta": "DE-001",
      "risks": "not-an-array",
    }

    old_errors, new_errors = self._validate_both(data)
    assert any("risks" in err.lower() or "array" in err.lower() for err in old_errors)
    assert any("risks" in err.lower() or "array" in err.lower() for err in new_errors)


class PlanPhasesMetadataTest(unittest.TestCase):
  """VT-SCHEMA-013-001: Test phase metadata fields in plan.overview (DE-012)."""

  def test_plan_with_full_phase_metadata(self):
    """Plan accepts phases with all optional metadata fields."""
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

    validator = MetadataValidator(PLAN_OVERVIEW_METADATA)
    errors = validator.validate(data)
    assert errors == [], f"Expected no errors, got: {errors}"

  def test_plan_with_id_only_phases(self):
    """Plan accepts phases with only required ID field (backward compat)."""
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

    validator = MetadataValidator(PLAN_OVERVIEW_METADATA)
    errors = validator.validate(data)
    assert errors == [], f"Expected no errors, got: {errors}"

  def test_plan_with_mixed_phase_formats(self):
    """Plan accepts mix of full metadata and ID-only phases."""
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
        {"id": "IP-012.PHASE-02"},  # ID-only
        {
          "id": "IP-012.PHASE-03",
          "name": "Partial metadata",
          "entrance_criteria": ["Entry 3"],
        },
      ],
    }

    validator = MetadataValidator(PLAN_OVERVIEW_METADATA)
    errors = validator.validate(data)
    assert errors == [], f"Expected no errors, got: {errors}"

  def test_plan_with_empty_criteria_arrays(self):
    """Plan accepts empty entrance_criteria and exit_criteria arrays."""
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

    validator = MetadataValidator(PLAN_OVERVIEW_METADATA)
    errors = validator.validate(data)
    assert errors == [], f"Expected no errors, got: {errors}"

  def test_plan_phase_name_wrong_type(self):
    """Plan rejects phase name of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "name": 123,  # Should be string
        }
      ],
    }

    validator = MetadataValidator(PLAN_OVERVIEW_METADATA)
    errors = validator.validate(data)
    assert len(errors) > 0
    assert any("name" in str(err).lower() for err in errors)

  def test_plan_phase_objective_wrong_type(self):
    """Plan rejects phase objective of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "objective": ["not", "a", "string"],  # Should be string
        }
      ],
    }

    validator = MetadataValidator(PLAN_OVERVIEW_METADATA)
    errors = validator.validate(data)
    assert len(errors) > 0
    assert any("objective" in str(err).lower() for err in errors)

  def test_plan_phase_entrance_criteria_wrong_type(self):
    """Plan rejects entrance_criteria of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "entrance_criteria": "not an array",  # Should be array
        }
      ],
    }

    validator = MetadataValidator(PLAN_OVERVIEW_METADATA)
    errors = validator.validate(data)
    assert len(errors) > 0
    assert any("entrance_criteria" in str(err).lower() for err in errors)

  def test_plan_phase_exit_criteria_wrong_type(self):
    """Plan rejects exit_criteria of wrong type."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          "exit_criteria": {"key": "value"},  # Should be array
        }
      ],
    }

    validator = MetadataValidator(PLAN_OVERVIEW_METADATA)
    errors = validator.validate(data)
    assert len(errors) > 0
    assert any("exit_criteria" in str(err).lower() for err in errors)

  def test_plan_phase_criteria_items_must_be_strings(self):
    """Plan rejects criteria arrays with non-string items."""
    data = {
      "schema": PLAN_SCHEMA,
      "version": PLAN_VERSION,
      "plan": "IP-012",
      "delta": "DE-012",
      "phases": [
        {
          "id": "IP-012.PHASE-01",
          # Has non-string item
          "entrance_criteria": ["Valid string", 123, "Another string"],
        }
      ],
    }

    validator = MetadataValidator(PLAN_OVERVIEW_METADATA)
    errors = validator.validate(data)
    assert len(errors) > 0


class JSONSchemaGenerationTest(unittest.TestCase):
  """Test JSON Schema generation for plan and phase metadata."""

  def test_plan_metadata_generates_json_schema(self):
    """Plan metadata can be converted to JSON Schema."""
    schema = metadata_to_json_schema(PLAN_OVERVIEW_METADATA)

    # Check basic structure
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "required" in schema

    # Check required fields
    assert "schema" in schema["required"]
    assert "version" in schema["required"]
    assert "plan" in schema["required"]
    assert "delta" in schema["required"]
    assert "phases" in schema["required"]

    # Check phases is array with min items
    assert schema["properties"]["phases"]["type"] == "array"
    assert schema["properties"]["phases"]["minItems"] == 1

  def test_plan_phases_optional_fields_in_json_schema(self):
    """Plan JSON Schema includes optional phase metadata fields."""
    schema = metadata_to_json_schema(PLAN_OVERVIEW_METADATA)

    # Get phase items schema
    phase_items = schema["properties"]["phases"]["items"]
    phase_props = phase_items["properties"]

    # Check that optional fields are present
    assert "name" in phase_props
    assert "objective" in phase_props
    assert "entrance_criteria" in phase_props
    assert "exit_criteria" in phase_props

    # Check field types
    assert phase_props["name"]["type"] == "string"
    assert phase_props["objective"]["type"] == "string"
    assert phase_props["entrance_criteria"]["type"] == "array"
    assert phase_props["exit_criteria"]["type"] == "array"

    # Check only ID is required in phase items
    assert "id" in phase_items["required"]
    assert "name" not in phase_items.get("required", [])
    assert "objective" not in phase_items.get("required", [])
    assert "entrance_criteria" not in phase_items.get("required", [])
    assert "exit_criteria" not in phase_items.get("required", [])

  def test_phase_metadata_generates_json_schema(self):
    """Phase metadata can be converted to JSON Schema."""
    schema = metadata_to_json_schema(PHASE_OVERVIEW_METADATA)

    # Check basic structure
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "required" in schema

    # Check required fields
    assert "schema" in schema["required"]
    assert "version" in schema["required"]
    assert "phase" in schema["required"]
    assert "plan" in schema["required"]
    assert "delta" in schema["required"]

    # Check verification is object
    assert schema["properties"]["verification"]["type"] == "object"
