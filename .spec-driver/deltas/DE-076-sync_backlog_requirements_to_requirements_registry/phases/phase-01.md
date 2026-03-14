---
id: IP-076.PHASE-01
slug: 076-sync_backlog_requirements_to_requirements_registry-phase-01
name: IP-076 Phase 01 — Cleanup and refactor sync pipeline
created: '2026-03-09'
updated: '2026-03-09'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-076.PHASE-01
plan: IP-076
delta: DE-076
objective: >-
  Extract _upsert_record, eliminate _iter_plan_files, rename sync_from_specs → sync().
  Pure refactor — no behavioral change.
entrance_criteria:
  - DR-076 design decisions DEC-076-01, DEC-076-04 reviewed
  - Existing test suite passing
exit_criteria:
  - _upsert_record extracted, both call sites consolidated
  - _iter_plan_files removed, replaced with _iter_change_files(dirs, prefix="IP-")
  - sync() is primary method, sync_from_specs is deprecated alias
  - All existing tests pass unchanged
  - Linters pass (ruff + pylint)
verification:
  tests:
    - VT-COMPAT-076-005
  evidence: []
tasks:
  - id: T1
    name: Extract _upsert_record helper
  - id: T2
    name: Eliminate _iter_plan_files
  - id: T3
    name: Rename sync_from_specs → sync()
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-076.PHASE-01
entrance_criteria:
  - item: "DR-076 design decisions DEC-076-01, DEC-076-04 reviewed"
    completed: true
  - item: "Existing test suite passing"
    completed: true
exit_criteria:
  - item: "_upsert_record extracted, both call sites consolidated"
    completed: true
  - item: "_iter_plan_files removed"
    completed: true
  - item: "sync() is primary method, sync_from_specs is deprecated alias"
    completed: true
  - item: "All existing tests pass unchanged"
    completed: true
  - item: "Linters pass"
    completed: true
```

# Phase 1 — Cleanup and refactor sync pipeline

## 1. Objective

Pure refactor of `RequirementsRegistry` in `registry.py` to reduce duplication and prepare for the backlog sync feature in phase 2. No behavioral change — all existing tests must pass identically.

## 2. Links & References

- **Delta**: [DE-076](../DE-076.md)
- **Design Revision**: [DR-076](../DR-076.md) — DEC-076-01 (rename), DEC-076-04 (cleanup), DEC-076-06 (seen set)
- **Primary Spec**: SPEC-122
- **File**: `supekku/scripts/lib/requirements/registry.py`

## 3. Entrance Criteria

- [x] DR-076 design decisions reviewed
- [x] Existing test suite passing (`just test`)

## 4. Exit Criteria / Done When

- [x] `_upsert_record(record, seen, stats)` extracted — single merge-or-create path
- [x] `_iter_plan_files` removed — call site uses `_iter_change_files(dirs, prefix="IP-")`
- [x] `sync()` is the primary method; `sync_from_specs` is a one-line deprecated alias
- [x] All existing tests pass unchanged (3492 passed, 4 skipped)
- [x] `just lint` and `just pylint-files supekku/scripts/lib/requirements/registry.py` pass

## 5. Verification

- Run `just test` — full suite must pass with zero failures
- Run `just lint` — zero warnings
- Run `just pylint-files supekku/scripts/lib/requirements/registry.py` — no regression
- Verify `sync_from_specs` alias: grep for all call sites, confirm they still work

## 6. Assumptions & STOP Conditions

- **Assumption**: The merge-or-create loop at lines 291–302 and 326–336 is functionally identical
- **Assumption**: `_iter_plan_files` has no callers outside `sync_from_specs`
- **STOP when**: Any existing test fails after refactor — investigate before proceeding

## 7. Tasks & Progress

| Status | ID  | Description                         | Parallel? | Notes                  |
| ------ | --- | ----------------------------------- | --------- | ---------------------- |
| [x]    | T1  | Extract `_upsert_record` helper     | [ ]       | DEC-076-04, DEC-076-06 |
| [x]    | T2  | Eliminate `_iter_plan_files`        | [P]       | Independent of T1      |
| [x]    | T3  | Rename `sync_from_specs` → `sync()` | [ ]       | After T1               |
| [x]    | T4  | Update all call sites               | [ ]       | After T3               |
| [x]    | T5  | Run tests + linters                 | [ ]       | After T1–T4            |

### Task Details

- **T1: Extract `_upsert_record`**
  - **Approach**: Extract lines 291–302 / 326–336 into `_upsert_record(self, record, seen, stats)`. The method merges with existing record if present, or creates new; adds `record.uid` to `seen`; updates `stats`.
  - **Files**: `supekku/scripts/lib/requirements/registry.py`
  - **Testing**: Existing tests cover both code paths — no new tests needed
  - **Signature consideration**: Add `source_kind=""` and `source_type=""` params now (defaulting to empty) to avoid a second signature change in phase 2. Stamp on record after merge.

- **T2: Eliminate `_iter_plan_files`**
  - **Approach**: Replace `self._iter_plan_files(plan_dirs)` call at line 378 with `self._iter_change_files(plan_dirs, prefix="IP-")`. Delete `_iter_plan_files` method (lines 999–1009).
  - **Files**: `supekku/scripts/lib/requirements/registry.py`
  - **Testing**: Existing coverage tests exercise this path

- **T3: Rename `sync_from_specs` → `sync()`**
  - **Approach**: Rename method. Add `sync_from_specs = sync` as deprecated alias (one-line assignment, no wrapper needed).
  - **Files**: `supekku/scripts/lib/requirements/registry.py`
  - **Testing**: All call sites (internal + CLI) must be updated

- **T4: Update all call sites**
  - **Approach**: `grep -r sync_from_specs` to find all callers. Update to `sync()`. Key sites: `cli/sync.py` line 634, test files.
  - **Files**: `supekku/cli/sync.py`, `supekku/scripts/lib/requirements/registry_test.py`

## 8. Risks & Mitigations

| Risk                                   | Mitigation                 | Status |
| -------------------------------------- | -------------------------- | ------ |
| Missed call site for `sync_from_specs` | grep + alias as safety net | open   |

## 9. Decisions & Outcomes

- DEC-076-04: Pre-implementation cleanup approved in DR
- T1 adds `source_kind`/`source_type` params to `_upsert_record` now (empty defaults) to prepare for phase 2
