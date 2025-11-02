# supekku.scripts.lib.core.frontmatter_metadata.spec_test

Dual-validation tests for spec frontmatter metadata.

Tests that the new metadata-driven validator handles spec-specific fields
correctly while maintaining compatibility with base field validation.

## Classes

### SpecFrontmatterValidationTest

Test metadata validator for spec-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_concern_missing_required_field(self) -> None`: New validator rejects concern missing name or description.
- `test_decision_missing_required_fields(self) -> None`: New validator rejects decision missing id or summary.
- `test_empty_hypotheses_array(self) -> None`: Both validators accept empty hypotheses array.
- `test_empty_spec_arrays_valid(self) -> None`: Both validators accept empty arrays for spec fields. - Array validation (4 tests)
- `test_hypothesis_with_all_fields(self) -> None`: Both validators accept hypothesis with all fields.
- `test_invalid_c4_level(self) -> None`: New validator rejects invalid c4_level.
- `test_invalid_hypothesis_status(self) -> None`: New validator rejects invalid hypothesis status.
- `test_source_empty_variants_array(self) -> None`: New validator rejects source with empty variants array.
- `test_source_invalid_language(self) -> None`: New validator rejects source with invalid language.
- `test_source_missing_language(self) -> None`: New validator rejects source missing language.
- `test_source_missing_variants(self) -> None`: New validator rejects source missing variants.
- `test_valid_c4_levels(self) -> None`: New validator accepts all valid c4_level values. - Enum validation (4 tests)
- `test_valid_concerns_array(self) -> None`: Both validators accept valid concerns array. - Nested object validation (8 tests)
- `test_valid_constraints_array(self) -> None`: Both validators accept valid constraints.
- `test_valid_decisions_array(self) -> None`: Both validators accept valid decisions array.
- `test_valid_go_source(self) -> None`: Both validators accept valid Go source.
- `test_valid_guiding_principles_array(self) -> None`: Both validators accept valid guiding_principles.
- `test_valid_hypothesis_statuses(self) -> None`: New validator accepts all valid hypothesis status values.
- `test_valid_minimal_spec(self) -> None`: Both validators accept minimal spec (base fields only). - Valid cases (3 tests)
- `test_valid_multiple_sources(self) -> None`: Both validators accept multiple sources.
- `test_valid_python_source(self) -> None`: Both validators accept valid Python source. - Sources validation (8 tests)
- `test_valid_real_world_spec(self) -> None`: Both validators accept real-world SPEC-090 style frontmatter.
- `test_valid_responsibilities_array(self) -> None`: Both validators accept valid responsibilities.
- `test_valid_spec_with_all_fields(self) -> None`: Both validators accept spec with all optional fields.
- `test_valid_verification_strategy(self) -> None`: Both validators accept valid verification_strategy.
- `test_variant_missing_required_fields(self) -> None`: New validator rejects variant missing name or path.
- `test_verification_missing_required_fields(self) -> None`: New validator rejects verification missing type or description.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).

Args:
  data: Frontmatter dictionary to validate

Returns:
  - old_error: None if valid, error message if invalid
  - new_errors: List of error strings from new validator
