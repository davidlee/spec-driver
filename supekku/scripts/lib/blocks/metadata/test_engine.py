"""Comprehensive tests for metadata validation engine and JSON Schema generation.

Test coverage:
- Field type validation (string, int, bool, const, enum, object, array)
- Pattern matching for strings
- Array constraints (min_items, max_items)
- Nested object validation
- Conditional rules (if/then logic)
- JSON Schema generation
- Error message quality
"""

from __future__ import annotations

import unittest

from .json_schema import metadata_to_json_schema
from .schema import BlockMetadata, ConditionalRule, FieldMetadata
from .validator import MetadataValidator, ValidationError


class StringFieldValidationTest(unittest.TestCase):
  """Test string field validation."""

  def test_string_field_valid(self):
    """String field accepts string values."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"name": FieldMetadata(type="string", required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"name": "test"})
    assert errors == []

  def test_string_field_invalid_type(self):
    """String field rejects non-string values."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"name": FieldMetadata(type="string", required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"name": 123})
    assert len(errors) == 1
    assert "must be a string" in errors[0].message
    assert errors[0].path == "name"

  def test_string_pattern_valid(self):
    """String pattern validation accepts matching values."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"id": FieldMetadata(type="string", required=True, pattern=r"^DE-\d{3}$")},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"id": "DE-001"})
    assert errors == []

  def test_string_pattern_invalid(self):
    """String pattern validation rejects non-matching values."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"id": FieldMetadata(type="string", required=True, pattern=r"^DE-\d{3}$")},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"id": "INVALID"})
    assert len(errors) == 1
    assert "does not match required pattern" in errors[0].message

  def test_optional_string_field_missing(self):
    """Optional string field can be omitted."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"name": FieldMetadata(type="string", required=False)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({})
    assert errors == []


class EnumFieldValidationTest(unittest.TestCase):
  """Test enum field validation."""

  def test_enum_field_valid(self):
    """Enum field accepts allowed values."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "status": FieldMetadata(
          type="enum", required=True, enum_values=["planned", "active", "done"]
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"status": "active"})
    assert errors == []

  def test_enum_field_invalid(self):
    """Enum field rejects values not in enum."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "status": FieldMetadata(
          type="enum", required=True, enum_values=["planned", "active", "done"]
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"status": "invalid"})
    assert len(errors) == 1
    assert "must be one of allowed values" in errors[0].message


class ConstFieldValidationTest(unittest.TestCase):
  """Test const field validation."""

  def test_const_field_valid(self):
    """Const field accepts exact value."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"version": FieldMetadata(type="const", const_value=1, required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"version": 1})
    assert errors == []

  def test_const_field_invalid(self):
    """Const field rejects different value."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"version": FieldMetadata(type="const", const_value=1, required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"version": 2})
    assert len(errors) == 1
    assert "must equal constant value" in errors[0].message


class IntFieldValidationTest(unittest.TestCase):
  """Test integer field validation."""

  def test_int_field_valid(self):
    """Int field accepts integer values."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"count": FieldMetadata(type="int", required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"count": 42})
    assert errors == []

  def test_int_field_invalid_type(self):
    """Int field rejects non-integer values."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"count": FieldMetadata(type="int", required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"count": "not-int"})
    assert len(errors) == 1
    assert "must be an integer" in errors[0].message

  def test_int_field_rejects_bool(self):
    """Int field rejects boolean (even though bool is subclass of int in Python)."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"count": FieldMetadata(type="int", required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"count": True})
    assert len(errors) == 1
    assert "must be an integer" in errors[0].message


