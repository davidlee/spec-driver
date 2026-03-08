"""Memory lifecycle status constants.

Trimmed set — 'deprecated' and 'obsolete' collapsed into 'archived'
and 'superseded'.  See DR-075 DEC-075-03.
"""

from __future__ import annotations

MEMORY_STATUSES: frozenset[str] = frozenset(
  {
    "draft",
    "active",
    "review",
    "superseded",
    "archived",
  }
)

__all__ = ["MEMORY_STATUSES"]
