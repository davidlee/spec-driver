# supekku.scripts.lib.core.frontmatter_metadata.risk_test

Dual-validation tests for risk frontmatter metadata.

## Classes

### RiskFrontmatterValidationTest

Test metadata validator for risk-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_controls_not_array(self) -> None`: New validator rejects controls when not an array.
- `test_empty_origin_string(self) -> None`: New validator rejects empty origin string.
- `test_empty_string_in_controls(self) -> None`: New validator rejects empty strings in controls array.
- `test_invalid_impact(self) -> None`: New validator rejects invalid impact.
- `test_invalid_likelihood(self) -> None`: New validator rejects invalid likelihood.
- `test_invalid_risk_kind(self) -> None`: New validator rejects invalid risk_kind. - Invalid cases (new validator only)
- `test_valid_controls(self) -> None`: Both validators accept controls as array.
- `test_valid_empty_controls(self) -> None`: Both validators accept empty controls array.
- `test_valid_impact_values(self) -> None`: Both validators accept all impact enum values.
- `test_valid_likelihood_values(self) -> None`: Both validators accept all likelihood enum values.
- `test_valid_minimal_risk(self) -> None`: Both validators accept minimal risk (base fields only). - Valid cases
- `test_valid_origin(self) -> None`: Both validators accept origin as string.
- `test_valid_risk_kind_delivery(self) -> None`: Both validators accept risk_kind=delivery.
- `test_valid_risk_kind_operational(self) -> None`: Both validators accept risk_kind=operational.
- `test_valid_risk_kind_systemic(self) -> None`: Both validators accept risk_kind=systemic.
- `test_valid_risk_with_all_fields(self) -> None`: Both validators accept risk with all optional fields.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
