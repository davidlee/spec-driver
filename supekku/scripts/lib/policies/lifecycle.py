"""Policy lifecycle status constants.

Enforcement-level statuses: 'required' is the active state for policies.
See DR-075 DEC-075-02.

OQ-137-02 sunset: ``POLICY_STATUSES`` is a transition-window re-export
derived from ``frontmatter_metadata/policy.POLICY_STATUS_ENUM_VALUES``.
"""

from __future__ import annotations

from supekku.scripts.lib.core.frontmatter_metadata.policy import (
  POLICY_FRONTMATTER_METADATA,
)

# OQ-137-02 sunset: derived re-export.
POLICY_STATUSES: frozenset[str] = frozenset(
  POLICY_FRONTMATTER_METADATA.fields["status"].enum_values or []
)

__all__ = ["POLICY_STATUSES"]
