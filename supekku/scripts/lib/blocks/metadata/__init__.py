"""Metadata-driven block validation system.

This package provides a declarative approach to block validation where
a single metadata definition drives both runtime validation and JSON Schema
generation for agent consumption.
"""

from .json_schema import metadata_to_json_schema
from .schema import BlockMetadata, ConditionalRule, FieldMetadata, ToleratedAlias
from .validator import MetadataValidator, ValidationError

__all__ = [
  "BlockMetadata",
  "ConditionalRule",
  "FieldMetadata",
  "MetadataValidator",
  "ToleratedAlias",
  "ValidationError",
  "metadata_to_json_schema",
]
