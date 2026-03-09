# supekku.scripts.lib.core.frontmatter_metadata.memory_test

Dual-validation tests for memory frontmatter metadata.

## Functions

- `_minimal_memory() -> dict`: Build a minimal valid memory record, with optional overrides.

## Classes

### MemoryFrontmatterValidationTest

Test metadata validator for memory-specific fields.

**Inherits from:** unittest.TestCase

#### Methods

- `test_audience_not_array(self) -> None`: New validator rejects audience when not an array.
- `test_empty_string_in_requires_reading(self) -> None`: New validator rejects empty strings in requires_reading.
- `test_empty_string_in_scope_commands(self) -> None`: New validator rejects empty strings in scope.commands.
- `test_empty_string_in_scope_globs(self) -> None`: New validator rejects empty strings in scope.globs.
- `test_empty_string_in_scope_paths(self) -> None`: New validator rejects empty strings in scope.paths.
- `test_invalid_audience_value(self) -> None`: New validator rejects invalid audience enum value.
- `test_invalid_confidence(self) -> None`: New validator rejects invalid confidence.
- `test_invalid_memory_type(self) -> None`: New validator rejects invalid memory_type. - ── Invalid cases (new validator only) ──────────────────────
- `test_invalid_review_by_date_format(self) -> None`: New validator rejects invalid review_by date format.
- `test_invalid_severity(self) -> None`: New validator rejects invalid priority.severity.
- `test_invalid_verified_date_format(self) -> None`: New validator rejects invalid verified date format.
- `test_invalid_visibility_value(self) -> None`: New validator rejects invalid visibility enum value.
- `test_missing_memory_type(self) -> None`: New validator rejects missing memory_type.
- `test_requires_reading_not_array(self) -> None`: New validator rejects requires_reading when not an array.
- `test_valid_all_confidence_values(self) -> None`: Both validators accept all confidence enum values.
- `test_valid_all_memory_types(self) -> None`: Both validators accept all memory_type enum values.
- `test_valid_all_severity_values(self) -> None`: Both validators accept all priority.severity enum values.
- `test_valid_audience_single(self) -> None`: Both validators accept single audience value.
- `test_valid_empty_arrays(self) -> None`: Both validators accept empty arrays for memory-specific fields.
- `test_valid_links_empty(self) -> None`: Both validators accept empty links object.
- `test_valid_links_mixed(self) -> None`: Both validators accept links with out and missing.
- `test_valid_links_with_label(self) -> None`: Both validators accept links out entry with optional label.
- `test_valid_links_with_missing(self) -> None`: Both validators accept links with missing entries.
- `test_valid_links_with_out(self) -> None`: Both validators accept links with resolved out entries. - ── Links field tests ──────────────────────────────────────
- `test_valid_memory_with_all_fields(self) -> None`: Both validators accept memory with all optional fields.
- `test_valid_minimal_memory(self) -> None`: Both validators accept minimal memory (base fields + memory_type). - ── Valid cases ──────────────────────────────────────────────
- `test_valid_priority_weight_only(self) -> None`: Both validators accept priority with weight only.
- `test_valid_provenance_empty_sources(self) -> None`: Both validators accept provenance with empty sources.
- `test_valid_review_by_date(self) -> None`: Both validators accept valid review_by date.
- `test_valid_scope_empty(self) -> None`: Both validators accept empty scope object.
- `test_valid_scope_partial(self) -> None`: Both validators accept scope with only some sub-fields.
- `test_valid_verified_date(self) -> None`: Both validators accept valid verified date.
- `test_valid_visibility_both(self) -> None`: Both validators accept both visibility values.
- `_assert_both_valid(self, data) -> None`: Assert both validators accept the data.
- `_validate_both(self, data) -> tuple[Tuple[<BinOp>, list[str]]]`: Run both validators and return (old_error, new_errors).
