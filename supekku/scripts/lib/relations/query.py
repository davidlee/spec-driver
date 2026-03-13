"""Generic relation query functions for artifact reference discovery.

Pure functions that operate on any artifact conforming to
:class:`RelationQueryable`.  Additional reference slots (``.applies_to``,
``.context_inputs``, ``.informed_by``) are searched when present but are
not required by the protocol.

Design reference: DR-085 §5.2.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RelationQueryable(Protocol):  # pylint: disable=too-few-public-methods
  """Artifact that exposes relations as ``list[dict]`` with type/target keys.

  Additional reference slots (``.applies_to``, ``.context_inputs``,
  ``.informed_by``) are searched by :func:`collect_references` when present
  but are not required by this protocol.

  Single-property Protocol is intentional — see ADR-009.
  """

  @property
  def relations(self) -> list[dict[str, Any]]:
    """Structured relation dicts with ``type`` and ``target`` keys."""
    ...  # pylint: disable=unnecessary-ellipsis


@dataclass(frozen=True)
class ReferenceHit:
  """A matched forward reference with provenance.

  Attributes:
    target: The referenced artifact ID.
    source: Which slot the reference came from
        (``"relation"``, ``"applies_to"``, ``"context_input"``,
        ``"informed_by"``, ``"domain_field"``, ``"backlog_field"``).
    detail: Slot-specific qualifier whose meaning varies by *source*:

        - ``source="relation"``: the relation type
          (e.g. ``"implements"``, ``"depends_on"``)
        - ``source="applies_to"``: the applies_to key
          (e.g. ``"spec"``, ``"requirement"``, ``"prod"``)
        - ``source="context_input"``: the context input type
          (e.g. ``"issue"``, ``"research"``)
        - ``source="informed_by"``: always ``"adr"``
        - ``source="domain_field"``: the field name
          (e.g. ``"specs"``, ``"implemented_by"``)
        - ``source="backlog_field"``: the field name
          (e.g. ``"linked_delta"``, ``"related_requirement"``)
  """

  target: str
  source: str
  detail: str


def _collect_from_relations(artifact: Any) -> list[ReferenceHit]:
  """Extract references from ``.relations`` (list of type/target dicts)."""
  hits: list[ReferenceHit] = []
  relations: list[dict[str, Any]] = getattr(artifact, "relations", None) or []
  for rel in relations:
    if not isinstance(rel, dict):
      continue
    target = str(rel.get("target", "")).strip()
    rel_type = str(rel.get("type", "")).strip()
    if target:
      hits.append(ReferenceHit(target=target, source="relation", detail=rel_type))
  return hits


def _collect_from_applies_to(artifact: Any) -> list[ReferenceHit]:
  """Extract references from ``.applies_to`` (dict of spec/req/prod lists)."""
  hits: list[ReferenceHit] = []
  applies_to: dict[str, Any] | None = getattr(artifact, "applies_to", None)
  if not isinstance(applies_to, dict):
    return hits
  slot_details = {"specs": "spec", "requirements": "requirement", "prod": "prod"}
  for key, detail in slot_details.items():
    values = applies_to.get(key)
    if isinstance(values, list):
      for value in values:
        target = str(value).strip()
        if target:
          hits.append(ReferenceHit(target=target, source="applies_to", detail=detail))
  return hits


def _collect_from_context_inputs(artifact: Any) -> list[ReferenceHit]:
  """Extract references from ``.context_inputs`` (list of type/id dicts)."""
  hits: list[ReferenceHit] = []
  raw = getattr(artifact, "context_inputs", None)
  context_inputs: list[Any] = raw if isinstance(raw, list) else []
  for ci in context_inputs:
    if not isinstance(ci, dict):
      continue
    target = str(ci.get("id", "")).strip()
    ci_type = str(ci.get("type", "")).strip()
    if target:
      hits.append(ReferenceHit(target=target, source="context_input", detail=ci_type))
  return hits


def _collect_from_informed_by(artifact: Any) -> list[ReferenceHit]:
  """Extract references from ``.informed_by`` (list of ADR IDs)."""
  hits: list[ReferenceHit] = []
  raw = getattr(artifact, "informed_by", None)
  informed_by: list[Any] = raw if isinstance(raw, list) else []
  for item in informed_by:
    target = str(item).strip()
    if target:
      hits.append(ReferenceHit(target=target, source="informed_by", detail="adr"))
  return hits


# --- Domain-field collectors (DR-090 §P3) ---

_DECISION_REFERENCE_FIELDS: tuple[str, ...] = (
  "specs", "deltas", "requirements", "revisions", "audits",
  "policies", "standards", "related_decisions", "related_policies",
  "supersedes", "superseded_by",
)

_GOVERNANCE_REFERENCE_FIELDS: tuple[str, ...] = (
  "specs", "requirements", "deltas", "standards", "policies",
  "related_policies", "related_standards",
  "supersedes", "superseded_by",
)

_REQUIREMENT_REFERENCE_FIELDS: tuple[str, ...] = (
  "specs", "implemented_by", "verified_by", "coverage_evidence",
)


def _collect_from_list_fields(
  artifact: Any,
  field_names: tuple[str, ...],
  source: str,
) -> list[ReferenceHit]:
  """Extract references from named list-of-str fields on *artifact*."""
  hits: list[ReferenceHit] = []
  for field_name in field_names:
    for target in getattr(artifact, field_name, None) or []:
      target_str = str(target).strip()
      if target_str:
        hits.append(ReferenceHit(
          target=target_str, source=source, detail=field_name,
        ))
  return hits


def _collect_from_decision_fields(artifact: Any) -> list[ReferenceHit]:
  """Extract references from DecisionRecord domain fields."""
  return _collect_from_list_fields(artifact, _DECISION_REFERENCE_FIELDS, "domain_field")


def _collect_from_governance_fields(artifact: Any) -> list[ReferenceHit]:
  """Extract references from Policy/Standard domain fields."""
  return _collect_from_list_fields(
    artifact, _GOVERNANCE_REFERENCE_FIELDS, "domain_field",
  )


def _collect_from_requirement_fields(artifact: Any) -> list[ReferenceHit]:
  """Extract references from RequirementRecord domain fields."""
  hits: list[ReferenceHit] = []
  # Scalar field
  primary = getattr(artifact, "primary_spec", None)
  if primary:
    hits.append(ReferenceHit(
      target=str(primary).strip(), source="domain_field", detail="primary_spec",
    ))
  # List fields
  hits.extend(_collect_from_list_fields(
    artifact, _REQUIREMENT_REFERENCE_FIELDS, "domain_field",
  ))
  return hits


def _collect_from_backlog_fields(artifact: Any) -> list[ReferenceHit]:
  """Extract references from backlog-specific frontmatter fields.

  BacklogItem stores references in ``frontmatter`` (a dict), not as
  dataclass fields.  This collector handles ``linked_deltas``,
  ``related_requirements``, and ``relations`` from the frontmatter dict.
  """
  hits: list[ReferenceHit] = []
  frontmatter = getattr(artifact, "frontmatter", None)
  if not isinstance(frontmatter, dict):
    return hits
  for delta_id in frontmatter.get("linked_deltas", []):
    target = str(delta_id).strip()
    if target:
      hits.append(ReferenceHit(
        target=target, source="backlog_field", detail="linked_delta",
      ))
  for req_id in frontmatter.get("related_requirements", []):
    target = str(req_id).strip()
    if target:
      hits.append(ReferenceHit(
        target=target, source="backlog_field", detail="related_requirement",
      ))
  # BacklogItem.relations live in frontmatter dict, not as a dataclass field
  for rel in frontmatter.get("relations", []):
    if not isinstance(rel, dict):
      continue
    target = str(rel.get("target", "")).strip()
    if target:
      rel_type = str(rel.get("type", "")).strip()
      hits.append(ReferenceHit(
        target=target, source="relation", detail=rel_type,
      ))
  return hits


def _collect_from_domain_fields(artifact: Any) -> list[ReferenceHit]:
  """Extract references from domain-specific fields (non-relation).

  Chains all domain-family collectors. Uses ``getattr`` with defaults
  so fields that don't exist on a given model yield no hits.
  """
  return (
    _collect_from_decision_fields(artifact)
    + _collect_from_governance_fields(artifact)
    + _collect_from_requirement_fields(artifact)
    + _collect_from_backlog_fields(artifact)
  )


def collect_references(artifact: Any) -> list[ReferenceHit]:
  """Collect all forward references from an artifact.

  Searches the following slots when present on *artifact*:

  - ``.relations``  — ``list[dict]`` with ``type`` and ``target`` keys
  - ``.applies_to`` — ``dict`` with ``specs``, ``requirements``, ``prod`` keys
  - ``.context_inputs`` — ``list[dict]`` with ``type`` and ``id`` keys
  - ``.informed_by`` — ``list[str]`` (spec-specific)
  - Domain-specific fields via dedicated collectors (Decision, Governance,
    Requirement, BacklogItem models)

  Returns:
    List of :class:`ReferenceHit` with provenance for each reference found.
  """
  return (
    _collect_from_relations(artifact)
    + _collect_from_applies_to(artifact)
    + _collect_from_context_inputs(artifact)
    + _collect_from_informed_by(artifact)
    + _collect_from_domain_fields(artifact)
  )


def matches_related_to(artifact: Any, target_id: str) -> bool:
  """Return True if *artifact* references *target_id* in any slot.

  Matching is case-insensitive on target IDs.
  """
  target_lower = target_id.lower()
  return any(hit.target.lower() == target_lower for hit in collect_references(artifact))


def matches_relation(
  artifact: Any,
  *,
  relation_type: str | None = None,
  target: str | None = None,
) -> bool:
  """Return True if *artifact* has a ``.relations`` entry matching criteria.

  Searches only ``.relations``, not other reference slots.  At least one of
  *relation_type* or *target* must be provided.

  Args:
    artifact: Any object; gracefully returns False if no ``.relations``.
    relation_type: Filter by relation type (case-insensitive).
    target: Filter by target ID (case-insensitive).
  """
  if not relation_type and not target:
    return False

  relations: list[dict[str, Any]] = getattr(artifact, "relations", None) or []
  for rel in relations:
    if not isinstance(rel, dict):
      continue
    if relation_type:
      rel_type = str(rel.get("type", "")).strip().lower()
      if rel_type != relation_type.lower():
        continue
    if target:
      rel_target = str(rel.get("target", "")).strip().lower()
      if rel_target != target.lower():
        continue
    return True
  return False


def find_related_to(
  artifacts: Iterable[Any],
  target_id: str,
) -> list[Any]:
  """Filter *artifacts* that reference *target_id* in any slot.

  Case-insensitive matching on target IDs.
  """
  return [a for a in artifacts if matches_related_to(a, target_id)]


def find_by_relation(
  artifacts: Iterable[Any],
  *,
  relation_type: str | None = None,
  target: str | None = None,
) -> list[Any]:
  """Filter *artifacts* by ``.relations`` type and/or target.

  Searches only ``.relations``, not other reference slots.
  """
  return [
    a
    for a in artifacts
    if matches_relation(a, relation_type=relation_type, target=target)
  ]


__all__ = [
  "ReferenceHit",
  "RelationQueryable",
  "_collect_from_backlog_fields",
  "_collect_from_decision_fields",
  "_collect_from_domain_fields",
  "_collect_from_governance_fields",
  "_collect_from_requirement_fields",
  "collect_references",
  "find_by_relation",
  "find_related_to",
  "matches_related_to",
  "matches_relation",
]
