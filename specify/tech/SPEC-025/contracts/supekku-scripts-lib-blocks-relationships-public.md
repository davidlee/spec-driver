# supekku.scripts.lib.blocks.relationships

Utilities for parsing structured spec YAML blocks.

## Constants

- `CAPABILITIES_MARKER`
- `CAPABILITIES_SCHEMA`
- `CAPABILITIES_VERSION`
- `RELATIONSHIPS_MARKER`
- `RELATIONSHIPS_SCHEMA`
- `RELATIONSHIPS_VERSION`

## Functions

- `extract_relationships(block) -> <BinOp>`: Extract and parse relationships block from markdown content.

Args:
  block: Markdown content containing relationships block.

Returns:
  Parsed RelationshipsBlock or None if not found.

Raises:
  ValueError: If YAML is invalid or doesn't parse to a mapping.
- `load_relationships_from_file(path) -> <BinOp>`: Load and extract relationships block from file.

Args:
  path: Path to markdown file.

Returns:
  Parsed RelationshipsBlock or None if not found.
- `render_spec_capabilities_block(spec_id) -> str`: Render a spec capabilities YAML block with given values.

This is the canonical source for the block structure. Templates and
creation code should use this instead of hardcoding the structure.

Args:
  spec_id: The specification ID.
  capabilities: List of capability dicts with:
    - id: str (kebab-case identifier)
    - name: str (human-readable name)
    - responsibilities: list[str] | None
    - requirements: list[str] | None
    - summary: str
    - success_criteria: list[str] | None

Returns:
  Formatted YAML code block as string.
- `render_spec_relationships_block(spec_id) -> str`: Render a spec relationships YAML block with given values.

This is the canonical source for the block structure. Templates and
creation code should use this instead of hardcoding the structure.

Args:
  spec_id: The specification ID.
  primary_requirements: List of primary requirement codes
    (e.g., ["FR-001", "FR-002"]).
  collaborator_requirements: List of collaborator requirement codes.
  interactions: List of interaction dicts with 'type' and 'spec' keys.

Returns:
  Formatted YAML code block as string.

## Classes

### RelationshipsBlock

Parsed YAML block containing specification relationships.

### RelationshipsBlockValidator

Validator for specification relationships blocks.

#### Methods

- `validate(self, block) -> list[str]`: Validate relationships block against schema.

Args:
  block: Parsed relationships block to validate.
  spec_id: Optional expected spec ID to match against.

Returns:
  List of error messages (empty if valid).
