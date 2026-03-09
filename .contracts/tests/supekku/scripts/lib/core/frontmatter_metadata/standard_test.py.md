# supekku.scripts.lib.core.frontmatter_metadata.standard_test

Dual-validation tests for standard frontmatter metadata.

## Classes

### StandardFrontmatterValidationTest

Test metadata validator for standard-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_empty_string_in_deltas_array(self) -> None`: New validator rejects empty strings in deltas array.
- `test_empty_string_in_requirements_array(self) -> None`: New validator rejects empty strings in requirements array.
- `test_empty_string_in_specs_array(self) -> None`: New validator rejects empty strings in specs array.
- `test_invalid_policies_id_format(self) -> None`: New validator rejects invalid policies ID format.
- `test_invalid_related_policies_id_format(self) -> None`: New validator rejects invalid related_policies ID format.
- `test_invalid_related_standards_id_format(self) -> None`: New validator rejects invalid related_standards ID format.
- `test_invalid_reviewed_date_format(self) -> None`: New validator rejects invalid reviewed date format. - Invalid cases (new validator only)
- `test_invalid_superseded_by_id_format(self) -> None`: New validator rejects invalid superseded_by ID format.
- `test_invalid_supersedes_id_format(self) -> None`: New validator rejects invalid supersedes ID format.
- `test_supersedes_not_array(self) -> None`: New validator rejects supersedes when not an array.
- `test_valid_empty_arrays(self) -> None`: Both validators accept empty arrays for standard-specific fields.
- `test_valid_minimal_standard(self) -> None`: Both validators accept minimal standard (base fields only). - Valid cases
- `test_valid_reviewed_date(self) -> None`: Both validators accept valid reviewed date.
- `test_valid_standard_with_all_fields(self) -> None`: Both validators accept standard with all optional fields.
- `test_valid_status_default(self) -> None`: Both validators accept status=default for standards.
- `test_valid_status_required(self) -> None`: Both validators accept status=required for standards.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
