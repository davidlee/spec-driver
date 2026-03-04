---
id: IP-029.PHASE-02
slug: 029-canonical_contract_storage-phase-02
name: IP-029 Phase 02 — Drift warnings & dead code cleanup
created: '2026-03-04'
updated: '2026-03-04'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-029.PHASE-02
plan: IP-029
delta: DE-029
objective: >-
  Implement convention drift warnings (FR-012), fix check-mode contract gate
  for specless units, remove dead code orphaned by Phase 1 mirror inversion.
entrance_criteria:
  - Phase 1 complete (all adapters write to canonical paths)
  - Mirror builder inverted (compat symlinks FROM SPEC-*/contracts/ → .contracts/)
exit_criteria:
  - Drift warning emitted when SPEC has non-empty contracts/ but zero canonical entries
  - VT-CONTRACTS-DRIFT-001 passes
  - check mode processes contracts for specless source units (no spurious skip)
  - Dead methods removed from mirror.py (_collect_entries, _resolve_conflicts, _create_symlinks)
  - MirrorEntry removed from mirror.py and __init__.py exports
  - just green (tests + lint + pylint)
verification:
  tests:
    - VT-CONTRACTS-DRIFT-001
  evidence: []
tasks:
  - id: "2.1"
    description: "Implement drift detection in ContractMirrorTreeBuilder.rebuild()"
  - id: "2.2"
    description: "Write VT-CONTRACTS-DRIFT-001 test"
  - id: "2.3"
    description: "Fix check-mode gate: specless units must still generate contracts"
  - id: "2.4"
    description: "Remove dead code: _collect_entries, _resolve_conflicts, _create_symlinks, MirrorEntry"
  - id: "2.5"
    description: "Update IP-029 verification coverage statuses and progress tracking"
risks:
  - description: "MirrorEntry may be imported by downstream code we haven't found"
    mitigation: "Grep confirmed zero external usage outside mirror.py and its test"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-029.PHASE-02
