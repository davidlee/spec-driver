# supekku.scripts.lib.blocks.schema_registry

Central registry of block schemas for documentation and tooling.

## Functions

- `get_block_schema(block_type) -> <BinOp>`: Get schema for block type.

Args:
  block_type: Block type identifier

Returns:
  BlockSchema instance or None if not found
- `list_block_types() -> list[str]`: List all registered block types.

Returns:
  Sorted list of block type identifiers
- `register_block_schema(block_type, schema) -> None`: Register a block schema.

Args:
  block_type: Block type identifier (e.g., "delta.relationships")
  schema: BlockSchema instance to register

## Classes

### BlockSchema

Schema information for a YAML block type.

#### Methods

- `get_parameters(self) -> dict[Tuple[str, Any]]`: Extract parameters from renderer function signature.

Returns:
  Dictionary mapping parameter names to their metadata:
    - 'required': bool - whether parameter is required
    - 'type': type annotation or 'Any'
    - 'default': default value or None - Human-readable description
