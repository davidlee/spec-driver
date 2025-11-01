"""Metadata-driven validation engine.

This module provides runtime validation of data against block metadata schemas.
The validator produces path-aware error messages for developer-friendly output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .schema import BlockMetadata, FieldMetadata


@dataclass
class ValidationError:
  """Validation error with path context.

  Attributes:
    path: Dot-notation path (e.g., "specs.primary[0]")
    message: Human-readable error message
    expected: Expected value/type (optional)
    actual: Actual value found (optional)
  """

  path: str
  message: str
  expected: str | None = None
  actual: str | None = None

  def __str__(self) -> str:
    """Format error for display."""
    parts = [f"{self.path}: {self.message}"]
    if self.expected:
      parts.append(f"expected {self.expected}")
    if self.actual:
      parts.append(f"got {self.actual}")
    return " - ".join(parts)


class MetadataValidator:
  """Validates data against block metadata definition.

  Usage:
    metadata = BlockMetadata(...)
    validator = MetadataValidator(metadata)
    errors = validator.validate(data)
    if errors:
      for error in errors:
        print(error)
  """

  def __init__(self, metadata: BlockMetadata):
    self.metadata = metadata

  def validate(self, data: dict[str, Any]) -> list[ValidationError]:
    """Validate data against metadata.

    Args:
      data: Parsed YAML data to validate

    Returns:
      List of validation errors (empty if valid)
    """
    errors: list[ValidationError] = []

    if not isinstance(data, dict):
      errors.append(
        ValidationError(
          path="<root>",
          message="block must be a mapping",
          expected="object",
          actual=type(data).__name__,
        )
      )
      return errors

    # Validate structure and types
    errors.extend(self._validate_fields(data, self.metadata.fields, ""))

    # Validate conditional rules
    if self.metadata.conditional_rules:
      errors.extend(self._validate_conditional_rules(data))

    return errors

  def _validate_fields(
    self,
    data: dict[str, Any],
    fields: dict[str, FieldMetadata],
    parent_path: str,
  ) -> list[ValidationError]:
    """Validate fields recursively."""
    errors: list[ValidationError] = []

    # Check required fields
    for field_name, field_meta in fields.items():
      field_path = f"{parent_path}.{field_name}" if parent_path else field_name

      if field_meta.required and field_name not in data:
        errors.append(ValidationError(path=field_path, message="is required"))
        continue

      if field_name not in data:
        continue  # Optional field not present

      value = data[field_name]
      errors.extend(self._validate_field(value, field_meta, field_path))

    return errors

  def _validate_field(
    self, value: Any, field_meta: FieldMetadata, field_path: str
  ) -> list[ValidationError]:
    """Validate a single field value."""
    errors: list[ValidationError] = []

    # Type-specific validation
    if field_meta.type == "const":
      if value != field_meta.const_value:
        errors.append(
          ValidationError(
            path=field_path,
            message="must equal constant value",
            expected=str(field_meta.const_value),
            actual=str(value),
          )
        )

    elif field_meta.type == "enum":
      if value not in field_meta.enum_values:
        errors.append(
          ValidationError(
            path=field_path,
            message="must be one of allowed values",
            expected=", ".join(str(v) for v in field_meta.enum_values),
            actual=str(value),
          )
        )

    elif field_meta.type == "string":
      if not isinstance(value, str):
        errors.append(
          ValidationError(
            path=field_path,
            message="must be a string",
            expected="string",
            actual=type(value).__name__,
          )
        )
      elif field_meta.pattern and not re.match(field_meta.pattern, value):
        errors.append(
          ValidationError(
            path=field_path,
            message="does not match required pattern",
            expected=f"pattern: {field_meta.pattern}",
            actual=value,
          )
        )

    elif field_meta.type == "int":
      if not isinstance(value, int) or isinstance(value, bool):
        errors.append(
          ValidationError(
            path=field_path,
            message="must be an integer",
            expected="int",
            actual=type(value).__name__,
          )
        )

    elif field_meta.type == "bool":
      if not isinstance(value, bool):
        errors.append(
          ValidationError(
            path=field_path,
            message="must be a boolean",
            expected="bool",
            actual=type(value).__name__,
          )
        )

    elif field_meta.type == "object":
      if not isinstance(value, dict):
        errors.append(
          ValidationError(
            path=field_path,
            message="must be an object",
            expected="object",
            actual=type(value).__name__,
          )
        )
      elif field_meta.properties:
        # Recursively validate nested object
        errors.extend(self._validate_fields(value, field_meta.properties, field_path))

    elif field_meta.type == "array":
      if not isinstance(value, list):
        errors.append(
          ValidationError(
            path=field_path,
            message="must be an array",
            expected="array",
            actual=type(value).__name__,
          )
        )
      else:
        # Check array length constraints
        if field_meta.min_items is not None and len(value) < field_meta.min_items:
          errors.append(
            ValidationError(
              path=field_path,
              message=f"must have at least {field_meta.min_items} items",
              actual=f"{len(value)} items",
            )
          )
        if field_meta.max_items is not None and len(value) > field_meta.max_items:
          errors.append(
            ValidationError(
              path=field_path,
              message=f"must have at most {field_meta.max_items} items",
              actual=f"{len(value)} items",
            )
          )

        # Validate array items
        if field_meta.items:
          for idx, item in enumerate(value):
            item_path = f"{field_path}[{idx}]"
            errors.extend(self._validate_field(item, field_meta.items, item_path))

    return errors

  def _validate_conditional_rules(self, data: dict[str, Any]) -> list[ValidationError]:
    """Validate conditional rules (if/then logic)."""
    errors: list[ValidationError] = []

    for rule in self.metadata.conditional_rules:
      # Get condition field value (supports nested paths)
      condition_value = self._get_nested_value(data, rule.condition_field)

      # Check if condition matches
      if condition_value == rule.condition_value:
        # Condition triggered - check required fields
        for required_field in rule.requires:
          if not self._has_nested_value(data, required_field):
            expected_msg = None
            if rule.description:
              expected_msg = f"field present (due to: {rule.description})"

            condition_desc = f"{rule.condition_field}={rule.condition_value}"
            errors.append(
              ValidationError(
                path=required_field,
                message=f"is required when {condition_desc}",
                expected=expected_msg,
              )
            )

    return errors

  def _get_nested_value(self, data: dict[str, Any], path: str) -> Any:
    """Get value from nested path (e.g., 'metadata.revision')."""
    parts = path.split(".")
    current = data
    for part in parts:
      if not isinstance(current, dict) or part not in current:
        return None
      current = current[part]
    return current

  def _has_nested_value(self, data: dict[str, Any], path: str) -> bool:
    """Check if nested path exists."""
    return self._get_nested_value(data, path) is not None


__all__ = [
  "MetadataValidator",
  "ValidationError",
]
