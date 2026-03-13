"""VT-085-001 / VT-090-P3: Tests for generic relation query functions."""

from __future__ import annotations

import unittest
from dataclasses import dataclass, field
from typing import Any

from supekku.scripts.lib.core.relation_types import RELATION_TYPES
from supekku.scripts.lib.relations.query import (
  ReferenceHit,
  RelationQueryable,
  _collect_from_backlog_fields,
  _collect_from_decision_fields,
  _collect_from_domain_fields,
  _collect_from_governance_fields,
  _collect_from_requirement_fields,
  collect_references,
  collect_reverse_reference_targets,
  find_by_relation,
  find_related_to,
  matches_related_to,
  matches_relation,
  partition_by_reverse_references,
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


@dataclass(frozen=True)
class MockDecision:
  """Artifact mimicking DecisionRecord domain fields."""

  id: str = "ADR-001"
  specs: list[str] = field(default_factory=list)
  deltas: list[str] = field(default_factory=list)
  requirements: list[str] = field(default_factory=list)
  revisions: list[str] = field(default_factory=list)
  audits: list[str] = field(default_factory=list)
  policies: list[str] = field(default_factory=list)
  standards: list[str] = field(default_factory=list)
  related_decisions: list[str] = field(default_factory=list)
  related_policies: list[str] = field(default_factory=list)
  supersedes: list[str] = field(default_factory=list)
  superseded_by: list[str] = field(default_factory=list)
  relations: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class MockPolicy:
  """Artifact mimicking PolicyRecord domain fields."""

  id: str = "POL-001"
  specs: list[str] = field(default_factory=list)
  requirements: list[str] = field(default_factory=list)
  deltas: list[str] = field(default_factory=list)
  standards: list[str] = field(default_factory=list)
  related_policies: list[str] = field(default_factory=list)
  related_standards: list[str] = field(default_factory=list)
  supersedes: list[str] = field(default_factory=list)
  superseded_by: list[str] = field(default_factory=list)
  relations: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class MockStandard:
  """Artifact mimicking StandardRecord domain fields."""

  id: str = "STD-001"
  specs: list[str] = field(default_factory=list)
  requirements: list[str] = field(default_factory=list)
  deltas: list[str] = field(default_factory=list)
  policies: list[str] = field(default_factory=list)
  related_policies: list[str] = field(default_factory=list)
  related_standards: list[str] = field(default_factory=list)
  supersedes: list[str] = field(default_factory=list)
  superseded_by: list[str] = field(default_factory=list)
  relations: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class MockRequirement:
  """Artifact mimicking RequirementRecord domain fields."""

  id: str = "FR-001"
  primary_spec: str = ""
  specs: list[str] = field(default_factory=list)
  implemented_by: list[str] = field(default_factory=list)
  verified_by: list[str] = field(default_factory=list)
  coverage_evidence: list[str] = field(default_factory=list)
  relations: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class MockBacklogItem:
  """Artifact mimicking BacklogItem with frontmatter dict."""

  id: str = "ISSUE-001"
  frontmatter: dict[str, Any] = field(default_factory=dict)
  relations: list[dict[str, Any]] = field(default_factory=list)


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


# --- VT-090-P3-1: _collect_from_decision_fields ---


class CollectFromDecisionFieldsTest(unittest.TestCase):
  def test_all_11_fields_yield_hits(self) -> None:
    adr = MockDecision(
      specs=["SPEC-100"],
      deltas=["DE-001"],
      requirements=["FR-001"],
      revisions=["RE-001"],
      audits=["AUD-001"],
      policies=["POL-001"],
      standards=["STD-001"],
      related_decisions=["ADR-002"],
      related_policies=["POL-002"],
      supersedes=["ADR-000"],
      superseded_by=["ADR-003"],
    )
    hits = _collect_from_decision_fields(adr)
    assert len(hits) == 11
    targets = {h.target for h in hits}
    assert "SPEC-100" in targets
    assert "DE-001" in targets
    assert "ADR-002" in targets
    assert "ADR-000" in targets
    assert "ADR-003" in targets

  def test_all_hits_have_domain_field_source(self) -> None:
    adr = MockDecision(specs=["SPEC-100"], deltas=["DE-001"])
    hits = _collect_from_decision_fields(adr)
    assert all(h.source == "domain_field" for h in hits)

  def test_detail_is_field_name(self) -> None:
    adr = MockDecision(specs=["SPEC-100"])
    hits = _collect_from_decision_fields(adr)
    assert hits[0].detail == "specs"

  def test_empty_decision_returns_empty(self) -> None:
    assert _collect_from_decision_fields(MockDecision()) == []

  def test_bare_artifact_returns_empty(self) -> None:
    assert _collect_from_decision_fields(MockBare()) == []

  def test_multiple_values_in_one_field(self) -> None:
    adr = MockDecision(specs=["SPEC-100", "SPEC-101", "SPEC-102"])
    hits = _collect_from_decision_fields(adr)
    assert len(hits) == 3
    assert all(h.detail == "specs" for h in hits)

  def test_whitespace_stripped(self) -> None:
    adr = MockDecision(specs=[" SPEC-100 "])
    hits = _collect_from_decision_fields(adr)
    assert hits[0].target == "SPEC-100"

  def test_empty_string_skipped(self) -> None:
    adr = MockDecision(specs=["", "SPEC-100"])
    hits = _collect_from_decision_fields(adr)
    assert len(hits) == 1
    assert hits[0].target == "SPEC-100"


# --- VT-090-P3-2: _collect_from_governance_fields ---


class CollectFromGovernanceFieldsTest(unittest.TestCase):
  def test_policy_fields(self) -> None:
    pol = MockPolicy(
      specs=["SPEC-100"],
      requirements=["FR-001"],
      deltas=["DE-001"],
      standards=["STD-001"],
      related_policies=["POL-002"],
      related_standards=["STD-002"],
      supersedes=["POL-000"],
      superseded_by=["POL-003"],
    )
    hits = _collect_from_governance_fields(pol)
    assert len(hits) == 8
    assert all(h.source == "domain_field" for h in hits)

  def test_standard_fields(self) -> None:
    std = MockStandard(
      specs=["SPEC-100"],
      requirements=["FR-001"],
      deltas=["DE-001"],
      policies=["POL-001"],
      related_policies=["POL-002"],
      related_standards=["STD-002"],
      supersedes=["STD-000"],
      superseded_by=["STD-003"],
    )
    hits = _collect_from_governance_fields(std)
    # policies field is not in _GOVERNANCE_REFERENCE_FIELDS (Decision-only)
    # but it IS in Standard model — governance collector covers shared fields
    assert len(hits) == 8
    assert all(h.source == "domain_field" for h in hits)

  def test_empty_governance_returns_empty(self) -> None:
    assert _collect_from_governance_fields(MockPolicy()) == []

  def test_bare_artifact_returns_empty(self) -> None:
    assert _collect_from_governance_fields(MockBare()) == []


# --- VT-090-P3-3: _collect_from_requirement_fields ---


class CollectFromRequirementFieldsTest(unittest.TestCase):
  def test_all_fields_including_primary_spec(self) -> None:
    req = MockRequirement(
      primary_spec="SPEC-100",
      specs=["SPEC-100", "SPEC-101"],
      implemented_by=["DE-001"],
      verified_by=["VT-001"],
      coverage_evidence=["CE-001"],
    )
    hits = _collect_from_requirement_fields(req)
    # 1 scalar + 2 specs + 1 implemented_by + 1 verified_by + 1 coverage_evidence
    assert len(hits) == 6
    targets = {h.target for h in hits}
    assert "SPEC-100" in targets
    assert "SPEC-101" in targets
    assert "DE-001" in targets

  def test_scalar_primary_spec(self) -> None:
    req = MockRequirement(primary_spec="SPEC-100")
    hits = _collect_from_requirement_fields(req)
    assert len(hits) == 1
    assert hits[0] == ReferenceHit(
      target="SPEC-100",
      source="domain_field",
      detail="primary_spec",
    )

  def test_empty_primary_spec_skipped(self) -> None:
    req = MockRequirement(primary_spec="")
    assert _collect_from_requirement_fields(req) == []

  def test_no_primary_spec_attribute(self) -> None:
    assert _collect_from_requirement_fields(MockBare()) == []

  def test_all_hits_have_domain_field_source(self) -> None:
    req = MockRequirement(specs=["SPEC-100"], implemented_by=["DE-001"])
    hits = _collect_from_requirement_fields(req)
    assert all(h.source == "domain_field" for h in hits)


# --- VT-090-P3-4: _collect_from_backlog_fields ---


class CollectFromBacklogFieldsTest(unittest.TestCase):
  def test_linked_deltas(self) -> None:
    item = MockBacklogItem(
      frontmatter={"linked_deltas": ["DE-001", "DE-002"]},
    )
    hits = _collect_from_backlog_fields(item)
    assert len(hits) == 2
    assert all(h.source == "backlog_field" for h in hits)
    assert all(h.detail == "linked_delta" for h in hits)
    assert hits[0].target == "DE-001"
    assert hits[1].target == "DE-002"

  def test_related_requirements(self) -> None:
    item = MockBacklogItem(
      frontmatter={"related_requirements": ["FR-001", "NF-002"]},
    )
    hits = _collect_from_backlog_fields(item)
    assert len(hits) == 2
    assert all(h.detail == "related_requirement" for h in hits)

  def test_mixed_frontmatter(self) -> None:
    item = MockBacklogItem(
      frontmatter={
        "linked_deltas": ["DE-001"],
        "related_requirements": ["FR-001"],
      },
    )
    hits = _collect_from_backlog_fields(item)
    assert len(hits) == 2

  def test_empty_frontmatter(self) -> None:
    item = MockBacklogItem(frontmatter={})
    assert _collect_from_backlog_fields(item) == []

  def test_no_frontmatter_attribute(self) -> None:
    assert _collect_from_backlog_fields(MockBare()) == []

  def test_non_dict_frontmatter(self) -> None:
    item = MockBacklogItem(frontmatter="not-a-dict")  # type: ignore[arg-type]
    assert _collect_from_backlog_fields(item) == []

  def test_empty_string_skipped(self) -> None:
    item = MockBacklogItem(
      frontmatter={"linked_deltas": ["", "DE-001"]},
    )
    hits = _collect_from_backlog_fields(item)
    assert len(hits) == 1
    assert hits[0].target == "DE-001"

  def test_whitespace_stripped(self) -> None:
    item = MockBacklogItem(
      frontmatter={"linked_deltas": [" DE-001 "]},
    )
    hits = _collect_from_backlog_fields(item)
    assert hits[0].target == "DE-001"

  def test_frontmatter_relations(self) -> None:
    item = MockBacklogItem(
      frontmatter={"relations": [{"type": "relates_to", "target": "DE-090"}]},
    )
    hits = _collect_from_backlog_fields(item)
    assert len(hits) == 1
    assert hits[0] == ReferenceHit(
      target="DE-090",
      source="relation",
      detail="relates_to",
    )

  def test_frontmatter_relations_skips_non_dict(self) -> None:
    item = MockBacklogItem(
      frontmatter={"relations": ["not-a-dict"]},
    )
    assert _collect_from_backlog_fields(item) == []

  def test_frontmatter_relations_skips_empty_target(self) -> None:
    item = MockBacklogItem(
      frontmatter={"relations": [{"type": "relates_to", "target": ""}]},
    )
    assert _collect_from_backlog_fields(item) == []


# --- VT-090-P3-5: _collect_from_domain_fields dispatcher ---


class CollectFromDomainFieldsTest(unittest.TestCase):
  def test_chains_decision_collector(self) -> None:
    adr = MockDecision(specs=["SPEC-100"])
    hits = _collect_from_domain_fields(adr)
    assert any(h.target == "SPEC-100" and h.source == "domain_field" for h in hits)

  def test_chains_governance_collector(self) -> None:
    pol = MockPolicy(standards=["STD-001"])
    hits = _collect_from_domain_fields(pol)
    assert any(h.target == "STD-001" and h.source == "domain_field" for h in hits)

  def test_chains_requirement_collector(self) -> None:
    req = MockRequirement(primary_spec="SPEC-100")
    hits = _collect_from_domain_fields(req)
    assert any(h.target == "SPEC-100" and h.detail == "primary_spec" for h in hits)

  def test_chains_backlog_collector(self) -> None:
    item = MockBacklogItem(frontmatter={"linked_deltas": ["DE-001"]})
    hits = _collect_from_domain_fields(item)
    assert any(h.target == "DE-001" and h.source == "backlog_field" for h in hits)

  def test_bare_artifact_returns_empty(self) -> None:
    assert _collect_from_domain_fields(MockBare()) == []


# --- VT-090-P3-6: collect_references picks up domain fields ---


class CollectReferencesDomainFieldsTest(unittest.TestCase):
  def test_decision_audits_via_collect_references(self) -> None:
    # Use a decision-only field to avoid overlap with other collectors
    adr = MockDecision(audits=["AUD-001"])
    hits = collect_references(adr)
    domain_hits = [h for h in hits if h.source == "domain_field"]
    assert len(domain_hits) == 1
    assert domain_hits[0].target == "AUD-001"

  def test_backlog_linked_deltas_via_collect_references(self) -> None:
    item = MockBacklogItem(frontmatter={"linked_deltas": ["DE-001"]})
    hits = collect_references(item)
    backlog_hits = [h for h in hits if h.source == "backlog_field"]
    assert len(backlog_hits) == 1
    assert backlog_hits[0].target == "DE-001"

  def test_domain_fields_combined_with_relations(self) -> None:
    adr = MockDecision(
      relations=[_rel("implements", "PROD-010")],
      audits=["AUD-001"],
    )
    hits = collect_references(adr)
    sources = {h.source for h in hits}
    assert "relation" in sources
    assert "domain_field" in sources


# --- VT-090-P3-7: find_related_to matches domain fields ---


class FindRelatedToDomainFieldsTest(unittest.TestCase):
  def test_match_decision_specs(self) -> None:
    adr = MockDecision(id="ADR-001", specs=["SPEC-100"])
    result = find_related_to([adr], "SPEC-100")
    assert len(result) == 1
    assert result[0].id == "ADR-001"

  def test_match_requirement_implemented_by(self) -> None:
    req = MockRequirement(id="FR-001", implemented_by=["DE-090"])
    result = find_related_to([req], "DE-090")
    assert len(result) == 1

  def test_match_backlog_linked_deltas(self) -> None:
    item = MockBacklogItem(
      id="ISSUE-001",
      frontmatter={"linked_deltas": ["DE-090"]},
    )
    result = find_related_to([item], "DE-090")
    assert len(result) == 1

  def test_no_match_domain_field(self) -> None:
    adr = MockDecision(id="ADR-001", specs=["SPEC-100"])
    result = find_related_to([adr], "SPEC-999")
    assert result == []


# --- VT-090-P3-8: semantic separation invariant ---

# Field names "supersedes" and "superseded_by" overlap with RELATION_TYPES
# by design — they exist in both domains. Semantic separation is enforced
# by source ("domain_field" vs "relation"), not by detail uniqueness.
_KNOWN_OVERLAP_FIELDS = {"supersedes", "superseded_by"}


class DomainFieldSemanticSeparationTest(unittest.TestCase):
  """Domain collectors use source="domain_field"/"backlog_field", not "relation"."""

  def test_decision_source_is_domain_field(self) -> None:
    adr = MockDecision(
      specs=["SPEC-100"],
      deltas=["DE-001"],
      supersedes=["ADR-000"],
    )
    hits = _collect_from_decision_fields(adr)
    assert all(h.source == "domain_field" for h in hits)

  def test_governance_source_is_domain_field(self) -> None:
    pol = MockPolicy(specs=["SPEC-100"], supersedes=["POL-000"])
    hits = _collect_from_governance_fields(pol)
    assert all(h.source == "domain_field" for h in hits)

  def test_requirement_source_is_domain_field(self) -> None:
    req = MockRequirement(primary_spec="SPEC-100", specs=["SPEC-100"])
    hits = _collect_from_requirement_fields(req)
    assert all(h.source == "domain_field" for h in hits)

  def test_backlog_source_is_backlog_field(self) -> None:
    item = MockBacklogItem(
      frontmatter={"linked_deltas": ["DE-001"], "related_requirements": ["FR-001"]},
    )
    hits = _collect_from_backlog_fields(item)
    assert all(h.source == "backlog_field" for h in hits)

  def test_non_overlap_details_not_in_relation_types(self) -> None:
    adr = MockDecision(specs=["SPEC-100"], audits=["AUD-001"])
    hits = _collect_from_decision_fields(adr)
    non_overlap = [h for h in hits if h.detail not in _KNOWN_OVERLAP_FIELDS]
    for h in non_overlap:
      assert h.detail not in RELATION_TYPES, (
        f"detail={h.detail!r} unexpectedly collides with RELATION_TYPES"
      )


class CollectReverseReferenceTargetsTest(unittest.TestCase):
  """VT-090-P4-1: Tests for collect_reverse_reference_targets()."""

  def test_empty_referrers(self) -> None:

    targets = collect_reverse_reference_targets([])
    assert targets == set()

  def test_single_referrer_with_relations(self) -> None:

    referrer = MockDelta(
      id="AUD-001",
      relations=[_rel("documents", "DE-090")],
    )
    targets = collect_reverse_reference_targets([referrer])
    assert "DE-090" in targets

  def test_multiple_referrers_aggregated(self) -> None:

    referrers = [
      MockDelta(id="AUD-001", relations=[_rel("documents", "DE-090")]),
      MockDelta(id="AUD-002", relations=[_rel("documents", "DE-091")]),
    ]
    targets = collect_reverse_reference_targets(referrers)
    assert "DE-090" in targets
    assert "DE-091" in targets

  def test_uppercased(self) -> None:

    referrer = MockDelta(
      id="AUD-001",
      relations=[_rel("documents", "de-090")],
    )
    targets = collect_reverse_reference_targets([referrer])
    assert "DE-090" in targets

  def test_applies_to_also_collected(self) -> None:

    referrer = MockDelta(
      id="DE-001",
      applies_to={"specs": ["SPEC-110"], "requirements": ["PROD-010.FR-005"]},
    )
    targets = collect_reverse_reference_targets([referrer])
    assert "SPEC-110" in targets
    assert "PROD-010.FR-005" in targets

  def test_duplicates_merged(self) -> None:

    referrers = [
      MockDelta(id="AUD-001", relations=[_rel("documents", "DE-090")]),
      MockDelta(id="AUD-002", relations=[_rel("reviews", "DE-090")]),
    ]
    targets = collect_reverse_reference_targets(referrers)
    assert targets == {"DE-090"}


class PartitionByReverseReferencesTest(unittest.TestCase):
  """VT-090-P4-2: Tests for partition_by_reverse_references()."""

  def test_basic_partition(self) -> None:

    candidates = [
      MockDelta(id="DE-090"),
      MockDelta(id="DE-091"),
      MockDelta(id="DE-092"),
    ]
    referrers = [
      MockDelta(id="AUD-001", relations=[_rel("documents", "DE-090")]),
    ]
    referenced, unreferenced = partition_by_reverse_references(candidates, referrers)
    assert [c.id for c in referenced] == ["DE-090"]
    assert [c.id for c in unreferenced] == ["DE-091", "DE-092"]

  def test_empty_referrers_all_unreferenced(self) -> None:

    candidates = [MockDelta(id="DE-090"), MockDelta(id="DE-091")]
    referenced, unreferenced = partition_by_reverse_references(candidates, [])
    assert referenced == []
    assert len(unreferenced) == 2

  def test_custom_id_fn(self) -> None:

    @dataclass(frozen=True)
    class ReqLike:
      uid: str

    candidates = [ReqLike(uid="PROD-010.FR-001"), ReqLike(uid="PROD-010.FR-002")]
    referrers = [
      MockDelta(
        id="DE-001",
        applies_to={"specs": [], "requirements": ["PROD-010.FR-001"]},
      ),
    ]
    referenced, unreferenced = partition_by_reverse_references(
      candidates,
      referrers,
      candidate_id_fn=lambda c: c.uid,
    )
    assert [c.uid for c in referenced] == ["PROD-010.FR-001"]
    assert [c.uid for c in unreferenced] == ["PROD-010.FR-002"]

  def test_case_insensitive_matching(self) -> None:

    candidates = [MockDelta(id="de-090")]
    referrers = [
      MockDelta(id="AUD-001", relations=[_rel("documents", "DE-090")]),
    ]
    referenced, _ = partition_by_reverse_references(candidates, referrers)
    assert len(referenced) == 1

  def test_self_reference_included(self) -> None:

    # An artifact that references itself should appear in referenced
    referrer = MockDelta(id="DE-090", relations=[_rel("updates", "DE-090")])
    candidates = [MockDelta(id="DE-090")]
    referenced, _ = partition_by_reverse_references(candidates, [referrer])
    assert len(referenced) == 1


if __name__ == "__main__":
  unittest.main()
