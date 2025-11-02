"""Standard frontmatter metadata for kind: standard artifacts.

This module defines the metadata schema for standard frontmatter,
extending the base metadata with standard-specific fields for governance
and lifecycle tracking.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

STANDARD_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.standard",
  description="Frontmatter fields for standards (kind: standard)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Standard-specific fields (all optional)
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
        pattern=r"^STD-\d{3}$",
        description="Previous standard ID",
      ),
      description="Previous standard IDs superseded by this one",
    ),
    "superseded_by": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r"^STD-\d{3}$",
        description="Superseding standard ID",
      ),
      description="Standard IDs that supersede this one",
    ),
    "policies": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r"^POL-\d{3}$",
        description="Policy ID",
      ),
      description="Related policy IDs",
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
    # Minimal standard (base fields only)
    {
      "id": "STD-001",
      "name": "Example Standard",
      "slug": "standard-example",
      "kind": "standard",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete standard with all fields
    {
      "id": "STD-015",
      "name": "Python Coding Standards",
      "slug": "standard-python-coding",
      "kind": "standard",
      "status": "default",
      "lifecycle": "maintenance",
      "created": "2024-02-15",
      "updated": "2025-01-15",
      "reviewed": "2025-01-05",
      "owners": ["engineering-standards"],
      "auditers": ["quality-team"],
      "summary": (
        "Defines code style, testing practices, and documentation "
        "requirements for Python codebases."
      ),
      "tags": ["python", "code-quality", "testing"],
      "supersedes": ["STD-008"],
      "policies": ["POL-042"],
      "specs": ["SPEC-101"],
      "requirements": ["SPEC-101.NF-02"],
      "deltas": ["DE-050"],
      "related_policies": ["POL-043"],
      "related_standards": ["STD-016"],
      "relations": [
        {"type": "supersedes", "target": "STD-008"},
        {"type": "relates_to", "target": "POL-042"},
      ],
    },
  ],
)

__all__ = [
  "STANDARD_FRONTMATTER_METADATA",
]