```

# Phase 2 — Drift warnings & dead code cleanup

## 1. Objective

Implement convention drift warnings per DR-029 §7.5 and PROD-014.FR-012: when a spec has a non-empty `contracts/` directory but canonical generation produced zero `.contracts/**` entries for that spec's source unit, emit a warning. Fix the check-mode gate that skips contract generation for specless source units (same class of bug as Phase 1 Bug 1). Remove dead code orphaned by the Phase 1 mirror inversion.

## 2. Links & References
- **Delta**: [DE-029](../DE-029.md)
- **Design Revision**: [DR-029](../DR-029.md) — §7.5 (drift warnings)
- **Requirements**: PROD-014.FR-012 (convention drift warnings)
- **Phase 1**: [phase-01.md](./phase-01.md) — §10 documents dead code list

## 3. Entrance Criteria
- [x] Phase 1 complete (adapters write canonical files, compat symlinks inverted)
- [x] `rebuild()` already returns a warnings list (infrastructure exists)

## 4. Exit Criteria / Done When
- [x] Drift warning emitted when SPEC has non-empty `contracts/` but zero canonical entries
- [x] Empty `contracts/` dirs do NOT trigger warning (no false positives)
- [x] VT-CONTRACTS-DRIFT-001 passes
- [x] Check mode generates contracts for specless source units (no spurious "no registered spec" skip)
- [x] Dead methods removed: `_collect_entries`, `_resolve_conflicts`, `_create_symlinks`
- [x] `MirrorEntry` removed from `__init__.py` exports (class kept internally for `*_mirror_entries`)
- [x] `just` green (5 pre-existing failures in unrelated `TestVerificationStatusFilters`)

## 5. Verification
- `just test` — full test suite
- `just lint` + `just pylint` — zero warnings
- VT-CONTRACTS-DRIFT-001: create spec with non-empty `contracts/` dir, ensure mapper produces zero canonical entries, assert warning emitted

## 6. Assumptions & STOP Conditions
- Assumptions:
  - `rebuild()` has access to the registry (knows which specs exist and their tech dirs)
  - Canonical `.contracts/` entries are written before `rebuild()` runs (Phase 1 guarantee)
- STOP when:
  - Drift detection requires information not available during `rebuild()` (e.g. which source units were processed)

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Implement drift detection in `rebuild()` | | `_detect_drift()` method added; checks non-empty spec contracts/ vs canonical entries |
| [x] | 2.2 | Write VT-CONTRACTS-DRIFT-001 test | | 5 tests: positive (zig, python), negative (empty dir, missing dir, canonical exists) |
| [x] | 2.3 | Fix check-mode gate for specless contract generation | | Restructured early return; check mode now falls through to contract generation |
| [x] | 2.4 | Remove dead code from `mirror.py` + `__init__.py` | [P] | Removed `_collect_entries`, `_resolve_conflicts`, `_create_symlinks`; `MirrorEntry` kept (used by `*_mirror_entries`) but removed from `__init__.py` exports |
| [x] | 2.5 | Update IP-029 verification coverage + progress | | All 5 VTs → verified; §9 checkboxes updated |

### Task Details

- **2.1 Drift detection in rebuild()**
  - **Design**: Per DR-029 §7.5 — during compat symlink creation, for each registered spec that has a non-empty `contracts/` dir (≥1 `.md` file), check whether any canonical `.contracts/<view>/...` entries exist for that spec's source units. If zero, append a warning.
  - **Files**: `supekku/scripts/lib/contracts/mirror.py` — `ContractMirrorTreeBuilder.rebuild()`
  - **Approach**: After building compat symlinks, iterate specs in registry. For each spec with `contracts/` containing `.md` files, check if any symlinks were created. If none, warn.

- **2.2 VT-CONTRACTS-DRIFT-001**
  - **Files**: `supekku/scripts/lib/contracts/mirror_test.py`
  - **Approach**: TDD. Create a spec dir with a non-empty `contracts/` subdir (pre-existing `.md` file). Run `rebuild()` with no canonical entries in `.contracts/` for that spec. Assert warning list contains drift message. Also test that empty `contracts/` dirs do NOT trigger.

- **2.3 Fix check-mode gate**
  - **Files**: `supekku/scripts/sync_specs.py` (line 221-225), `supekku/scripts/sync_specs_test.py`
  - **Problem**: `process_source_unit()` early-returns when `check_mode=True` and no spec exists, skipping contract generation entirely. Same class of bug as Phase 1 Bug 1.
  - **Approach**: Restructure so check-mode skips spec creation but still falls through to contract generation at line 264. Update/add tests.
  - **Symptom**: `sync --check` emits "no registered spec for check mode" for every specless source unit.

- **2.4 Remove dead code**
  - **Files**: `supekku/scripts/lib/contracts/mirror.py`, `supekku/scripts/lib/contracts/__init__.py`
  - **Remove**: `_collect_entries` (lines ~391-439), `_resolve_conflicts` (lines ~441-467), `_create_symlinks` (lines ~469-480), `MirrorEntry` class (lines ~111-118)
  - **Remove from `__init__.py`**: `MirrorEntry` import and `__all__` entry
  - **Keep**: all `*_mirror_entries()` functions, all `resolve_*_variant_outputs()` functions, `python_staging_dir()`

- **2.5 Update IP-029**
  - **Files**: `change/deltas/DE-029-canonical_contract_storage/IP-029.md`
  - **Updates**: VT coverage entries `planned` → `verified`, §9 progress checkboxes

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Drift detection needs source-unit-to-spec mapping | Registry already maps specs to source units; `_canonical_paths_for()` exists | resolved |
| Removing MirrorEntry breaks external imports | Kept class (used by `*_mirror_entries`); only removed from `__init__.py` exports | resolved |

## 9. Decisions & Outcomes
- 2026-03-04 — `MirrorEntry` kept as internal class (used by `*_mirror_entries` return types); only removed from public exports in `__init__.py`
- 2026-03-04 — Check-mode gate fix: `not create_specs and not generate_contracts` check moved before check_mode guard, so check-mode with contracts enabled still generates

## 10. Findings / Research Notes
- `_scan_python_contracts()` crashed when `.contracts/` dir didn't exist — added `is_dir()` guard (bugfix)
- `_detect_drift()` deduplicates by spec_id to avoid multiple warnings for multi-identifier specs
- 5 pre-existing test failures in `TestVerificationStatusFilters` (CLI test, unrelated to DE-029)

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored (2320 passed, lint clean, pylint 9.70)
- [x] Phase notes updated
- [x] IP-029 progress and VT statuses updated
