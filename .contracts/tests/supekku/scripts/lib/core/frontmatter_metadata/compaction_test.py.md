# supekku.scripts.lib.core.frontmatter_metadata.compaction_test

Tests for frontmatter compaction using FieldMetadata persistence annotations.

## Functions

- `_make_metadata() -> BlockMetadata`: Build a minimal BlockMetadata with the given fields.

## Classes

### TestCompactFrontmatter

Core compaction logic tests.

**Inherits from:** unittest.TestCase

#### Methods

- `test_canonical_fields_always_kept(self) -> None`
- `test_default_omit_dict_equal_to_default_stripped(self) -> None`
- `test_default_omit_dict_with_superset_keys_kept(self) -> None`: applies_to with prod key differs from default {specs:[], requirements:[]}.
- `test_default_omit_kept_when_non_default(self) -> None`
- `test_default_omit_stripped_when_equal(self) -> None`
- `test_derived_fields_kept_in_full_mode(self) -> None`
- `test_derived_fields_omitted(self) -> None`
- `test_empty_data_returns_empty(self) -> None`
- `test_full_mode_keeps_everything(self) -> None`
- `test_invalid_mode_raises(self) -> None`
- `test_optional_kept_when_non_default(self) -> None`
- `test_optional_kept_when_present_no_default(self) -> None`
- `test_optional_omitted_when_absent(self) -> None`
- `test_optional_omitted_when_none(self) -> None`
- `test_optional_with_default_omitted_when_equal(self) -> None`
- `test_preserves_field_order(self) -> None`: Compacted output preserves insertion order of surviving fields.
- `test_unknown_fields_pass_through(self) -> None`

### TestDeltaCompactionRoundTrip

Round-trip tests using real DELTA_FRONTMATTER_METADATA.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_applies_to_with_prod_not_stripped(self) -> None`: Known pitfall: applies_to with prod key != default, must be kept.
- `test_empty_defaults_stripped(self) -> None`: Empty-default fields (aliases, relations, applies_to) are removed.
- `test_full_mode_preserves_all_fields(self) -> None`: Full mode keeps everything, including empty defaults.
- `test_minimal_delta_unchanged(self) -> None`: Minimal delta (canonical fields only) survives compaction.
- `test_optional_fields_kept_when_populated(self) -> None`
- `test_optional_fields_stripped_when_empty(self) -> None`: Optional fields (owners, tags, etc.) stripped when empty/default.
- `test_populated_defaults_kept(self) -> None`: Non-default values for default-omit fields are preserved.
- `test_round_trip_semantic_equivalence(self) -> None`: Compacted data + defaults reconstructs original semantics.
