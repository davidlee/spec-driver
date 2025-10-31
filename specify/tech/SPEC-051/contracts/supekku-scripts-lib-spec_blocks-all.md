# supekku.scripts.lib.spec_blocks

Utilities for parsing structured spec YAML blocks.

## Constants

- `RELATIONSHIPS_MARKER`
- `RELATIONSHIPS_SCHEMA`
- `RELATIONSHIPS_VERSION`
- `_RELATIONSHIPS_PATTERN`
- `__all__`

## Functions

- `extract_relationships(block) -> <BinOp>`
- `load_relationships_from_file(path) -> <BinOp>`

## Classes

### RelationshipsBlock

Parsed YAML block containing specification relationships.

### RelationshipsBlockValidator

Validator for specification relationships blocks.

#### Methods

- `validate(self, block) -> list[str]`
