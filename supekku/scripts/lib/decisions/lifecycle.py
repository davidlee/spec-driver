"""ADR/decision lifecycle status constants.

Values align with directory-based status inference in registry.py.
See DR-075 DEC-075-04.
"""

from __future__ import annotations

ADR_STATUSES: frozenset[str] = frozenset({
  "draft",
  "proposed",
  "accepted",
  "rejected",
  "deprecated",
  "superseded",
  "revision-required",
})

__all__ = ["ADR_STATUSES"]
