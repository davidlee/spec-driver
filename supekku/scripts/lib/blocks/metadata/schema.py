"""Metadata schema definitions for block validation.

This module defines the core data structures for declarative block validation.
Metadata drives both runtime validation and JSON Schema generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldMetadata:
  """Metadata for a single field in a block schema.

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
  """

  type: str
  required: bool = False
  pattern: str | None = None
  const_value: Any | None = None
  enum_values: list[Any] | None = None
  properties: dict[str, FieldMetadata] | None = None
  items: FieldMetadata | None = None
  description: str = ""
  min_items: int | None = None
  max_items: int | None = None

  def __post_init__(self) -> None:
    """Validate field metadata consistency."""
    valid_types = {
      "string",
      "int",
      "bool",
      "object",
      "array",
      "const",
      "enum",
    }
    if self.type not in valid_types:
      msg = f"Invalid field type: {self.type}"
      raise ValueError(msg)

    if self.type == "const" and self.const_value is None:
      msg = "const type requires const_value"
      raise ValueError(msg)

    if self.type == "enum" and not self.enum_values:
      msg = "enum type requires enum_values"
      raise ValueError(msg)

    if self.type == "object" and not self.properties:
      msg = "object type requires properties"
      raise ValueError(msg)

    if self.type == "array" and not self.items:
      msg = "array type requires items"
      raise ValueError(msg)


@dataclass
class ConditionalRule:
  """Conditional validation rule (if/then logic).

  Represents rules like "if field X has value Y, then fields Z are required".

  Attributes:
    condition_field: Field path to check (e.g., "action")
    condition_value: Value that triggers the rule
    requires: List of field paths that become required
    description: Human-readable rule description
  """

  condition_field: str
  condition_value: Any
  requires: list[str]
  description: str = ""


@dataclass
class BlockMetadata:
  """Complete metadata for a block schema.

  This is the single source of truth for validation and documentation.

  Attributes:
    version: Schema version number
    schema_id: Fully qualified schema identifier
    fields: Mapping of field names to their metadata
    conditional_rules: Optional list of conditional validation rules
    description: Human-readable block description
    examples: Example blocks for documentation
  """

  version: int
  schema_id: str
  fields: dict[str, FieldMetadata]
  conditional_rules: list[ConditionalRule] = field(default_factory=list)
  description: str = ""
  examples: list[dict[str, Any]] = field(default_factory=list)


__all__ = [
  "BlockMetadata",
  "ConditionalRule",
  "FieldMetadata",
]
