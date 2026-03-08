"""Audit frontmatter metadata for kind: audit artifacts.

This module defines the metadata schema for audit frontmatter,
extending the base metadata with audit-specific fields including
the per-finding disposition contract (DEC-079-001).
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

# -- Disposition constants (DEC-079-001, DEC-079-007) --

DISPOSITION_STATUS_RECONCILED = "reconciled"
DISPOSITION_STATUS_ACCEPTED = "accepted"
DISPOSITION_STATUS_PENDING = "pending"

DISPOSITION_STATUSES: set[str] = {
  DISPOSITION_STATUS_RECONCILED,
  DISPOSITION_STATUS_ACCEPTED,
  DISPOSITION_STATUS_PENDING,
}

DISPOSITION_KIND_ALIGNED = "aligned"
DISPOSITION_KIND_SPEC_PATCH = "spec_patch"
DISPOSITION_KIND_REVISION = "revision"
DISPOSITION_KIND_FOLLOW_UP_DELTA = "follow_up_delta"
DISPOSITION_KIND_FOLLOW_UP_BACKLOG = "follow_up_backlog"
DISPOSITION_KIND_TOLERATED_DRIFT = "tolerated_drift"

DISPOSITION_KINDS: set[str] = {
  DISPOSITION_KIND_ALIGNED,
  DISPOSITION_KIND_SPEC_PATCH,
  DISPOSITION_KIND_REVISION,
  DISPOSITION_KIND_FOLLOW_UP_DELTA,
  DISPOSITION_KIND_FOLLOW_UP_BACKLOG,
  DISPOSITION_KIND_TOLERATED_DRIFT,
}

# -- Finding outcome constants --

FINDING_OUTCOME_ALIGNED = "aligned"
FINDING_OUTCOME_DRIFT = "drift"
FINDING_OUTCOME_RISK = "risk"

FINDING_OUTCOMES: set[str] = {
  FINDING_OUTCOME_ALIGNED,
  FINDING_OUTCOME_DRIFT,
  FINDING_OUTCOME_RISK,
}

# -- Audit mode constants --

AUDIT_MODE_CONFORMANCE = "conformance"
AUDIT_MODE_DISCOVERY = "discovery"

AUDIT_MODES: set[str] = {
  AUDIT_MODE_CONFORMANCE,
  AUDIT_MODE_DISCOVERY,
}

# -- Validity matrices (DEC-079-007, DEC-079-009) --

VALID_STATUS_KIND_PAIRS: dict[str, set[str]] = {
  DISPOSITION_KIND_ALIGNED: {DISPOSITION_STATUS_RECONCILED},
  DISPOSITION_KIND_SPEC_PATCH: {
    DISPOSITION_STATUS_PENDING,
    DISPOSITION_STATUS_RECONCILED,
  },
  DISPOSITION_KIND_REVISION: {
    DISPOSITION_STATUS_PENDING,
    DISPOSITION_STATUS_RECONCILED,
  },
  DISPOSITION_KIND_FOLLOW_UP_DELTA: {
    DISPOSITION_STATUS_PENDING,
    DISPOSITION_STATUS_ACCEPTED,
  },
  DISPOSITION_KIND_FOLLOW_UP_BACKLOG: {
    DISPOSITION_STATUS_PENDING,
    DISPOSITION_STATUS_ACCEPTED,
  },
  DISPOSITION_KIND_TOLERATED_DRIFT: {DISPOSITION_STATUS_ACCEPTED},
}

VALID_OUTCOME_KINDS: dict[str, set[str]] = {
  FINDING_OUTCOME_ALIGNED: {DISPOSITION_KIND_ALIGNED},
  FINDING_OUTCOME_DRIFT: {
    DISPOSITION_KIND_SPEC_PATCH,
    DISPOSITION_KIND_REVISION,
    DISPOSITION_KIND_FOLLOW_UP_DELTA,
    DISPOSITION_KIND_FOLLOW_UP_BACKLOG,
    DISPOSITION_KIND_TOLERATED_DRIFT,
  },
  FINDING_OUTCOME_RISK: {
    DISPOSITION_KIND_SPEC_PATCH,
    DISPOSITION_KIND_REVISION,
    DISPOSITION_KIND_FOLLOW_UP_DELTA,
    DISPOSITION_KIND_FOLLOW_UP_BACKLOG,
    DISPOSITION_KIND_TOLERATED_DRIFT,
  },
}

# -- Structured ref sub-schema (shared by refs and drift_refs) --

_REF_ITEM_SCHEMA = FieldMetadata(
  type="object",
  description="Structured reference",
  properties={
    "kind": FieldMetadata(
      type="string",
      required=True,
      pattern=r".+",
      description="Reference kind (e.g. spec, delta, drift_entry)",
    ),
    "ref": FieldMetadata(
      type="string",
      required=True,
      pattern=r".+",
      description="Reference ID (e.g. SPEC-101, DL-047.003)",
    ),
  },
)

# -- Disposition sub-schema (DEC-079-001) --

_DISPOSITION_SCHEMA = FieldMetadata(
  type="object",
  required=False,
  description="Per-finding disposition (DEC-079-001)",
  properties={
    "status": FieldMetadata(
      type="enum",
      required=True,
      enum_values=sorted(DISPOSITION_STATUSES),
      description="Whether this audit has finished routing the finding",
    ),
    "kind": FieldMetadata(
      type="enum",
      required=True,
      enum_values=sorted(DISPOSITION_KINDS),
      description="What routing path was taken",
    ),
    "refs": FieldMetadata(
      type="array",
      required=False,
      items=_REF_ITEM_SCHEMA,
      description="Reconciliation references (spec patches, revisions, follow-up work)",
    ),
    "drift_refs": FieldMetadata(
      type="array",
      required=False,
      items=_REF_ITEM_SCHEMA,
      description="Optional drift-ledger entry references",
    ),
    "rationale": FieldMetadata(
      type="string",
      required=False,
      description="Why this disposition is correct",
    ),
    "closure_override": FieldMetadata(
      type="object",
      required=False,
      description="Non-default gate relaxation (DEC-079-005)",
      properties={
        "effect": FieldMetadata(
          type="enum",
          required=True,
          enum_values=["warn", "none"],
          description="Relaxed closure effect (must be less strict than derived)",
        ),
        "rationale": FieldMetadata(
          type="string",
          required=True,
          pattern=r".+",
          description="Why the default gate is being relaxed",
        ),
      },
    ),
  },
)

# -- Audit frontmatter schema --

AUDIT_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.audit",
  description="Frontmatter fields for audits (kind: audit)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,
    # Audit-specific fields
    "mode": FieldMetadata(
      type="enum",
      required=False,
      enum_values=sorted(AUDIT_MODES),
      description=(
        "Audit mode: conformance (post-implementation) or discovery (backfill)"
      ),
    ),
    "delta_ref": FieldMetadata(
      type="string",
      required=False,
      pattern=r"^DE-\d+$",
      description="Owning delta ID",
    ),
    "spec_refs": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(type="string", pattern=r".+", description="Spec ID"),
      description="Referenced specification IDs",
    ),
    "prod_refs": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(type="string", pattern=r".+", description="Product spec ID"),
      description="Referenced product specification IDs",
    ),
    "code_scope": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Code path pattern"
      ),
      description="Code paths or patterns inspected during audit",
    ),
    "audit_window": FieldMetadata(
      type="object",
      required=False,
      description="Time window for the audit",
      properties={
        "start": FieldMetadata(
          type="string",
          required=True,
          pattern=r"^\d{4}-\d{2}-\d{2}$",
          description="Audit start date (ISO-8601)",
        ),
        "end": FieldMetadata(
          type="string",
          required=True,
          pattern=r"^\d{4}-\d{2}-\d{2}$",
          description="Audit end date (ISO-8601)",
        ),
      },
    ),
    "findings": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Individual audit finding",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Finding ID",
          ),
          "description": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Description of the finding",
          ),
          "outcome": FieldMetadata(
            type="enum",
            required=True,
            enum_values=sorted(FINDING_OUTCOMES),
            description="Finding outcome",
          ),
          "linked_issue": FieldMetadata(
            type="string",
            required=False,
            pattern=r".+",
            description="Related issue ID",
          ),
          "linked_delta": FieldMetadata(
            type="string",
            required=False,
            pattern=r".+",
            description="Related delta ID",
          ),
          "disposition": _DISPOSITION_SCHEMA,
        },
      ),
      description="Audit findings with optional per-finding disposition",
    ),
  },
  examples=[
    # Minimal audit
    {
      "id": "AUD-001",
      "name": "Example Audit",
      "slug": "audit-example",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Conformance audit with disposition
    {
      "id": "AUD-042",
      "name": "Content Binding Alignment Review",
      "slug": "audit-content-binding",
      "kind": "audit",
      "status": "completed",
      "created": "2024-06-01",
      "updated": "2024-06-08",
      "mode": "conformance",
      "delta_ref": "DE-021",
      "owners": ["qa-team"],
      "summary": (
        "Snapshot of how content reconciler aligns with SPEC-101 responsibilities"
      ),
      "tags": ["alignment", "content", "reconciler"],
      "spec_refs": ["SPEC-101"],
      "prod_refs": ["PROD-020"],
      "code_scope": ["internal/content/**", "cmd/vice/*"],
      "audit_window": {
        "start": "2024-06-01",
        "end": "2024-06-08",
      },
      "findings": [
        {
          "id": "FIND-001",
          "description": "Content reconciler deviates from SPEC-101 responsibility",
          "outcome": "drift",
          "linked_delta": "DE-021",
          "disposition": {
            "status": "reconciled",
            "kind": "spec_patch",
            "refs": [{"kind": "spec", "ref": "SPEC-101"}],
            "rationale": "Patched SPEC-101 to match observed behaviour",
          },
        }
      ],
    },
  ],
)

__all__ = [
  "AUDIT_FRONTMATTER_METADATA",
  "AUDIT_MODE_CONFORMANCE",
  "AUDIT_MODE_DISCOVERY",
  "AUDIT_MODES",
  "DISPOSITION_KIND_ALIGNED",
  "DISPOSITION_KIND_FOLLOW_UP_BACKLOG",
  "DISPOSITION_KIND_FOLLOW_UP_DELTA",
  "DISPOSITION_KIND_REVISION",
  "DISPOSITION_KIND_SPEC_PATCH",
  "DISPOSITION_KIND_TOLERATED_DRIFT",
  "DISPOSITION_KINDS",
  "DISPOSITION_STATUS_ACCEPTED",
  "DISPOSITION_STATUS_PENDING",
  "DISPOSITION_STATUS_RECONCILED",
  "DISPOSITION_STATUSES",
  "FINDING_OUTCOME_ALIGNED",
  "FINDING_OUTCOME_DRIFT",
  "FINDING_OUTCOME_RISK",
  "FINDING_OUTCOMES",
  "VALID_OUTCOME_KINDS",
  "VALID_STATUS_KIND_PAIRS",
]
