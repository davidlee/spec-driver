"""Audit frontmatter metadata for kind: audit artifacts.

This module defines the metadata schema for audit frontmatter,
extending the base metadata with audit-specific fields.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

AUDIT_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.audit",
  description="Frontmatter fields for audits (kind: audit)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Audit-specific fields (all optional)
    "spec_refs": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Spec ID"
      ),
      description="Referenced specification IDs",
    ),
    "prod_refs": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Product spec ID"
      ),
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
            enum_values=["drift", "aligned", "risk"],
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
        },
      ),
      description="Audit findings",
    ),
    "patch_level": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Patch-level alignment status",
        properties={
          "artefact": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Artifact ID",
          ),
          "status": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["aligned", "divergent", "unknown"],
            description="Alignment status",
          ),
          "notes": FieldMetadata(
            type="string",
            required=False,
            description="Additional notes",
          ),
        },
      ),
      description="Per-artifact alignment status",
    ),
    "next_actions": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Recommended next action",
        properties={
          "type": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["delta", "issue", "spec", "requirement"],
            description="Type of action",
          ),
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Action artifact ID",
          ),
        },
      ),
      description="Recommended next actions from audit",
    ),
  },
  examples=[
    # Minimal audit (base fields only)
    {
      "id": "AUDIT-001",
      "name": "Example Audit",
      "slug": "audit-example",
      "kind": "audit",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete audit with all fields
    {
      "id": "AUDIT-042",
      "name": "Content Binding Alignment Review",
      "slug": "audit-content-binding",
      "kind": "audit",
      "status": "approved",
      "lifecycle": "verification",
      "created": "2024-06-01",
      "updated": "2024-06-08",
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
          "linked_issue": "ISSUE-018",
          "linked_delta": "DE-021",
        }
      ],
      "patch_level": [
        {
          "artefact": "SPEC-101",
          "status": "divergent",
          "notes": (
            "Implementation matches responsibilities except schema validation"
          ),
        }
      ],
      "next_actions": [
        {"type": "delta", "id": "DE-021"},
        {"type": "issue", "id": "ISSUE-052"},
      ],
    },
  ],
)

__all__ = [
  "AUDIT_FRONTMATTER_METADATA",
]
