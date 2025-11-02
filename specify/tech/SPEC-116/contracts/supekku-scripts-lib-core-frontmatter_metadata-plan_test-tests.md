# supekku.scripts.lib.core.frontmatter_metadata.plan_test

Dual-validation tests for plan frontmatter metadata.

## Classes

### PlanFrontmatterValidationTest

Test metadata validator for plan/phase/task-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_empty_string_in_entrance_criteria(self) -> None`: New validator rejects empty strings in entrance_criteria. - Invalid cases (new validator only)
- `test_empty_string_in_exit_criteria(self) -> None`: New validator rejects empty strings in exit_criteria.
- `test_valid_empty_arrays(self) -> None`: Both validators accept empty arrays.
- `test_valid_entrance_criteria(self) -> None`: Both validators accept entrance_criteria as array.
- `test_valid_exit_criteria(self) -> None`: Both validators accept exit_criteria as array.
- `test_valid_minimal_phase(self) -> None`: Both validators accept minimal phase (base fields only).
- `test_valid_minimal_plan(self) -> None`: Both validators accept minimal plan (base fields only). - Valid cases
- `test_valid_minimal_task(self) -> None`: Both validators accept minimal task (base fields only).
- `test_valid_objective(self) -> None`: Both validators accept objective as text.
- `test_valid_plan_with_all_fields(self) -> None`: Both validators accept plan with all optional fields.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
