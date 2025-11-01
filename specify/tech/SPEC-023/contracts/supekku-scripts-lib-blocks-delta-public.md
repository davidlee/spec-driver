# supekku.scripts.lib.blocks.delta

Utilities for parsing structured delta YAML blocks.

## Constants

- `RELATIONSHIPS_MARKER`
- `RELATIONSHIPS_SCHEMA`
- `RELATIONSHIPS_VERSION`

## Functions

- `extract_delta_relationships(text) -> <BinOp>`: Extract delta relationships block from markdown text.
- `load_delta_relationships(path) -> <BinOp>`: Load and extract delta relationships block from file.
- `render_delta_relationships_block(delta_id) -> str`: Render a delta relationships YAML block with given values.

This is the canonical source for the block structure. Templates and
creation code should use this instead of hardcoding the structure.

Args:
  delta_id: The delta ID.
  primary_specs: List of primary spec IDs.
  collaborator_specs: List of collaborator spec IDs.
  implements_requirements: List of requirement IDs this implements.
  updates_requirements: List of requirement IDs this updates.
  verifies_requirements: List of requirement IDs this verifies.
  phases: List of phase IDs.
  introduces_revisions: List of revision IDs this introduces.
  supersedes_revisions: List of revision IDs this supersedes.

Returns:
  Formatted YAML code block as string.

## Classes

### DeltaRelationshipsBlock

Parsed YAML block containing delta relationships.

### DeltaRelationshipsValidator

Validator for delta relationships blocks.

#### Methods

- `validate(self, block) -> list[str]`: Validate delta relationships block structure and content.
