"""VT-085-001: Tests for generic relation query functions."""

from __future__ import annotations

import unittest
from dataclasses import dataclass, field
from typing import Any

from supekku.scripts.lib.relations.query import (
  ReferenceHit,
  RelationQueryable,
  collect_references,
  find_by_relation,
  find_related_to,
  matches_related_to,
  matches_relation,
)


def _rel(rtype: str, target: str) -> dict[str, str]:
  return {"type": rtype, "target": target}


def _ci(ci_type: str, ci_id: str) -> dict[str, str]:
  return {"type": ci_type, "id": ci_id}


# --- Test fixtures: duck-typed mock artifacts ---


@dataclass(frozen=True)
class MockDelta:
  """Artifact with all reference slots (like ChangeArtifact)."""

  id: str = "DE-001"
  relations: list[dict[str, Any]] = field(default_factory=list)
  applies_to: dict[str, Any] = field(default_factory=dict)
  context_inputs: list[dict[str, Any]] = field(
    default_factory=list,
  )


@dataclass(frozen=True)
class MockSpec:
  """Artifact with relations and informed_by (like Spec)."""

  id: str = "SPEC-001"
  relations: list[dict[str, Any]] = field(default_factory=list)
  informed_by: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MockBare:
  """Artifact with no reference slots at all."""

  id: str = "BARE-001"


# --- RelationQueryable Protocol ---


class ProtocolTest(unittest.TestCase):
  def test_mock_delta_is_queryable(self) -> None:
    assert isinstance(MockDelta(), RelationQueryable)

  def test_mock_spec_is_queryable(self) -> None:
    assert isinstance(MockSpec(), RelationQueryable)

  def test_mock_bare_is_not_queryable(self) -> None:
    assert not isinstance(MockBare(), RelationQueryable)


# --- collect_references ---


class CollectReferencesTest(unittest.TestCase):
  def test_empty_artifact(self) -> None:
    assert collect_references(MockDelta()) == []

  def test_bare_artifact_returns_empty(self) -> None:
    assert collect_references(MockBare()) == []

  def test_relations_slot(self) -> None:
    delta = MockDelta(
      relations=[
        _rel("implements", "PROD-010"),
        _rel("depends_on", "SPEC-100"),
      ]
    )
    hits = collect_references(delta)
    assert len(hits) == 2
    assert hits[0] == ReferenceHit(
      target="PROD-010",
      source="relation",
      detail="implements",
    )
    assert hits[1] == ReferenceHit(
      target="SPEC-100",
      source="relation",
      detail="depends_on",
    )

  def test_applies_to_slot(self) -> None:
    delta = MockDelta(
      applies_to={
        "specs": ["SPEC-100", "SPEC-101"],
        "requirements": ["SPEC-100.FR-001"],
        "prod": ["PROD-010"],
      }
    )
    hits = collect_references(delta)
    assert len(hits) == 4
    targets = {h.target for h in hits}
    assert targets == {
      "SPEC-100",
      "SPEC-101",
      "SPEC-100.FR-001",
      "PROD-010",
    }
    spec_hits = [h for h in hits if h.detail == "spec"]
    assert len(spec_hits) == 2
    req_hits = [h for h in hits if h.detail == "requirement"]
    assert len(req_hits) == 1

  def test_context_inputs_slot(self) -> None:
    delta = MockDelta(
      context_inputs=[
        _ci("issue", "IMPR-006"),
        _ci("research", "RC-010"),
      ]
    )
    hits = collect_references(delta)
    assert len(hits) == 2
    assert hits[0] == ReferenceHit(
      target="IMPR-006",
      source="context_input",
      detail="issue",
    )
    assert hits[1] == ReferenceHit(
      target="RC-010",
      source="context_input",
      detail="research",
    )

  def test_informed_by_slot(self) -> None:
    spec = MockSpec(informed_by=["ADR-001", "ADR-002"])
    hits = collect_references(spec)
    assert len(hits) == 2
    assert hits[0] == ReferenceHit(
      target="ADR-001",
      source="informed_by",
      detail="adr",
    )
    assert hits[1] == ReferenceHit(
      target="ADR-002",
      source="informed_by",
      detail="adr",
    )

  def test_all_slots_combined(self) -> None:
    delta = MockDelta(
      relations=[_rel("implements", "PROD-010")],
      applies_to={"specs": ["SPEC-100"]},
      context_inputs=[_ci("issue", "IMPR-006")],
    )
    hits = collect_references(delta)
    assert len(hits) == 3
    sources = {h.source for h in hits}
    assert sources == {"relation", "applies_to", "context_input"}

  def test_relation_missing_target_skipped(self) -> None:
    delta = MockDelta(
      relations=[
        {"type": "implements"},  # no target
        _rel("depends_on", "SPEC-100"),
      ]
    )
    hits = collect_references(delta)
    assert len(hits) == 1
    assert hits[0].target == "SPEC-100"

  def test_relation_empty_target_skipped(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "")])
    assert collect_references(delta) == []

  def test_context_input_missing_id_skipped(self) -> None:
    delta = MockDelta(context_inputs=[{"type": "issue"}])
    assert collect_references(delta) == []

  def test_non_dict_relation_skipped(self) -> None:
    delta = MockDelta(
      relations=["not-a-dict"],  # type: ignore[list-item]
    )
    assert collect_references(delta) == []

  def test_non_dict_context_input_skipped(self) -> None:
    delta = MockDelta(
      context_inputs=["not-a-dict"],  # type: ignore[list-item]
    )
    assert collect_references(delta) == []

  def test_applies_to_non_list_values_skipped(self) -> None:
    delta = MockDelta(applies_to={"specs": "not-a-list"})
    assert collect_references(delta) == []

  def test_whitespace_stripped(self) -> None:
    delta = MockDelta(
      relations=[{"type": " implements ", "target": " PROD-010 "}],
    )
    hits = collect_references(delta)
    assert len(hits) == 1
    assert hits[0].target == "PROD-010"
    assert hits[0].detail == "implements"


