"""Cross-artifact reference graph model and query API.

Pure graph construction from pre-collected artifact triples. No I/O,
no workspace dependency — the graph is a pure function of its inputs.

Workspace-dependent artifact collection remains in the legacy location
(``supekku.scripts.lib.relations.graph``) until orchestration boundaries
are established.

Design reference: DR-097.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from supekku.scripts.lib.core.artifact_ids import normalize_artifact_id

from .query import ReferenceHit, collect_references


@dataclass(frozen=True)
class GraphEdge:
  """A directed reference edge in the artifact graph.

  Attributes:
    source: Source artifact ID.
    target: Target artifact ID (normalized).
    source_slot: Provenance slot (e.g. "relation", "applies_to").
    detail: Slot-specific qualifier (relation type, field name, etc.).
  """

  source: str
  target: str
  source_slot: str
  detail: str


@dataclass
class ReferenceGraph:
  """Cross-artifact reference graph computed from registry state.

  Nodes are artifact IDs mapped to their kind. Edges are forward
  references extracted by ``collect_references``, with targets
  normalized against the node index.
  """

  nodes: dict[str, str]
  edges: list[GraphEdge]
  diagnostics: list[str] = field(default_factory=list)
  forward_index: dict[str, list[GraphEdge]] = field(
    default_factory=lambda: defaultdict(list),
    repr=False,
  )
  inverse_index: dict[str, list[GraphEdge]] = field(
    default_factory=lambda: defaultdict(list),
    repr=False,
  )


def _build_indices(graph: ReferenceGraph) -> None:
  """Populate forward and inverse lookup indices from edges."""
  graph.forward_index.clear()
  graph.inverse_index.clear()
  for edge in graph.edges:
    graph.forward_index[edge.source].append(edge)
    graph.inverse_index[edge.target].append(edge)


def _hit_to_edge(source_id: str, hit: ReferenceHit) -> GraphEdge:
  """Convert a ReferenceHit to a GraphEdge."""
  return GraphEdge(
    source=source_id,
    target=hit.target,
    source_slot=hit.source,
    detail=hit.detail,
  )


def build_reference_graph_from_artifacts(
  artifacts: list[tuple[str, str, Any]],
) -> ReferenceGraph:
  """Build a reference graph from pre-collected artifact triples.

  This is the pure core — no I/O. Accepts ``(id, kind, obj)`` triples
  and produces a ``ReferenceGraph``.

  Args:
    artifacts: List of (artifact_id, kind, artifact_object) triples.

  Returns:
    ReferenceGraph with nodes, edges, forward/inverse indices,
    and normalization diagnostics.
  """
  nodes: dict[str, str] = {}
  edges: list[GraphEdge] = []
  diagnostics: list[str] = []

  # Collect nodes
  for art_id, kind, _ in artifacts:
    nodes[art_id] = kind

  known_ids = frozenset(nodes)

  # Collect edges with normalization
  for art_id, _, obj in artifacts:
    hits = collect_references(obj)
    for hit in hits:
      target = hit.target
      # Normalize target against known IDs
      if target not in known_ids:
        result = normalize_artifact_id(target, known_ids)
        if result.canonical is not None:
          target = result.canonical
          if result.diagnostic:
            diagnostics.append(result.diagnostic)

      edges.append(
        GraphEdge(
          source=art_id,
          target=target,
          source_slot=hit.source,
          detail=hit.detail,
        )
      )

  graph = ReferenceGraph(
    nodes=nodes,
    edges=edges,
    diagnostics=diagnostics,
  )
  _build_indices(graph)
  return graph


# ── Query functions ──────────────────────────────────────────


def query_forward(graph: ReferenceGraph, artifact_id: str) -> list[GraphEdge]:
  """Return edges where *artifact_id* is the source.

  Args:
    graph: Reference graph to query.
    artifact_id: Source artifact ID.

  Returns:
    List of GraphEdge with this ID as source. Empty if not found.
  """
  return list(graph.forward_index.get(artifact_id, []))


def query_inverse(graph: ReferenceGraph, artifact_id: str) -> list[GraphEdge]:
  """Return edges where *artifact_id* is the target.

  Args:
    graph: Reference graph to query.
    artifact_id: Target artifact ID.

  Returns:
    List of GraphEdge with this ID as target. Empty if not found.
  """
  return list(graph.inverse_index.get(artifact_id, []))


def query_neighbourhood(
  graph: ReferenceGraph,
  artifact_id: str,
  direction: str = "both",
) -> dict[str, list[GraphEdge]]:
  """Return grouped edges for an artifact's reference neighbourhood.

  Args:
    graph: Reference graph to query.
    artifact_id: Artifact ID to query.
    direction: ``"forward"``, ``"inverse"``, or ``"both"`` (default).

  Returns:
    Dict with ``"forward"`` and/or ``"inverse"`` keys mapping to edge lists.
  """
  result: dict[str, list[GraphEdge]] = {}
  if direction in ("forward", "both"):
    result["forward"] = query_forward(graph, artifact_id)
  if direction in ("inverse", "both"):
    result["inverse"] = query_inverse(graph, artifact_id)
  return result


def find_unresolved_references(graph: ReferenceGraph) -> list[GraphEdge]:
  """Return edges whose target is not in graph.nodes.

  Args:
    graph: Reference graph to check.

  Returns:
    List of GraphEdge with unresolved (unknown) targets.
  """
  return [edge for edge in graph.edges if edge.target not in graph.nodes]


__all__ = [
  "GraphEdge",
  "ReferenceGraph",
  "build_reference_graph_from_artifacts",
  "find_unresolved_references",
  "query_forward",
  "query_inverse",
  "query_neighbourhood",
]
