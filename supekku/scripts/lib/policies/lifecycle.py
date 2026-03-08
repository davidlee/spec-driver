"""Policy lifecycle status constants.

Enforcement-level statuses: 'required' is the active state for policies.
See DR-075 DEC-075-02.
"""

from __future__ import annotations

POLICY_STATUSES: frozenset[str] = frozenset(
  {
    "draft",
    "required",
    "deprecated",
  }
)

__all__ = ["POLICY_STATUSES"]
