# supekku.scripts.lib.core.frontmatter_metadata.problem_test

Dual-validation tests for problem frontmatter metadata.

## Classes

### ProblemFrontmatterValidationTest

Test metadata validator for problem-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_context_empty_id(self) -> None`: New validator rejects context with empty id.
- `test_context_missing_id(self) -> None`: New validator rejects context missing id field.
- `test_context_missing_type(self) -> None`: New validator rejects context missing type field.
- `test_empty_string_in_related_requirements(self) -> None`: New validator rejects empty strings in related_requirements.
- `test_empty_string_in_success_criteria(self) -> None`: New validator rejects empty strings in success_criteria.
- `test_invalid_context_type(self) -> None`: New validator rejects invalid context type. - Invalid cases (new validator only)
- `test_valid_context_feedback(self) -> None`: Both validators accept context with type=feedback.
- `test_valid_context_metric(self) -> None`: Both validators accept context with type=metric.
- `test_valid_context_observation(self) -> None`: Both validators accept context with type=observation.
- `test_valid_context_research(self) -> None`: Both validators accept context with type=research.
- `test_valid_empty_arrays(self) -> None`: Both validators accept empty arrays for problem-specific fields.
- `test_valid_minimal_problem(self) -> None`: Both validators accept minimal problem (base fields only). - Valid cases
- `test_valid_problem_statement(self) -> None`: Both validators accept problem_statement as text.
- `test_valid_problem_with_all_fields(self) -> None`: Both validators accept problem with all optional fields.
- `test_valid_success_criteria(self) -> None`: Both validators accept success_criteria as array of strings.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
