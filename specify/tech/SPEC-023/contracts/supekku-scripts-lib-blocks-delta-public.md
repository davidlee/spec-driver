# supekku.scripts.lib.blocks.delta

Utilities for parsing structured delta YAML blocks.

## Constants

- `RELATIONSHIPS_MARKER`
- `RELATIONSHIPS_SCHEMA`
- `RELATIONSHIPS_VERSION`

## Functions

- `extract_delta_relationships(text) -> <BinOp>`: Extract delta relationships block from markdown text.
- `load_delta_relationships(path) -> <BinOp>`: Load and extract delta relationships block from file.

## Classes

### DeltaRelationshipsBlock

Parsed YAML block containing delta relationships.

### DeltaRelationshipsValidator

Validator for delta relationships blocks.

#### Methods

- `validate(self, block) -> list[str]`: Validate delta relationships block structure and content.
