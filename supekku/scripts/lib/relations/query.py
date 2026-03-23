"""Re-export shim — canonical location is spec_driver.domain.relations.query."""

# ruff: noqa: F401
from spec_driver.domain.relations.query import (
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

__all__ = [
  "ReferenceHit",
  "RelationQueryable",
  "_collect_from_backlog_fields",
  "_collect_from_decision_fields",
  "_collect_from_domain_fields",
  "_collect_from_governance_fields",
  "_collect_from_requirement_fields",
  "collect_references",
  "collect_reverse_reference_targets",
  "find_by_relation",
  "find_related_to",
  "matches_related_to",
  "matches_relation",
  "partition_by_reverse_references",
]
