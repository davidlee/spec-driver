# supekku.scripts.lib.core.frontmatter_metadata.issue_test

Dual-validation tests for issue frontmatter metadata.

## Classes

### IssueFrontmatterValidationTest

Test metadata validator for issue-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_empty_string_in_affected_verifications(self) -> None`: New validator rejects empty strings in affected_verifications.
- `test_empty_string_in_categories(self) -> None`: New validator rejects empty strings in categories.
- `test_empty_string_in_linked_deltas(self) -> None`: New validator rejects empty strings in linked_deltas.
- `test_empty_string_in_problem_refs(self) -> None`: New validator rejects empty strings in problem_refs.
- `test_empty_string_in_related_requirements(self) -> None`: New validator rejects empty strings in related_requirements.
- `test_invalid_impact(self) -> None`: New validator rejects invalid impact.
- `test_invalid_severity(self) -> None`: New validator rejects invalid severity. - Invalid cases (new validator only)
- `test_valid_categories_array(self) -> None`: Both validators accept categories as array.
- `test_valid_empty_arrays(self) -> None`: Both validators accept empty arrays for issue-specific fields.
- `test_valid_impact_process(self) -> None`: Both validators accept impact=process.
- `test_valid_impact_systemic(self) -> None`: Both validators accept impact=systemic.
- `test_valid_impact_user(self) -> None`: Both validators accept impact=user.
- `test_valid_issue_with_all_fields(self) -> None`: Both validators accept issue with all optional fields.
- `test_valid_minimal_issue(self) -> None`: Both validators accept minimal issue (base fields only). - Valid cases
- `test_valid_severity_values(self) -> None`: Both validators accept all severity enum values.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
