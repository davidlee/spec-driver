# supekku.scripts.lib.memory.ids_test

Tests for memory ID validation and normalization.

## Classes

### TestExtractTypeFromId

Type extraction: second segment of canonical ID.

#### Methods

- `test_four_segment(self) -> None`
- `test_non_canonical_returns_none(self) -> None`
- `test_old_style_returns_none(self) -> None`
- `test_three_segment(self) -> None`
- `test_two_segment(self) -> None`

### TestFilenameFromId

Filename derivation from canonical ID.

#### Methods

- `test_four_segment(self) -> None`
- `test_preserves_hyphens(self) -> None`
- `test_simple(self) -> None`

### TestNormalizeMemoryId

Normalization: prepend mem. if missing, lowercase.

#### Methods

- `test_already_canonical(self) -> None`
- `test_canonical_with_uppercase(self) -> None`
- `test_lowercases(self) -> None`
- `test_prepends_mem_prefix(self) -> None`
- `test_rejects_empty(self) -> None`
- `test_single_segment_shorthand(self) -> None`
- `test_strips_whitespace(self) -> None`
- `test_validates_after_normalization(self) -> None`: Invalid characters still rejected after prefix prepend.

### TestValidateMemoryId

Validation: canonical form, rejection, normalization on input.

#### Methods

- `test_canonical_four_segments(self) -> None`
- `test_canonical_six_segments(self) -> None`
- `test_canonical_three_segments(self) -> None`
- `test_digits_in_segments(self) -> None`
- `test_hyphens_in_segments(self) -> None`
- `test_lowercases_input(self) -> None`
- `test_rejects_empty_segment(self) -> None`
- `test_rejects_empty_string(self) -> None`
- `test_rejects_leading_hyphen_in_segment(self) -> None`
- `test_rejects_missing_mem_prefix(self) -> None`
- `test_rejects_single_segment(self) -> None`
- `test_rejects_spaces_in_segment(self) -> None`
- `test_rejects_too_many_segments(self) -> None`
- `test_rejects_trailing_dot(self) -> None`
- `test_rejects_trailing_hyphen_in_segment(self) -> None`
- `test_rejects_underscores(self) -> None`
- `test_rejects_uppercase_after_normalize(self) -> None`
- `test_rejects_whitespace(self) -> None`
- `test_two_segments_minimum(self) -> None`
