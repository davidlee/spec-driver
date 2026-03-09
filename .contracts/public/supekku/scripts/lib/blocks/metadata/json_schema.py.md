# supekku.scripts.lib.blocks.metadata.json_schema

JSON Schema generation from block metadata.

This module translates block metadata into JSON Schema Draft 2020-12 for
agent consumption and validation tooling integration.

## Functions

- `metadata_to_json_schema(metadata) -> dict[Tuple[str, Any]]`: Generate JSON Schema Draft 2020-12 from block metadata.

Args:
  metadata: Block metadata definition

Returns:
  JSON Schema dictionary
