# supekku.scripts.lib.relations.query

Generic relation query functions for artifact reference discovery.

Pure functions that operate on any artifact conforming to
:class:`RelationQueryable`.  Additional reference slots (``.applies_to``,
``.context_inputs``, ``.informed_by``) are searched when present but are
not required by the protocol.

Design reference: DR-085 §5.2.

## Constants

- `__all__`

## Functions

- `_collect_from_applies_to(artifact) -> list[ReferenceHit]`: Extract references from ``.applies_to`` (dict of spec/req/prod lists).
- `_collect_from_backlog_fields(artifact) -> list[ReferenceHit]`: Extract references from backlog-specific frontmatter fields.

BacklogItem stores references in ``frontmatter`` (a dict), not as
dataclass fields.  This collector handles ``linked_deltas``,
``related_requirements``, and ``relations`` from the frontmatter dict.
- `_collect_from_context_inputs(artifact) -> list[ReferenceHit]`: Extract references from ``.context_inputs`` (list of type/id dicts).
- `_collect_from_decision_fields(artifact) -> list[ReferenceHit]`: Extract references from DecisionRecord domain fields.
- `_collect_from_domain_fields(artifact) -> list[ReferenceHit]`: Extract references from domain-specific fields (non-relation).

Chains all domain-family collectors. Uses ``getattr`` with defaults
so fields that don't exist on a given model yield no hits.
- `_collect_from_governance_fields(artifact) -> list[ReferenceHit]`: Extract references from Policy/Standard domain fields.
- `_collect_from_informed_by(artifact) -> list[ReferenceHit]`: Extract references from ``.informed_by`` (list of ADR IDs).
- `_collect_from_list_fields(artifact, field_names, source) -> list[ReferenceHit]`: Extract references from named list-of-str fields on *artifact*.
- `_collect_from_relations(artifact) -> list[ReferenceHit]`: Extract references from ``.relations`` (list of type/target dicts).
- `_collect_from_requirement_fields(artifact) -> list[ReferenceHit]`: Extract references from RequirementRecord domain fields.
- `collect_references(artifact) -> list[ReferenceHit]`: Collect all forward references from an artifact.

Searches the following slots when present on *artifact*:

- ``.relations``  — ``list[dict]`` with ``type`` and ``target`` keys
- ``.applies_to`` — ``dict`` with ``specs``, ``requirements``, ``prod`` keys
- ``.context_inputs`` — ``list[dict]`` with ``type`` and ``id`` keys
- ``.informed_by`` — ``list[str]`` (spec-specific)
- Domain-specific fields via dedicated collectors (Decision, Governance,
  Requirement, BacklogItem models)

Returns:
  List of :class:`ReferenceHit` with provenance for each reference found.
- `collect_reverse_reference_targets(referrers) -> set[str]`: Collect all target IDs referenced by a set of artifacts.

Returns a set of uppercased target IDs for O(1) membership testing.
- `find_by_relation(artifacts) -> list[Any]`: Filter *artifacts* by ``.relations`` type and/or target.

Searches only ``.relations``, not other reference slots.
- `find_related_to(artifacts, target_id) -> list[Any]`: Filter *artifacts* that reference *target_id* in any slot.

Case-insensitive matching on target IDs.
- `matches_related_to(artifact, target_id) -> bool`: Return True if *artifact* references *target_id* in any slot.

Matching is case-insensitive on target IDs.
- `matches_relation(artifact) -> bool`: Return True if *artifact* has a ``.relations`` entry matching criteria.

Searches only ``.relations``, not other reference slots.  At least one of
*relation_type* or *target* must be provided.

Args:
  artifact: Any object; gracefully returns False if no ``.relations``.
  relation_type: Filter by relation type (case-insensitive).
  target: Filter by target ID (case-insensitive).
- `partition_by_reverse_references(candidates, referrers, candidate_id_fn) -> tuple[Tuple[list[T], list[T]]]`: Partition candidates into (referenced, unreferenced) by referrers.

Returns a tuple of two lists:
  - candidates whose ID appears as a target in any referrer's references
  - candidates whose ID does not

## Classes

### ReferenceHit

A matched forward reference with provenance.

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

### RelationQueryable

Artifact that exposes relations as ``list[dict]`` with type/target keys.

Additional reference slots (``.applies_to``, ``.context_inputs``,
``.informed_by``) are searched by :func:`collect_references` when present
but are not required by this protocol.

Single-property Protocol is intentional — see ADR-009.

*pylint: disable=too-few-public-methods*

**Inherits from:** Protocol

#### Methods

- @property `relations(self) -> list[dict[Tuple[str, Any]]]`: Structured relation dicts with ``type`` and ``target`` keys.
