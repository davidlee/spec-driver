# supekku.scripts.lib.requirements.parser_strict_test

Tests for strict-mode parser behavior (DE-140 P05).

Covers VT-140-021, VT-140-023, VT-140-024.

## Functions

- `_block_body(spec_id) -> str`
- `_make_repo() -> Path`
- `_malformed_block_body(spec_id) -> str`
- `_prose_body(spec_id) -> str`
- `_write_spec(root, spec_id, body) -> Path`

## Classes

### TestPostFlipExtractionFailure

VT-140-024: strict mode, extraction failure → zero records.

#### Methods

- `test_malformed_block_strict_increments_stats(self) -> None`
- `test_malformed_block_strict_yields_zero_records(self) -> None`

### TestPostFlipNoBlock

VT-140-021: strict mode, no block → zero records.

#### Methods

- `test_non_strict_no_block_falls_back(self) -> None`: Confirm non-strict still produces regex records (baseline).
- `test_strict_no_block_does_not_fall_back_to_regex(self) -> None`: Prose requirements exist but strict mode ignores them.
- `test_strict_no_block_yields_zero_records(self) -> None`
- `test_strict_with_block_still_works(self) -> None`: Strict mode with valid block produces normal records.

### TestPreFlipExtractionFailure

VT-140-023: tolerant mode, extraction failure → regex fallback.

#### Methods

- `test_default_strict_is_false(self) -> None`: Default behavior (no strict kwarg) falls back on extraction failure.
- `test_malformed_block_falls_back_to_regex(self) -> None`
