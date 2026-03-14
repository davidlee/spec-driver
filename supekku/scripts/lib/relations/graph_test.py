"""VT-097-graph, VT-097-query-forward, VT-097-query-inverse: reference graph tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from supekku.scripts.lib.relations.graph import (
  GraphEdge,
  ReferenceGraph,
  build_reference_graph_from_artifacts,
  find_unresolved_references,
  query_forward,
  query_inverse,
  query_neighbourhood,
)


# ── Test fixtures ─────────────────────────────────────────────


@dataclass
class FakeArtifact:
  """Minimal artifact with relations and applies_to for testing."""

  id: str = ""
  relations: list[dict[str, Any]] = field(default_factory=list)
  applies_to: dict[str, list[str]] | None = None
  context_inputs: list[dict[str, Any]] | None = None


def _make_artifacts() -> list[tuple[str, str, Any]]:
  """Build a small test graph.

  DE-097 --relates_to--> ISSUE-031
  DE-097 --relates_to--> ISSUE-035
  DE-097 --builds_on--> DE-045
  DR-097 --implements--> DE-097
  DE-097 --applies_to(spec)--> SPEC-001
  """
  de097 = FakeArtifact(
    id="DE-097",
    relations=[
      {"type": "relates_to", "target": "ISSUE-031"},
      {"type": "relates_to", "target": "ISSUE-035"},
      {"type": "builds_on", "target": "DE-045"},
    ],
    applies_to={"specs": ["SPEC-001"], "requirements": []},
  )
  dr097 = FakeArtifact(
    id="DR-097",
    relations=[{"type": "implements", "target": "DE-097"}],
  )
  de045 = FakeArtifact(id="DE-045", relations=[])
  issue031 = FakeArtifact(id="ISSUE-031", relations=[])
  issue035 = FakeArtifact(id="ISSUE-035", relations=[])
  spec001 = FakeArtifact(id="SPEC-001", relations=[])

  return [
    ("DE-097", "delta", de097),
    ("DR-097", "design_revision", dr097),
    ("DE-045", "delta", de045),
    ("ISSUE-031", "issue", issue031),
    ("ISSUE-035", "issue", issue035),
    ("SPEC-001", "spec", spec001),
  ]


# ── Graph build ───────────────────────────────────────────────


class TestBuildReferenceGraph:
  """VT-097-graph: graph builder produces correct nodes and edges."""

  def test_nodes_collected(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    assert "DE-097" in graph.nodes
    assert "SPEC-001" in graph.nodes
    assert graph.nodes["DE-097"] == "delta"
    assert graph.nodes["SPEC-001"] == "spec"

  def test_node_count(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    assert len(graph.nodes) == 6

  def test_edges_from_relations(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    de097_edges = [e for e in graph.edges if e.source == "DE-097"]
    targets = {e.target for e in de097_edges}
    assert "ISSUE-031" in targets
    assert "ISSUE-035" in targets
    assert "DE-045" in targets

  def test_edges_from_applies_to(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    applies_edges = [
      e for e in graph.edges
      if e.source == "DE-097" and e.source_slot == "applies_to"
    ]
    assert len(applies_edges) == 1
    assert applies_edges[0].target == "SPEC-001"

  def test_dr_implements_edge(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    dr_edges = [e for e in graph.edges if e.source == "DR-097"]
    assert len(dr_edges) == 1
    assert dr_edges[0].target == "DE-097"
    assert dr_edges[0].detail == "implements"

  def test_empty_artifacts(self) -> None:
    graph = build_reference_graph_from_artifacts([])
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0


# ── Query forward ─────────────────────────────────────────────


class TestQueryForward:
  """VT-097-query-forward: forward queries return correct edges."""

  def test_forward_de097(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    edges = query_forward(graph, "DE-097")
    targets = {e.target for e in edges}
    assert targets == {"ISSUE-031", "ISSUE-035", "DE-045", "SPEC-001"}

  def test_forward_leaf_node(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    edges = query_forward(graph, "ISSUE-031")
    assert edges == []

  def test_forward_unknown_id(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    edges = query_forward(graph, "NONEXISTENT")
    assert edges == []


# ── Query inverse ─────────────────────────────────────────────


class TestQueryInverse:
  """VT-097-query-inverse: inverse queries return correct edges."""

  def test_inverse_de097(self) -> None:
    """DR-097 implements DE-097, so DE-097 has one inverse edge."""
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    edges = query_inverse(graph, "DE-097")
    assert len(edges) == 1
    assert edges[0].source == "DR-097"

  def test_inverse_issue031(self) -> None:
    """ISSUE-031 is referenced by DE-097."""
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    edges = query_inverse(graph, "ISSUE-031")
    assert len(edges) == 1
    assert edges[0].source == "DE-097"

  def test_inverse_no_referrers(self) -> None:
    """DE-045 is referenced by DE-097 (builds_on)."""
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    edges = query_inverse(graph, "DE-045")
    assert len(edges) == 1
    assert edges[0].source == "DE-097"

  def test_inverse_unknown_id(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    edges = query_inverse(graph, "NONEXISTENT")
    assert edges == []


# ── Query neighbourhood ──────────────────────────────────────


class TestQueryNeighbourhood:
  """query_neighbourhood groups by direction."""

  def test_both_directions(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    result = query_neighbourhood(graph, "DE-097")
    assert "forward" in result
    assert "inverse" in result
    assert len(result["forward"]) == 4  # 3 relations + 1 applies_to
    assert len(result["inverse"]) == 1  # DR-097

  def test_forward_only(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    result = query_neighbourhood(graph, "DE-097", direction="forward")
    assert "forward" in result
    assert "inverse" not in result

  def test_inverse_only(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    result = query_neighbourhood(graph, "DE-097", direction="inverse")
    assert "inverse" in result
    assert "forward" not in result


# ── Unresolved references ────────────────────────────────────


class TestFindUnresolvedReferences:
  """VT-097-unresolved (domain layer): find edges to unknown targets."""

  def test_no_unresolved_in_clean_graph(self) -> None:
    graph = build_reference_graph_from_artifacts(_make_artifacts())
    unresolved = find_unresolved_references(graph)
    assert unresolved == []

  def test_unresolved_target(self) -> None:
    arts = [
      ("DE-001", "delta", FakeArtifact(
        id="DE-001",
        relations=[{"type": "implements", "target": "SPEC-999"}],
      )),
    ]
    graph = build_reference_graph_from_artifacts(arts)
    unresolved = find_unresolved_references(graph)
    assert len(unresolved) == 1
    assert unresolved[0].target == "SPEC-999"
    assert unresolved[0].source == "DE-001"


# ── ID normalization in graph build ──────────────────────────


class TestGraphNormalization:
  """Graph builder normalizes non-canonical edge targets."""

  def test_non_canonical_target_normalized(self) -> None:
    """ADR-11 in a relation should resolve to ADR-011 if in nodes."""
    arts = [
      ("DE-001", "delta", FakeArtifact(
        id="DE-001",
        relations=[{"type": "relates_to", "target": "ADR-11"}],
      )),
      ("ADR-011", "adr", FakeArtifact(id="ADR-011")),
    ]
    graph = build_reference_graph_from_artifacts(arts)
    edges = query_forward(graph, "DE-001")
    assert len(edges) == 1
    assert edges[0].target == "ADR-011"
    assert len(graph.diagnostics) == 1
    assert "ADR-11" in graph.diagnostics[0]

  def test_canonical_target_no_diagnostic(self) -> None:
    arts = [
      ("DE-001", "delta", FakeArtifact(
        id="DE-001",
        relations=[{"type": "relates_to", "target": "ADR-011"}],
      )),
      ("ADR-011", "adr", FakeArtifact(id="ADR-011")),
    ]
    graph = build_reference_graph_from_artifacts(arts)
    assert len(graph.diagnostics) == 0
