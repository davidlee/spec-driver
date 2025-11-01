"""JSON Schema generation from block metadata.

This module translates block metadata into JSON Schema Draft 2020-12 for
agent consumption and validation tooling integration.
"""

from __future__ import annotations

from typing import Any

from .schema import BlockMetadata, ConditionalRule, FieldMetadata


def metadata_to_json_schema(metadata: BlockMetadata) -> dict[str, Any]:
  """Generate JSON Schema Draft 2020-12 from block metadata.

  Args:
    metadata: Block metadata definition

  Returns:
    JSON Schema dictionary
  """
  schema_id = metadata.schema_id.replace(".", "-")
  schema: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": (
      f"https://vice.supekku.dev/schemas/{schema_id}@v{metadata.version}.json"
    ),
    "title": f"Supekku {metadata.schema_id} Block",
    "type": "object",
  }

  if metadata.description:
    schema["description"] = metadata.description

  # Build required fields list
  required = [name for name, field in metadata.fields.items() if field.required]
  if required:
    schema["required"] = required

  # Build properties
  schema["properties"] = _build_properties(metadata.fields)

  # Add examples if available
  if metadata.examples:
    schema["examples"] = metadata.examples

  # Add conditional rules as allOf
  if metadata.conditional_rules:
    schema["allOf"] = _build_conditional_rules(metadata.conditional_rules)

  return schema


def _build_properties(fields: dict[str, FieldMetadata]) -> dict[str, Any]:
  """Build properties object from field metadata."""
  properties = {}

  for name, field in fields.items():
    properties[name] = _build_field_schema(field)

  return properties


def _build_field_schema(field: FieldMetadata) -> dict[str, Any]:
  """Build JSON Schema for a single field."""
  schema: dict[str, Any] = {}

  if field.description:
    schema["description"] = field.description

  if field.type == "const":
    schema["const"] = field.const_value

  elif field.type == "enum":
    schema["enum"] = field.enum_values

  elif field.type == "string":
    schema["type"] = "string"
    if field.pattern:
      schema["pattern"] = field.pattern

  elif field.type == "int":
    schema["type"] = "integer"

  elif field.type == "bool":
    schema["type"] = "boolean"

  elif field.type == "object":
    schema["type"] = "object"
    if field.properties:
      schema["properties"] = _build_properties(field.properties)
      # Find required properties
      required = [name for name, prop in field.properties.items() if prop.required]
      if required:
        schema["required"] = required

  elif field.type == "array":
    schema["type"] = "array"
    if field.items:
      schema["items"] = _build_field_schema(field.items)
    if field.min_items is not None:
      schema["minItems"] = field.min_items
    if field.max_items is not None:
      schema["maxItems"] = field.max_items

  return schema


def _build_conditional_rules(
  rules: list[ConditionalRule],
) -> list[dict[str, Any]]:
  """Build allOf conditional rules for JSON Schema."""
  all_of = []

  for rule in rules:
    # Build if/then structure
    condition_parts = rule.condition_field.split(".")

    # Simple case: top-level field
    if len(condition_parts) == 1:
      all_of.append(
        {
          "if": {"properties": {rule.condition_field: {"const": rule.condition_value}}},
          "then": {"required": rule.requires},
        }
      )
    else:
      # Nested field - build nested structure
      # For now, handle one level of nesting
      parent = condition_parts[0]
      child = condition_parts[1]
      all_of.append(
        {
          "if": {
            "properties": {
              parent: {"properties": {child: {"const": rule.condition_value}}}
            }
          },
          "then": {"required": rule.requires},
        }
      )

  return all_of


__all__ = [
  "metadata_to_json_schema",
]
