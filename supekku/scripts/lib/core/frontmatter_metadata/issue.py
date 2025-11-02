"""Issue frontmatter metadata for kind: issue artifacts.

This module defines the metadata schema for issue frontmatter,
extending the base metadata with issue-specific fields.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

ISSUE_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.issue",
  description="Frontmatter fields for issues (kind: issue)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Issue-specific fields (all optional)
    "categories": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Issue category"
      ),
      description=(
        "Issue categories (e.g., regression, verification_gap, enhancement)"
      ),
    ),
    "severity": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["p1", "p2", "p3", "p4"],
      description="Priority/severity level (p1=critical, p4=low)",
    ),
    "impact": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["user", "systemic", "process"],
      description="Type of impact",
    ),
    "problem_refs": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Problem ID"
      ),
      description="Related problem statement IDs",
    ),
    "related_requirements": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Requirement ID"
      ),
      description="Related requirement IDs",
    ),
    "affected_verifications": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Verification ID"
      ),
      description="Affected verification artifact IDs",
    ),
    "linked_deltas": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Delta ID"
      ),
      description="Related delta IDs",
    ),
  },
  examples=[
    # Minimal issue (base fields only)
    {
      "id": "ISSUE-001",
      "name": "Example Issue",
      "slug": "issue-example",
      "kind": "issue",
      "status": "open",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete issue with all fields
    {
      "id": "ISSUE-234",
      "name": "Token Refresh Fails on Slow Networks",
      "slug": "issue-token-refresh-slow-network",
      "kind": "issue",
      "status": "triaged",
      "lifecycle": "implementation",
      "created": "2024-11-05",
      "updated": "2025-01-15",
      "owners": ["auth-team"],
      "summary": (
        "OAuth2 token refresh fails when network latency exceeds 5 seconds"
      ),
      "tags": ["auth", "reliability", "networking"],
      "categories": ["regression", "verification_gap"],
      "severity": "p2",
      "impact": "user",
      "problem_refs": ["PROB-012"],
      "related_requirements": ["SPEC-101.FR-01", "PROD-005.NF-02"],
      "affected_verifications": ["VT-210", "VA-044"],
      "linked_deltas": ["DE-021"],
      "relations": [
        {"type": "tracked_by", "target": "PROB-012"},
        {"type": "blocks", "target": "FR-102"},
      ],
    },
  ],
)

__all__ = [
  "ISSUE_FRONTMATTER_METADATA",
]
