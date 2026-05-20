# supekku.scripts.lib.blocks.metadata.aliases_test

Tests for normalize_field (DE-137 IP-137-P01 task 1.9).

VT-CC-013 parity: every entry of the legacy ``CANONICAL_STATUS_MAP``
plus its case/whitespace variants must canonicalise via
``normalize_field("delta", "status", ...)``.

## Constants

- `_DELTA_STATUS_PARITY` - coverage in changes/lifecycle_test.py).

## Functions

- `test_delta_status_case_insensitive() -> None`
- @pytest.mark.parametrize(Tuple[raw, expected], _DELTA_STATUS_PARITY) `test_delta_status_parity(raw, expected) -> None`: Permanent aliases canonicalise via metadata for delta.status.
- `test_delta_status_strips_whitespace() -> None`
- `test_kinds_without_aliases_just_normalise() -> None`: A kind with enum_values but empty aliases preserves the canonical input.
- `test_missing_field_returns_normalised_value() -> None`
- `test_missing_kind_returns_normalised_value() -> None`
- `test_non_string_passes_through_unchanged() -> None`
- `test_plan_status_shared_aliases() -> None`: plan/phase/task share the same alias matrix.
- `test_unknown_value_preserved_after_normalisation() -> None`: Values without alias mapping return their case-folded form.
