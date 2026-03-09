# supekku.scripts.lib.core.frontmatter_metadata.prod_test

Dual-validation tests for product frontmatter metadata.

This module tests the metadata validator for product-specific fields,
comparing behavior against the legacy imperative validator.

## Classes

### ProdFrontmatterValidationTest

Test metadata validator for product-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_decision_missing_id(self) -> None`: New validator rejects decision missing required id field.
- `test_decision_missing_summary(self) -> None`: New validator rejects decision missing required summary field.
- `test_decision_with_empty_id(self) -> None`: New validator rejects decision with empty id string.
- `test_decision_with_empty_summary(self) -> None`: New validator rejects decision with empty summary string.
- `test_empty_arrays_are_valid(self) -> None`: Both validators accept empty arrays for optional array fields.
- `test_empty_string_in_assumptions_array(self) -> None`: New validator rejects empty string in assumptions array.
- `test_empty_string_in_guiding_principles_array(self) -> None`: New validator rejects empty string in guiding_principles array.
- `test_empty_string_in_problems_array(self) -> None`: New validator rejects empty string in problems array.
- `test_hypothesis_missing_id(self) -> None`: New validator rejects hypothesis missing required id field.
- `test_hypothesis_missing_statement(self) -> None`: New validator rejects hypothesis missing required statement field.
- `test_hypothesis_missing_status(self) -> None`: New validator rejects hypothesis missing required status field.
- `test_hypothesis_with_empty_id(self) -> None`: New validator rejects hypothesis with empty id string.
- `test_hypothesis_with_empty_statement(self) -> None`: New validator rejects hypothesis with empty statement string.
- `test_invalid_hypothesis_status(self) -> None`: New validator rejects invalid hypothesis status enum value. - Invalid cases (new validator only)
- `test_product_requirement_missing_code(self) -> None`: New validator rejects product requirement missing required code field.
- `test_product_requirement_missing_statement(self) -> None`: New validator rejects product requirement missing statement field.
- `test_product_requirement_with_empty_code(self) -> None`: New validator rejects product requirement with empty code string.
- `test_product_requirement_with_empty_statement(self) -> None`: New validator rejects product requirement with empty statement string.
- `test_valid_hypothesis_statuses(self) -> None`: Both validators accept all valid hypothesis status enum values.
- `test_valid_minimal_prod(self) -> None`: Both validators accept minimal product spec (base fields only). - Valid cases
- `test_valid_prod_with_all_fields(self) -> None`: Both validators accept product spec with all optional fields.
- `test_verification_strategy_with_empty_metric(self) -> None`: New validator rejects verification_strategy with empty metric.
- `test_verification_strategy_with_empty_research(self) -> None`: New validator rejects verification_strategy with empty research.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
