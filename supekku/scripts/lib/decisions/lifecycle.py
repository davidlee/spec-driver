"""ADR/decision lifecycle status constants.

Values align with directory-based status inference in registry.py.
See DR-075 DEC-075-04.

OQ-137-02 sunset: ``ADR_STATUSES`` is a transition-window re-export
derived from ``frontmatter_metadata/adr.ADR_STATUS_ENUM_VALUES``.
"""

from __future__ import annotations

from supekku.scripts.lib.core.frontmatter_metadata.adr import (
  ADR_FRONTMATTER_METADATA,
)

# OQ-137-02 sunset: derived re-export.
ADR_STATUSES: frozenset[str] = frozenset(
  ADR_FRONTMATTER_METADATA.fields["status"].enum_values or []
)

__all__ = ["ADR_STATUSES"]
