# Notes for DE-140

## P01 — Block Infrastructure

### Done

- **Task 1.1**: `supekku/scripts/lib/blocks/spec_requirements.py` — marker, constants, `SpecRequirementsBlock` dataclass, `extract_spec_requirements()`, `load_spec_requirements()`, `render_spec_requirements_block()`, schema registration.
- **Task 1.2**: `supekku/scripts/lib/blocks/spec_requirements_metadata.py` — `SPEC_REQUIREMENTS_METADATA` (BlockMetadata), `SPEC_REQUIREMENTS_VALIDATOR`, `validate_spec_requirements()` wrapper with cross-field invariant (DEC-140-10), duplicate ID check (DEC-140-15), spec ID cross-validation. ToleratedAlias entries for `kind`: FR/NF/NFR.
- **Tasks 1.3–1.6**: `supekku/scripts/lib/blocks/spec_requirements_test.py` — 39 tests covering all 11 VTs (VT-140-001 through -008, -027, -028) plus JSON schema gen, spec ID cross-validation, file loading.
- **Task 1.7**: Ruff clean. Pylint 9.94 (only `wrong-import-position` from established tail-end registration pattern matching `verification.py`).

### Verification

- 39/39 tests passing. Full regression suite pending.
- Ruff: zero warnings.
- Pylint: 9.94/10, 2 messages (both `wrong-import-position` — established pattern).

### Adaptations

- Refactored `validate_spec_requirements()` into 3 functions (`_check_duplicate_ids`, `_check_kind_prefix_invariant`, main wrapper) to satisfy pylint complexity/locals thresholds.
- `_canonicalize_kind()` resolves tolerated aliases by walking the metadata declaration rather than hardcoding, so alias changes propagate automatically.

### Status

- Committed: `3ef2d04d`
- Full regression: 5139 passed, 0 failures.

## P02 — Block-first Reading Pipeline

### Done

- **Task 2.1**: `records_from_spec()` in `parser.py` — block-first with regex fallback. Extracted helpers: `_try_extract_block()`, `_records_from_block()`, `_record_from_block_entry()`, `_apply_breakout_metadata()`, `_relative_path()`.
- **Task 2.2**: `registry.py` rewired — both spec_registry and spec_dirs paths now call `records_from_spec()`. Removed unused imports (`_records_from_frontmatter`, `_records_from_content`, `_load_breakout_metadata`).
- **Tasks 2.3–2.4**: `parser_block_test.py` — 19 tests covering all 8 VTs (VT-140-009 through -014, -025, -026) plus edge cases (malformed fallback, empty block, validation warnings, tolerated aliases).
- **Tasks 2.5–2.6**: 172/172 requirements tests pass. Ruff clean. Pylint: new code clean; pre-existing `_records_from_content` complexity unchanged.

### Verification

- 19/19 new tests passing. 172/172 requirements module tests passing.
- Full regression suite pending confirmation.
- Ruff: zero warnings.

### Adaptations

- Refactored aggressively to keep new functions under pylint complexity thresholds — 6 focused helpers instead of 2 monolithic functions.
- `_canonicalize_kind_value()` in parser uses a simple map (separate from metadata's `_canonicalize_kind()`) — keeps parser dependency-light.

### Status

- Committed: `f5987672`
- Full regression running.

