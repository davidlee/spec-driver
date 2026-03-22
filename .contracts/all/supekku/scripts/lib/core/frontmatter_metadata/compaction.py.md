# supekku.scripts.lib.core.frontmatter_metadata.compaction

Frontmatter compaction using FieldMetadata persistence annotations.

Pure function that strips default/derived fields from frontmatter data
based on BlockMetadata field classifications. See DR-036 §7 (DEC-036-004)
and phase-01 §10.5 for compaction semantics.

## Constants

- `_VALID_MODES`
- `__all__`

## Functions

- `_should_keep(persistence, value, default_value) -> bool`: Decide whether a field should be kept during compaction.
- `compact_frontmatter(data, metadata, mode) -> dict[Tuple[str, Any]]`: Remove default/derived fields from frontmatter data.

Applies persistence semantics per field classification:

- canonical: always kept
- derived: omitted in compact mode
- optional: omitted when absent, None, or equal to default_value
- default-omit: omitted when equal to default_value

Fields present in data but absent from metadata pass through unchanged.

Args:
data: Frontmatter dict to compact.
metadata: BlockMetadata with field persistence annotations.
mode: "compact" (default) strips per rules; "full" preserves everything.

Returns:
New dict with omitted fields removed. Input is not mutated.

Raises:
ValueError: If mode is not "compact" or "full".
