# supekku.scripts.lib.blocks.metadata.schema

Metadata schema definitions for block validation.

This module defines the core data structures for declarative block validation.
Metadata drives both runtime validation and JSON Schema generation.

## Constants

- `__all__`

## Classes

### BlockMetadata

Complete metadata for a block schema.

This is the single source of truth for validation and documentation.

Attributes:
  version: Schema version number
  schema_id: Fully qualified schema identifier
  fields: Mapping of field names to their metadata
  conditional_rules: Optional list of conditional validation rules
  description: Human-readable block description
  examples: Example blocks for documentation

### ConditionalRule

Conditional validation rule (if/then logic).

Represents rules like "if field X has value Y, then fields Z are required".

Attributes:
  condition_field: Field path to check (e.g., "action")
  condition_value: Value that triggers the rule
  requires: List of field paths that become required
  description: Human-readable rule description

### FieldMetadata

Metadata for a single field in a block schema.

Attributes:
  type: Field type (string, int, bool, object, array, const, enum)
  required: Whether field is required in the data
  pattern: Regex pattern for string validation
  const_value: Fixed value for const type
  enum_values: Allowed values for enum type
  properties: Nested field metadata for object type
  items: Item metadata for array type
  description: Human-readable field description
  min_items: Minimum array length (for array type)
  max_items: Maximum array length (for array type)

#### Methods

- `__post_init__(self) -> None`: Validate field metadata consistency.
