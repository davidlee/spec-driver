"""Tests for workflow orchestration schema metadata.

Validates that MetadataValidator correctly accepts valid input and rejects
invalid input for all 7 workflow/bridge schemas defined in DR-102.
"""

from __future__ import annotations

import unittest

from supekku.scripts.lib.blocks.metadata import MetadataValidator

from .workflow_metadata import (
  HANDOFF_SCHEMA,
  HANDOFF_VERSION,
  NOTES_BRIDGE_METADATA,
  NOTES_BRIDGE_SCHEMA,
  NOTES_BRIDGE_VERSION,
  PHASE_BRIDGE_METADATA,
  PHASE_BRIDGE_SCHEMA,
  PHASE_BRIDGE_VERSION,
  REVIEW_FINDINGS_METADATA,
  REVIEW_FINDINGS_SCHEMA,
  REVIEW_FINDINGS_VERSION,
  REVIEW_INDEX_METADATA,
  REVIEW_INDEX_SCHEMA,
  REVIEW_INDEX_VERSION,
  SESSIONS_SCHEMA,
  SESSIONS_VERSION,
  STATE_SCHEMA,
  STATE_VERSION,
  WORKFLOW_HANDOFF_METADATA,
  WORKFLOW_SESSIONS_METADATA,
  WORKFLOW_STATE_METADATA,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate(metadata, data):
  """Run MetadataValidator and return error strings."""
  v = MetadataValidator(metadata)
  return [str(e) for e in v.validate(data)]


# ---------------------------------------------------------------------------
# 3.1  Workflow State
# ---------------------------------------------------------------------------


class WorkflowStateTest(unittest.TestCase):
  """Tests for supekku.workflow.state schema."""

  def _minimal_valid(self):
    return {
      "schema": STATE_SCHEMA,
      "version": STATE_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "phase": {
        "id": "IP-090.PHASE-05",
        "status": "complete",
      },
      "workflow": {
        "status": "implementing",
        "active_role": "implementer",
      },
      "timestamps": {
        "created": "2026-03-21T10:00:00Z",
        "updated": "2026-03-21T10:30:00Z",
      },
    }

  def test_valid_minimal(self):
    errors = _validate(WORKFLOW_STATE_METADATA, self._minimal_valid())
    assert errors == [], errors

  def test_valid_full(self):
    data = self._minimal_valid()
    data["plan"] = {"id": "IP-090", "path": "IP-090.md"}
    data["phase"]["path"] = "phases/phase-05.md"
    data["artifact"]["path"] = ".spec-driver/deltas/DE-090-slug"
    data["artifact"]["notes_path"] = ".spec-driver/deltas/DE-090-slug/notes.md"
    data["workflow"]["next_role"] = "reviewer"
    data["workflow"]["handoff_boundary"] = "phase"
    data["workflow"]["claimed_by"] = "impl-claude"
    data["pointers"] = {
      "current_handoff": "workflow/handoff.current.yaml",
      "review_index": "workflow/review-index.yaml",
    }
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert errors == [], errors

  def test_missing_schema(self):
    data = self._minimal_valid()
    del data["schema"]
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("schema" in e and "required" in e for e in errors)

  def test_missing_artifact(self):
    data = self._minimal_valid()
    del data["artifact"]
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("artifact" in e and "required" in e for e in errors)

  def test_missing_artifact_id(self):
    data = self._minimal_valid()
    del data["artifact"]["id"]
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("artifact.id" in e for e in errors)

  def test_invalid_artifact_kind(self):
    data = self._minimal_valid()
    data["artifact"]["kind"] = "widget"
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("artifact.kind" in e for e in errors)

  def test_missing_phase(self):
    data = self._minimal_valid()
    del data["phase"]
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("phase" in e and "required" in e for e in errors)

  def test_invalid_phase_status(self):
    data = self._minimal_valid()
    data["phase"]["status"] = "done"
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("phase.status" in e for e in errors)

  def test_missing_workflow(self):
    data = self._minimal_valid()
    del data["workflow"]
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("workflow" in e and "required" in e for e in errors)

  def test_invalid_workflow_status(self):
    data = self._minimal_valid()
    data["workflow"]["status"] = "done"
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("workflow.status" in e for e in errors)

  def test_invalid_active_role(self):
    data = self._minimal_valid()
    data["workflow"]["active_role"] = "intern"
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("workflow.active_role" in e for e in errors)

  def test_missing_timestamps(self):
    data = self._minimal_valid()
    del data["timestamps"]
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("timestamps" in e and "required" in e for e in errors)

  def test_missing_timestamp_created(self):
    data = self._minimal_valid()
    del data["timestamps"]["created"]
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("timestamps.created" in e for e in errors)

  def test_plan_optional(self):
    """Plan block is optional — absence should not error."""
    data = self._minimal_valid()
    assert "plan" not in data
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert errors == [], errors

  def test_plan_requires_id(self):
    data = self._minimal_valid()
    data["plan"] = {"path": "IP-090.md"}
    errors = _validate(WORKFLOW_STATE_METADATA, data)
    assert any("plan.id" in e for e in errors)


# ---------------------------------------------------------------------------
# 3.2  Handoff
# ---------------------------------------------------------------------------


class WorkflowHandoffTest(unittest.TestCase):
  """Tests for supekku.workflow.handoff schema."""

  def _minimal_valid(self):
    return {
      "schema": HANDOFF_SCHEMA,
      "version": HANDOFF_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "transition": {
        "from_role": "implementer",
        "to_role": "reviewer",
        "status": "pending",
      },
      "phase": {"id": "IP-090.PHASE-05"},
      "required_reading": ["DE-090.md"],
      "next_activity": {"kind": "review"},
      "timestamps": {"emitted_at": "2026-03-21T10:30:00Z"},
    }

  def test_valid_minimal(self):
    errors = _validate(WORKFLOW_HANDOFF_METADATA, self._minimal_valid())
    assert errors == [], errors

  def test_valid_full(self):
    data = self._minimal_valid()
    data["transition"]["boundary"] = "phase"
    data["phase"]["status"] = "complete"
    data["related_documents"] = ["notes.md"]
    data["key_files"] = ["supekku/cli/common.py"]
    data["verification"] = {
      "commands": ["uv run pytest"],
      "summary": "all pass",
      "status": "pass",
    }
    data["git"] = {
      "head": "e31eca9",
      "branch": "main",
      "worktree": {
        "has_uncommitted_changes": False,
        "has_staged_changes": False,
      },
    }
    data["open_items"] = [
      {
        "id": "OI-001",
        "kind": "next_step",
        "summary": "Implement Phase 06",
        "blocking": False,
      }
    ]
    data["design_tensions"] = []
    data["unresolved_assumptions"] = []
    data["decisions_to_preserve"] = ["use uid not id"]
    data["next_activity"]["summary"] = "Review Phase 05"
    errors = _validate(WORKFLOW_HANDOFF_METADATA, data)
    assert errors == [], errors

  def test_missing_required_reading(self):
    data = self._minimal_valid()
    del data["required_reading"]
    errors = _validate(WORKFLOW_HANDOFF_METADATA, data)
    assert any("required_reading" in e for e in errors)

  def test_empty_required_reading(self):
    data = self._minimal_valid()
    data["required_reading"] = []
    errors = _validate(WORKFLOW_HANDOFF_METADATA, data)
    assert any("required_reading" in e and "at least" in e for e in errors)

  def test_missing_transition(self):
    data = self._minimal_valid()
    del data["transition"]
    errors = _validate(WORKFLOW_HANDOFF_METADATA, data)
    assert any("transition" in e and "required" in e for e in errors)

  def test_invalid_transition_status(self):
    data = self._minimal_valid()
    data["transition"]["status"] = "awaiting_review"
    errors = _validate(WORKFLOW_HANDOFF_METADATA, data)
    assert any("transition.status" in e for e in errors)

  def test_missing_next_activity(self):
    data = self._minimal_valid()
    del data["next_activity"]
    errors = _validate(WORKFLOW_HANDOFF_METADATA, data)
    assert any("next_activity" in e for e in errors)

  def test_invalid_next_activity_kind(self):
    data = self._minimal_valid()
    data["next_activity"]["kind"] = "coffee_break"
    errors = _validate(WORKFLOW_HANDOFF_METADATA, data)
    assert any("next_activity.kind" in e for e in errors)

  def test_verification_requires_status(self):
    data = self._minimal_valid()
    data["verification"] = {"summary": "all pass"}
    errors = _validate(WORKFLOW_HANDOFF_METADATA, data)
    assert any("verification.status" in e for e in errors)

  def test_open_item_requires_all_fields(self):
    data = self._minimal_valid()
    data["open_items"] = [{"id": "OI-001"}]
    errors = _validate(WORKFLOW_HANDOFF_METADATA, data)
    assert any("kind" in e and "required" in e for e in errors)
    assert any("summary" in e and "required" in e for e in errors)
    assert any("blocking" in e and "required" in e for e in errors)

  def test_git_worktree_requires_bools(self):
    data = self._minimal_valid()
    data["git"] = {
      "head": "abc123",
      "worktree": {"has_uncommitted_changes": "yes"},
    }
    errors = _validate(WORKFLOW_HANDOFF_METADATA, data)
    assert any("has_uncommitted_changes" in e and "boolean" in e for e in errors)


# ---------------------------------------------------------------------------
# 3.3  Review Index
# ---------------------------------------------------------------------------


class ReviewIndexTest(unittest.TestCase):
  """Tests for supekku.workflow.review-index schema."""

  def _minimal_valid(self):
    return {
      "schema": REVIEW_INDEX_SCHEMA,
      "version": REVIEW_INDEX_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "review": {
        "bootstrap_status": "warm",
        "last_bootstrapped_at": "2026-03-21T10:25:00Z",
      },
      "domain_map": [
        {
          "area": "cli",
          "purpose": "command routing",
          "files": ["supekku/cli/common.py"],
        }
      ],
      "staleness": {
        "cache_key": {
          "phase_id": "IP-090.PHASE-05",
          "head": "e31eca9",
        },
      },
    }

  def test_valid_minimal(self):
    errors = _validate(REVIEW_INDEX_METADATA, self._minimal_valid())
    assert errors == [], errors

  def test_valid_full(self):
    data = self._minimal_valid()
    data["review"]["session_scope"] = "artifact"
    data["review"]["source_handoff"] = "workflow/handoff.current.yaml"
    data["invariants"] = [
      {"id": "INV-001", "summary": "JSON output stable"},
    ]
    data["risk_areas"] = [
      {"id": "RA-001", "summary": "Reverse lookup gaps", "files": []},
    ]
    data["review_focus"] = ["output stability"]
    data["known_decisions"] = [
      {"id": "KD-001", "summary": "use uid not id"},
    ]
    data["staleness"]["invalidation_triggers"] = ["major_scope_change"]
    errors = _validate(REVIEW_INDEX_METADATA, data)
    assert errors == [], errors

  def test_missing_domain_map(self):
    data = self._minimal_valid()
    del data["domain_map"]
    errors = _validate(REVIEW_INDEX_METADATA, data)
    assert any("domain_map" in e and "required" in e for e in errors)

  def test_empty_domain_map(self):
    data = self._minimal_valid()
    data["domain_map"] = []
    errors = _validate(REVIEW_INDEX_METADATA, data)
    assert any("domain_map" in e and "at least" in e for e in errors)

  def test_domain_entry_requires_area(self):
    data = self._minimal_valid()
    data["domain_map"] = [{"purpose": "x", "files": ["a.py"]}]
    errors = _validate(REVIEW_INDEX_METADATA, data)
    assert any("area" in e and "required" in e for e in errors)

  def test_domain_entry_requires_files(self):
    data = self._minimal_valid()
    data["domain_map"] = [{"area": "cli", "purpose": "x"}]
    errors = _validate(REVIEW_INDEX_METADATA, data)
    assert any("files" in e and "required" in e for e in errors)

  def test_domain_entry_files_min_1(self):
    data = self._minimal_valid()
    data["domain_map"] = [{"area": "cli", "purpose": "x", "files": []}]
    errors = _validate(REVIEW_INDEX_METADATA, data)
    assert any("files" in e and "at least" in e for e in errors)

  def test_invalid_bootstrap_status(self):
    data = self._minimal_valid()
    data["review"]["bootstrap_status"] = "hot"
    errors = _validate(REVIEW_INDEX_METADATA, data)
    assert any("bootstrap_status" in e for e in errors)

  def test_missing_staleness(self):
    data = self._minimal_valid()
    del data["staleness"]
    errors = _validate(REVIEW_INDEX_METADATA, data)
    assert any("staleness" in e and "required" in e for e in errors)

  def test_missing_cache_key_head(self):
    data = self._minimal_valid()
    del data["staleness"]["cache_key"]["head"]
    errors = _validate(REVIEW_INDEX_METADATA, data)
    assert any("head" in e and "required" in e for e in errors)


# ---------------------------------------------------------------------------
# 3.4  Review Findings
# ---------------------------------------------------------------------------


class ReviewFindingsTest(unittest.TestCase):
  """Tests for supekku.workflow.review-findings schema."""

  def _minimal_valid(self):
    return {
      "schema": REVIEW_FINDINGS_SCHEMA,
      "version": REVIEW_FINDINGS_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "review": {"round": 1, "status": "in_progress"},
      "timestamps": {"updated": "2026-03-21T10:35:00Z"},
    }

  def test_valid_minimal(self):
    errors = _validate(REVIEW_FINDINGS_METADATA, self._minimal_valid())
    assert errors == [], errors

  def test_valid_with_findings(self):
    data = self._minimal_valid()
    data["review"]["round"] = 3
    data["review"]["status"] = "changes_requested"
    data["review"]["reviewer_role"] = "reviewer"
    data["blocking"] = [
      {
        "id": "R3-001",
        "title": "Output regression",
        "summary": "Field change breaks consumers",
        "status": "open",
        "files": ["supekku/cli/output.py"],
        "related_invariants": ["INV-001"],
      }
    ]
    data["non_blocking"] = [
      {
        "id": "R3-002",
        "title": "Add regression test",
        "summary": "Coverage gap",
        "status": "open",
      }
    ]
    data["resolved"] = [
      {
        "id": "R2-001",
        "title": "ID mismatch",
        "status": "resolved",
        "resolution_summary": "Switched to uid",
      }
    ]
    data["waived"] = []
    data["history"] = [
      {"round": 1, "summary": "Initial review"},
      {"round": 2, "summary": "Follow-up"},
    ]
    errors = _validate(REVIEW_FINDINGS_METADATA, data)
    assert errors == [], errors

  def test_missing_review_round(self):
    data = self._minimal_valid()
    del data["review"]["round"]
    errors = _validate(REVIEW_FINDINGS_METADATA, data)
    assert any("round" in e and "required" in e for e in errors)

  def test_invalid_review_status(self):
    data = self._minimal_valid()
    data["review"]["status"] = "done"
    errors = _validate(REVIEW_FINDINGS_METADATA, data)
    assert any("review.status" in e for e in errors)

  def test_finding_requires_id_title_status(self):
    data = self._minimal_valid()
    data["blocking"] = [{"summary": "something wrong"}]
    errors = _validate(REVIEW_FINDINGS_METADATA, data)
    assert any("id" in e and "required" in e for e in errors)
    assert any("title" in e and "required" in e for e in errors)
    assert any("status" in e and "required" in e for e in errors)

  def test_invalid_finding_status(self):
    data = self._minimal_valid()
    data["blocking"] = [
      {
        "id": "R1-001",
        "title": "Bug",
        "summary": "Bad",
        "status": "fixed",
      }
    ]
    errors = _validate(REVIEW_FINDINGS_METADATA, data)
    assert any("status" in e for e in errors)

  def test_round_must_be_int(self):
    data = self._minimal_valid()
    data["review"]["round"] = "three"
    errors = _validate(REVIEW_FINDINGS_METADATA, data)
    assert any("round" in e and "integer" in e for e in errors)

  def test_history_entry_requires_round_summary(self):
    data = self._minimal_valid()
    data["history"] = [{"round": 1}]
    errors = _validate(REVIEW_FINDINGS_METADATA, data)
    assert any("summary" in e and "required" in e for e in errors)


# ---------------------------------------------------------------------------
# 3.5  Sessions
# ---------------------------------------------------------------------------


class WorkflowSessionsTest(unittest.TestCase):
  """Tests for supekku.workflow.sessions schema."""

  def _minimal_valid(self):
    return {
      "schema": SESSIONS_SCHEMA,
      "version": SESSIONS_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "sessions": {
        "implementer": {
          "session_name": "sd-DE-090-impl",
          "status": "active",
          "last_seen": "2026-03-21T10:20:00Z",
        },
      },
    }

  def test_valid_minimal(self):
    errors = _validate(WORKFLOW_SESSIONS_METADATA, self._minimal_valid())
    assert errors == [], errors

  def test_valid_multi_role(self):
    data = self._minimal_valid()
    data["sessions"]["reviewer"] = {
      "session_name": "sd-DE-090-review",
      "sandbox": "gemini-review",
      "status": "paused",
      "last_seen": "2026-03-21T10:34:00Z",
    }
    errors = _validate(WORKFLOW_SESSIONS_METADATA, data)
    assert errors == [], errors

  def test_missing_sessions(self):
    data = self._minimal_valid()
    del data["sessions"]
    errors = _validate(WORKFLOW_SESSIONS_METADATA, data)
    assert any("sessions" in e and "required" in e for e in errors)

  def test_missing_artifact(self):
    data = self._minimal_valid()
    del data["artifact"]
    errors = _validate(WORKFLOW_SESSIONS_METADATA, data)
    assert any("artifact" in e and "required" in e for e in errors)


# ---------------------------------------------------------------------------
# 7.1  Notes Bridge
# ---------------------------------------------------------------------------


class NotesBridgeTest(unittest.TestCase):
  """Tests for supekku.workflow.notes-bridge schema."""

  def _minimal_valid(self):
    return {
      "schema": NOTES_BRIDGE_SCHEMA,
      "version": NOTES_BRIDGE_VERSION,
      "artifact": "DE-090",
      "workflow_state": "workflow/state.yaml",
    }

  def test_valid_minimal(self):
    errors = _validate(NOTES_BRIDGE_METADATA, self._minimal_valid())
    assert errors == [], errors

  def test_valid_full(self):
    data = self._minimal_valid()
    data["current_handoff"] = "workflow/handoff.current.yaml"
    data["review_index"] = "workflow/review-index.yaml"
    data["review_findings"] = "workflow/review-findings.yaml"
    data["review_bootstrap"] = "workflow/review-bootstrap.md"
    errors = _validate(NOTES_BRIDGE_METADATA, data)
    assert errors == [], errors

  def test_missing_artifact(self):
    data = self._minimal_valid()
    del data["artifact"]
    errors = _validate(NOTES_BRIDGE_METADATA, data)
    assert any("artifact" in e and "required" in e for e in errors)

  def test_missing_workflow_state(self):
    data = self._minimal_valid()
    del data["workflow_state"]
    errors = _validate(NOTES_BRIDGE_METADATA, data)
    assert any("workflow_state" in e and "required" in e for e in errors)

  def test_wrong_schema_value(self):
    data = self._minimal_valid()
    data["schema"] = "supekku.workflow.state"
    errors = _validate(NOTES_BRIDGE_METADATA, data)
    assert any("schema" in e for e in errors)


# ---------------------------------------------------------------------------
# 7.2  Phase Bridge
# ---------------------------------------------------------------------------


class PhaseBridgeTest(unittest.TestCase):
  """Tests for supekku.workflow.phase-bridge schema."""

  def _minimal_valid(self):
    return {
      "schema": PHASE_BRIDGE_SCHEMA,
      "version": PHASE_BRIDGE_VERSION,
      "phase": "IP-090.PHASE-05",
      "status": "complete",
      "handoff_ready": True,
    }

  def test_valid_minimal(self):
    errors = _validate(PHASE_BRIDGE_METADATA, self._minimal_valid())
    assert errors == [], errors

  def test_valid_full(self):
    data = self._minimal_valid()
    data["review_required"] = True
    data["current_handoff"] = "../workflow/handoff.current.yaml"
    errors = _validate(PHASE_BRIDGE_METADATA, data)
    assert errors == [], errors

  def test_missing_phase(self):
    data = self._minimal_valid()
    del data["phase"]
    errors = _validate(PHASE_BRIDGE_METADATA, data)
    assert any("phase" in e and "required" in e for e in errors)

  def test_missing_status(self):
    data = self._minimal_valid()
    del data["status"]
    errors = _validate(PHASE_BRIDGE_METADATA, data)
    assert any("status" in e and "required" in e for e in errors)

  def test_invalid_status(self):
    data = self._minimal_valid()
    data["status"] = "finished"
    errors = _validate(PHASE_BRIDGE_METADATA, data)
    assert any("status" in e for e in errors)

  def test_missing_handoff_ready(self):
    data = self._minimal_valid()
    del data["handoff_ready"]
    errors = _validate(PHASE_BRIDGE_METADATA, data)
    assert any("handoff_ready" in e and "required" in e for e in errors)

  def test_handoff_ready_must_be_bool(self):
    data = self._minimal_valid()
    data["handoff_ready"] = "yes"
    errors = _validate(PHASE_BRIDGE_METADATA, data)
    assert any("handoff_ready" in e and "boolean" in e for e in errors)

  def test_wrong_schema_value(self):
    data = self._minimal_valid()
    data["schema"] = "supekku.workflow.notes-bridge"
    errors = _validate(PHASE_BRIDGE_METADATA, data)
    assert any("schema" in e for e in errors)

  def test_wrong_version(self):
    data = self._minimal_valid()
    data["version"] = 2
    errors = _validate(PHASE_BRIDGE_METADATA, data)
    assert any("version" in e for e in errors)


# ---------------------------------------------------------------------------
# Cross-cutting: schema/version constants match
# ---------------------------------------------------------------------------


class SchemaConstantsTest(unittest.TestCase):
  """Verify schema constants are consistent."""

  def test_state_metadata_matches_constants(self):
    assert WORKFLOW_STATE_METADATA.schema_id == STATE_SCHEMA
    assert WORKFLOW_STATE_METADATA.version == STATE_VERSION

  def test_handoff_metadata_matches_constants(self):
    assert WORKFLOW_HANDOFF_METADATA.schema_id == HANDOFF_SCHEMA
    assert WORKFLOW_HANDOFF_METADATA.version == HANDOFF_VERSION

  def test_review_index_metadata_matches_constants(self):
    assert REVIEW_INDEX_METADATA.schema_id == REVIEW_INDEX_SCHEMA
    assert REVIEW_INDEX_METADATA.version == REVIEW_INDEX_VERSION

  def test_review_findings_metadata_matches_constants(self):
    assert REVIEW_FINDINGS_METADATA.schema_id == REVIEW_FINDINGS_SCHEMA
    assert REVIEW_FINDINGS_METADATA.version == REVIEW_FINDINGS_VERSION

  def test_notes_bridge_metadata_matches_constants(self):
    assert NOTES_BRIDGE_METADATA.schema_id == NOTES_BRIDGE_SCHEMA
    assert NOTES_BRIDGE_METADATA.version == NOTES_BRIDGE_VERSION

  def test_phase_bridge_metadata_matches_constants(self):
    assert PHASE_BRIDGE_METADATA.schema_id == PHASE_BRIDGE_SCHEMA
    assert PHASE_BRIDGE_METADATA.version == PHASE_BRIDGE_VERSION


if __name__ == "__main__":
  unittest.main()
