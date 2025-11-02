"""Policy frontmatter metadata for kind: policy artifacts.

This module defines the metadata schema for policy frontmatter,
extending the base metadata with policy-specific fields for governance
and lifecycle tracking.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

POLICY_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.policy",
  description="Frontmatter fields for policies (kind: policy)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Policy-specific fields (all optional)
    "reviewed": FieldMetadata(
      type="string",
      required=False,
      pattern=r"^\d{4}-\d{2}-\d{2}$",
      description="ISO-8601 date of last review (YYYY-MM-DD)",
    ),
    "supersedes": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r"^POL-\d{3}$",
        description="Previous policy ID",
      ),
      description="Previous policy IDs superseded by this one",
    ),
    "superseded_by": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r"^POL-\d{3}$",
        description="Superseding policy ID",
      ),
      description="Policy IDs that supersede this one",
    ),
    "standards": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r"^STD-\d{3}$",
        description="Standard ID",
      ),
      description="Related standard IDs",
    ),
    "specs": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(type="string", pattern=r".+", description="Spec ID"),
      description="Related specification IDs",
    ),
    "requirements": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(type="string", pattern=r".+", description="Requirement ID"),
      description="Related requirement IDs",
    ),
    "deltas": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(type="string", pattern=r".+", description="Delta ID"),
      description="Related delta IDs",
    ),
    "related_policies": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r"^POL-\d{3}$",
        description="Related policy ID",
      ),
      description="Related policy IDs (not supersession)",
    ),
    "related_standards": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r"^STD-\d{3}$",
        description="Related standard ID",
      ),
      description="Related standard IDs",
    ),
  },
  examples=[
    # Minimal policy (base fields only)
    {
      "id": "POL-001",
      "name": "Example Policy",
      "slug": "policy-example",
      "kind": "policy",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete policy with all fields
    {
      "id": "POL-042",
      "name": "Code Review and Approval Policy",
      "slug": "policy-code-review",
      "kind": "policy",
      "status": "required",
      "lifecycle": "maintenance",
      "created": "2024-03-10",
      "updated": "2025-01-15",
      "reviewed": "2025-01-10",
      "owners": ["engineering-leads"],
      "auditers": ["quality-team"],
      "summary": (
        "Mandates peer review for all production code changes with "
        "approval from at least one technical lead."
      ),
      "tags": ["quality", "governance", "engineering"],
      "supersedes": ["POL-012", "POL-023"],
      "standards": ["STD-001", "STD-015"],
      "specs": ["SPEC-101"],
      "requirements": ["SPEC-101.FR-05"],
      "deltas": ["DE-042"],
      "related_policies": ["POL-043"],
      "related_standards": ["STD-002"],
      "relations": [
        {"type": "supersedes", "target": "POL-012"},
        {"type": "relates_to", "target": "STD-001"},
      ],
    },
  ],
)

__all__ = [
  "POLICY_FRONTMATTER_METADATA",
]
