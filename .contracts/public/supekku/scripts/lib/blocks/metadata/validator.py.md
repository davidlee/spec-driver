# supekku.scripts.lib.blocks.metadata.validator

Metadata-driven validation engine.

This module provides runtime validation of data against block metadata schemas.
The validator produces path-aware error messages for developer-friendly output.

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

### ValidationError

Validation error with path context.

Attributes:
  path: Dot-notation path (e.g., "specs.primary[0]")
  message: Human-readable error message
  expected: Expected value/type (optional)
  actual: Actual value found (optional)
