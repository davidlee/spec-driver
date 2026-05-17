"""Metadata schema definitions for block validation.

This module defines the core data structures for declarative block validation.
Metadata drives both runtime validation and JSON Schema generation.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToleratedAlias:
  """Time-bounded alias for a field VALUE.

  Tolerated aliases live in `FieldMetadata.tolerated_aliases`. They are
  accepted at read time so unmigrated payloads continue to load, but the
  ``--no-tolerated-aliases`` strict mode rejects them, and ``--fix`` does
  not rewrite them (migration concern; rides through ``admin migrate``).

  Attributes:
    canonical: Canonical value that this alias maps to.
    sunset_after: Delta ID or semver (e.g. ``"DE-140"`` or ``"0.11.0"``)
      after which the alias should be retired.
    rationale: Short explanation of why the alias is tolerated.
  """

  canonical: str
  sunset_after: str
  rationale: str


@dataclass
class FieldMetadata:
  """Metadata for a single field in a block schema.

  Attributes:
    type: Field type (string, int, bool, object, array, const, enum)
    required: Whether field is required in the data
    pattern: Regex pattern for string validation
    const_value: Fixed value for const type
    enum_values: Allowed values for enum type
    properties: Nested field metadata for object type (declared keys)
    items: Item metadata for array type
    description: Human-readable field description
    min_items: Minimum array length (for array type)
    max_items: Maximum array length (for array type)
    persistence: Compaction classification — canonical (always persist),
      derived (reconstructible; omit by default), optional (omit when
      absent/default), default-omit (omit when equal to default_value).
    default_value: Value that signals "omit during compaction" for
      optional/default-omit fields (e.g. [] for empty arrays).
    additional_properties: Shape applied to keys not in `properties`
      (object type). Combines with `properties` for hybrid declared-plus-
      dynamic objects, or stands alone for fully dynamic-key maps. Object
      type requires `properties`, `additional_properties`, or both.
    aliases: Permanent field-VALUE alias map ``{alias_value: canonical_value}``.
      Applied after per-field dispatch. Same strict/--fix semantics as
      ``BlockMetadata.field_aliases``, scoped to value rewrites. Example
      (delta status FieldMetadata): ``{"complete": "completed"}``.
    tolerated_aliases: Migration-window field-VALUE alias map. Accepted
      under default strict; rejected under ``--no-tolerated-aliases``;
      ``--fix`` ignores them (migrations rewrite during ``admin migrate``).
    field_aliases: Field-NAME alias map for nested object schemas, mirroring
      ``BlockMetadata.field_aliases``. Carried on object-typed FieldMetadata
      so nested schemas (e.g. the relations item) can declare key renames at
      their own layer rather than only at the top-level block.
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
  persistence: str = "canonical"
  default_value: Any = None
  additional_properties: FieldMetadata | None = None
  aliases: Mapping[str, str] | None = None
  tolerated_aliases: Mapping[str, ToleratedAlias] | None = None
  field_aliases: Mapping[str, str] | None = None

  _VALID_PERSISTENCE = frozenset(
    {
      "canonical",
      "derived",
      "optional",
      "default-omit",
    }
  )

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

    if self.persistence not in self._VALID_PERSISTENCE:
      msg = f"Invalid persistence: {self.persistence}"
      raise ValueError(msg)

    if self.type == "const" and self.const_value is None:
      msg = "const type requires const_value"
      raise ValueError(msg)

    if self.type == "enum" and not self.enum_values:
      msg = "enum type requires enum_values"
      raise ValueError(msg)

    if (
      self.type == "object"
      and not self.properties
      and self.additional_properties is None
    ):
      msg = "object type requires properties or additional_properties"
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
    field_aliases: Field-NAME alias map ``{alias_key: canonical_key}``.
      Applied at parse time: when ``alias_key`` is present in the parsed
      YAML the validator renames it to ``canonical_key`` before per-field
      dispatch. Example (relations item BlockMetadata):
      ``{"annotation": "nature"}``. Loaders apply silently when
      ``strict=False``; under strict the rename emits a warning whose
      ``--fix`` rewrites the source key.
  """

  version: int
  schema_id: str
  fields: dict[str, FieldMetadata]
  conditional_rules: list[ConditionalRule] = field(default_factory=list)
  description: str = ""
  examples: list[dict[str, Any]] = field(default_factory=list)
  field_aliases: Mapping[str, str] | None = None


__all__ = [
  "BlockMetadata",
  "ConditionalRule",
  "FieldMetadata",
  "ToleratedAlias",
]
