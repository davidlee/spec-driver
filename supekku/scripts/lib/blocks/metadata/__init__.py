"""Metadata-driven block validation system.

This package provides a declarative approach to block validation where
a single metadata definition drives both runtime validation and JSON Schema
generation for agent consumption.
"""

from .schema import BlockMetadata, ConditionalRule, FieldMetadata

__all__ = [
  "BlockMetadata",
  "ConditionalRule",
  "FieldMetadata",
]
