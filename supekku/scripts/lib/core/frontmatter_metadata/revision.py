"""Revision frontmatter metadata for kind: revision artifacts (DE-142 P02).

Completes the DE-137 stub to the **narrow** DR-142 §5 shape (DEC-CONSULT-01,
user-approved 2026-05-29): Base 7 + ``relations`` + ``tags`` +
``ext_id``/``ext_url``. Unlike audit/delta (which keep the full BASE spread),
revisions deliberately OMIT ``lifecycle``/``auditers``/``source``/``owners``/
``summary`` and the hand-rolled scope keys — those reject under strict at the
P04 flip. Verified zero corpus lossage: no revision in the 42-record corpus
carries any omitted key.

``applies_to`` is derived from the ``supekku:revision.change@v1`` block at load
(DEC-142-05 / DEC-138-10), never stored in frontmatter here.

Note: the shared BASE ``kind`` enum omits ``revision`` (it lists
``design_revision`` for DR-* artefacts, not RE-* revisions), so this class pins
``kind`` to ``["revision"]`` locally rather than widening the shared enum.
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

_BASE = BASE_FRONTMATTER_METADATA.fields

REVISION_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.revision",
  description="Frontmatter fields for revisions (kind: revision) — narrow DR-142 §5",
  # Narrow field set (DEC-CONSULT-01): explicit picks from BASE, NOT a full
  # ``**BASE.fields`` spread — that would re-admit the universal-cut keys.
  fields={
    "id": _BASE["id"],
    "name": _BASE["name"],
    "slug": _BASE["slug"],
    # BASE enum omits "revision"; pin it for this class (see module docstring).
    "kind": replace(_BASE["kind"], enum_values=["revision"]),
    "status": replace(
      _BASE["status"],
      type="enum",
      pattern=None,
      enum_values=REVISION_STATUS_ENUM_VALUES,
      aliases=REVISION_STATUS_ALIASES,
    ),
    "created": _BASE["created"],
    "updated": _BASE["updated"],
    "relations": _BASE["relations"],
    "tags": _BASE["tags"],
    "ext_id": _BASE["ext_id"],
    "ext_url": _BASE["ext_url"],
  },
  examples=[
    # Minimal revision
    {
      "id": "RE-001",
      "name": "Example Revision",
      "slug": "revision-example",
      "kind": "revision",
      "status": "draft",
      "created": "2026-01-15",
      "updated": "2026-01-15",
    },
    # Revision with relations + tags (declared-valid fields only)
    {
      "id": "RE-042",
      "name": "Delta DE-138 completion",
      "slug": "delta-de-138-completion",
      "kind": "revision",
      "status": "completed",
      "created": "2026-05-21",
      "updated": "2026-05-21",
      "relations": [{"type": "implements", "target": "DE-138"}],
      "tags": ["metadata"],
    },
  ],
)

__all__ = [
  "REVISION_FRONTMATTER_METADATA",
  "REVISION_STATUS_ALIASES",
  "REVISION_STATUS_ENUM_VALUES",
]
