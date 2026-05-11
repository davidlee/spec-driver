"""Metadata-driven validation tests for phase.tracking blocks.

Captures hand-rolled ``PhaseTrackingValidator`` behaviour as of DE-118
(IP-118-P03 C2 retirement); tightening or relaxing rules is an *intended*
drift event handled in the delta that introduces it.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator

from .plan import TRACKING_SCHEMA, TRACKING_VERSION
from .tracking_metadata import PHASE_TRACKING_METADATA


def _validate(data: dict) -> list[str]:
  """Validate ``data`` against the phase.tracking metadata in strict mode."""
  validator = MetadataValidator(PHASE_TRACKING_METADATA, strict_unknown_keys=True)
  return [str(err) for err in validator.validate(data)]


class TopLevelValidationTest(unittest.TestCase):
  """Cover top-level field validation (schema, version, phase)."""

  def test_valid_minimal_block(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
    }
    assert _validate(data) == []

  def test_valid_complete_block(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "files": {
        "references": ["supekku/foo.py"],
        "context": ["change/bar.md"],
      },
      "entrance_criteria": [
        {"item": "Phases 01, 02 complete", "completed": True},
      ],
      "exit_criteria": [
        {"item": "Schema defined", "completed": False, "notes": "blocked on X"},
      ],
      "tasks": [
        {
          "id": "5.1",
          "description": "Define schema",
          "status": "completed",
          "files": {
            "added": ["foo.py"],
            "modified": ["bar.py"],
            "removed": [],
            "tests": ["foo_test.py"],
          },
        },
      ],
    }
    assert _validate(data) == []

  def test_missing_schema_field(self):
    data = {
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
    }
    assert any("schema" in err.lower() for err in _validate(data))

  def test_wrong_schema_value(self):
    data = {
      "schema": "wrong.schema",
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
    }
    assert any("schema" in err.lower() for err in _validate(data))

  def test_missing_version_field(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "phase": "IP-004.PHASE-05",
    }
    assert any("version" in err.lower() for err in _validate(data))

  def test_wrong_version_value(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": 999,
      "phase": "IP-004.PHASE-05",
    }
    assert any("version" in err.lower() for err in _validate(data))

  def test_missing_phase_id(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
    }
    assert any("phase" in err.lower() for err in _validate(data))

  def test_phase_id_wrong_type(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": 123,
    }
    errors = _validate(data)
    assert any("phase" in err.lower() or "string" in err.lower() for err in errors)


class CriteriaValidationTest(unittest.TestCase):
  """Cover entrance/exit criteria structure (item, completed, notes)."""

  def test_criteria_missing_item(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "entrance_criteria": [{"completed": True}],
    }
    errors = _validate(data)
    assert any("item" in err.lower() for err in errors)

  def test_criteria_missing_completed(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "entrance_criteria": [{"item": "do thing"}],
    }
    errors = _validate(data)
    assert any("completed" in err.lower() for err in errors)

  def test_criteria_completed_wrong_type(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "entrance_criteria": [{"item": "do thing", "completed": "yes"}],
    }
    errors = _validate(data)
    assert any("completed" in err.lower() or "bool" in err.lower() for err in errors)

  def test_exit_criteria_missing_item(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "exit_criteria": [{"completed": False}],
    }
    errors = _validate(data)
    assert any("item" in err.lower() for err in errors)


class TasksValidationTest(unittest.TestCase):
  """Cover tasks array structure (id, description, status enum, files)."""

  def test_tasks_missing_id(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "tasks": [{"description": "task without id", "status": "pending"}],
    }
    errors = _validate(data)
    assert any("id" in err.lower() for err in errors)

  def test_tasks_missing_description(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "tasks": [{"id": "1", "status": "pending"}],
    }
    errors = _validate(data)
    assert any("description" in err.lower() for err in errors)

  def test_tasks_missing_status(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "tasks": [{"id": "1", "description": "task without status"}],
    }
    errors = _validate(data)
    assert any("status" in err.lower() for err in errors)

  def test_tasks_invalid_status_enum(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "tasks": [
        {"id": "1", "description": "bad status", "status": "invalid_value"},
      ],
    }
    errors = _validate(data)
    assert any("status" in err.lower() for err in errors)

  def test_tasks_accepts_all_valid_statuses(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "tasks": [
        {"id": "1", "description": "a", "status": "pending"},
        {"id": "2", "description": "b", "status": "in_progress"},
        {"id": "3", "description": "c", "status": "completed"},
        {"id": "4", "description": "d", "status": "blocked"},
      ],
    }
    assert _validate(data) == []

  def test_task_files_wrong_type(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "tasks": [
        {
          "id": "1",
          "description": "task",
          "status": "pending",
          "files": {"added": "not-an-array"},
        },
      ],
    }
    errors = _validate(data)
    assert any("added" in err.lower() or "array" in err.lower() for err in errors)


class FilesValidationTest(unittest.TestCase):
  """Cover phase-level files.{references,context} validation."""

  def test_phase_files_references_wrong_type(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "files": {"references": "not-an-array"},
    }
    errors = _validate(data)
    assert any("references" in err.lower() or "array" in err.lower() for err in errors)

  def test_phase_files_context_wrong_type(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "files": {"context": {"not": "an array"}},
    }
    errors = _validate(data)
    assert any("context" in err.lower() or "array" in err.lower() for err in errors)


class StrictModeBehaviourTest(unittest.TestCase):
  """Strict-mode-only rejection paths (unknown keys)."""

  def test_rejects_unknown_top_level_key(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "bogus_field": "value",
    }
    errors = _validate(data)
    assert any("bogus_field" in err for err in errors)

  def test_rejects_unknown_task_key(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "tasks": [
        {
          "id": "1",
          "description": "task",
          "status": "pending",
          "unexpected_task_key": True,
        },
      ],
    }
    errors = _validate(data)
    assert any("unexpected_task_key" in err for err in errors)

  def test_rejects_unknown_criterion_key(self):
    data = {
      "schema": TRACKING_SCHEMA,
      "version": TRACKING_VERSION,
      "phase": "IP-004.PHASE-05",
      "entrance_criteria": [
        {"item": "do thing", "completed": True, "stray_key": "value"},
      ],
    }
    errors = _validate(data)
    assert any("stray_key" in err for err in errors)
