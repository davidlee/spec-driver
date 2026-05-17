# supekku.scripts.lib.blocks.metadata.test_engine

Comprehensive tests for metadata validation engine and JSON Schema generation.

Test coverage:
- Field type validation (string, int, bool, const, enum, object, array)
- Pattern matching for strings
- Array constraints (min_items, max_items)
- Nested object validation
- Conditional rules (if/then logic)
- JSON Schema generation
- Error message quality

## Classes

### AdditionalPropertiesValidationTest

`additional_properties` validates dynamic-key entries (DE-118 DEC-004).

**Inherits from:** unittest.TestCase

#### Methods

- `test_additional_properties_accepts_matching_shape(self)`: Dynamic keys validated against additional_properties shape.
- `test_additional_properties_combined_rejects_wrong_extra_type(self)`: Extras of wrong type rejected by additional_properties shape.
- `test_additional_properties_combined_with_properties(self)`: Declared properties take precedence; extras validated against additional.
- `test_additional_properties_rejects_shape_mismatch(self)`: Dynamic-key value of wrong shape produces a path-aware error.
- `test_empty_dynamic_map_passes_silently(self)`: Empty data with additional_properties passes (DEC-004 documented behaviour).

### ArrayFieldValidationTest

Test array field validation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_array_field_invalid_item_type(self)`: Array field validates item types.
- `test_array_field_invalid_type(self)`: Array field rejects non-list values.
- `test_array_field_valid(self)`: Array field accepts list of correct type.
- `test_array_max_items_invalid(self)`: Array field rejects arrays above max_items.
- `test_array_max_items_valid(self)`: Array field respects max_items constraint.
- `test_array_min_items_invalid(self)`: Array field rejects arrays below min_items.
- `test_array_min_items_valid(self)`: Array field respects min_items constraint.

### BoolFieldValidationTest

Test boolean field validation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_bool_field_invalid_type(self)`: Bool field rejects non-boolean values.
- `test_bool_field_valid_false(self)`: Bool field accepts False.
- `test_bool_field_valid_true(self)`: Bool field accepts True.

### ComplexIntegrationTest

Integration tests with complex, realistic metadata.

**Inherits from:** unittest.TestCase

#### Methods

- `test_decision_metadata_json_schema_generation(self)`: Generate JSON Schema for decision metadata.
- `test_decision_metadata_validation(self)`: Validate realistic decision metadata block.

### ConditionalRuleValidationTest

Test conditional validation rules.

**Inherits from:** unittest.TestCase

#### Methods

- `test_conditional_rule_nested_field(self)`: Conditional rule works with nested condition fields.
- `test_conditional_rule_not_triggered(self)`: Conditional rule does not apply when condition not met.
- `test_conditional_rule_triggered_invalid(self)`: Conditional rule fails when required field missing.
- `test_conditional_rule_triggered_valid(self)`: Conditional rule passes when required field present.

### ConstFieldValidationTest

Test const field validation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_const_field_invalid(self)`: Const field rejects different value.
- `test_const_field_valid(self)`: Const field accepts exact value.

### EnumFieldValidationTest

Test enum field validation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_enum_field_invalid(self)`: Enum field rejects values not in enum.
- `test_enum_field_valid(self)`: Enum field accepts allowed values.

### FieldMetadataPersistenceTest

Test persistence and default_value fields on FieldMetadata.

**Inherits from:** unittest.TestCase

#### Methods

- `test_default_persistence_is_canonical(self)`: New fields default to canonical persistence.
- `test_default_value_is_none(self)`: default_value defaults to None.
- `test_default_value_with_dict(self)`: default_value can hold a dict for object default-omit.
- `test_default_value_with_empty_list(self)`: default_value can hold an empty list for array default-omit.
- `test_existing_fields_unaffected(self)`: Adding persistence fields doesn't break existing FieldMetadata usage.
- `test_invalid_persistence_raises(self)`: Invalid persistence value raises ValueError.
- `test_valid_persistence_values(self)`: All four persistence classifications are accepted.

### FieldMetadataPostInitObjectShapeTest

