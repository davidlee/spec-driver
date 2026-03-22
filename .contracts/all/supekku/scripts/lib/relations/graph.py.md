# supekku.scripts.lib.relations.graph

Cross-artifact reference graph builder and query API.

On-demand graph computation from registry state. No persisted file —
the graph is a pure function of workspace registries and
`collect_references`.

Design reference: DR-097.

## Constants

- `__all__`

## Functions

- `_build_indices(graph) -> None`: Populate forward and inverse lookup indices from edges.
- `_collect_all_artifacts(workspace) -> list[tuple[Tuple[str, str, Any]]]`: Collect (id, kind, artifact_obj) triples from all registries.

Uses Workspace properties where available, constructs registries
directly for domains not yet exposed on Workspace (memory, backlog,
drift).

- `_collect_standalone_registry_artifacts(root, out) -> None`: Collect artifacts from registries not exposed on Workspace.
- `_collect_workspace_artifacts(workspace, out) -> None`: Collect artifacts from registries exposed as Workspace properties.
- `_hit_to_edge(source_id, hit) -> GraphEdge`: Convert a ReferenceHit to a GraphEdge.
- `build_reference_graph(workspace) -> ReferenceGraph`: Build a reference graph from all workspace registries.

Iterates all registries, calls `collect_references` per artifact,
normalizes edge targets, and builds forward/inverse indices.

Args:
workspace: Workspace instance with access to all registries.

Returns:
ReferenceGraph computed from current workspace state.

- `build_reference_graph_from_artifacts(artifacts) -> ReferenceGraph`: Build a reference graph from pre-collected artifact triples.

This is the pure core — no I/O. Accepts `(id, kind, obj)` triples
and produces a `ReferenceGraph`.

Args:
artifacts: List of (artifact_id, kind, artifact_object) triples.

Returns:
ReferenceGraph with nodes, edges, forward/inverse indices,
and normalization diagnostics.

- `find_unresolved_references(graph) -> list[GraphEdge]`: Return edges whose target is not in graph.nodes.

Args:
graph: Reference graph to check.

Returns:
List of GraphEdge with unresolved (unknown) targets.

- `query_forward(graph, artifact_id) -> list[GraphEdge]`: Return edges where _artifact_id_ is the source.

Args:
graph: Reference graph to query.
artifact_id: Source artifact ID.

Returns:
List of GraphEdge with this ID as source. Empty if not found.

- `query_inverse(graph, artifact_id) -> list[GraphEdge]`: Return edges where _artifact_id_ is the target.

Args:
graph: Reference graph to query.
artifact_id: Target artifact ID.

Returns:
List of GraphEdge with this ID as target. Empty if not found.

- `query_neighbourhood(graph, artifact_id, direction) -> dict[Tuple[str, list[GraphEdge]]]`: Return grouped edges for an artifact's reference neighbourhood.

Args:
graph: Reference graph to query.
artifact_id: Artifact ID to query.
direction: `"forward"`, `"inverse"`, or `"both"` (default).

Returns:
Dict with `"forward"` and/or `"inverse"` keys mapping to edge lists.

## Classes

### GraphEdge

A directed reference edge in the artifact graph.

Attributes:
source: Source artifact ID.
target: Target artifact ID (normalized).
source_slot: Provenance slot (e.g. "relation", "applies_to").
detail: Slot-specific qualifier (relation type, field name, etc.).

### ReferenceGraph

Cross-artifact reference graph computed from registry state.

Nodes are artifact IDs mapped to their kind. Edges are forward
references extracted by `collect_references`, with targets
normalized against the node index.
