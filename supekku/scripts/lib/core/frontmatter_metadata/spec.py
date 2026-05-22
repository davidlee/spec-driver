"""Spec frontmatter metadata for kind: spec artifacts.

This module defines the metadata schema for specification frontmatter,
extending the base metadata with spec-specific fields.
"""

from __future__ import annotations

from dataclasses import replace

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata
from supekku.scripts.lib.blocks.metadata.schema import ToleratedAlias

from .base import BASE_FRONTMATTER_METADATA

SPEC_STATUS_ENUM_VALUES: list[str] = [
  "active",
  "archived",
  "deprecated",
  "draft",
  "stub",
]

SPEC_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.spec",
  description="Frontmatter fields for specifications (kind: spec)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # DE-137 IP-137-P01: status enum promotion.
    # DE-139: taxonomy strict; FM fields moved to blocks or cut.
    "status": replace(
      BASE_FRONTMATTER_METADATA.fields["status"],
      type="enum",
      pattern=None,
      enum_values=SPEC_STATUS_ENUM_VALUES,
    ),
    # Spec-specific fields (all optional)
    "category": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["unit", "assembly"],
      tolerated_aliases={
        "unknown": ToleratedAlias(
          canonical="unknown",
          sunset_after="DE-139 taxonomy reconciliation",
          rationale=("Sweep assigns unknown; human reconciliation required"),
        ),
      },
      description=(
        "Spec taxonomy category. "
        "'unit' (1:1 with a code unit) or 'assembly' (cross-unit). "
        "See ADR-003."
      ),
    ),
    "c4_level": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["system", "container", "component", "code", "interaction"],
      tolerated_aliases={
        "unknown": ToleratedAlias(
          canonical="unknown",
          sunset_after="DE-139 taxonomy reconciliation",
          rationale=("Sweep assigns unknown; human reconciliation required"),
        ),
      },
      description="C4 architecture granularity level",
    ),
    "responsibilities": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Responsibility statement"
      ),
      description="Explicit services or behaviors this spec promises",
    ),
    "guiding_principles": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Guiding principle statement"
      ),
      description="Enduring heuristics that shape solutions",
    ),
    "assumptions": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Assumption statement"
      ),
      description="Beliefs that need validation",
    ),
    "constraints": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Constraint statement"
      ),
      description="Hard requirements or limitations",
    ),
    "sources": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Source code implementation tracked by this spec",
        properties={
          "language": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["go", "python", "typescript"],
            description="Implementation language",
          ),
          "identifier": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Source code path or identifier",
          ),
          "module": FieldMetadata(
            type="string",
            required=False,
            description="Dotted module name (Python-specific)",
          ),
          "variants": FieldMetadata(
            type="array",
            required=True,
            min_items=1,
            items=FieldMetadata(
              type="object",
              description="Documentation variant",
              properties={
                "name": FieldMetadata(
                  type="string",
                  required=True,
                  pattern=r".+",
                  description="Variant name (e.g., api, implementation)",
                ),
                "path": FieldMetadata(
                  type="string",
                  required=True,
                  pattern=r".+",
                  description="Documentation file path",
                ),
              },
            ),
            description="Documentation perspectives for this source",
          ),
        },
      ),
      description="Multi-language source code tracking",
    ),
  },
  examples=[
    # Minimal spec (base fields only)
    {
      "id": "SPEC-001",
      "name": "Example Specification",
      "slug": "example-spec",
      "kind": "spec",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete spec with all fields
    {
      "id": "SPEC-101",
      "name": "Content Binding Specification",
      "slug": "spec-content-binding",
      "kind": "spec",
      "status": "approved",
      "lifecycle": "implementation",
      "created": "2024-06-08",
      "updated": "2025-01-15",
      "owners": ["alice"],
      "auditers": ["bob"],
      "summary": "Defines canonical content binding lifecycle and schema enforcement",
      "c4_level": "container",
      "responsibilities": [
        "canonical content binding lifecycle",
        "expose schema enforcement operations to other containers",
      ],
      "guiding_principles": ["Maintain block identity end-to-end"],
      "assumptions": ["Agents will reconcile markdown without manual edits"],
      "constraints": ["Must preserve block UUIDs during edits"],
      "sources": [
        {
          "language": "python",
          "identifier": "supekku/scripts/lib/workspace.py",
          "module": "supekku.scripts.lib.workspace",
          "variants": [
            {"name": "api", "path": "contracts/python/workspace-api.md"},
            {
              "name": "implementation",
              "path": "contracts/python/workspace-implementation.md",
            },
          ],
        },
        {
          "language": "go",
          "identifier": "internal/application/services/git",
          "variants": [
            {"name": "public", "path": "contracts/go/git-service-public.md"},
            {"name": "internal", "path": "contracts/go/git-service-internal.md"},
          ],
        },
      ],
      "relations": [
        {"type": "depends_on", "target": "SPEC-004"},
      ],
    },
  ],
)

__all__ = [
  "SPEC_FRONTMATTER_METADATA",
]
