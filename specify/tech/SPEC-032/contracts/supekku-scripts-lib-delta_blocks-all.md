# supekku.scripts.lib.delta_blocks

Utilities for parsing structured delta YAML blocks.

## Constants

- `RELATIONSHIPS_MARKER`
- `RELATIONSHIPS_SCHEMA`
- `RELATIONSHIPS_VERSION`
- `_BLOCK_PATTERN`
- `__all__`

## Functions

- `extract_delta_relationships(text) -> <BinOp>`
- `load_delta_relationships(path) -> <BinOp>`

## Classes

### DeltaRelationshipsBlock

Parsed YAML block containing delta relationships.

### DeltaRelationshipsValidator

Validator for delta relationships blocks.

#### Methods

- `validate(self, block) -> list[str]`
