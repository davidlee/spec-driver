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

- Uncommitted. Will commit after full regression suite confirms clean.
- `.spec-driver` delta status already flipped to `in-progress`.

