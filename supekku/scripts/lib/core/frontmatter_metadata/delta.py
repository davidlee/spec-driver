"""Delta frontmatter metadata for kind: delta artifacts.

This module defines the metadata schema for delta frontmatter,
extending the base metadata with delta-specific fields.
"""

from __future__ import annotations

from dataclasses import replace

from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata

from .base import BASE_FRONTMATTER_METADATA

# Canonical change-artefact status enum. This is the source of truth after
# DE-137; ``supekku/scripts/lib/changes/lifecycle.py`` re-exports the
# frozenset from this list (OQ-137-02 sunset target).
DELTA_STATUS_ENUM_VALUES: list[str] = [
  "completed",
  "deferred",
  "draft",
  "in-progress",
  "pending",
]

# Delta-status field-VALUE aliases (DR-137 §5.2 / DEC-137-23 — corpus matrix).
DELTA_STATUS_ALIASES: dict[str, str] = {
  "complete": "completed",
  "active": "in-progress",
  "done": "completed",
  "in_progress": "in-progress",
}

# -- Audit gate constants (DEC-079-003, DEC-079-010) --

AUDIT_GATE_AUTO = "auto"
AUDIT_GATE_REQUIRED = "required"
AUDIT_GATE_EXEMPT = "exempt"

AUDIT_GATE_VALUES: set[str] = {
  AUDIT_GATE_AUTO,
  AUDIT_GATE_REQUIRED,
  AUDIT_GATE_EXEMPT,
}

DELTA_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.delta",
  description="Frontmatter fields for deltas (kind: delta)",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    # DE-137 IP-137-P01: status promoted to enum, with legacy aliases (F-30).
    "status": replace(
      BASE_FRONTMATTER_METADATA.fields["status"],
      type="enum",
      pattern=None,
      enum_values=DELTA_STATUS_ENUM_VALUES,
      aliases=DELTA_STATUS_ALIASES,
    ),
    # Base field persistence overrides for delta compaction
    "lifecycle": replace(
      BASE_FRONTMATTER_METADATA.fields["lifecycle"],
      persistence="optional",
    ),
    "owners": replace(
      BASE_FRONTMATTER_METADATA.fields["owners"],
      persistence="optional",
      default_value=[],
    ),
    "auditers": replace(
      BASE_FRONTMATTER_METADATA.fields["auditers"],
      persistence="optional",
      default_value=[],
    ),
    "source": replace(
      BASE_FRONTMATTER_METADATA.fields["source"],
      persistence="optional",
    ),
    "summary": replace(
      BASE_FRONTMATTER_METADATA.fields["summary"],
      persistence="optional",
    ),
    "tags": replace(
      BASE_FRONTMATTER_METADATA.fields["tags"],
      persistence="optional",
      default_value=[],
    ),
    "relations": replace(
      BASE_FRONTMATTER_METADATA.fields["relations"],
      persistence="default-omit",
      default_value=[],
    ),
    # Delta-specific fields (all optional)
    # NOTE (DE-138 P01): applies_to / context_inputs / risk_register /
    # outcome_summary declarations removed. applies_to is derived at load
    # from the supekku:delta.relationships@v1 block (DR-138 §6.1); the
    # other three move to dedicated blocks / body section (DR-138 §3.1).
    # FM keys remain tolerated on read until P03 sweep; strict-flip in P04
    # rejects them via validator layer (DEC-138-10).
    "audit_gate": FieldMetadata(
      type="enum",
      required=False,
      enum_values=sorted(AUDIT_GATE_VALUES),
      description=(
        "Audit gating for delta completion: auto resolves from applies_to.requirements"
      ),
      persistence="default-omit",
      default_value=AUDIT_GATE_AUTO,
    ),
    "audit_gate_rationale": FieldMetadata(
      type="string",
      required=False,
      description="Required when audit_gate is exempt",
      persistence="optional",
    ),
  },
  examples=[
    # Minimal delta (base fields only)
    {
      "id": "DE-001",
      "name": "Example Delta",
      "slug": "delta-example",
      "kind": "delta",
      "status": "draft",
      "created": "2025-01-15",
      "updated": "2025-01-15",
    },
    # Complete delta — DE-138 P01: applies_to/context_inputs/risk_register/
    # outcome_summary now live in dedicated blocks (DR-138 §3.1) rather than FM.
    {
      "id": "DE-021",
      "name": "Content Binding Schema Migration",
      "slug": "delta-content-binding-migration",
      "kind": "delta",
      "status": "in-progress",
      "lifecycle": "implementation",
      "created": "2024-06-08",
      "updated": "2025-01-15",
      "owners": ["alice"],
      "summary": "Migrate content binding to event sourcing architecture",
      "relations": [
        {"type": "implements", "target": "SPEC-101"},
        {"type": "depends_on", "target": "RC-010"},
      ],
    },
  ],
)

__all__ = [
  "AUDIT_GATE_AUTO",
  "AUDIT_GATE_EXEMPT",
  "AUDIT_GATE_REQUIRED",
  "AUDIT_GATE_VALUES",
  "DELTA_FRONTMATTER_METADATA",
]
