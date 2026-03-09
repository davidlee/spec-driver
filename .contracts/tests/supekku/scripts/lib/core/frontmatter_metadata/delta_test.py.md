# supekku.scripts.lib.core.frontmatter_metadata.delta_test

Dual-validation tests for delta frontmatter metadata.

Tests that the new metadata-driven validator handles delta-specific fields
correctly while maintaining compatibility with base field validation.

## Classes

### DeltaFrontmatterValidationTest

Test metadata validator for delta-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_applies_to_empty_string_in_array(self) -> None`: New validator rejects empty strings in applies_to arrays.
- `test_applies_to_not_object(self) -> None`: New validator rejects applies_to as non-object.
- `test_applies_to_specs_not_array(self) -> None`: New validator rejects applies_to.specs as non-array.
- `test_context_input_invalid_type(self) -> None`: New validator rejects invalid context_input type.
- `test_context_input_missing_id(self) -> None`: New validator rejects context_input missing id.
- `test_context_input_missing_type(self) -> None`: New validator rejects context_input missing type.
- `test_outcome_summary_not_string(self) -> None`: New validator rejects outcome_summary as non-string.
- `test_risk_invalid_exposure(self) -> None`: New validator rejects invalid exposure type.
- `test_risk_invalid_impact(self) -> None`: New validator rejects invalid impact.
- `test_risk_invalid_likelihood(self) -> None`: New validator rejects invalid likelihood.
- `test_risk_missing_required_fields(self) -> None`: New validator rejects risk missing required fields.
- `test_valid_applies_to_all_categories(self) -> None`: Both validators accept applies_to with all categories. - applies_to validation (5 tests)
- `test_valid_applies_to_empty_arrays(self) -> None`: Both validators accept applies_to with empty arrays.
- `test_valid_context_inputs_all_types(self) -> None`: Both validators accept all context_inputs types. - context_inputs validation (5 tests)
- `test_valid_context_inputs_multiple(self) -> None`: Both validators accept multiple context_inputs.
- `test_valid_delta_partial_applies_to(self) -> None`: Both validators accept applies_to with only some fields.
- `test_valid_delta_with_all_fields(self) -> None`: Both validators accept delta with all optional fields.
- `test_valid_minimal_delta(self) -> None`: Both validators accept minimal delta (base fields only). - Valid cases (3 tests)
- `test_valid_outcome_summary(self) -> None`: Both validators accept outcome_summary as string. - outcome_summary validation (2 tests)
- `test_valid_risk_exposure_types(self) -> None`: New validator accepts all valid exposure types.
- `test_valid_risk_likelihood_values(self) -> None`: New validator accepts all valid likelihood values.
- `test_valid_risk_register_complete(self) -> None`: Both validators accept complete risk entry. - risk_register validation (8 tests)
- `test_valid_risk_register_minimal(self) -> None`: Both validators accept risk without optional mitigation.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
