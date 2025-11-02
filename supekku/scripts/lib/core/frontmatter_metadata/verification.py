"""Verification frontmatter metadata for kind: verification artifacts.

This module defines the metadata schema for verification frontmatter,
extending the base metadata with verification-specific fields.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

VERIFICATION_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.verification",
  description="Frontmatter fields for verifications (kind: verification)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Verification-specific fields (all optional)
    "verification_kind": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["automated", "agent", "manual"],
      description="Type of verification approach",
    ),
    "covers": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(type="string", pattern=r".+", description="Requirement ID"),
      description="Requirement IDs that this verification covers",
    ),
    "procedure": FieldMetadata(
      type="string",
      required=False,
      description="Outline of steps or tooling for verification",
    ),
  },
  examples=[
    # Minimal verification (base fields only)
    {
      "id": "VT-001",
      "name": "Example Verification",
      "slug": "verification-example",
      "kind": "verification",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete verification with all fields
    {
      "id": "VT-102",
      "name": "OAuth2 Authentication Flow Verification",
      "slug": "verification-oauth2-auth",
      "kind": "verification",
      "status": "approved",
      "lifecycle": "verification",
      "created": "2024-08-15",
      "updated": "2025-01-15",
      "owners": ["qa-team"],
      "summary": (
        "Automated verification of OAuth2 authentication flow "
        "including token generation and refresh"
      ),
      "tags": ["security", "auth", "automated"],
      "verification_kind": "automated",
      "covers": [
        "FR-102",
        "NF-020",
        "SPEC-100.FR-05",
      ],
      "procedure": (
        "Run integration test suite auth_flow_test.py with "
        "assertions on token validity and refresh behavior"
      ),
      "relations": [
        {"type": "verifies", "target": "FR-102"},
        {"type": "verifies", "target": "NF-020"},
      ],
    },
  ],
)

__all__ = [
  "VERIFICATION_FRONTMATTER_METADATA",
]
