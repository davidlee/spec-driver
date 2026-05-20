# supekku.scripts.lib.blocks.metadata.schema_test

Tests for the metadata schema dataclasses (DE-137 IP-137-P01 task 1.3).

Covers the alias-mechanism extensions:
- `ToleratedAlias`
- `FieldMetadata.aliases` / `.tolerated_aliases`
- `BlockMetadata.field_aliases`

## Functions

- `_enum_field() -> FieldMetadata`
- `test_block_metadata_accepts_field_aliases_mapping() -> None`
- `test_block_metadata_field_aliases_default_none() -> None`
- `test_existing_field_metadata_construction_unchanged() -> None`: Pre-existing constructions without aliases continue to work.
- `test_field_metadata_accepts_aliases_mapping() -> None`
- `test_field_metadata_accepts_field_aliases_mapping() -> None`: Nested object schemas (e.g. relations item) carry their own field_aliases.
- `test_field_metadata_accepts_mappingproxytype_for_aliases() -> None`
- `test_field_metadata_accepts_tolerated_aliases_with_metadata_value() -> None`
- `test_field_metadata_aliases_default_none() -> None`
- `test_field_metadata_field_aliases_default_none() -> None`
- `test_field_metadata_replace_preserves_aliases() -> None`
- `test_tolerated_alias_is_frozen_dataclass() -> None`