class BoolFieldValidationTest(unittest.TestCase):
  """Test boolean field validation."""

  def test_bool_field_valid_true(self):
    """Bool field accepts True."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"enabled": FieldMetadata(type="bool", required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"enabled": True})
    assert errors == []

  def test_bool_field_valid_false(self):
    """Bool field accepts False."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"enabled": FieldMetadata(type="bool", required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"enabled": False})
    assert errors == []

  def test_bool_field_invalid_type(self):
    """Bool field rejects non-boolean values."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"enabled": FieldMetadata(type="bool", required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"enabled": "yes"})
    assert len(errors) == 1
    assert "must be a boolean" in errors[0].message


class ObjectFieldValidationTest(unittest.TestCase):
  """Test object (nested) field validation."""

  def test_object_field_valid(self):
    """Object field accepts dict with correct properties."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "metadata": FieldMetadata(
          type="object",
          required=True,
          properties={
            "author": FieldMetadata(type="string", required=True),
            "version": FieldMetadata(type="int", required=True),
          },
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"metadata": {"author": "Alice", "version": 1}})
    assert errors == []

  def test_object_field_invalid_type(self):
    """Object field rejects non-dict values."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "metadata": FieldMetadata(
          type="object",
          required=True,
          properties={"author": FieldMetadata(type="string", required=True)},
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"metadata": "not-object"})
    assert len(errors) == 1
    assert "must be an object" in errors[0].message

  def test_object_field_missing_required_property(self):
    """Object field reports missing required nested property."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "metadata": FieldMetadata(
          type="object",
          required=True,
          properties={"author": FieldMetadata(type="string", required=True)},
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"metadata": {}})
    assert len(errors) == 1
    assert errors[0].path == "metadata.author"
    assert "is required" in errors[0].message


