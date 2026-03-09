# supekku.scripts.lib.blocks.metadata.validator

Metadata-driven validation engine.

This module provides runtime validation of data against block metadata schemas.
The validator produces path-aware error messages for developer-friendly output.

## Constants

- `__all__`

## Classes

### MetadataValidator

Validates data against block metadata definition.

Usage:
  metadata = BlockMetadata(...)
  validator = MetadataValidator(metadata)
  errors = validator.validate(data)
  if errors:
    for error in errors:
      print(error)

#### Methods

- `validate(self, data) -> list[ValidationError]`: Validate data against metadata.

Args:
  data: Parsed YAML data to validate

Returns:
  List of validation errors (empty if valid)
- `__init__(self, metadata)`
- `_get_nested_value(self, data, path) -> Any`: Get value from nested path (e.g., 'metadata.revision').
- `_has_nested_value(self, data, path) -> bool`: Check if nested path exists.
- `_validate_conditional_rules(self, data) -> list[ValidationError]`: Validate conditional rules (if/then logic).
- `_validate_field(self, value, field_meta, field_path) -> list[ValidationError]`: Validate a single field value.
- `_validate_fields(self, data, fields, parent_path) -> list[ValidationError]`: Validate fields recursively.

### ValidationError

Validation error with path context.

Attributes:
  path: Dot-notation path (e.g., "specs.primary[0]")
  message: Human-readable error message
  expected: Expected value/type (optional)
  actual: Actual value found (optional)

#### Methods

- `__str__(self) -> str`: Format error for display.