Object-type accepts properties OR additional_properties (DE-118 DEC-004).

**Inherits from:** unittest.TestCase

#### Methods

- `test_object_with_additional_properties_only(self)`: Object type with only additional_properties constructs (DEC-004).
- `test_object_with_both(self)`: Object type with both properties and additional_properties constructs.
- `test_object_with_neither_raises(self)`: Object type without properties or additional_properties raises ValueError.
- `test_object_with_properties_only(self)`: Object type with only properties constructs (existing behaviour).

### IntFieldValidationTest

Test integer field validation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_int_field_invalid_type(self)`: Int field rejects non-integer values.
- `test_int_field_rejects_bool(self)`: Int field rejects boolean (even though bool is subclass of int in Python).
- `test_int_field_valid(self)`: Int field accepts integer values.

### JSONSchemaGenerationTest

Test JSON Schema generation from metadata.

**Inherits from:** unittest.TestCase

#### Methods

- `test_array_field(self)`: Generate schema for array field.
- `test_array_with_constraints(self)`: Generate schema for array with min/max items.
- `test_bool_field(self)`: Generate schema for boolean field.
- `test_conditional_rules_simple(self)`: Generate schema with conditional rules (if/then).
- `test_const_field(self)`: Generate schema with const constraint.
- `test_enum_field(self)`: Generate schema with enum constraint.
- `test_int_field(self)`: Generate schema for integer field.
- `test_object_field(self)`: Generate schema for nested object.
- `test_optional_fields_not_in_required(self)`: Optional fields are not included in required list.
- `test_pattern_field(self)`: Generate schema with pattern constraint.
- `test_schema_examples(self)`: Generate schema includes examples when provided.
- `test_schema_metadata_fields(self)`: Generate schema includes metadata fields ($schema, $id, title, description).
- `test_simple_string_field(self)`: Generate schema for simple string field.

### ObjectFieldValidationTest

Test object (nested) field validation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_object_field_invalid_type(self)`: Object field rejects non-dict values.
- `test_object_field_missing_required_property(self)`: Object field reports missing required nested property.
- `test_object_field_valid(self)`: Object field accepts dict with correct properties.

### RequiredFieldValidationTest

Test required field enforcement.

**Inherits from:** unittest.TestCase

#### Methods

- `test_required_field_missing(self)`: Required field validation fails when missing.
- `test_required_field_present(self)`: Required field validation passes when present.

### RootValidationTest

Test root-level validation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_root_must_be_object(self)`: Root data must be a mapping.

### StrictUnknownKeysTest

`strict_unknown_keys` flag rejects undeclared keys (DE-118 DEC-001).

**Inherits from:** unittest.TestCase

#### Methods

- `test_default_lax_accepts_extra_top_level_key(self)`: Default behaviour (lax) accepts unknown top-level keys.
- `test_strict_accepts_known_keys(self)`: strict_unknown_keys=True does not regress on valid documents.
- `test_strict_rejects_extra_key_at_nested_depth(self)`: strict_unknown_keys propagates through nested object recursion.
- `test_strict_rejects_extra_top_level_key(self)`: strict_unknown_keys=True rejects unknown top-level keys.
- `test_strict_with_additional_properties_accepts_matching_extras(self)`: strict_unknown_keys does not double-reject keys covered by additional.

### StringFieldValidationTest

Test string field validation.

**Inherits from:** unittest.TestCase

#### Methods

- `test_optional_string_field_missing(self)`: Optional string field can be omitted.
- `test_string_field_invalid_type(self)`: String field rejects non-string values.
- `test_string_field_valid(self)`: String field accepts string values.
- `test_string_pattern_invalid(self)`: String pattern validation rejects non-matching values.
- `test_string_pattern_valid(self)`: String pattern validation accepts matching values.

### ValidationErrorFormattingTest

Test ValidationError formatting.

**Inherits from:** unittest.TestCase

#### Methods

- `test_error_str_with_expected_and_actual(self)`: ValidationError formats with expected and actual values.
- `test_error_str_without_expected_actual(self)`: ValidationError formats without expected/actual when not provided.
