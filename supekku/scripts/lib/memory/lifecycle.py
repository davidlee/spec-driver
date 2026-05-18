"""Memory lifecycle status constants.

Trimmed set — 'deprecated' and 'obsolete' collapsed into 'archived'
and 'superseded'.  See DR-075 DEC-075-03.

OQ-137-02 sunset: ``MEMORY_STATUSES`` is a transition-window re-export
derived from ``frontmatter_metadata/memory.MEMORY_STATUS_ENUM_VALUES``.
"""

from __future__ import annotations

from supekku.scripts.lib.core.frontmatter_metadata.memory import (
  MEMORY_FRONTMATTER_METADATA,
)

# OQ-137-02 sunset: derived re-export.
MEMORY_STATUSES: frozenset[str] = frozenset(
  MEMORY_FRONTMATTER_METADATA.fields["status"].enum_values or []
)

__all__ = ["MEMORY_STATUSES"]
