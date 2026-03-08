"""Specification lifecycle status constants.

Covers both tech specs (SPEC-xxx) and product specs (PROD-xxx).
See DR-075 DEC-075-01.
"""

from __future__ import annotations

SPEC_STATUSES: frozenset[str] = frozenset({
  "stub",
  "draft",
  "active",
  "deprecated",
  "archived",
})

__all__ = ["SPEC_STATUSES"]
