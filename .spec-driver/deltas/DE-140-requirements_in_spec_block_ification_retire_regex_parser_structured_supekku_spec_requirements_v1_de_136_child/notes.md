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
- Full regression: pending (was clean at P01; requirements module 172/172 pass).

## New Agent Instructions

### Context

DE-140 implements `supekku:spec.requirements@v1` — structured YAML blocks replacing regex-based requirement parsing. Part of DE-136 umbrella program.

**Completed**: P01 (block infrastructure), P02 (reading pipeline).
**Remaining**: P03, P04, P05. P03 and P04 can run in parallel. P05 depends on all three.

### Required Reading

1. **Delta**: `.spec-driver/deltas/DE-140-requirements_in_spec_block_ification_retire_regex_parser_structured_supekku_spec_requirements_v1_de_136_child/DE-140.md`
2. **Design Revision**: `DR-140.md` in same directory — §7 (Validation & Strict Flip) for P03, §6 (Migration) for P04
3. **IP**: `IP-140.md` in same directory — phase overview, VT assignments, dependency graph
4. **This file** for P01/P02 execution context

### Key Files (P01/P02 output — available for import)

- `supekku/scripts/lib/blocks/spec_requirements.py` — `extract_spec_requirements()`, `render_spec_requirements_block()`, `REQUIREMENTS_MARKER`
- `supekku/scripts/lib/blocks/spec_requirements_metadata.py` — `validate_spec_requirements()`, `SPEC_REQUIREMENTS_METADATA`
- `supekku/scripts/lib/requirements/parser.py` — `records_from_spec()` (new public API)
- `supekku/scripts/lib/requirements/registry.py` — already wired to `records_from_spec()`

### P03 — Validation & Template (6 VTs)

- **Scope**: Wire `_validate_spec_requirements_blocks()` in `WorkspaceValidator`, update `specs/creation.py` to emit empty block, update spec template
- **DR reference**: DR-140 §7 (WorkspaceValidator Wiring)
- **Key files to modify**: `supekku/scripts/lib/validation/validator.py`, `supekku/scripts/lib/specs/creation.py`, `supekku/templates/spec.md`
- **VTs**: VT-140-015, -016, -019, -020, -022, -030
- **Phase sheet**: needs creation via `spec-driver create phase`

### P04 — Migration (5 VAs)

- **Scope**: Interactive per-spec migration step in `spec_driver/migrations/`
- **DR reference**: DR-140 §6 (Migration) — DEC-138-12 isolation constraint is critical
- **Key constraint**: migration module imports only stdlib + `_helpers` + `_protocol` + pyyaml. Frozen-local constants. Zero supekku imports.
- **VAs**: VA-140-001 through -005
- **Phase sheet**: needs creation via `spec-driver create phase`

### Relevant Memories

- `mem.fact.spec-driver.status-enums` — canonical lifecycle enums
- `mem.concept.spec-driver.requirement-lifecycle` — requirement lifecycle guidance
- `mem.fact.yaml.strenum-serialization` — StrEnum .value at YAML boundaries
- `mem.pattern.architecture.migration-principles` — migration isolation patterns from DE-125

## P03 — Validation & Template

### Done

- **Task 3.1**: `_validate_spec_requirements_blocks()` in `validator.py` — schema validation via `SPEC_REQUIREMENTS_VALIDATOR` with severity-preserving `_block_issue()` dispatch, spec field cross-validation, strict-mode trimmed-empty/blank-item rejection.
- **Task 3.2**: `creation.py` — `render_spec_requirements_block(next_id)` emits empty `requirements: []` block (DEC-140-14).
- **Task 3.3**: `spec.md` template — `{{ spec_requirements_block }}` placeholder added in section 3.
- **Tasks 3.4–3.5**: `validator_spec_requirements_test.py` — 11 tests covering VT-140-015, -016, -022. `creation_test.py` — 3 new tests covering VT-140-019, -020, -030.
- **Task 3.6**: Ruff clean. Pylint: no new messages; fixed pre-existing `unused-variable` in creation_test.py.

### Verification

- 14 new tests passing. 5172/5172 total tests passing.
- Ruff: zero warnings.
- Pylint: no new messages from P03 changes.

### Adaptations

- WorkspaceValidator uses `SPEC_REQUIREMENTS_VALIDATOR.validate()` (raw validator) for severity-preserving dispatch via `_block_issue()`, plus inline checks for spec field cross-validation and strict-mode content rejection. Did NOT use `validate_spec_requirements()` wrapper because it returns `list[str]` (no severity) — would lose warning/error distinction. The custom checks (duplicate IDs, kind-prefix invariant) from the wrapper are already covered by the raw validator's schema checks.
- Strict-mode content checks (`_check_strict_content_requirements`) separated into own method to keep `_validate_spec_requirements_blocks` complexity low.

### Status

- Committed: `625ce858`
- Phase sheet + code committed together per doctrine.
- Full regression: 5172 passed, 0 failures.

### Worktree State

- Clean for DE-140. Only pre-existing `flake.nix` modification remains.
- All `.spec-driver` changes committed promptly per doctrine.

### Advice

- P03 is simpler (validation wiring follows established patterns in `validator.py`). P04 is more complex (migration isolation, interactive flow, drift ledger).
- For P04, study existing migration steps in `spec_driver/migrations/` before writing — the isolation constraint (DEC-138-12) is strict and easy to violate.
- DEC-140-14: template emits *empty* requirements block, not sample FR-001.
- P02's `_records_from_frontmatter()` is still importable (not deleted) for backward compatibility with existing tests, but new code should use `records_from_spec()`.

