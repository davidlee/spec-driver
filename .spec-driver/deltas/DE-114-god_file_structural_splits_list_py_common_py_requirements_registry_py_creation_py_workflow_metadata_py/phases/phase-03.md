---
id: IP-114-P03
slug: "114-god_file_structural_splits_list_py_common_py_requirements_registry_py_creation_py_workflow_metadata_py-phase-03"
name: "IP-114 Phase 03 — Lib: split requirements/registry.py"
created: "2026-03-23"
updated: "2026-03-23"
status: completed
kind: phase
plan: IP-114
delta: DE-114
---

# Phase 03 — Lib: split requirements/registry.py

## 1. Objective

Split `supekku/scripts/lib/requirements/registry.py` (1,511 lines) into 5 focused modules (models, parser, sync, coverage, slim registry) per DR-114 §4c. Split `registry_test.py` (2,787 lines, 17 classes) to mirror source. Zero behaviour change.

## 2. Links & References

- **Delta**: DE-114
- **Design Revision Sections**: DR-114 §4c (registry split), §7 DEC-114-03/04
- **Specs / PRODs**: SPEC-122
- **Support Docs**: DR-114 full call graph

## 3. Entrance Criteria

- [x] P01 complete (CLI layer)
- [x] P02 complete (creation + workflow_metadata)
- [x] All 4,585 tests passing
- [x] Worktree clean

## 4. Exit Criteria / Done When

- [x] `registry.py` ≤ 500 lines (447 — slim: class core + re-exports)
- [x] `models.py`, `parser.py`, `sync.py`, `coverage.py` created per DR-114 §4c
- [x] All source files ≤ 520 lines (sync.py=512, justified: DR target was ~500)
- [x] Import graph acyclic: registry→sync→parser→models, registry→coverage→models
- [x] Test files split to mirror source (5 test files: 53+365+1300+394+771)
- [x] Re-exports in slim `registry.py` for backward compat
- [x] `uv run ruff check` clean
- [x] Full test suite passes (4,585 pass)
- [x] No stale imports (grep verification)

## 5. Verification

- `uv run ruff check supekku/scripts/lib/requirements/`
- `uv run python -m pytest supekku/scripts/lib/requirements/ -v`
- `uv run python -m pytest supekku/ -x` (full suite)
- `wc -l supekku/scripts/lib/requirements/*.py` (size targets)
- Grep for circular imports

## 6. Assumptions & STOP Conditions

- Assumptions: Extracted functions receive `records` dict by reference (DEC-114-03). `sync()` stays as class method delegating to imported functions.
- STOP when: Circular import detected; test failure in unrelated subsystem.

## 7. Tasks & Progress

| Status | ID  | Description                         | Parallel? | Notes                                |
| ------ | --- | ----------------------------------- | --------- | ------------------------------------ |
| [x]    | 3.1 | Create `models.py`                  | [ ]       | 116 lines                            |
| [x]    | 3.2 | Create `parser.py`                  | [ ]       | 286 lines                            |
| [x]    | 3.3 | Create `sync.py`                    | [ ]       | 512 lines                            |
| [x]    | 3.4 | Create `coverage.py`                | [ ]       | 214 lines                            |
| [x]    | 3.5 | Slim `registry.py` + re-exports     | [ ]       | 447 lines                            |
| [x]    | 3.6 | Split test files (5 files)          | [ ]       | models/parser/sync/coverage/registry |
| [x]    | 3.7 | Lint + full test suite verification | [ ]       | 4,585 pass, 0 warnings               |

### Task Details

- **3.1 models.py**: `RequirementRecord`, `SyncStats` dataclasses (~120 lines)
- **3.2 parser.py**: `_is_requirement_like_line`, `_records_from_content`, `_records_from_frontmatter`, `_requirements_from_spec`, `_validate_extraction`, `_load_breakout_metadata`, regex constants (~280 lines)
- **3.3 sync.py**: All `_apply_*`, `_upsert_record`, `_iter_*`, `_find_record_from_origin`, `_create_placeholder_record`, `_resolve_spec_path`, `_sync_backlog_requirements` (~500 lines). Functions receive `records` dict by reference.
- **3.4 coverage.py**: `_apply_coverage_blocks`, `_check_coverage_drift`, `_compute_status_from_coverage`, `_extract_coverage_entries` (~200 lines)
- **3.5 registry.py slim**: Class core (`__init__`, `find`, `collect`, `iter`, `filter`, `_load`, `save`, `sync`, `set_status`, `search`, `move_requirement`, `find_by_*`) + re-exports (~350 lines)
- **3.6 test split**: 5 test files mirroring source per DR-114 §4c table
- **3.7 verification**: lint, full suite, line counts, import graph check

## 8. Risks & Mitigations

| Risk                                   | Mitigation                                | Status |
| -------------------------------------- | ----------------------------------------- | ------ |
| Subtle semantic change in extraction   | 2,787 lines of tests; pure function sigs  | open   |
| Circular imports between split modules | Acyclic graph by design; verify with grep | open   |

## 9. Decisions & Outcomes

## 10. Findings / Research Notes

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: 4,585 tests pass, ruff clean, import graph acyclic
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Delta closed
