"""Metadata definition for delta relationships blocks.

This module defines the metadata schema for delta relationships blocks,
enabling metadata-driven validation and JSON Schema generation.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import (
  BlockMetadata,
  FieldMetadata,
  MetadataValidator,
)

# Reuse constants and block dataclass from delta.py
from .delta import (
  RELATIONSHIPS_SCHEMA,
  RELATIONSHIPS_VERSION,
  DeltaRelationshipsBlock,
)

# Metadata definition for delta relationships blocks
DELTA_RELATIONSHIPS_METADATA = BlockMetadata(
  version=RELATIONSHIPS_VERSION,
  schema_id=RELATIONSHIPS_SCHEMA,
  description=(
    "Tracks delta relationships to specs, requirements, phases, and revisions"
  ),
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=RELATIONSHIPS_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{RELATIONSHIPS_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=RELATIONSHIPS_VERSION,
      required=True,
      description=f"Schema version (must be {RELATIONSHIPS_VERSION})",
    ),
    "delta": FieldMetadata(
      type="string",
      required=True,
      description="Delta ID (e.g., DE-001)",
    ),
    "revision_links": FieldMetadata(
      type="object",
      required=False,
      description="Links to related revisions",
      properties={
        "introduces": FieldMetadata(
          type="array",
          required=False,
          description="Revision IDs introduced by this delta",
          items=FieldMetadata(type="string", description="Revision ID"),
        ),
        "supersedes": FieldMetadata(
          type="array",
          required=False,
          description="Revision IDs superseded by this delta",
          items=FieldMetadata(type="string", description="Revision ID"),
        ),
      },
    ),
    "specs": FieldMetadata(
      type="object",
      required=False,
      description="Specifications related to this delta",
      properties={
        "primary": FieldMetadata(
          type="array",
          required=False,
          description="Primary specification IDs",
          items=FieldMetadata(type="string", description="Spec ID"),
        ),
        "collaborators": FieldMetadata(
          type="array",
          required=False,
          description="Collaborator specification IDs",
          items=FieldMetadata(type="string", description="Spec ID"),
        ),
      },
    ),
    "requirements": FieldMetadata(
      type="object",
      required=False,
      description="Requirements related to this delta",
      properties={
        "implements": FieldMetadata(
          type="array",
          required=False,
          description="Requirement IDs implemented by this delta",
          items=FieldMetadata(type="string", description="Requirement ID"),
        ),
        "updates": FieldMetadata(
          type="array",
          required=False,
          description="Requirement IDs updated by this delta",
          items=FieldMetadata(type="string", description="Requirement ID"),
        ),
        "verifies": FieldMetadata(
          type="array",
          required=False,
          description="Requirement IDs verified by this delta",
          items=FieldMetadata(type="string", description="Requirement ID"),
        ),
      },
    ),
    "phases": FieldMetadata(
      type="array",
      required=False,
      description="Implementation phases for this delta",
      items=FieldMetadata(
        type="object",
        description="A single phase entry",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Phase ID (e.g., IP-001.PHASE-01)",
          ),
          "goal": FieldMetadata(
            type="string",
            required=False,
            description="Free-text phase goal (legacy authoring; prefer plan.overview)",
          ),
          "status": FieldMetadata(
            type="string",
            required=False,
            description="Phase status (legacy authoring; prefer plan.overview)",
          ),
        },
      ),
    ),
    "backlog_items": FieldMetadata(
      type="array",
      required=False,
      description="Backlog item IDs related to this delta",
      items=FieldMetadata(type="string", description="Backlog item ID"),
    ),
  },
  examples=[
    {
      "schema": RELATIONSHIPS_SCHEMA,
      "version": RELATIONSHIPS_VERSION,
      "delta": "DE-001",
      "revision_links": {
        "introduces": ["RE-001", "RE-002"],
        "supersedes": ["RE-000"],
      },
      "specs": {
        "primary": ["SPEC-100"],
        "collaborators": ["SPEC-200", "SPEC-300"],
      },
      "requirements": {
        "implements": [
          "SPEC-100.FR-AUTH",
          "SPEC-100.FR-USER-001",
          "SPEC-100.NFR-SECURITY",
        ],
        "updates": ["SPEC-200.FR-PROFILE"],
        "verifies": ["SPEC-100.NFR-PERFORMANCE"],
      },
      "phases": [
        {"id": "IP-001.PHASE-01"},
        {"id": "IP-001.PHASE-02"},
      ],
    }
  ],
)

_DELTA_RELATIONSHIPS_VALIDATOR = MetadataValidator(DELTA_RELATIONSHIPS_METADATA)


def validate_delta_relationships(
  block: DeltaRelationshipsBlock,
  *,
  delta_id: str | None = None,
) -> list[str]:
  """Validate a delta relationships block against its metadata declaration.

  Returns the metadata-driven errors plus, when ``delta_id`` is provided,
  an ID-equality check matching the legacy ``DeltaRelationshipsValidator``
  message string (callers test truthiness of the returned list).
  """
  errors = [
    str(err) for err in _DELTA_RELATIONSHIPS_VALIDATOR.validate(block.data, strict=True)
  ]
  delta_value = str(block.data.get("delta", ""))
  if delta_id and delta_value and delta_value != delta_id:
    errors.append(
      f"delta relationships block id {delta_value} does not match expected {delta_id}",
    )
  return errors


__all__ = [
  "DELTA_RELATIONSHIPS_METADATA",
  "validate_delta_relationships",
]
