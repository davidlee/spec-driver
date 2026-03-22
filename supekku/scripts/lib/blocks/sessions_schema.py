"""Workflow sessions schema definition — supekku:workflow.sessions@v1."""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata
from supekku.scripts.lib.blocks.workflow_metadata import (
  ARTIFACT_KIND_VALUES,
  SESSION_STATUS_VALUES,
  SESSIONS_SCHEMA,
  SESSIONS_VERSION,
)

_SESSION_ENTRY = FieldMetadata(
  type="object",
  description="Session entry for a role",
  properties={
    "session_name": FieldMetadata(
      type="string",
      required=True,
      description="Session name (string or null)",
    ),
    "sandbox": FieldMetadata(
      type="string",
      required=False,
      description="Sandbox identifier",
    ),
    "status": FieldMetadata(
      type="enum",
      required=True,
      enum_values=SESSION_STATUS_VALUES,
      description="Session status",
    ),
    "last_seen": FieldMetadata(
      type="string",
      required=True,
      description="Last seen timestamp (ISO 8601 or null)",
    ),
  },
)

WORKFLOW_SESSIONS_METADATA = BlockMetadata(
  version=SESSIONS_VERSION,
  schema_id=SESSIONS_SCHEMA,
  description="Runtime mapping of roles to sessions (optional, non-authority)",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=SESSIONS_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{SESSIONS_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=SESSIONS_VERSION,
      required=True,
      description=f"Schema version (must be {SESSIONS_VERSION})",
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
    # Sessions is a map of role_name → session_entry with dynamic keys.
    # FieldMetadata requires non-empty properties for object type, so we
    # model it as a sentinel object with a single documented example key.
    # Command-level validation handles per-entry checks.
    "sessions": FieldMetadata(
      type="object",
      required=True,
      description=("Map of role name to session entry (at least one entry required)"),
      properties={
        # Sentinel — FieldMetadata requires non-empty properties
        # for object type.  Real entries use dynamic role-name keys;
        # command-level code validates per-entry shape.
        "_entry_shape": _SESSION_ENTRY,
      },
    ),
  },
  examples=[
    {
      "schema": SESSIONS_SCHEMA,
      "version": SESSIONS_VERSION,
      "artifact": {"id": "DE-090", "kind": "delta"},
      "sessions": {
        "implementer": {
          "session_name": "pi-session-abc",
          "status": "active",
          "last_seen": "2026-03-20T14:30:00+00:00",
        },
        "reviewer": {
          "session_name": None,
          "status": "absent",
          "last_seen": None,
        },
      },
    }
  ],
)
