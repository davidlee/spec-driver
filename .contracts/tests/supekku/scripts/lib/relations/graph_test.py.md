# supekku.scripts.lib.relations.graph_test

VT-097-graph, VT-097-query-forward, VT-097-query-inverse: reference graph tests.

## Functions

- `_make_artifacts() -> list[tuple[Tuple[str, str, Any]]]`: Build a small test graph.

DE-097 --relates_to--> ISSUE-031
DE-097 --relates_to--> ISSUE-035
DE-097 --builds_on--> DE-045
DR-097 --implements--> DE-097
DE-097 --applies_to(spec)--> SPEC-001

## Classes

### FakeArtifact

Minimal artifact with relations and applies_to for testing.

### TestBuildReferenceGraph

VT-097-graph: graph builder produces correct nodes and edges.

#### Methods

- `test_dr_implements_edge(self) -> None`
- `test_edges_from_applies_to(self) -> None`
- `test_edges_from_relations(self) -> None`
- `test_empty_artifacts(self) -> None`
- `test_node_count(self) -> None`
- `test_nodes_collected(self) -> None`

### TestFindUnresolvedReferences

VT-097-unresolved (domain layer): find edges to unknown targets.

#### Methods

- `test_no_unresolved_in_clean_graph(self) -> None`
- `test_unresolved_target(self) -> None`

### TestGraphNormalization

Graph builder normalizes non-canonical edge targets.

#### Methods

- `test_canonical_target_no_diagnostic(self) -> None`
- `test_non_canonical_target_normalized(self) -> None`: ADR-11 in a relation should resolve to ADR-011 if in nodes.

### TestQueryForward

VT-097-query-forward: forward queries return correct edges.

#### Methods

- `test_forward_de097(self) -> None`
- `test_forward_leaf_node(self) -> None`
- `test_forward_unknown_id(self) -> None`

### TestQueryInverse

VT-097-query-inverse: inverse queries return correct edges.

#### Methods

- `test_inverse_de097(self) -> None`: DR-097 implements DE-097, so DE-097 has one inverse edge.
- `test_inverse_issue031(self) -> None`: ISSUE-031 is referenced by DE-097.
- `test_inverse_no_referrers(self) -> None`: DE-045 is referenced by DE-097 (builds_on).
- `test_inverse_unknown_id(self) -> None`

### TestQueryNeighbourhood

query_neighbourhood groups by direction.

#### Methods

- `test_both_directions(self) -> None`
- `test_forward_only(self) -> None` - DR-097
- `test_inverse_only(self) -> None`
