# supekku.scripts.lib.core.frontmatter_metadata.verification_test

Dual-validation tests for verification frontmatter metadata.

## Classes

### VerificationFrontmatterValidationTest

Test metadata validator for verification-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_covers_not_array(self) -> None`: New validator rejects covers when not an array.
- `test_empty_string_in_covers_array(self) -> None`: New validator rejects empty strings in covers array.
- `test_invalid_verification_kind(self) -> None`: New validator rejects invalid verification_kind. - Invalid cases (new validator only)
- `test_procedure_not_string(self) -> None`: New validator rejects procedure when not a string.
- `test_valid_covers_array(self) -> None`: Both validators accept covers as array of requirement IDs.
- `test_valid_empty_covers_array(self) -> None`: Both validators accept empty covers array.
- `test_valid_minimal_verification(self) -> None`: Both validators accept minimal verification (base fields only). - Valid cases
- `test_valid_procedure_text(self) -> None`: Both validators accept procedure as text.
- `test_valid_verification_kind_agent(self) -> None`: Both validators accept verification_kind=agent.
- `test_valid_verification_kind_automated(self) -> None`: Both validators accept verification_kind=automated.
- `test_valid_verification_kind_manual(self) -> None`: Both validators accept verification_kind=manual.
- `test_valid_verification_with_all_fields(self) -> None`: Both validators accept verification with all optional fields.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
