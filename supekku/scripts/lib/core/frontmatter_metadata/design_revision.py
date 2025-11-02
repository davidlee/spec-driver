"""Design revision frontmatter metadata for kind: design_revision artifacts.

This module defines the metadata schema for design revision frontmatter,
extending the base metadata with design revision-specific fields.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

DESIGN_REVISION_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.design_revision",
  description="Frontmatter fields for design revisions (kind: design_revision)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Design revision-specific fields (all optional)
    "delta_ref": FieldMetadata(
      type="string",
      required=False,
      pattern=r".+",
      description="Reference to the delta this revision implements",
    ),
    "source_context": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Source context entry (research or hypothesis)",
        properties={
          "type": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["research", "hypothesis"],
            description="Type of source context",
          ),
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Source context ID",
          ),
        },
      ),
      description="Research or hypotheses informing this revision",
    ),
    "code_impacts": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Code area impacted by this revision",
        properties={
          "path": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Code path affected",
          ),
          "current_state": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Summary of existing behavior",
          ),
          "target_state": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Intended behavior after revision",
          ),
        },
      ),
      description="Code areas affected by this design revision",
    ),
    "verification_alignment": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="How this revision affects a verification",
        properties={
          "verification": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Verification ID (e.g., VT-210)",
          ),
          "impact": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["regression", "new"],
            description="Impact on verification (regression or new)",
          ),
        },
      ),
      description="How this revision affects existing tests",
    ),
    "design_decisions": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Design decision made in this revision",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Decision ID (e.g., SPEC-101.DEC-04)",
          ),
          "summary": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Decision summary",
          ),
        },
      ),
      description="Design decisions made in this revision",
    ),
    "open_questions": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Question needing resolution",
        properties={
          "description": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Question description",
          ),
          "owner": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Person responsible for answering",
          ),
          "due": FieldMetadata(
            type="string",
            required=True,
            pattern=r"^\d{4}-\d{2}-\d{2}$",
            description="Due date (ISO-8601)",
          ),
        },
      ),
      description="Questions needing resolution",
    ),
  },
  examples=[
    # Minimal design revision (base fields only)
    {
      "id": "REV-001",
      "name": "Example Design Revision",
      "slug": "example-revision",
      "kind": "design_revision",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete design revision with all fields
    {
      "id": "REV-021",
      "name": "Schema Update Design Revision",
      "slug": "rev-schema-update",
      "kind": "design_revision",
      "status": "approved",
      "lifecycle": "design",
      "created": "2024-06-08",
      "updated": "2025-01-15",
      "owners": ["dev-team"],
      "summary": "Design for implementing optimistic locking in schema updates",
      "delta_ref": "DE-021",
      "source_context": [
        {"type": "research", "id": "RC-010"},
        {"type": "hypothesis", "id": "PROD-020.HYP-03"},
      ],
      "code_impacts": [
        {
          "path": "internal/content/reconciler.go",
          "current_state": "Direct schema updates without locking",
          "target_state": "Optimistic locking with version checks",
        },
        {
          "path": "internal/content/schema_repo.go",
          "current_state": "Single transaction per update",
          "target_state": "Retry logic with exponential backoff",
        },
      ],
      "verification_alignment": [
        {"verification": "VT-210", "impact": "regression"},
        {"verification": "VA-044", "impact": "new"},
      ],
      "design_decisions": [
        {
          "id": "SPEC-101.DEC-04",
          "summary": "Adopt optimistic locking for schema updates",
        }
      ],
      "open_questions": [
        {
          "description": "Do we need a background repair job?",
          "owner": "david",
          "due": "2024-06-12",
        }
      ],
      "relations": [
        {"type": "implements", "target": "DE-021"},
      ],
    },
  ],
)

__all__ = [
  "DESIGN_REVISION_FRONTMATTER_METADATA",
]
