# supekku.scripts.lib.core.frontmatter_metadata.policy_test

Dual-validation tests for policy frontmatter metadata.

## Classes

### PolicyFrontmatterValidationTest

Test metadata validator for policy-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_empty_string_in_deltas_array(self) -> None`: New validator rejects empty strings in deltas array.
- `test_empty_string_in_requirements_array(self) -> None`: New validator rejects empty strings in requirements array.
- `test_empty_string_in_specs_array(self) -> None`: New validator rejects empty strings in specs array.
- `test_invalid_related_policies_id_format(self) -> None`: New validator rejects invalid related_policies ID format.
- `test_invalid_related_standards_id_format(self) -> None`: New validator rejects invalid related_standards ID format.
- `test_invalid_reviewed_date_format(self) -> None`: New validator rejects invalid reviewed date format. - Invalid cases (new validator only)
- `test_invalid_standards_id_format(self) -> None`: New validator rejects invalid standards ID format.
- `test_invalid_superseded_by_id_format(self) -> None`: New validator rejects invalid superseded_by ID format.
- `test_invalid_supersedes_id_format(self) -> None`: New validator rejects invalid supersedes ID format.
- `test_supersedes_not_array(self) -> None`: New validator rejects supersedes when not an array.
- `test_valid_empty_arrays(self) -> None`: Both validators accept empty arrays for policy-specific fields.
- `test_valid_minimal_policy(self) -> None`: Both validators accept minimal policy (base fields only). - Valid cases
- `test_valid_policy_with_all_fields(self) -> None`: Both validators accept policy with all optional fields.
- `test_valid_reviewed_date(self) -> None`: Both validators accept valid reviewed date.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
