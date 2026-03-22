# Notes for DE-114

## Status

All 3 phases **complete**. Delta ready for closure.

### Phase Summary

| Phase | Target                          | Result                                   |
| ----- | ------------------------------- | ---------------------------------------- |
| P01   | CLI layer (common.py, list.py)  | common.py 1,124→316, list.py 3,195→pkg   |
| P02   | creation.py, workflow_metadata  | creation.py 1,056→276, wf_meta 1,485→251 |
| P03   | requirements/registry.py        | registry.py 1,511→447 (5 modules)        |

### Phase 03 Results

**Source split** (registry.py 1,511 → 5 files):
- `models.py` (116): `RequirementRecord`, `SyncStats`
- `parser.py` (286): regex constants, `_records_from_content`, `_records_from_frontmatter`, `_validate_extraction`, `_load_breakout_metadata`
- `sync.py` (512): `_upsert_record`, all `_apply_*`, `_iter_*`, `_sync_backlog_requirements`, `_find_record_from_origin`, `_create_placeholder_record`, `_resolve_spec_path`
- `coverage.py` (214): `_apply_coverage_blocks`, `_check_coverage_drift`, `_compute_status_from_coverage`, `_extract_coverage_entries`
- `registry.py` (447): `RequirementsRegistry` class core + re-exports

**Test split** (registry_test.py 2,787 → 5 files):
- `models_test.py` (53): 1 class
- `parser_test.py` (365): 4 classes
- `sync_test.py` (1,300): 5 classes
- `coverage_test.py` (394): 2 classes
- `registry_test.py` (771): 5 classes

**Import graph** (acyclic): registry→sync→parser→models, registry→coverage→models

### Key Decisions

- **DEC-114-03**: Sync internals receive mutable `records` dict by reference — identical semantics.
- Test calls to extracted methods (e.g. `registry._compute_status_from_coverage()`) updated to call standalone functions directly.
- `sync.py` at 512 lines — slightly above 500 target but within justified range (DR §4c estimated ~500).
- Re-exports in slim `registry.py` for zero-change migration of all external importers.

### Verification

- 4,585 tests pass, 4 skipped
- `ruff check` clean
- Import graph verified acyclic via grep
- All external importers (8 files) use re-exported symbols — zero changes needed

### Follow-ups

- Backlog issue (tracked in DR-114 §9): Remove re-export shims and update importers to canonical paths.
- DE-116: registry split positions `RequirementRecord` in `models.py` for protocol work.
