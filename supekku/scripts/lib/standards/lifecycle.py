"""Standard lifecycle status constants.

Enforcement-level statuses: 'required' (must comply) and 'default'
(recommended, opt-out allowed).  See DR-075 DEC-075-02.
"""

from __future__ import annotations

STANDARD_STATUSES: frozenset[str] = frozenset({
  "draft",
  "required",
  "default",
  "deprecated",
})

__all__ = ["STANDARD_STATUSES"]
