"""ADR frontmatter metadata for kind: adr artifacts (DE-137 IP-137-P01).

Minimal status-only metadata so the derived `_kind_status("adr")` view
returns the canonical enum. Full ADR frontmatter schema lands in a
future per-artefact delta (see DR-137 §5.2).
"""

from __future__ import annotations

from dataclasses import replace

from supekku.scripts.lib.blocks.metadata import BlockMetadata

from .base import BASE_FRONTMATTER_METADATA

ADR_STATUS_ENUM_VALUES: list[str] = [
  "accepted",
  "deprecated",
  "draft",
  "proposed",
  "rejected",
  "revision-required",
  "superseded",
]

ADR_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.adr",
  description=(
    "Minimal frontmatter fields for ADRs (kind: adr) — DE-137 ships only the"
    " status enum; full schema is a future-delta scope."
  ),
  fields={
    **BASE_FRONTMATTER_METADATA.fields,
    "status": replace(
      BASE_FRONTMATTER_METADATA.fields["status"],
      type="enum",
      pattern=None,
      enum_values=ADR_STATUS_ENUM_VALUES,
    ),
  },
  examples=[
    {
      "id": "ADR-001",
      "name": "Example Decision",
      "slug": "adr-example",
      "kind": "adr",
      "status": "draft",
      "created": "2026-01-15",
      "updated": "2026-01-15",
    },
  ],
)

__all__ = [
  "ADR_FRONTMATTER_METADATA",
  "ADR_STATUS_ENUM_VALUES",
]
