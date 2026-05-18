"""Revision frontmatter metadata for kind: revision artifacts (DE-137 IP-137-P01).

Minimal status-only metadata so the derived `_kind_status("revision")`
view returns the canonical enum. Full revision frontmatter schema lands
in DE-142 (see DR-137 §5.2 / DEC-137-28).
"""

from __future__ import annotations

from dataclasses import replace

from supekku.scripts.lib.blocks.metadata import BlockMetadata

from .base import BASE_FRONTMATTER_METADATA
from .delta import DELTA_STATUS_ALIASES, DELTA_STATUS_ENUM_VALUES

# Revisions inherit the change-artefact status enum + alias set. DR-137 §5.2
# marks revision aliases "reserved for DE-142" — DE-142 owns any *additional*
# revision-specific aliases; the inherited change-status aliases stay here so
# legacy values continue to load tolerantly.
REVISION_STATUS_ENUM_VALUES: list[str] = DELTA_STATUS_ENUM_VALUES
REVISION_STATUS_ALIASES: dict[str, str] = DELTA_STATUS_ALIASES

REVISION_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.revision",
  description=(
    "Minimal frontmatter fields for revisions (kind: revision) — DE-137 ships"
    " only the status enum; full schema is DE-142 scope."
  ),
  fields={
    **BASE_FRONTMATTER_METADATA.fields,
    "status": replace(
      BASE_FRONTMATTER_METADATA.fields["status"],
      type="enum",
      pattern=None,
      enum_values=REVISION_STATUS_ENUM_VALUES,
      aliases=REVISION_STATUS_ALIASES,
    ),
  },
  examples=[
    {
      "id": "RE-001",
      "name": "Example Revision",
      "slug": "revision-example",
      "kind": "revision",
      "status": "draft",
      "created": "2026-01-15",
      "updated": "2026-01-15",
    },
  ],
)

__all__ = [
  "REVISION_FRONTMATTER_METADATA",
  "REVISION_STATUS_ALIASES",
  "REVISION_STATUS_ENUM_VALUES",
]
