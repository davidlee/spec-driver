"""Notes bridge schema definition — supekku:workflow.notes-bridge@v1."""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata
from supekku.scripts.lib.blocks.workflow_metadata import (
  NOTES_BRIDGE_SCHEMA,
  NOTES_BRIDGE_VERSION,
)

NOTES_BRIDGE_METADATA = BlockMetadata(
  version=NOTES_BRIDGE_VERSION,
  schema_id=NOTES_BRIDGE_SCHEMA,
  description="Pointer block in notes.md linking to workflow control plane files",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=NOTES_BRIDGE_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{NOTES_BRIDGE_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=NOTES_BRIDGE_VERSION,
      required=True,
      description=f"Schema version (must be {NOTES_BRIDGE_VERSION})",
    ),
    "artifact": FieldMetadata(
      type="string",
      required=True,
      description="Entity ID (e.g., DE-090)",
    ),
    "workflow_state": FieldMetadata(
      type="string",
      required=True,
      description="Relative path to workflow/state.yaml",
    ),
    "current_handoff": FieldMetadata(
      type="string",
      required=False,
      description="Relative path to handoff file",
    ),
    "review_index": FieldMetadata(
      type="string",
      required=False,
      description="Relative path to review index",
    ),
    "review_findings": FieldMetadata(
      type="string",
      required=False,
      description="Relative path to review findings",
    ),
    "review_bootstrap": FieldMetadata(
      type="string",
      required=False,
      description="Relative path to review bootstrap doc",
    ),
  },
  examples=[
    {
      "schema": NOTES_BRIDGE_SCHEMA,
      "version": NOTES_BRIDGE_VERSION,
      "artifact": "DE-090",
      "workflow_state": "workflow/state.yaml",
      "current_handoff": "workflow/handoff.current.yaml",
      "review_index": "workflow/review-index.yaml",
    }
  ],
)
