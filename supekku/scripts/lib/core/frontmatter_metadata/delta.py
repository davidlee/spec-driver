"""Delta frontmatter metadata for kind: delta artifacts.

This module defines the metadata schema for delta frontmatter,
extending the base metadata with delta-specific fields.
"""

from __future__ import annotations

from dataclasses import replace

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

# -- Audit gate constants (DEC-079-003, DEC-079-010) --

AUDIT_GATE_AUTO = "auto"
AUDIT_GATE_REQUIRED = "required"
AUDIT_GATE_EXEMPT = "exempt"

AUDIT_GATE_VALUES: set[str] = {
  AUDIT_GATE_AUTO,
  AUDIT_GATE_REQUIRED,
  AUDIT_GATE_EXEMPT,
}

DELTA_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.delta",
  description="Frontmatter fields for deltas (kind: delta)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Base field persistence overrides for delta compaction
    "lifecycle": replace(
      BASE_FRONTMATTER_METADATA.fields["lifecycle"],
      persistence="optional",
    ),
    "owners": replace(
      BASE_FRONTMATTER_METADATA.fields["owners"],
      persistence="optional",
      default_value=[],
    ),
    "auditers": replace(
      BASE_FRONTMATTER_METADATA.fields["auditers"],
      persistence="optional",
      default_value=[],
    ),
    "source": replace(
      BASE_FRONTMATTER_METADATA.fields["source"],
      persistence="optional",
    ),
    "summary": replace(
      BASE_FRONTMATTER_METADATA.fields["summary"],
      persistence="optional",
    ),
    "tags": replace(
      BASE_FRONTMATTER_METADATA.fields["tags"],
      persistence="optional",
      default_value=[],
    ),
    "relations": replace(
      BASE_FRONTMATTER_METADATA.fields["relations"],
      persistence="default-omit",
      default_value=[],
    ),
    # Delta-specific fields (all optional)
    "applies_to": FieldMetadata(
      type="object",
      required=False,
      description="Declarative inputs this delta aligns with",
      persistence="default-omit",
      default_value={"specs": [], "requirements": []},
      properties={
        "specs": FieldMetadata(
          type="array",
          required=False,
          items=FieldMetadata(type="string", pattern=r".+", description="Spec ID"),
          description="Specification IDs this delta applies to",
        ),
        "prod": FieldMetadata(
          type="array",
          required=False,
          items=FieldMetadata(
            type="string", pattern=r".+", description="Product spec ID"
          ),
          description="Product specification IDs this delta applies to",
        ),
        "requirements": FieldMetadata(
          type="array",
          required=False,
          items=FieldMetadata(
            type="string", pattern=r".+", description="Requirement ID"
          ),
          description="Requirement IDs this delta applies to",
        ),
      },
    ),
    "context_inputs": FieldMetadata(
      type="array",
      required=False,
      persistence="optional",
      default_value=[],
      items=FieldMetadata(
        type="object",
        description="Supporting research or decision context",
        properties={
          "type": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["research", "decision", "hypothesis", "issue"],
            description="Type of context input",
          ),
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Context artifact ID",
          ),
        },
      ),
      description="Supporting research, decisions, or hypotheses",
    ),
    "outcome_summary": FieldMetadata(
      type="string",
      required=False,
      description=("Declarative description of target state after applying delta"),
      persistence="optional",
    ),
    "audit_gate": FieldMetadata(
      type="enum",
      required=False,
      enum_values=sorted(AUDIT_GATE_VALUES),
      description=(
        "Audit gating for delta completion: auto resolves from applies_to.requirements"
      ),
      persistence="default-omit",
      default_value=AUDIT_GATE_AUTO,
    ),
    "audit_gate_rationale": FieldMetadata(
      type="string",
      required=False,
      description="Required when audit_gate is exempt",
      persistence="optional",
    ),
    "risk_register": FieldMetadata(
      type="array",
      required=False,
      persistence="optional",
      default_value=[],
      items=FieldMetadata(
        type="object",
        description="Risk entry for this delta",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Risk ID (e.g., RISK-DC-001)",
          ),
          "title": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Risk title/summary",
          ),
          "exposure": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["change", "systemic", "operational", "delivery"],
            description="Type of risk exposure",
          ),
          "likelihood": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["low", "medium", "high"],
            description="Probability of occurrence",
          ),
          "impact": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["low", "medium", "high"],
            description="Severity of impact",
          ),
          "mitigation": FieldMetadata(
            type="string",
            required=False,
            description="Mitigation strategy",
          ),
        },
      ),
      description="Risks associated with this change",
    ),
  },
  examples=[
    # Minimal delta (base fields only)
    {
      "id": "DE-001",
      "name": "Example Delta",
      "slug": "delta-example",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete delta with all fields
    {
      "id": "DE-021",
      "name": "Content Binding Schema Migration",
      "slug": "delta-content-binding-migration",
      "kind": "delta",
      "status": "approved",
      "lifecycle": "implementation",
      "created": "2024-06-08",
      "updated": "2025-01-15",
      "owners": ["alice"],
      "summary": "Migrate content binding to event sourcing architecture",
      "applies_to": {
        "specs": ["SPEC-101", "SPEC-102"],
        "prod": ["PROD-020"],
        "requirements": ["SPEC-101.FR-01", "PROD-020.NF-03"],
      },
      "context_inputs": [
        {"type": "research", "id": "RC-010"},
        {"type": "decision", "id": "SPEC-101.DEC-02"},
      ],
      "outcome_summary": (
        "Content binding uses event sourcing with optimistic locking, "
        "maintaining block UUIDs across reconciliation cycles"
      ),
      "risk_register": [
        {
          "id": "RISK-DC-001",
          "title": "Schema migration might lose historical block IDs",
          "exposure": "change",
          "likelihood": "medium",
          "impact": "high",
          "mitigation": "Add dry-run checksum validation before applying events",
        }
      ],
      "relations": [
        {"type": "implements", "target": "SPEC-101"},
        {"type": "depends_on", "target": "RC-010"},
      ],
    },
  ],
)

__all__ = [
  "AUDIT_GATE_AUTO",
  "AUDIT_GATE_EXEMPT",
  "AUDIT_GATE_REQUIRED",
  "AUDIT_GATE_VALUES",
  "DELTA_FRONTMATTER_METADATA",
]
