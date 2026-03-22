# supekku.scripts.lib.core.frontmatter_metadata.base_test

Dual-validation tests for base frontmatter metadata.

Tests that the new metadata-driven validator produces compatible results
with the existing frontmatter validator.

## Classes

### BaseFrontmatterDualValidationTest

Test metadata validator matches existing validator behavior.

**Inherits from:** unittest.TestCase

#### Methods

- `test_auditers_not_array(self) -> None`: Both validators reject non-array auditers.
- `test_auditers_with_empty_string(self) -> None`: Both validators reject empty strings in auditers.
- `test_date_with_invalid_format_not_iso(self) -> None`: Both validators reject non-ISO date format. - Date pattern validation (3 tests)
- `test_date_with_time_component(self) -> None`: Both validators reject date with time component.
- `test_empty_arrays_are_valid(self) -> None`: Both validators accept empty arrays for optional fields.
- `test_empty_relations_array_is_valid(self) -> None`: Both validators accept empty relations array.
- `test_empty_string_id(self) -> None`: Both validators reject empty string for required fields.
- `test_id_not_string(self) -> None`: Both validators reject non-string id. - Type validation (8 tests)
- `test_invalid_date_format(self) -> None`: Both validators reject invalid date format.
- `test_invalid_kind_value(self) -> None`: New validator rejects invalid kind value (old validator doesn't check). - Enum validation (3 tests)
- `test_invalid_lifecycle_value(self) -> None`: New validator rejects invalid lifecycle value.
- `test_invalid_relation_type_value(self) -> None`: Both validators reject invalid relation type.
- `test_missing_created(self) -> None`: Both validators reject missing created.
- `test_missing_id(self) -> None`: Both validators reject missing id. - Required field validation (6 tests)
- `test_missing_name(self) -> None`: Both validators reject missing name.
- `test_missing_slug(self) -> None`: Both validators reject missing slug.
- `test_missing_status(self) -> None`: Both validators reject missing status.
- `test_missing_updated(self) -> None`: Both validators reject missing updated.
- `test_name_not_string(self) -> None`: Both validators reject non-string name.
- `test_owners_not_array(self) -> None`: Both validators reject non-array owners.
- `test_owners_with_non_string_item(self) -> None`: Both validators reject non-string items in owners. - Array item validation (5 tests)
- `test_relation_missing_target(self) -> None`: Both validators reject relation missing target.
- `test_relation_missing_type(self) -> None`: Both validators reject relation missing type.
- `test_relation_target_empty_string(self) -> None`: Both validators reject empty target string.
- `test_relation_type_not_in_enum(self) -> None`: New validator rejects relation type not in enum.
- `test_relation_with_extra_fields_preserved(self) -> None`: Both validators preserve extra fields in relations.
- `test_relations_not_array(self) -> None`: Both validators reject non-array relations.
- `test_relations_with_non_object_item(self) -> None`: Both validators reject non-object items in relations.
- `test_tags_not_array(self) -> None`: New validator rejects non-array tags (old validator doesn't validate tags).
- `test_tags_with_empty_string(self) -> None`: New validator rejects empty strings in tags (old doesn't validate).
- `test_valid_complete_frontmatter(self) -> None`: Both validators accept frontmatter with all optional fields.
- `test_valid_date_as_date_object(self) -> None`: Old validator accepts date objects, new validator requires strings.
- `test_valid_date_as_string(self) -> None`: Both validators accept dates as ISO strings.
- `test_valid_empty_relations_array(self) -> None`: Both validators accept empty relations array.
- `test_valid_iso_date(self) -> None`: Both validators accept valid ISO date (YYYY-MM-DD).
- `test_valid_minimal_frontmatter(self) -> None`: Both validators accept minimal valid frontmatter. - Valid cases (5 tests)
- `test_valid_relation_minimal_fields(self) -> None`: Both validators accept relation with just type and target. - Relations validation (8 tests)
- `test_valid_relation_with_extra_fields(self) -> None`: Both validators accept relation with additional fields.
- `_assert_both_invalid(self, data) -> None`: Assert both validators reject the data.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).

Args:
  data: Frontmatter dictionary to validate

Returns:
  - old_error: None if valid, error message if invalid
  - new_errors: List of error strings from new validator
