"""Spec frontmatter metadata for kind: spec artifacts.

This module defines the metadata schema for specification frontmatter,
extending the base metadata with spec-specific fields.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

SPEC_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.spec",
  description="Frontmatter fields for specifications (kind: spec)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # Spec-specific fields (all optional)
    "c4_level": FieldMetadata(
      type="enum",
      required=False,
      enum_values=["system", "container", "component", "code", "interaction"],
      description="C4 architecture granularity level",
    ),
    "scope": FieldMetadata(
      type="string",
      required=False,
      description="Statement of boundaries and responsibilities",
    ),
    "concerns": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="A concern this specification addresses",
        properties={
          "name": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Concern identifier",
          ),
          "description": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="What this concern addresses",
          ),
        },
      ),
      description="Enduring problem spaces or quality dimensions",
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
    "hypotheses": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="A hypothesis to be validated",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Hypothesis ID (e.g., SPEC-101.HYP-01)",
          ),
          "statement": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="The hypothesis statement",
          ),
          "status": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["proposed", "validated", "invalid"],
            description="Validation status",
          ),
        },
      ),
      description="Hypotheses tracking belief evolution",
    ),
    "decisions": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="An architectural or design decision",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Decision ID (e.g., SPEC-101.DEC-01)",
          ),
          "summary": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Short decision summary",
          ),
          "rationale": FieldMetadata(
            type="string",
            required=False,
            description="Why this decision was made",
          ),
        },
      ),
      description="Key architectural or design decisions",
    ),
    "constraints": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Constraint statement"
      ),
      description="Hard requirements or limitations",
    ),
    "verification_strategy": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        description="Verification approach entry",
        properties={
          "type": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="Verification artifact ID (e.g., VT-210)",
          ),
          "description": FieldMetadata(
            type="string",
            required=True,
            pattern=r".+",
            description="What is being verified",
          ),
        },
      ),
      description="Strategy for verifying this specification",
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
    "packages": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="string", pattern=r".+", description="Package path"
      ),
      description="Legacy Go package tracking (deprecated, use sources instead)",
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
      "scope": "Maintain canonical content binding state and expose schema operations",
      "concerns": [
        {
          "name": "content synchronisation",
          "description": "Maintain canonical content binding state",
        }
      ],
      "responsibilities": [
        "canonical content binding lifecycle",
        "expose schema enforcement operations to other containers",
      ],
      "guiding_principles": ["Maintain block identity end-to-end"],
      "assumptions": ["Agents will reconcile markdown without manual edits"],
      "hypotheses": [
        {
          "id": "SPEC-101.HYP-01",
          "statement": "Rich diffing will reduce merge conflicts",
          "status": "proposed",
        }
      ],
      "decisions": [
        {
          "id": "SPEC-101.DEC-01",
          "summary": "Adopt optimistic locking for schema updates",
          "rationale": "Based on RC-010 findings",
        }
      ],
      "constraints": ["Must preserve block UUIDs during edits"],
      "verification_strategy": [
        {"type": "VT-210", "description": "End-to-end sync tests remain green"}
      ],
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
      "packages": ["internal/application/services/git"],  # Legacy
      "relations": [
        {"type": "depends_on", "target": "SPEC-004"},
      ],
    },
  ],
)

__all__ = [
  "SPEC_FRONTMATTER_METADATA",
]
