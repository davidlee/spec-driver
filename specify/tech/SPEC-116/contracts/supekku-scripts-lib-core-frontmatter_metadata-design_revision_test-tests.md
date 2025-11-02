# supekku.scripts.lib.core.frontmatter_metadata.design_revision_test

Dual-validation tests for design revision frontmatter metadata.

This module tests the metadata validator for design revision-specific fields,
comparing behavior against the legacy imperative validator.

## Classes

### DesignRevisionFrontmatterValidationTest

Test metadata validator for design revision-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_code_impact_missing_current_state(self) -> None`: New validator rejects code_impact missing current_state field.
- `test_code_impact_missing_path(self) -> None`: New validator rejects code_impact missing required path field.
- `test_code_impact_missing_target_state(self) -> None`: New validator rejects code_impact missing target_state field.
- `test_design_decision_missing_id(self) -> None`: New validator rejects design_decision missing required id field.
- `test_design_decision_missing_summary(self) -> None`: New validator rejects design_decision missing required summary field.
- `test_empty_arrays_are_valid(self) -> None`: Both validators accept empty arrays for optional array fields.
- `test_empty_string_in_code_impact_path(self) -> None`: New validator rejects code_impact with empty path string.
- `test_empty_string_in_verification(self) -> None`: New validator rejects verification_alignment with empty verification.
- `test_invalid_source_context_type(self) -> None`: New validator rejects invalid source_context type enum value. - Invalid cases (new validator only)
- `test_invalid_verification_alignment_impact(self) -> None`: New validator rejects invalid verification_alignment impact enum.
- `test_open_question_invalid_due_format(self) -> None`: New validator rejects open_question with invalid due date format.
- `test_open_question_missing_description(self) -> None`: New validator rejects open_question missing required description.
- `test_open_question_missing_due(self) -> None`: New validator rejects open_question missing required due field.
- `test_open_question_missing_owner(self) -> None`: New validator rejects open_question missing required owner field.
- `test_source_context_missing_id(self) -> None`: New validator rejects source_context missing required id field.
- `test_source_context_missing_type(self) -> None`: New validator rejects source_context missing required type field.
- `test_valid_design_revision_with_all_fields(self) -> None`: Both validators accept design revision with all optional fields.
- `test_valid_minimal_design_revision(self) -> None`: Both validators accept minimal design revision (base fields only). - Valid cases
- `test_valid_source_context_types(self) -> None`: Both validators accept all valid source_context type enum values.
- `test_valid_verification_impact_types(self) -> None`: Both validators accept all valid verification impact enum values.
- `test_verification_alignment_missing_impact(self) -> None`: New validator rejects verification_alignment missing impact field.
- `test_verification_alignment_missing_verification(self) -> None`: New validator rejects verification_alignment missing verification.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
