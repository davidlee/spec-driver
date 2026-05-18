"""Specification lifecycle status constants.

Covers both tech specs (SPEC-xxx) and product specs (PROD-xxx).
See DR-075 DEC-075-01.

OQ-137-02 sunset: ``SPEC_STATUSES`` is a transition-window re-export
derived from ``frontmatter_metadata/spec.SPEC_STATUS_ENUM_VALUES``.
"""

from __future__ import annotations

from supekku.scripts.lib.core.frontmatter_metadata.spec import (
  SPEC_FRONTMATTER_METADATA,
)

# OQ-137-02 sunset: derived re-export.
SPEC_STATUSES: frozenset[str] = frozenset(
  SPEC_FRONTMATTER_METADATA.fields["status"].enum_values or []
)

__all__ = ["SPEC_STATUSES"]
