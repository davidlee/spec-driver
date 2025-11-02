"""Problem frontmatter metadata for kind: problem artifacts.

This module defines the metadata schema for problem frontmatter,
extending the base metadata with problem-specific fields.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

PROBLEM_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.problem",
  description="Frontmatter fields for problems (kind: problem)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Problem-specific fields (all optional)
    "problem_statement": FieldMetadata(
      type="string",
      required=False,
      description="Crisp description of the pain or gap",
    ),
    "context": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Supporting evidence or context",
        properties={
          "type": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["research", "metric", "feedback", "observation"],
            description="Type of context evidence",
          ),
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Context artifact ID or metric name",
          ),
        },
      ),
      description="Evidence and context supporting the problem statement",
    ),
    "success_criteria": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Success criterion"
      ),
      description="Measurable criteria for problem resolution",
    ),
    "related_requirements": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Requirement ID"
      ),
      description="Requirements affected by or related to this problem",
    ),
  },
  examples=[
    # Minimal problem (base fields only)
    {
      "id": "PROB-001",
      "name": "Example Problem",
      "slug": "problem-example",
      "kind": "problem",
      "status": "captured",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete problem with all fields
    {
      "id": "PROB-012",
      "name": "Slow Sync Performance",
      "slug": "problem-slow-sync",
      "kind": "problem",
      "status": "validated",
      "lifecycle": "discovery",
      "created": "2024-09-10",
      "updated": "2025-01-15",
      "owners": ["product-team"],
      "summary": (
        "Users experience unacceptable sync latency causing workflow disruption"
      ),
      "tags": ["performance", "sync", "ux"],
      "problem_statement": (
        "Sync operations take over 15 seconds during peak usage, "
        "causing user frustration and workflow interruptions. "
        "Users expect real-time or near-real-time synchronization."
      ),
      "context": [
        {"type": "research", "id": "UX-023"},
        {"type": "metric", "id": "sync_latency_p99"},
        {"type": "feedback", "id": "support-ticket-4521"},
      ],
      "success_criteria": [
        "Users report sync completes within 5s in interviews",
        "P99 latency < 7s for two consecutive releases",
        "Customer satisfaction score > 4.0 for sync feature",
      ],
      "related_requirements": [
        "PROD-005.FR-02",
        "SPEC-101.NF-01",
      ],
      "relations": [
        {"type": "tracked_by", "target": "ISSUE-234"},
      ],
    },
  ],
)

__all__ = [
  "PROBLEM_FRONTMATTER_METADATA",
]
