"""Metadata definition for delta relationships blocks.

This module defines the metadata schema for delta relationships blocks,
enabling metadata-driven validation and JSON Schema generation.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import (
  BlockMetadata,
  FieldMetadata,
  MetadataValidator,
  ToleratedAlias,
)

# Reuse constants and block dataclass from delta.py
from .delta import (
  CONTEXT_INPUTS_SCHEMA,
  CONTEXT_INPUTS_VERSION,
  RELATIONSHIPS_SCHEMA,
  RELATIONSHIPS_VERSION,
  RISK_REGISTER_SCHEMA,
  RISK_REGISTER_VERSION,
  DeltaContextInputsBlock,
  DeltaRelationshipsBlock,
  DeltaRiskRegisterBlock,
)

# -- delta.context_inputs@v1 (DR-138 §5.1) --

CONTEXT_INPUTS_TYPE_ENUM: list[str] = [
  "delta",
  "revision",
  "audit",
  "phase",
  "plan",
  "spec",
  "prod",
  "adr",
  "issue",
  "problem",
  "improvement",
  "risk",
  "memory",
  "decision",
  "policy",
  "standard",
  "document",
  "code",
  "research",
]

CONTEXT_INPUTS_TYPE_ALIASES: dict[str, str] = {
  "reference": "document",
  "brief": "document",
  "external": "document",
  "investigation": "research",
}

CONTEXT_INPUTS_TYPE_TOLERATED_ALIASES: dict[str, ToleratedAlias] = {
  "unknown": ToleratedAlias(
    canonical="document",
    sunset_after="delta-sweep close",
    rationale=(
      "DR-138 §5.1 (F-138-B): migration emits 'unknown' for FM types that "
      "fail alias map AND canonical enum; tolerated_alias normalises to "
      "'document' at load while --no-tolerated-aliases flags artefacts for "
      "human re-classification before sunset"
    ),
  ),
}

# Risk-entry enums (DR-138 §5.2)
RISK_LIKELIHOOD_ENUM: list[str] = ["low", "medium", "high"]
RISK_IMPACT_ENUM: list[str] = ["low", "medium", "high"]
RISK_EXPOSURE_ENUM: list[str] = ["change", "delivery", "systemic"]
RISK_STATUS_ENUM: list[str] = ["open", "planned", "mitigated", "accepted", "closed"]

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


# -- delta.context_inputs@v1 (DR-138 §5.1) --

DELTA_CONTEXT_INPUTS_METADATA = BlockMetadata(
  version=CONTEXT_INPUTS_VERSION,
  schema_id=CONTEXT_INPUTS_SCHEMA,
  description=(
    "Context inputs (research, decisions, prior artefacts) consumed by this delta"
  ),
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=CONTEXT_INPUTS_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{CONTEXT_INPUTS_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=CONTEXT_INPUTS_VERSION,
      required=True,
      description=f"Schema version (must be {CONTEXT_INPUTS_VERSION})",
    ),
    "entries": FieldMetadata(
      type="array",
      required=True,
      description="Context input entries (may be empty)",
      items=FieldMetadata(
        type="object",
        description="A single context input entry",
        properties={
          "type": FieldMetadata(
            type="enum",
            required=True,
            enum_values=CONTEXT_INPUTS_TYPE_ENUM,
            aliases=CONTEXT_INPUTS_TYPE_ALIASES,
            tolerated_aliases=CONTEXT_INPUTS_TYPE_TOLERATED_ALIASES,
            description="Kind of context input",
          ),
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Identifier for the referenced artefact",
          ),
          "summary": FieldMetadata(
            type="string",
            required=False,
            description=(
              "Optional short summary; emitters MUST omit the key when "
              "absent (schema is non-nullable str; F-138-31)"
            ),
          ),
        },
        field_aliases={
          "ref": "id",
          "note": "summary",
          "annotation": "summary",
        },
      ),
    ),
  },
  examples=[
    {
      "schema": CONTEXT_INPUTS_SCHEMA,
      "version": CONTEXT_INPUTS_VERSION,
      "entries": [
        {"type": "delta", "id": "DE-136", "summary": "Umbrella program"},
        {"type": "adr", "id": "ADR-010", "summary": "Placement heuristic"},
      ],
    },
  ],
)

_DELTA_CONTEXT_INPUTS_VALIDATOR = MetadataValidator(DELTA_CONTEXT_INPUTS_METADATA)


def validate_delta_context_inputs(
  block: DeltaContextInputsBlock,
  *,
  strict: bool = True,
  accept_tolerated: bool = True,
) -> list[str]:
  """Validate a delta context_inputs block against its metadata declaration."""
  return [
    str(err)
    for err in _DELTA_CONTEXT_INPUTS_VALIDATOR.validate(
      block.data, strict=strict, accept_tolerated=accept_tolerated
    )
  ]


# -- delta.risk_register@v1 (DR-138 §5.2) --

DELTA_RISK_REGISTER_METADATA = BlockMetadata(
  version=RISK_REGISTER_VERSION,
  schema_id=RISK_REGISTER_SCHEMA,
  description="Delta risk register — risks scoped to this delta's execution",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=RISK_REGISTER_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{RISK_REGISTER_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=RISK_REGISTER_VERSION,
      required=True,
      description=f"Schema version (must be {RISK_REGISTER_VERSION})",
    ),
    "risks": FieldMetadata(
      type="array",
      required=True,
      description="Risk entries (may be empty)",
      items=FieldMetadata(
        type="object",
        description="A single risk entry",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Risk identifier (convention: '<DE-id>.RISK-NN')",
          ),
          "title": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Risk title / short statement",
          ),
          "likelihood": FieldMetadata(
            type="enum",
            required=True,
            enum_values=RISK_LIKELIHOOD_ENUM,
            description="Probability of occurrence",
          ),
          "impact": FieldMetadata(
            type="enum",
            required=True,
            enum_values=RISK_IMPACT_ENUM,
            description="Severity if it occurs",
          ),
          "exposure": FieldMetadata(
            type="enum",
            required=False,
            enum_values=RISK_EXPOSURE_ENUM,
            description="Type of exposure (change|delivery|systemic)",
          ),
          "mitigation": FieldMetadata(
            type="string",
            required=True,
            description="Mitigation strategy",
          ),
          "status": FieldMetadata(
            type="enum",
            required=False,
            enum_values=RISK_STATUS_ENUM,
            default_value="open",
            description="Risk status (default 'open' if absent)",
          ),
        },
        field_aliases={"description": "title"},
      ),
    ),
  },
  examples=[
    {
      "schema": RISK_REGISTER_SCHEMA,
      "version": RISK_REGISTER_VERSION,
      "risks": [
        {
          "id": "DE-138.RISK-01",
          "title": "Transition-window fallback dead code post-strict-flip",
          "likelihood": "high",
          "impact": "low",
          "exposure": "systemic",
          "mitigation": "Tracked for removal in follow-up cleanup delta",
          "status": "open",
        },
      ],
    },
  ],
)

_DELTA_RISK_REGISTER_VALIDATOR = MetadataValidator(DELTA_RISK_REGISTER_METADATA)


def validate_delta_risk_register(
  block: DeltaRiskRegisterBlock,
  *,
  strict: bool = True,
  accept_tolerated: bool = True,
) -> list[str]:
  """Validate a delta risk_register block against its metadata declaration."""
  return [
    str(err)
    for err in _DELTA_RISK_REGISTER_VALIDATOR.validate(
      block.data, strict=strict, accept_tolerated=accept_tolerated
    )
  ]


__all__ = [
  "CONTEXT_INPUTS_TYPE_ALIASES",
  "CONTEXT_INPUTS_TYPE_ENUM",
  "CONTEXT_INPUTS_TYPE_TOLERATED_ALIASES",
  "DELTA_CONTEXT_INPUTS_METADATA",
  "DELTA_RELATIONSHIPS_METADATA",
  "DELTA_RISK_REGISTER_METADATA",
  "RISK_EXPOSURE_ENUM",
  "RISK_IMPACT_ENUM",
  "RISK_LIKELIHOOD_ENUM",
  "RISK_STATUS_ENUM",
  "validate_delta_context_inputs",
  "validate_delta_relationships",
  "validate_delta_risk_register",
]
