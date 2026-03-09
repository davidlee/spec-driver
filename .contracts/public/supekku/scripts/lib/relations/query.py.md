# supekku.scripts.lib.relations.query

Generic relation query functions for artifact reference discovery.

Pure functions that operate on any artifact conforming to
:class:`RelationQueryable`.  Additional reference slots (``.applies_to``,
``.context_inputs``, ``.informed_by``) are searched when present but are
not required by the protocol.

Design reference: DR-085 §5.2.

## Functions

- `collect_references(artifact) -> list[ReferenceHit]`: Collect all forward references from an artifact.

Searches the following slots when present on *artifact*:

- ``.relations``  — ``list[dict]`` with ``type`` and ``target`` keys
- ``.applies_to`` — ``dict`` with ``specs``, ``requirements``, ``prod`` keys
- ``.context_inputs`` — ``list[dict]`` with ``type`` and ``id`` keys
- ``.informed_by`` — ``list[str]`` (spec-specific)

Returns:
  List of :class:`ReferenceHit` with provenance for each reference found.
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

## Classes

### ReferenceHit

A matched forward reference with provenance.

Attributes:
  target: The referenced artifact ID.
  source: Which slot the reference came from
      (``"relation"``, ``"applies_to"``, ``"context_input"``,
      ``"informed_by"``).
  detail: Slot-specific qualifier whose meaning varies by *source*:

      - ``source="relation"``: the relation type
        (e.g. ``"implements"``, ``"depends_on"``)
      - ``source="applies_to"``: the applies_to key
        (e.g. ``"spec"``, ``"requirement"``, ``"prod"``)
      - ``source="context_input"``: the context input type
        (e.g. ``"issue"``, ``"research"``)
      - ``source="informed_by"``: always ``"adr"``

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
