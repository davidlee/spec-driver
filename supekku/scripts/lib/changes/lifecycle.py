"""Change artifact lifecycle status constants.

For deltas, revisions, and audits — distinct from requirement lifecycle
statuses. After DE-137 IP-137-P01 the canonical inventory lives on the
per-kind ``FieldMetadata`` (``frontmatter_metadata/delta.py``); this
module is a thin transition-window re-export so legacy callers (which
read ``CHANGE_STATUSES`` directly) continue to work.

OQ-137-02 sunset: this re-export retires in a successor delta named at
the DE-136 umbrella close; until then the alias inventory + canonical
enum live on the metadata.

Use ``blocks.metadata.aliases.normalize_field`` for read-time
canonicalisation. ``CANONICAL_STATUS_MAP`` and the legacy
``normalize_status`` were retired (DEC-137-14 / DEC-137-23).
"""

from __future__ import annotations

from supekku.scripts.lib.core.frontmatter_metadata.delta import (
  DELTA_FRONTMATTER_METADATA,
)

ChangeStatus = str

# Status constants for callers that need named references (compat layer).
STATUS_DRAFT: ChangeStatus = "draft"
STATUS_PENDING: ChangeStatus = "pending"
STATUS_IN_PROGRESS: ChangeStatus = "in-progress"
STATUS_COMPLETED: ChangeStatus = "completed"
STATUS_DEFERRED: ChangeStatus = "deferred"

# OQ-137-02 sunset: derived re-export from per-kind metadata.
CHANGE_STATUSES: frozenset[ChangeStatus] = frozenset(
  DELTA_FRONTMATTER_METADATA.fields["status"].enum_values or []
)


__all__ = [
  "STATUS_COMPLETED",
  "STATUS_DEFERRED",
  "STATUS_DRAFT",
  "STATUS_IN_PROGRESS",
  "STATUS_PENDING",
  "CHANGE_STATUSES",
  "ChangeStatus",
]
