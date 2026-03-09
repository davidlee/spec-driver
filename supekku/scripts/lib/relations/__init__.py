"""Relations domain - managing relationships between artifacts.

This package handles artifact relationships, references, and queries.
"""

from __future__ import annotations

from .query import (
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
