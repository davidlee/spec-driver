"""Cross-artifact reference graph builder and query API.

On-demand graph computation from registry state. No persisted file —
the graph is a pure function of workspace registries and
``collect_references``.

Design reference: DR-097.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from supekku.scripts.lib.core.artifact_ids import normalize_artifact_id
from supekku.scripts.lib.relations.query import ReferenceHit, collect_references

if TYPE_CHECKING:
  from supekku.scripts.lib.workspace import Workspace


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

      edges.append(GraphEdge(
        source=art_id,
        target=target,
        source_slot=hit.source,
        detail=hit.detail,
      ))

  graph = ReferenceGraph(
    nodes=nodes,
    edges=edges,
    diagnostics=diagnostics,
  )
  _build_indices(graph)
  return graph


def build_reference_graph(workspace: Workspace) -> ReferenceGraph:
  """Build a reference graph from all workspace registries.

  Iterates all registries, calls ``collect_references`` per artifact,
  normalizes edge targets, and builds forward/inverse indices.

  Args:
    workspace: Workspace instance with access to all registries.

  Returns:
    ReferenceGraph computed from current workspace state.
  """
  artifacts = _collect_all_artifacts(workspace)
  return build_reference_graph_from_artifacts(artifacts)


def _collect_all_artifacts(
  workspace: Workspace,
) -> list[tuple[str, str, Any]]:
  """Collect (id, kind, artifact_obj) triples from all registries.

  Uses Workspace properties where available, constructs registries
  directly for domains not yet exposed on Workspace (memory, backlog,
  drift).
  """
  artifacts: list[tuple[str, str, Any]] = []
  _collect_workspace_artifacts(workspace, artifacts)
  _collect_standalone_registry_artifacts(workspace.root, artifacts)
  return artifacts


def _collect_workspace_artifacts(
  workspace: Workspace,
  out: list[tuple[str, str, Any]],
) -> None:
  """Collect artifacts from registries exposed as Workspace properties."""
  # Decisions
  for dec_id, dec in workspace.decisions.collect().items():
    out.append((dec_id, "adr", dec))

  # Specs
  for spec in workspace.specs.all_specs():
    out.append((spec.id, "spec", spec))

  # Changes (delta, revision, audit)
  for registry in (
    workspace.delta_registry,
    workspace.revision_registry,
    workspace.audit_registry,
  ):
    for art_id, art in registry.collect().items():
      out.append((art_id, registry.kind, art))

  # Requirements
  for req_id, req in workspace.requirements.records.items():
    out.append((req_id, "requirement", req))

  # Policies
  for pol_id, pol in workspace.policies.collect().items():
    out.append((pol_id, "policy", pol))

  # Standards
  for std_id, std in workspace.standards.collect().items():
    out.append((std_id, "standard", std))


def _collect_standalone_registry_artifacts(
  root: Any,
  out: list[tuple[str, str, Any]],
) -> None:
  """Collect artifacts from registries not exposed on Workspace."""
  from supekku.scripts.lib.backlog.registry import BacklogRegistry  # noqa: PLC0415  # pylint: disable=import-outside-toplevel
  from supekku.scripts.lib.drift.registry import DriftLedgerRegistry  # noqa: PLC0415  # pylint: disable=import-outside-toplevel
  from supekku.scripts.lib.memory.registry import MemoryRegistry  # noqa: PLC0415  # pylint: disable=import-outside-toplevel

  for mem_id, mem in MemoryRegistry(root=root).collect().items():
    out.append((mem_id, "memory", mem))

  for item_id, item in BacklogRegistry(root=root).collect().items():
    out.append((item_id, item.kind, item))

  for dl_id, dl in DriftLedgerRegistry(root=root).collect().items():
    out.append((dl_id, "drift_ledger", dl))


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
  "build_reference_graph",
  "build_reference_graph_from_artifacts",
  "find_unresolved_references",
  "query_forward",
  "query_inverse",
  "query_neighbourhood",
]
