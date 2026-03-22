"""Workflow state schema definition — supekku:workflow.state@v1."""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata
from supekku.scripts.lib.blocks.workflow_metadata import (
  ARTIFACT_KIND_VALUES,
  HANDOFF_BOUNDARY_VALUES,
  PHASE_STATUS_VALUES,
  ROLE_VALUES,
  STATE_SCHEMA,
  STATE_VERSION,
  WORKFLOW_STATUS_VALUES,
  _timestamps_block,
)


def _artifact_block(*, required: bool = True) -> FieldMetadata:
  """Common artifact identification block."""
  return FieldMetadata(
    type="object",
    required=required,
    description="Artifact identification",
    properties={
      "id": FieldMetadata(
        type="string",
        required=True,
        description="Entity ID (e.g., DE-090)",
      ),
      "kind": FieldMetadata(
        type="enum",
        required=True,
        enum_values=ARTIFACT_KIND_VALUES,
        description="Artifact kind",
      ),
      "path": FieldMetadata(
        type="string",
        required=False,
        description="Relative path to artifact",
      ),
      "notes_path": FieldMetadata(
        type="string",
        required=False,
        description="Relative path to notes file",
      ),
    },
  )


WORKFLOW_STATE_METADATA = BlockMetadata(
  version=STATE_VERSION,
  schema_id=STATE_SCHEMA,
  description="Current orchestration status and pointers for a workflow artifact",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=STATE_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{STATE_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=STATE_VERSION,
      required=True,
      description=f"Schema version (must be {STATE_VERSION})",
    ),
    "artifact": _artifact_block(),
    "plan": FieldMetadata(
      type="object",
      required=False,
      description="Plan reference (absent if no IP exists)",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Plan ID (e.g., IP-090)",
        ),
        "path": FieldMetadata(
          type="string",
          required=False,
          description="Relative path to plan file",
        ),
      },
    ),
    "phase": FieldMetadata(
      type="object",
      required=True,
      description="Current phase",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Phase ID (e.g., IP-090.PHASE-05)",
        ),
        "path": FieldMetadata(
          type="string",
          required=False,
          description="Relative path to phase sheet",
        ),
        "status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=PHASE_STATUS_VALUES,
          description="Phase status",
        ),
      },
    ),
    "workflow": FieldMetadata(
      type="object",
      required=True,
      description="Workflow orchestration state",
      properties={
        "status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=WORKFLOW_STATUS_VALUES,
          description="Current workflow status",
        ),
        "active_role": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ROLE_VALUES,
          description="Currently active role",
        ),
        "next_role": FieldMetadata(
          type="enum",
          required=False,
          enum_values=ROLE_VALUES,
          description="Expected next role",
        ),
        "handoff_boundary": FieldMetadata(
          type="enum",
          required=False,
          enum_values=HANDOFF_BOUNDARY_VALUES,
          description="Default trigger boundary",
        ),
        "claimed_by": FieldMetadata(
          type="string",
          required=False,
          description="Agent/operator identity holding the claim (null when unclaimed)",
        ),
        "previous_state": FieldMetadata(
          type="enum",
          required=False,
          enum_values=WORKFLOW_STATUS_VALUES,
          description="State before blocking (set by block, cleared by unblock)",
        ),
      },
    ),
    "pointers": FieldMetadata(
      type="object",
      required=False,
      description="Paths to related workflow files",
      properties={
        "current_handoff": FieldMetadata(
          type="string",
          required=False,
          description="Path to handoff file",
        ),
        "review_index": FieldMetadata(
          type="string",
          required=False,
          description="Path to review index",
        ),
        "review_findings": FieldMetadata(
          type="string",
          required=False,
          description="Path to review findings",
        ),
        "sessions": FieldMetadata(
          type="string",
          required=False,
          description="Path to sessions file",
        ),
        "review_bootstrap": FieldMetadata(
          type="string",
          required=False,
          description="Path to review bootstrap doc",
        ),
      },
    ),
    "timestamps": _timestamps_block(
      {
        "created": FieldMetadata(
          type="string",
          required=True,
          description="Creation timestamp (ISO 8601)",
        ),
        "updated": FieldMetadata(
          type="string",
          required=True,
          description="Last update timestamp (ISO 8601)",
        ),
      }
    ),
  },
  examples=[
    {
      "schema": STATE_SCHEMA,
      "version": STATE_VERSION,
      "artifact": {
        "id": "DE-090",
        "kind": "delta",
        "path": ".spec-driver/deltas/DE-090-example",
        "notes_path": ".spec-driver/deltas/DE-090-example/notes.md",
      },
      "plan": {
        "id": "IP-090",
        "path": ".spec-driver/deltas/DE-090-example/IP-090.md",
      },
      "phase": {
        "id": "IP-090.PHASE-01",
        "status": "in_progress",
        "path": ".spec-driver/deltas/DE-090-example/phases/phase-01.md",
      },
      "workflow": {
        "status": "implementing",
        "active_role": "implementer",
        "handoff_boundary": "phase",
      },
      "timestamps": {
        "created": "2026-03-20T10:00:00+00:00",
        "updated": "2026-03-20T12:30:00+00:00",
      },
    }
  ],
)