class ArrayFieldValidationTest(unittest.TestCase):
  """Test array field validation."""

  def test_array_field_valid(self):
    """Array field accepts list of correct type."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "tags": FieldMetadata(
          type="array", required=True, items=FieldMetadata(type="string")
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"tags": ["foo", "bar"]})
    assert errors == []

  def test_array_field_invalid_type(self):
    """Array field rejects non-list values."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "tags": FieldMetadata(
          type="array", required=True, items=FieldMetadata(type="string")
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"tags": "not-array"})
    assert len(errors) == 1
    assert "must be an array" in errors[0].message

  def test_array_field_invalid_item_type(self):
    """Array field validates item types."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "tags": FieldMetadata(
          type="array", required=True, items=FieldMetadata(type="string")
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"tags": ["foo", 123, "bar"]})
    assert len(errors) == 1
    assert errors[0].path == "tags[1]"
    assert "must be a string" in errors[0].message

  def test_array_min_items_valid(self):
    """Array field respects min_items constraint."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "tags": FieldMetadata(
          type="array",
          required=True,
          items=FieldMetadata(type="string"),
          min_items=2,
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"tags": ["foo", "bar"]})
    assert errors == []

  def test_array_min_items_invalid(self):
    """Array field rejects arrays below min_items."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "tags": FieldMetadata(
          type="array",
          required=True,
          items=FieldMetadata(type="string"),
          min_items=2,
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"tags": ["foo"]})
    assert len(errors) == 1
    assert "must have at least 2 items" in errors[0].message

  def test_array_max_items_valid(self):
    """Array field respects max_items constraint."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "tags": FieldMetadata(
          type="array",
          required=True,
          items=FieldMetadata(type="string"),
          max_items=3,
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"tags": ["foo", "bar"]})
    assert errors == []

  def test_array_max_items_invalid(self):
    """Array field rejects arrays above max_items."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "tags": FieldMetadata(
          type="array",
          required=True,
          items=FieldMetadata(type="string"),
          max_items=2,
        )
      },
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"tags": ["foo", "bar", "baz"]})
    assert len(errors) == 1
    assert "must have at most 2 items" in errors[0].message


class ConditionalRuleValidationTest(unittest.TestCase):
  """Test conditional validation rules."""

  def test_conditional_rule_not_triggered(self):
    """Conditional rule does not apply when condition not met."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "action": FieldMetadata(
          type="enum", required=True, enum_values=["create", "update"]
        ),
        "target": FieldMetadata(type="string", required=False),
      },
      conditional_rules=[
        ConditionalRule(
          condition_field="action",
          condition_value="update",
          requires=["target"],
          description="update requires target",
        )
      ],
    )
    validator = MetadataValidator(metadata)
    # Action is "create", so target is not required
    errors = validator.validate({"action": "create"})
    assert errors == []

  def test_conditional_rule_triggered_valid(self):
    """Conditional rule passes when required field present."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "action": FieldMetadata(
          type="enum", required=True, enum_values=["create", "update"]
        ),
        "target": FieldMetadata(type="string", required=False),
      },
      conditional_rules=[
        ConditionalRule(
          condition_field="action",
          condition_value="update",
          requires=["target"],
          description="update requires target",
        )
      ],
    )
    validator = MetadataValidator(metadata)
    # Action is "update", and target is present
    errors = validator.validate({"action": "update", "target": "foo"})
    assert errors == []

  def test_conditional_rule_triggered_invalid(self):
    """Conditional rule fails when required field missing."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "action": FieldMetadata(
          type="enum", required=True, enum_values=["create", "update"]
        ),
        "target": FieldMetadata(type="string", required=False),
      },
      conditional_rules=[
        ConditionalRule(
          condition_field="action",
          condition_value="update",
          requires=["target"],
          description="update requires target",
        )
      ],
    )
    validator = MetadataValidator(metadata)
    # Action is "update", but target is missing
    errors = validator.validate({"action": "update"})
    assert len(errors) == 1
    assert errors[0].path == "target"
    assert "is required when action=update" in errors[0].message

  def test_conditional_rule_nested_field(self):
    """Conditional rule works with nested condition fields."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "metadata": FieldMetadata(
          type="object",
          required=True,
          properties={
            "revision": FieldMetadata(type="int", required=False),
          },
        ),
        "changes": FieldMetadata(type="string", required=False),
      },
      conditional_rules=[
        ConditionalRule(
          condition_field="metadata.revision",
          condition_value=2,
          requires=["changes"],
          description="revision 2+ requires changes",
        )
      ],
    )
    validator = MetadataValidator(metadata)
    # Revision is 2, but changes missing
    errors = validator.validate({"metadata": {"revision": 2}})
    assert len(errors) == 1
    assert errors[0].path == "changes"


class RequiredFieldValidationTest(unittest.TestCase):
  """Test required field enforcement."""

  def test_required_field_present(self):
    """Required field validation passes when present."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"name": FieldMetadata(type="string", required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({"name": "test"})
    assert errors == []

  def test_required_field_missing(self):
    """Required field validation fails when missing."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"name": FieldMetadata(type="string", required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate({})
    assert len(errors) == 1
    assert errors[0].path == "name"
    assert "is required" in errors[0].message


class RootValidationTest(unittest.TestCase):
  """Test root-level validation."""

  def test_root_must_be_object(self):
    """Root data must be a mapping."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"name": FieldMetadata(type="string", required=True)},
    )
    validator = MetadataValidator(metadata)
    errors = validator.validate("not-object")
    assert len(errors) == 1
    assert errors[0].path == "<root>"
    assert "must be a mapping" in errors[0].message


class ValidationErrorFormattingTest(unittest.TestCase):
  """Test ValidationError formatting."""

  def test_error_str_with_expected_and_actual(self):
    """ValidationError formats with expected and actual values."""
    error = ValidationError(
      path="field", message="is wrong", expected="string", actual="int"
    )
    error_str = str(error)
    assert "field: is wrong" in error_str
    assert "expected string" in error_str
    assert "got int" in error_str

  def test_error_str_without_expected_actual(self):
    """ValidationError formats without expected/actual when not provided."""
    error = ValidationError(path="field", message="is required")
    error_str = str(error)
    assert error_str == "field: is required"


