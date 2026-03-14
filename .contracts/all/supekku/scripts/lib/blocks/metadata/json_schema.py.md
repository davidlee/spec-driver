# supekku.scripts.lib.blocks.metadata.json_schema

JSON Schema generation from block metadata.

This module translates block metadata into JSON Schema Draft 2020-12 for
agent consumption and validation tooling integration.

## Constants

- `__all__`

## Functions

- `_build_conditional_rules(rules) -> list[dict[Tuple[str, Any]]]`: Build allOf conditional rules for JSON Schema.
- `_build_field_schema(field) -> dict[Tuple[str, Any]]`: Build JSON Schema for a single field.
- `_build_properties(fields) -> dict[Tuple[str, Any]]`: Build properties object from field metadata.
- `metadata_to_json_schema(metadata) -> dict[Tuple[str, Any]]`: Generate JSON Schema Draft 2020-12 from block metadata.

Args:
  metadata: Block metadata definition

Returns:
  JSON Schema dictionary
