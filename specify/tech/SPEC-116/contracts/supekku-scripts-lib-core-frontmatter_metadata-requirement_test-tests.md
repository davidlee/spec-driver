# supekku.scripts.lib.core.frontmatter_metadata.requirement_test

Dual-validation tests for requirement frontmatter metadata.

## Classes

### RequirementFrontmatterValidationTest

Test metadata validator for requirement-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_empty_string_in_acceptance_criteria(self) -> None`: New validator rejects empty strings in acceptance_criteria.
- `test_empty_string_in_verification_refs(self) -> None`: New validator rejects empty strings in verification_refs.
- `test_invalid_requirement_kind(self) -> None`: New validator rejects invalid requirement_kind. - Invalid cases (new validator only)
- `test_invalid_rfc2119_level(self) -> None`: New validator rejects invalid rfc2119_level.
- `test_invalid_value_driver(self) -> None`: New validator rejects invalid value_driver.
- `test_valid_acceptance_criteria(self) -> None`: Both validators accept acceptance_criteria as array.
- `test_valid_empty_arrays(self) -> None`: Both validators accept empty arrays.
- `test_valid_minimal_requirement(self) -> None`: Both validators accept minimal requirement (base fields only). - Valid cases
- `test_valid_requirement_kind_functional(self) -> None`: Both validators accept requirement_kind=functional.
- `test_valid_requirement_kind_non_functional(self) -> None`: Both validators accept requirement_kind=non-functional.
- `test_valid_requirement_kind_policy(self) -> None`: Both validators accept requirement_kind=policy.
- `test_valid_requirement_kind_standard(self) -> None`: Both validators accept requirement_kind=standard.
- `test_valid_requirement_with_all_fields(self) -> None`: Both validators accept requirement with all optional fields.
- `test_valid_rfc2119_level_may(self) -> None`: Both validators accept rfc2119_level=may.
- `test_valid_rfc2119_level_must(self) -> None`: Both validators accept rfc2119_level=must.
- `test_valid_rfc2119_level_should(self) -> None`: Both validators accept rfc2119_level=should.
- `test_valid_value_driver_values(self) -> None`: Both validators accept all value_driver enum values.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
