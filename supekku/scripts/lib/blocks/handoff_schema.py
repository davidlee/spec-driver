"""Workflow handoff schema definition — supekku:workflow.handoff@v1."""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata
from supekku.scripts.lib.blocks.workflow_metadata import (
  ARTIFACT_KIND_VALUES,
  HANDOFF_BOUNDARY_VALUES,
  HANDOFF_SCHEMA,
  HANDOFF_TRANSITION_STATUS_VALUES,
  HANDOFF_VERSION,
  NEXT_ACTIVITY_KIND_VALUES,
  OPEN_ITEM_KIND_VALUES,
  PHASE_STATUS_VALUES,
  ROLE_VALUES,
  VERIFICATION_STATUS_VALUES,
  _timestamps_block,
)

WORKFLOW_HANDOFF_METADATA = BlockMetadata(
  version=HANDOFF_VERSION,
  schema_id=HANDOFF_SCHEMA,
  description=("Durable phase-boundary transition payload for structured handoffs"),
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=HANDOFF_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{HANDOFF_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=HANDOFF_VERSION,
      required=True,
      description=f"Schema version (must be {HANDOFF_VERSION})",
    ),
    "artifact": FieldMetadata(
      type="object",
      required=True,
      description="Artifact identification",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Entity ID",
        ),
        "kind": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ARTIFACT_KIND_VALUES,
          description="Artifact kind",
        ),
      },
    ),
    "transition": FieldMetadata(
      type="object",
      required=True,
      description="Role transition details",
      properties={
        "from_role": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ROLE_VALUES,
          description="Originating role",
        ),
        "to_role": FieldMetadata(
          type="enum",
          required=True,
          enum_values=ROLE_VALUES,
          description="Target role",
        ),
        "boundary": FieldMetadata(
          type="enum",
          required=False,
          enum_values=HANDOFF_BOUNDARY_VALUES,
          description="Transition boundary type",
        ),
        "status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=HANDOFF_TRANSITION_STATUS_VALUES,
          description="Transition status",
        ),
      },
    ),
    "phase": FieldMetadata(
      type="object",
      required=True,
      description="Phase context for handoff",
      properties={
        "id": FieldMetadata(
          type="string",
          required=True,
          description="Phase ID",
        ),
        "status": FieldMetadata(
          type="enum",
          required=False,
          enum_values=PHASE_STATUS_VALUES,
          description="Phase status at handoff time",
        ),
      },
    ),
    "required_reading": FieldMetadata(
      type="array",
      required=True,
      min_items=1,
      description="Documents the receiving role must read",
      items=FieldMetadata(type="string", description="Document path"),
    ),
    "related_documents": FieldMetadata(
      type="array",
      required=False,
      description="Additional related documents",
      items=FieldMetadata(type="string", description="Document path"),
    ),
    "key_files": FieldMetadata(
      type="array",
      required=False,
      description="Key source files relevant to handoff",
      items=FieldMetadata(type="string", description="File path"),
    ),
    "verification": FieldMetadata(
      type="object",
      required=False,
      description="Verification state at handoff time",
      properties={
        "commands": FieldMetadata(
          type="array",
          required=False,
          description="Verification commands",
          items=FieldMetadata(type="string", description="Command"),
        ),
        "summary": FieldMetadata(
          type="string",
          required=False,
          description="Verification summary",
        ),
        "status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=VERIFICATION_STATUS_VALUES,
          description="Overall verification status",
        ),
      },
    ),
    "git": FieldMetadata(
      type="object",
      required=False,
      description="Git state at handoff time",
      properties={
        "head": FieldMetadata(
          type="string",
          required=True,
          description="HEAD commit (short hash)",
        ),
        "branch": FieldMetadata(
          type="string",
          required=False,
          description="Current branch",
        ),
        "worktree": FieldMetadata(
          type="object",
          required=False,
          description="Worktree state",
          properties={
            "has_uncommitted_changes": FieldMetadata(
              type="bool",
              required=True,
              description="Whether worktree has uncommitted changes",
            ),
            "has_staged_changes": FieldMetadata(
              type="bool",
              required=True,
              description="Whether worktree has staged changes",
            ),
          },
        ),
      },
    ),
    "open_items": FieldMetadata(
      type="array",
      required=False,
      description="Open items (next steps, blockers, questions, risks)",
      items=FieldMetadata(
        type="object",
        description="Open item",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Item ID (unique within handoff)",
          ),
          "kind": FieldMetadata(
            type="enum",
            required=True,
            enum_values=OPEN_ITEM_KIND_VALUES,
            description="Item kind",
          ),
          "summary": FieldMetadata(
            type="string",
            required=True,
            description="Item summary",
          ),
          "blocking": FieldMetadata(
            type="bool",
            required=True,
            description="Whether this item blocks progress",
          ),
        },
      ),
    ),
    "design_tensions": FieldMetadata(
      type="array",
      required=False,
      description="Unresolved design tensions",
      items=FieldMetadata(type="string", description="Tension description"),
    ),
    "unresolved_assumptions": FieldMetadata(
      type="array",
      required=False,
      description="Unresolved assumptions",
      items=FieldMetadata(type="string", description="Assumption"),
    ),
    "decisions_to_preserve": FieldMetadata(
      type="array",
      required=False,
      description="Decisions the next role should preserve",
      items=FieldMetadata(type="string", description="Decision"),
    ),
    "next_activity": FieldMetadata(
      type="object",
      required=True,
      description="What the receiving role should do next",
      properties={
        "kind": FieldMetadata(
          type="enum",
          required=True,
          enum_values=NEXT_ACTIVITY_KIND_VALUES,
          description="Next activity kind",
        ),
        "summary": FieldMetadata(
          type="string",
          required=False,
          description="Activity summary",
        ),
      },
    ),
    "timestamps": _timestamps_block(
      {
        "emitted_at": FieldMetadata(
          type="string",
          required=True,
          description="Handoff emission timestamp (ISO 8601)",
        ),
      }
    ),
  },
  examples=[
    {
      "schema": HANDOFF_SCHEMA,
      "version": HANDOFF_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "transition": {
        "from_role": "implementer",
        "to_role": "reviewer",
        "boundary": "phase",
        "status": "pending",
      },
      "phase": {"id": "IP-090.PHASE-01", "status": "complete"},
      "required_reading": [
        ".spec-driver/deltas/DE-090-example/notes.md",
        ".spec-driver/deltas/DE-090-example/phases/phase-01.md",
      ],
      "key_files": ["supekku/cli/show.py"],
      "verification": {
        "status": "pass",
        "commands": ["uv run python -m pytest"],
        "summary": "All tests pass",
      },
      "git": {
        "head": "abc1234",
        "branch": "main",
        "worktree": {
          "has_uncommitted_changes": False,
          "has_staged_changes": False,
        },
      },
      "open_items": [
        {
          "id": "OI-001",
          "kind": "next_step",
          "summary": "Review phase 01 output",
          "blocking": False,
        },
      ],
      "next_activity": {"kind": "review", "summary": "Review phase 01 changes"},
      "timestamps": {"emitted_at": "2026-03-20T14:00:00+00:00"},
    }
  ],
)
