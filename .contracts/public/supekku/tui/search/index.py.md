# supekku.tui.search.index

Search index builder — flattens registry records to a searchable surface.

Self-contained: instantiates its own registries via `_REGISTRY_FACTORIES`.
No dependency on :class:`ArtifactSnapshot`.

Design reference: DR-087 DEC-087-01, DEC-087-05.

## Constants

- `FIELD_ID` - Field name constants for searchable_fields keys (POL-002).
- `FIELD_STATUS`
- `FIELD_TITLE` - Field name constants for searchable_fields keys (POL-002).
- `logger`

## Functions

- `build_search_index() -> list[SearchEntry]`: Build a search index from fresh registry instances.

Iterates all artifact types, instantiates each registry, calls
`collect()`, and flattens records into :class:`SearchEntry` values.

Returns:
List of search entries covering all loadable artifact types.

## Classes

### SearchEntry

A single searchable artifact with flattened fields and relation targets.

Attributes:
entry: The normalised view model for display and navigation.
searchable_fields: `field_name -> text` mapping for the scorer.
relation_targets: Forward-referenced artifact IDs for lower-weight matching.
