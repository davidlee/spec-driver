"""Base frontmatter metadata for all artifacts.

This module defines the metadata schema for base frontmatter fields common to
all spec-driver artifacts, enabling metadata-driven validation and JSON Schema
generation.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

BASE_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.base",
  description="Base frontmatter fields for all spec-driver artifacts",
  fields={
    "id": FieldMetadata(
      type="string",
      required=True,
      pattern=r".+",  # Non-empty string
      description=(
        "Globally unique identifier with family prefix (e.g., SPEC-001, FR-102)"
      ),
    ),
    "name": FieldMetadata(
      type="string",
      required=True,
      pattern=r".+",  # Non-empty string
      description="Human-readable artifact name",
    ),
    "slug": FieldMetadata(
      type="string",
      required=True,
      pattern=r".+",  # Non-empty string
      description="URL-safe slug for linking and file moves",
    ),
    "kind": FieldMetadata(
      type="enum",
      required=True,
      enum_values=[
        "audit",
        "delta",
        "design_revision",
        "issue",
        "phase",
        "plan",
        "policy",
        "problem",
        "prod",
        "requirement",
        "risk",
        "spec",
        "standard",
        "task",
        "verification",
      ],
      description="Artifact family/type",
    ),
    "status": FieldMetadata(
      type="string",
      required=True,
      pattern=r".+",  # Non-empty string
      description="Approval/lifecycle status (varies by kind)",
    ),
    "lifecycle": FieldMetadata(
      type="enum",
      required=False,
      enum_values=[
        "discovery",
        "design",
        "implementation",
        "verification",
        "maintenance",
      ],
      description="Current lifecycle phase",
    ),
    "created": FieldMetadata(
      type="string",
      required=True,
      pattern=r"^\d{4}-\d{2}-\d{2}$",
      description="ISO-8601 date (YYYY-MM-DD)",
    ),
    "updated": FieldMetadata(
      type="string",
      required=True,
      pattern=r"^\d{4}-\d{2}-\d{2}$",
      description="ISO-8601 date (YYYY-MM-DD)",
    ),
    "owners": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(type="string", pattern=r".+", description="Owner identifier"),
      description="Responsible owners",
    ),
    "auditers": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Auditer identifier"
      ),
      description="Audit reviewers",
    ),
    "source": FieldMetadata(
      type="string",
      required=False,
      description="Canonical source path for syncing across folders",
    ),
    "summary": FieldMetadata(
      type="string",
      required=False,
      description="1-2 sentence overview for search and agents",
    ),
    "tags": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(type="string", pattern=r".+", description="Tag value"),
      description="Discovery tags for loose categorization",
    ),
    "relations": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Relationship edge to another artifact",
        properties={
          "type": FieldMetadata(
            type="enum",
            required=True,
            enum_values=[
              "implements",
              "verifies",
              "depends_on",
              "collaborates_with",
              "provides_for",
              "supersedes",
              "superseded_by",
              "relates_to",
              "blocks",
              "blocked_by",
              "decomposes",
              "tracked_by",
            ],
            description="Relationship type",
          ),
          "target": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",  # Non-empty string
            description="Target artifact ID",
          ),
          # Note: Additional fields like via, method, annotation, strength, effective
          # are allowed but not strictly validated (forward compatibility)
        },
      ),
      description="Relationship edges to other artifacts",
    ),
  },
  examples=[
    # Minimal example
    {
      "id": "SPEC-001",
      "name": "Example Specification",
      "slug": "example-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete example
    {
      "id": "SPEC-100",
      "name": "Authentication and Authorization Specification",
      "slug": "spec-auth",
      "kind": "spec",
      "status": "approved",
      "lifecycle": "implementation",
      "created": "2024-06-08",
      "updated": "2025-01-15",
      "owners": ["alice", "bob"],
      "auditers": ["charlie"],
      "source": "docs/specs/SPEC-100.md",
      "summary": (
        "Defines authentication flows and authorization policies for the platform."
      ),
      "tags": ["security", "auth", "core"],
      "relations": [
        {
          "type": "implements",
          "target": "FR-102",
          "via": "VT-102",
          "annotation": "OAuth2 implementation",
        },
        {
          "type": "depends_on",
          "target": "SPEC-004",
          "strength": "strong",
        },
      ],
    },
  ],
)

__all__ = [
  "BASE_FRONTMATTER_METADATA",
]