class JSONSchemaGenerationTest(unittest.TestCase):
  """Test JSON Schema generation from metadata."""

  def test_simple_string_field(self):
    """Generate schema for simple string field."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"name": FieldMetadata(type="string", required=True)},
    )
    schema = metadata_to_json_schema(metadata)

    assert schema["type"] == "object"
    assert schema["required"] == ["name"]
    assert schema["properties"]["name"]["type"] == "string"
    assert "$schema" in schema
    assert "$id" in schema

  def test_pattern_field(self):
    """Generate schema with pattern constraint."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"id": FieldMetadata(type="string", required=True, pattern=r"^DE-\d{3}$")},
    )
    schema = metadata_to_json_schema(metadata)

    assert schema["properties"]["id"]["pattern"] == r"^DE-\d{3}$"

  def test_enum_field(self):
    """Generate schema with enum constraint."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "status": FieldMetadata(
          type="enum", required=True, enum_values=["planned", "active", "done"]
        )
      },
    )
    schema = metadata_to_json_schema(metadata)

    assert schema["properties"]["status"]["enum"] == ["planned", "active", "done"]

  def test_const_field(self):
    """Generate schema with const constraint."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"version": FieldMetadata(type="const", const_value=1, required=True)},
    )
    schema = metadata_to_json_schema(metadata)

    assert schema["properties"]["version"]["const"] == 1

  def test_int_field(self):
    """Generate schema for integer field."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"count": FieldMetadata(type="int", required=True)},
    )
    schema = metadata_to_json_schema(metadata)

    assert schema["properties"]["count"]["type"] == "integer"

  def test_bool_field(self):
    """Generate schema for boolean field."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"enabled": FieldMetadata(type="bool", required=True)},
    )
    schema = metadata_to_json_schema(metadata)

    assert schema["properties"]["enabled"]["type"] == "boolean"

  def test_object_field(self):
    """Generate schema for nested object."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "metadata": FieldMetadata(
          type="object",
          required=True,
          properties={
            "author": FieldMetadata(type="string", required=True),
            "version": FieldMetadata(type="int", required=False),
          },
        )
      },
    )
    schema = metadata_to_json_schema(metadata)

    assert schema["properties"]["metadata"]["type"] == "object"
    assert "properties" in schema["properties"]["metadata"]
    assert schema["properties"]["metadata"]["properties"]["author"]["type"] == "string"
    assert schema["properties"]["metadata"]["required"] == ["author"]

  def test_array_field(self):
    """Generate schema for array field."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "tags": FieldMetadata(
          type="array", required=True, items=FieldMetadata(type="string")
        )
      },
    )
    schema = metadata_to_json_schema(metadata)

    assert schema["properties"]["tags"]["type"] == "array"
    assert schema["properties"]["tags"]["items"]["type"] == "string"

  def test_array_with_constraints(self):
    """Generate schema for array with min/max items."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "tags": FieldMetadata(
          type="array",
          required=True,
          items=FieldMetadata(type="string"),
          min_items=1,
          max_items=5,
        )
      },
    )
    schema = metadata_to_json_schema(metadata)

    assert schema["properties"]["tags"]["minItems"] == 1
    assert schema["properties"]["tags"]["maxItems"] == 5

  def test_conditional_rules_simple(self):
    """Generate schema with conditional rules (if/then)."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "action": FieldMetadata(
          type="enum", required=True, enum_values=["create", "update"]
        ),
        "target": FieldMetadata(type="string", required=False),
      },
      conditional_rules=[
        ConditionalRule(
          condition_field="action",
          condition_value="update",
          requires=["target"],
          description="update requires target",
        )
      ],
    )
    schema = metadata_to_json_schema(metadata)

    assert "allOf" in schema
    assert len(schema["allOf"]) == 1
    assert "if" in schema["allOf"][0]
    assert "then" in schema["allOf"][0]
    assert schema["allOf"][0]["then"]["required"] == ["target"]

  def test_schema_metadata_fields(self):
    """Generate schema includes metadata fields ($schema, $id, title, description)."""
    metadata = BlockMetadata(
      version=2,
      schema_id="decision.metadata",
      description="Decision metadata block",
      fields={"name": FieldMetadata(type="string", required=True)},
    )
    schema = metadata_to_json_schema(metadata)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert "decision-metadata@v2.json" in schema["$id"]
    assert schema["title"] == "Supekku decision.metadata Block"
    assert schema["description"] == "Decision metadata block"

  def test_schema_examples(self):
    """Generate schema includes examples when provided."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={"name": FieldMetadata(type="string", required=True)},
      examples=[{"name": "example1"}, {"name": "example2"}],
    )
    schema = metadata_to_json_schema(metadata)

    assert "examples" in schema
    assert len(schema["examples"]) == 2
    assert schema["examples"][0] == {"name": "example1"}

  def test_optional_fields_not_in_required(self):
    """Optional fields are not included in required list."""
    metadata = BlockMetadata(
      version=1,
      schema_id="test.schema",
      fields={
        "required_field": FieldMetadata(type="string", required=True),
        "optional_field": FieldMetadata(type="string", required=False),
      },
    )
    schema = metadata_to_json_schema(metadata)

    assert schema["required"] == ["required_field"]
    assert "optional_field" in schema["properties"]


class ComplexIntegrationTest(unittest.TestCase):
  """Integration tests with complex, realistic metadata."""

  def test_decision_metadata_validation(self):
    """Validate realistic decision metadata block."""
    metadata = BlockMetadata(
      version=1,
      schema_id="decision.metadata",
      description="Decision metadata block",
      fields={
        "id": FieldMetadata(type="string", required=True, pattern=r"^ADR-\d{3}$"),
        "title": FieldMetadata(type="string", required=True),
        "status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=["proposed", "accepted", "deprecated", "superseded"],
        ),
        "date": FieldMetadata(
          type="string", required=True, pattern=r"^\d{4}-\d{2}-\d{2}$"
        ),
        "supersedes": FieldMetadata(
          type="string", required=False, pattern=r"^ADR-\d{3}$"
        ),
      },
      conditional_rules=[
        ConditionalRule(
          condition_field="status",
          condition_value="superseded",
          requires=["supersedes"],
          description="superseded status requires supersedes field",
        )
      ],
    )

    validator = MetadataValidator(metadata)

    # Valid decision
    valid_data = {
      "id": "ADR-001",
      "title": "Use metadata-driven validation",
      "status": "accepted",
      "date": "2025-01-15",
    }
    errors = validator.validate(valid_data)
    assert errors == []

    # Invalid: missing required field
    invalid_missing = {
      "id": "ADR-001",
      "title": "Use metadata-driven validation",
      "status": "accepted",
    }
    errors = validator.validate(invalid_missing)
    assert len(errors) == 1
    assert "date" in errors[0].path

    # Invalid: bad ID pattern
    invalid_pattern = {
      "id": "INVALID",
      "title": "Use metadata-driven validation",
      "status": "accepted",
      "date": "2025-01-15",
    }
    errors = validator.validate(invalid_pattern)
    assert len(errors) == 1
    assert "does not match required pattern" in errors[0].message

    # Invalid: conditional rule violated
    invalid_conditional = {
      "id": "ADR-001",
      "title": "Use metadata-driven validation",
      "status": "superseded",
      "date": "2025-01-15",
    }
    errors = validator.validate(invalid_conditional)
    assert len(errors) == 1
    assert "supersedes" in errors[0].path

  def test_decision_metadata_json_schema_generation(self):
    """Generate JSON Schema for decision metadata."""
    metadata = BlockMetadata(
      version=1,
      schema_id="decision.metadata",
      description="Decision metadata block",
      fields={
        "id": FieldMetadata(type="string", required=True, pattern=r"^ADR-\d{3}$"),
        "title": FieldMetadata(type="string", required=True),
        "status": FieldMetadata(
          type="enum",
          required=True,
          enum_values=["proposed", "accepted", "deprecated", "superseded"],
        ),
      },
    )

    schema = metadata_to_json_schema(metadata)

    assert schema["type"] == "object"
    assert set(schema["required"]) == {"id", "title", "status"}
    assert schema["properties"]["id"]["pattern"] == r"^ADR-\d{3}$"
    assert schema["properties"]["status"]["enum"] == [
      "proposed",
      "accepted",
      "deprecated",
      "superseded",
    ]


if __name__ == "__main__":
  unittest.main()