# --- matches_related_to ---


class MatchesRelatedToTest(unittest.TestCase):
  def test_match_in_relations(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert matches_related_to(delta, "PROD-010")

  def test_case_insensitive(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert matches_related_to(delta, "prod-010")

  def test_no_match(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert not matches_related_to(delta, "PROD-999")

  def test_match_in_applies_to(self) -> None:
    delta = MockDelta(applies_to={"specs": ["SPEC-100"]})
    assert matches_related_to(delta, "SPEC-100")

  def test_match_in_context_inputs(self) -> None:
    delta = MockDelta(
      context_inputs=[_ci("issue", "IMPR-006")],
    )
    assert matches_related_to(delta, "IMPR-006")

  def test_match_in_informed_by(self) -> None:
    spec = MockSpec(informed_by=["ADR-001"])
    assert matches_related_to(spec, "ADR-001")

  def test_bare_artifact_no_match(self) -> None:
    assert not matches_related_to(MockBare(), "anything")

  def test_empty_target_id(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert not matches_related_to(delta, "")


# --- matches_relation ---


class MatchesRelationTest(unittest.TestCase):
  def test_match_by_type(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert matches_relation(delta, relation_type="implements")

  def test_match_by_target(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert matches_relation(delta, target="PROD-010")

  def test_match_by_both(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert matches_relation(
      delta,
      relation_type="implements",
      target="PROD-010",
    )

  def test_no_match_wrong_type(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert not matches_relation(delta, relation_type="depends_on")

  def test_no_match_wrong_target(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert not matches_relation(delta, target="PROD-999")

  def test_case_insensitive_type(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert matches_relation(delta, relation_type="IMPLEMENTS")

  def test_case_insensitive_target(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert matches_relation(delta, target="prod-010")

  def test_no_criteria_returns_false(self) -> None:
    delta = MockDelta(relations=[_rel("implements", "PROD-010")])
    assert not matches_relation(delta)

  def test_bare_artifact_returns_false(self) -> None:
    assert not matches_relation(MockBare(), relation_type="implements")

  def test_does_not_search_applies_to(self) -> None:
    delta = MockDelta(applies_to={"specs": ["SPEC-100"]})
    assert not matches_relation(delta, target="SPEC-100")


# --- find_related_to ---


class FindRelatedToTest(unittest.TestCase):
  def test_filters_matching(self) -> None:
    d1 = MockDelta(
      id="DE-001",
      relations=[_rel("implements", "PROD-010")],
    )
    d2 = MockDelta(
      id="DE-002",
      relations=[_rel("depends_on", "SPEC-100")],
    )
    d3 = MockDelta(
      id="DE-003",
      context_inputs=[_ci("issue", "PROD-010")],
    )
    result = find_related_to([d1, d2, d3], "PROD-010")
    assert len(result) == 2
    assert result[0].id == "DE-001"
    assert result[1].id == "DE-003"

  def test_empty_input(self) -> None:
    assert find_related_to([], "PROD-010") == []

  def test_no_matches(self) -> None:
    d1 = MockDelta(
      id="DE-001",
      relations=[_rel("implements", "PROD-010")],
    )
    assert find_related_to([d1], "NONEXISTENT") == []


# --- find_by_relation ---


class FindByRelationTest(unittest.TestCase):
  def test_filters_by_type(self) -> None:
    d1 = MockDelta(
      id="DE-001",
      relations=[_rel("implements", "PROD-010")],
    )
    d2 = MockDelta(
      id="DE-002",
      relations=[_rel("depends_on", "SPEC-100")],
    )
    result = find_by_relation([d1, d2], relation_type="implements")
    assert len(result) == 1
    assert result[0].id == "DE-001"

  def test_filters_by_target(self) -> None:
    d1 = MockDelta(
      id="DE-001",
      relations=[_rel("implements", "PROD-010")],
    )
    d2 = MockDelta(
      id="DE-002",
      relations=[_rel("depends_on", "PROD-010")],
    )
    result = find_by_relation([d1, d2], target="PROD-010")
    assert len(result) == 2

  def test_filters_by_both(self) -> None:
    d1 = MockDelta(
      id="DE-001",
      relations=[_rel("implements", "PROD-010")],
    )
    d2 = MockDelta(
      id="DE-002",
      relations=[_rel("depends_on", "PROD-010")],
    )
    result = find_by_relation(
      [d1, d2],
      relation_type="implements",
      target="PROD-010",
    )
    assert len(result) == 1
    assert result[0].id == "DE-001"

  def test_does_not_search_other_slots(self) -> None:
    d1 = MockDelta(
      id="DE-001",
      context_inputs=[_ci("issue", "IMPR-006")],
    )
    result = find_by_relation([d1], target="IMPR-006")
    assert result == []


if __name__ == "__main__":
  unittest.main()
