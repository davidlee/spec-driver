"""Product frontmatter metadata for kind: prod artifacts.

This module defines the metadata schema for product specification frontmatter,
extending the base metadata with product-specific fields.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

PROD_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.prod",
  description="Frontmatter fields for product specifications (kind: prod)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Product-specific fields (all optional)
    "scope": FieldMetadata(
      type="string",
      required=False,
      description="Statement of user or market intent",
    ),
    "problems": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r".+",
        description="Problem ID (e.g., PROB-012)",
      ),
      description="Referenced problem statements",
    ),
    "value_proposition": FieldMetadata(
      type="string",
      required=False,
      description="Why solving this matters",
    ),
    "guiding_principles": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r".+",
        description="Guiding principle statement",
      ),
      description="Enduring heuristics for product decisions",
    ),
    "assumptions": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r".+",
        description="Assumption statement",
      ),
      description="Beliefs that need validation",
    ),
    "hypotheses": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Product hypothesis to validate",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Hypothesis ID (e.g., PROD-020.HYP-01)",
          ),
          "statement": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Hypothesis statement",
          ),
          "status": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["proposed", "validated", "invalid"],
            description="Validation status",
          ),
        },
      ),
      description="Hypotheses tracking product belief evolution",
    ),
    "decisions": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Product decision",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Decision ID (e.g., PROD-020.DEC-01)",
          ),
          "summary": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Decision summary",
          ),
        },
      ),
      description="Key product decisions",
    ),
    "product_requirements": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Product requirement",
        properties={
          "code": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Requirement code (e.g., PROD-020.FR-01)",
          ),
          "statement": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Requirement statement",
          ),
        },
      ),
      description="Product requirements",
    ),
    "verification_strategy": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Verification approach (research or metrics)",
        properties={
          "research": FieldMetadata(
            type="string",
            required=False,
            pattern=r".+",
            description="Research ID (e.g., UX-023)",
          ),
          "metric": FieldMetadata(
            type="string",
            required=False,
            pattern=r".+",
            description="Metric ID (e.g., sync_latency_p99)",
          ),
        },
      ),
      description="Verification strategy (research or metrics)",
    ),
  },
  examples=[
    # Minimal product spec (base fields only)
    {
      "id": "PROD-001",
      "name": "Example Product Spec",
      "slug": "example-product",
      "kind": "prod",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete product spec with all fields
    {
      "id": "PROD-020",
      "name": "Sync Performance Product Spec",
      "slug": "prod-sync-performance",
      "kind": "prod",
      "status": "approved",
      "lifecycle": "implementation",
      "created": "2024-06-01",
      "updated": "2025-01-15",
      "owners": ["product-team"],
      "summary": "Improve sync speed to reduce user churn",
      "scope": "Reduce sync latency for all sync operations",
      "problems": ["PROB-012"],
      "value_proposition": "Faster sync improves user retention",
      "guiding_principles": ["Resolve user pain without sacrificing offline mode"],
      "assumptions": ["Users are comfortable with 5s sync delays"],
      "hypotheses": [
        {
          "id": "PROD-020.HYP-01",
          "statement": "Improving sync speed will reduce churn",
          "status": "proposed",
        }
      ],
      "decisions": [
        {
          "id": "PROD-020.DEC-01",
          "summary": "Prioritise sync speed over new features this quarter",
        }
      ],
      "product_requirements": [
        {
          "code": "PROD-020.FR-01",
          "statement": "Sync completes within 5s",
        },
        {
          "code": "PROD-020.NF-01",
          "statement": "Sync success rate ≥ 99%",
        },
      ],
      "verification_strategy": [
        {"research": "UX-023"},
        {"metric": "sync_latency_p99"},
      ],
      "relations": [
        {"type": "relates_to", "target": "PROB-012"},
      ],
    },
  ],
)

__all__ = [
  "PROD_FRONTMATTER_METADATA",
]
