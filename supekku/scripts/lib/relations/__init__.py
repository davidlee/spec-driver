"""Relations domain — re-export shim.

Canonical location: ``spec_driver.domain.relations``.
"""

from __future__ import annotations

# ruff: noqa: F401
from spec_driver.domain.relations.query import (
  ReferenceHit,
  RelationQueryable,
  collect_references,
  find_by_relation,
  find_related_to,
  matches_related_to,
  matches_relation,
)

__all__: list[str] = [
  "ReferenceHit",
  "RelationQueryable",
  "collect_references",
  "find_by_relation",
  "find_related_to",
  "matches_related_to",
  "matches_relation",
]
