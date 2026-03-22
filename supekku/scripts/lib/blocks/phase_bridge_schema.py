"""Phase bridge schema definition — supekku:workflow.phase-bridge@v1."""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata
from supekku.scripts.lib.blocks.workflow_metadata import (
  PHASE_BRIDGE_SCHEMA,
  PHASE_BRIDGE_VERSION,
  PHASE_STATUS_VALUES,
)


def _placeholder_renderer(**kwargs: object) -> str:  # noqa: ARG001
  """Placeholder renderer for workflow schemas (real renderers in Phase 02+)."""
  return ""


PHASE_BRIDGE_METADATA = BlockMetadata(
  version=PHASE_BRIDGE_VERSION,
  schema_id=PHASE_BRIDGE_SCHEMA,
  description="Phase-close signal block in phase sheets for handoff emission",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=PHASE_BRIDGE_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{PHASE_BRIDGE_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=PHASE_BRIDGE_VERSION,
      required=True,
      description=f"Schema version (must be {PHASE_BRIDGE_VERSION})",
    ),
    "phase": FieldMetadata(
      type="string",
      required=True,
      description="Phase ID (e.g., IP-090.PHASE-05)",
    ),
    "status": FieldMetadata(
      type="enum",
      required=True,
      enum_values=PHASE_STATUS_VALUES,
      description="Phase status",
    ),
    "handoff_ready": FieldMetadata(
      type="bool",
      required=True,
      description="Whether phase completion should trigger handoff emission",
    ),
    "review_required": FieldMetadata(
      type="bool",
      required=False,
      description="Whether handoff should target reviewer role (defaults to false)",
    ),
    "current_handoff": FieldMetadata(
      type="string",
      required=False,
      description="Relative path to current handoff file",
    ),
  },
  examples=[
    {
      "schema": PHASE_BRIDGE_SCHEMA,
      "version": PHASE_BRIDGE_VERSION,
      "phase": "IP-090.PHASE-01",
      "status": "complete",
      "handoff_ready": True,
      "review_required": False,
    }
  ],
)
