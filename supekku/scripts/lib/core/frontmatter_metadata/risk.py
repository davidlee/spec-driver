"""Risk frontmatter metadata for kind: risk artifacts.

This module defines the metadata schema for risk frontmatter,
extending the base metadata with risk-specific fields.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

RISK_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.risk",
  description="Frontmatter fields for risks (kind: risk)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Risk-specific fields (all optional)
    "risk_kind": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["systemic", "operational", "delivery"],
      description="Type of risk exposure",
    ),
    "likelihood": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["low", "medium", "high"],
      description="Probability of occurrence",
    ),
    "impact": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["low", "medium", "high"],
      description="Severity of impact if risk occurs",
    ),
    "origin": FieldMetadata(
      type="string",
      required=False,
      pattern=r".+",
      description="Source artifact where risk was identified (e.g., ADR-012)",
    ),
    "controls": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string",
        pattern=r".+",
        description="Control or mitigation artifact ID",
      ),
      description="Control measures or mitigations in place",
    ),
  },
  examples=[
    # Minimal risk (base fields only)
    {
      "id": "RISK-001",
      "name": "Example Risk",
      "slug": "risk-example",
      "kind": "risk",
      "status": "identified",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete risk with all fields
    {
      "id": "RISK-SYS-042",
      "name": "Third-Party API Dependency Failure",
      "slug": "risk-api-dependency",
      "kind": "risk",
      "status": "mitigating",
      "lifecycle": "maintenance",
      "created": "2024-07-20",
      "updated": "2025-01-15",
      "owners": ["reliability-team"],
      "summary": (
        "External payment API may become unavailable, "
        "blocking checkout functionality"
      ),
      "tags": ["availability", "dependencies", "payment"],
      "risk_kind": "systemic",
      "likelihood": "medium",
      "impact": "high",
      "origin": "ADR-012",
      "controls": [
        "TS-015",
        "SPEC-201.FR-08",
      ],
      "relations": [
        {"type": "threatens", "target": "SPEC-004"},
        {"type": "tracked_by", "target": "ISSUE-567"},
      ],
    },
  ],
)

__all__ = [
  "RISK_FRONTMATTER_METADATA",
]
