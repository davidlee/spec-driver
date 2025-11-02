"""Requirement frontmatter metadata for kind: requirement artifacts.

This module defines the metadata schema for requirement frontmatter,
extending the base metadata with requirement-specific fields.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

REQUIREMENT_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.requirement",
  description="Frontmatter fields for requirements (kind: requirement)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Requirement-specific fields (all optional)
    "requirement_kind": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["functional", "non-functional", "policy", "standard"],
      description="Category of requirement",
    ),
    "rfc2119_level": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["must", "should", "may"],
      description="RFC 2119 requirement level",
    ),
    "value_driver": FieldMetadata(
      type="enum",
      required=False,
      enum_values=[
        "user-capability",
        "operational-excellence",
        "compliance",
        "experience",
      ],
      description="Primary value driver for this requirement",
    ),
    "acceptance_criteria": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Acceptance criterion"
      ),
      description="Given/When/Then style acceptance criteria",
    ),
    "verification_refs": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Verification ID"
      ),
      description="References to verification artifacts",
    ),
  },
  examples=[
    # Minimal requirement (base fields only)
    {
      "id": "FR-001",
      "name": "Example Requirement",
      "slug": "requirement-example",
      "kind": "requirement",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete requirement with all fields
    {
      "id": "FR-102",
      "name": "OAuth2 Token Refresh",
      "slug": "requirement-oauth2-refresh",
      "kind": "requirement",
      "status": "approved",
      "lifecycle": "implementation",
      "created": "2024-06-15",
      "updated": "2025-01-15",
      "owners": ["auth-team"],
      "summary": "System must support automatic OAuth2 token refresh",
      "tags": ["auth", "security", "oauth2"],
      "requirement_kind": "functional",
      "rfc2119_level": "must",
      "value_driver": "user-capability",
      "acceptance_criteria": [
        "Given an expired access token",
        "When the system detects token expiration",
        "Then it automatically refreshes using the refresh token",
        "And the user session continues without interruption",
      ],
      "verification_refs": [
        "VT-210",
        "VH-044",
      ],
      "relations": [
        {"type": "implements", "target": "SPEC-100.FR-05"},
        {"type": "verifies", "target": "VT-210"},
      ],
    },
  ],
)

__all__ = [
  "REQUIREMENT_FRONTMATTER_METADATA",
]
