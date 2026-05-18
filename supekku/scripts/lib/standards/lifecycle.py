"""Standard lifecycle status constants.

Enforcement-level statuses: 'required' (must comply) and 'default'
(recommended, opt-out allowed).  See DR-075 DEC-075-02.

OQ-137-02 sunset: ``STANDARD_STATUSES`` is a transition-window
re-export derived from
``frontmatter_metadata/standard.STANDARD_STATUS_ENUM_VALUES``.
"""

from __future__ import annotations

from supekku.scripts.lib.core.frontmatter_metadata.standard import (
  STANDARD_FRONTMATTER_METADATA,
)

# OQ-137-02 sunset: derived re-export.
STANDARD_STATUSES: frozenset[str] = frozenset(
  STANDARD_FRONTMATTER_METADATA.fields["status"].enum_values or []
)

__all__ = ["STANDARD_STATUSES"]
