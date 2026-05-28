# supekku.scripts.lib.requirements.parser_block_test

Tests for block-first reading pipeline in parser.

Covers VT-140-009 through VT-140-014, VT-140-025, VT-140-026.

## Functions

- `_block_body(spec_id) -> str`
- `_make_repo() -> Path`
- `_prose_body(spec_id) -> str`
- `_write_spec(root, spec_id, body) -> Path`

## Classes

### TestBlockFirst

VT-140-009: block present → records from block.

#### Methods

- `test_block_path_used_when_block_present(self) -> None`
- `test_block_records_have_correct_status(self) -> None`

### TestBlockOnlyFields

VT-140-026: description/acceptance_criteria not on record.

#### Methods

- `test_no_description_on_record(self) -> None`

### TestBreakoutMerge

VT-140-013: breakout metadata merges for both block and prose.

#### Methods

- `test_breakout_merges_with_block_source(self) -> None`
- `test_breakout_merges_with_prose_source(self) -> None`
- `_write_breakout(self, spec_path, req_id, ext_id) -> None`

### TestEdgeCases

Extraction failure and stats tracking.

#### Methods

- `test_empty_requirements_block_yields_nothing(self) -> None`
- `test_malformed_block_falls_back_to_regex(self) -> None`
- `test_stats_tracks_validation_warnings(self) -> None`
- `test_tolerated_kind_alias_canonicalized(self) -> None`

### TestFieldMapping

VT-140-012: lifecycle→status, kind canonicalized, UID derived.

#### Methods

- `test_category_from_block(self) -> None`
- `test_kind_canonicalized(self) -> None`
- `test_lifecycle_maps_to_status(self) -> None`
- `test_tags_from_block(self) -> None`
- `test_uid_derived_from_spec_and_id(self) -> None`

### TestMutualExclusion

VT-140-011: block and regex never both for same spec.

#### Methods

- `test_block_present_ignores_prose_requirements(self) -> None`: Spec with both block and prose — only block records emitted.

### TestOrphanedBreakout

VT-140-025: breakout files for missing requirements tolerated.

#### Methods

- `test_orphaned_breakout_does_not_create_record(self) -> None`

### TestRegexFallback

VT-140-010: no block → regex path.

#### Methods

- `test_regex_path_when_no_block(self) -> None`

### TestSourceKindTracking

VT-140-014: source_kind set correctly per path.

#### Methods

- `test_block_source_kind(self) -> None`
- `test_prose_source_kind(self) -> None`
