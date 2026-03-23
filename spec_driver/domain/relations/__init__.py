"""Domain relations — cross-artifact reference discovery and traversal.

This package provides the sanctioned location for cross-artifact
relationship logic: reference queries, graph construction, frontmatter
relation management, and backlink computation.

Design reference: DR-125 §3.2, §3.3.
"""

from __future__ import annotations

from .backlinks import BacklinkTarget, build_backlinks, build_backlinks_multi
from .graph import (
  GraphEdge,
  ReferenceGraph,
  build_reference_graph_from_artifacts,
  find_unresolved_references,
  query_forward,
  query_inverse,
  query_neighbourhood,
)
from .manager import add_relation, list_relations, remove_relation
from .query import (
  ReferenceHit,
  RelationQueryable,
  collect_references,
  collect_reverse_reference_targets,
  find_by_relation,
  find_related_to,
  matches_related_to,
  matches_relation,
  partition_by_reverse_references,
)

__all__ = [
  "BacklinkTarget",
  "GraphEdge",
  "ReferenceGraph",
  "ReferenceHit",
  "RelationQueryable",
  "add_relation",
  "build_backlinks",
  "build_backlinks_multi",
  "build_reference_graph_from_artifacts",
  "collect_references",
  "collect_reverse_reference_targets",
  "find_by_relation",
  "find_related_to",
  "find_unresolved_references",
  "list_relations",
  "matches_related_to",
  "matches_relation",
  "partition_by_reverse_references",
  "query_forward",
  "query_inverse",
  "query_neighbourhood",
  "remove_relation",
]
