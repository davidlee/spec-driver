"""Metadata definitions for spec relationships and capabilities blocks.

Enables metadata-driven JSON Schema generation and yaml-example output
for the two spec block types registered in relationships.py.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import (
  BlockMetadata,
  FieldMetadata,
  MetadataValidator,
)
from supekku.scripts.lib.blocks.relationships import (
  CAPABILITIES_SCHEMA,
  CAPABILITIES_VERSION,
  RELATIONSHIPS_SCHEMA,
  RELATIONSHIPS_VERSION,
  RelationshipsBlock,
)

# ---------------------------------------------------------------------------
# spec.relationships
# ---------------------------------------------------------------------------

SPEC_RELATIONSHIPS_METADATA = BlockMetadata(
  version=RELATIONSHIPS_VERSION,
  schema_id=RELATIONSHIPS_SCHEMA,
  description="Defines spec relationships to requirements and other specs",
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
    "spec": FieldMetadata(
      type="string",
      required=True,
      description="Spec ID (e.g., SPEC-001 or PROD-001)",
    ),
    "requirements": FieldMetadata(
      type="object",
      required=False,
      description="Requirement references grouped by relationship",
      properties={
        "primary": FieldMetadata(
          type="array",
          required=False,
          description="Primary requirement IDs owned by this spec",
          items=FieldMetadata(type="string", description="Requirement ID"),
        ),
        "collaborators": FieldMetadata(
          type="array",
          required=False,
          description="Collaborator requirement IDs from other specs",
          items=FieldMetadata(type="string", description="Requirement ID"),
        ),
      },
    ),
    "interactions": FieldMetadata(
      type="array",
      required=False,
      description="Cross-spec interaction declarations",
      items=FieldMetadata(
        type="object",
        description="Interaction entry",
        properties={
          "type": FieldMetadata(
            type="string",
            required=True,
            description="Interaction type (e.g., calls, extends, implements)",
          ),
          "spec": FieldMetadata(
            type="string",
            required=True,
            description="Target spec ID",
          ),
          "notes": FieldMetadata(
            type="string",
            required=False,
            description="Free-text notes about the interaction",
          ),
          "description": FieldMetadata(
            type="string",
            required=False,
            description="Free-text description of the interaction",
          ),
        },
      ),
    ),
  },
  examples=[
    {
      "schema": RELATIONSHIPS_SCHEMA,
      "version": RELATIONSHIPS_VERSION,
      "spec": "SPEC-100",
      "requirements": {
        "primary": [
          "SPEC-100.FR-001",
          "SPEC-100.FR-002",
          "SPEC-100.NF-001",
        ],
        "collaborators": ["SPEC-200.FR-010"],
      },
      "interactions": [
        {"type": "calls", "spec": "SPEC-200", "notes": "Registry lookup"},
      ],
    }
  ],
)

# ---------------------------------------------------------------------------
# spec.capabilities
# ---------------------------------------------------------------------------

SPEC_CAPABILITIES_METADATA = BlockMetadata(
  version=CAPABILITIES_VERSION,
  schema_id=CAPABILITIES_SCHEMA,
  description=("Defines spec capabilities with responsibilities and success criteria"),
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=CAPABILITIES_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{CAPABILITIES_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=CAPABILITIES_VERSION,
      required=True,
      description=f"Schema version (must be {CAPABILITIES_VERSION})",
    ),
    "spec": FieldMetadata(
      type="string",
      required=True,
      description="Spec ID (e.g., PROD-001)",
    ),
    "capabilities": FieldMetadata(
      type="array",
      required=True,
      description="List of capability definitions",
      items=FieldMetadata(
        type="object",
        description="Capability entry",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            description="Kebab-case capability identifier",
          ),
          "name": FieldMetadata(
            type="string",
            required=True,
            description="Human-readable capability name",
          ),
          "responsibilities": FieldMetadata(
            type="array",
            required=False,
            description="What this capability is responsible for",
            items=FieldMetadata(type="string", description="Responsibility"),
          ),
          "requirements": FieldMetadata(
            type="array",
            required=False,
            description="Requirement IDs this capability addresses",
            items=FieldMetadata(type="string", description="Requirement ID"),
          ),
          "summary": FieldMetadata(
            type="string",
            required=False,
            description="Prose summary of the capability",
          ),
          "success_criteria": FieldMetadata(
            type="array",
            required=False,
            description="Measurable success criteria",
            items=FieldMetadata(type="string", description="Criterion"),
          ),
        },
      ),
    ),
  },
  examples=[
    {
      "schema": CAPABILITIES_SCHEMA,
      "version": CAPABILITIES_VERSION,
      "spec": "PROD-001",
      "capabilities": [
        {
          "id": "user-authentication",
          "name": "User Authentication",
          "responsibilities": [
            "Validate user credentials",
            "Issue session tokens",
          ],
          "requirements": ["PROD-001.FR-001", "PROD-001.NF-001"],
          "summary": "Handles user identity verification and session management.",
          "success_criteria": [
            "Valid credentials produce a session token",
            "Invalid credentials return 401 within 200ms",
          ],
        }
      ],
    }
  ],
)

_SPEC_RELATIONSHIPS_VALIDATOR = MetadataValidator(SPEC_RELATIONSHIPS_METADATA)

_SPEC_CAPABILITIES_VALIDATOR = MetadataValidator(SPEC_CAPABILITIES_METADATA)


def validate_spec_relationships(
  block: RelationshipsBlock,
  *,
  spec_id: str | None = None,
) -> list[str]:
  """Validate a spec relationships block against its metadata declaration.

  Returns the metadata-driven errors plus, when ``spec_id`` is provided,
  an ID-equality check matching the legacy ``RelationshipsBlockValidator``
  message string (callers test truthiness of the returned list).
  """
  errors = [
    str(err)
    for err in _SPEC_RELATIONSHIPS_VALIDATOR.validate(block.data, strict=True)
  ]
  spec_value = str(block.data.get("spec", ""))
  if spec_id and spec_value and spec_value != spec_id:
    errors.append(
      f"relationships block spec {spec_value} does not match expected {spec_id}",
    )
  return errors


def validate_spec_capabilities(
  block: RelationshipsBlock,
  *,
  spec_id: str | None = None,
) -> list[str]:
  """Validate a spec capabilities block against its metadata declaration.

  Ergonomic counterpart to :func:`validate_spec_relationships`. The
  ``spec_id`` parameter is accepted for API symmetry but is **not**
  enforced — no legacy hand-rolled validator existed for this block, so
  introducing an ID-equality check here would tighten validation beyond
  the DE-118 invariant-preserving scope. The metadata declaration
  already enforces the ``spec`` field's presence and string type via
  :class:`MetadataValidator`.
  """
  del spec_id  # accepted for API symmetry; see docstring above.
  return [
    str(err)
    for err in _SPEC_CAPABILITIES_VALIDATOR.validate(block.data, strict=True)
  ]


__all__ = [
  "SPEC_CAPABILITIES_METADATA",
  "SPEC_RELATIONSHIPS_METADATA",
  "validate_spec_capabilities",
  "validate_spec_relationships",
]
