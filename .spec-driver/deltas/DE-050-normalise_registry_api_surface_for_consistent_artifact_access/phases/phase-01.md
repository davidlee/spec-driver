---
id: IP-050.PHASE-01
slug: 050-normalise_registry_api_surface_for_consistent_artifact_access-phase-01
name: IP-050 Phase 01 - Group B registries
created: "2026-03-06"
updated: "2026-03-06"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-050.PHASE-01
plan: IP-050
delta: DE-050
objective: >-
  Add ADR-009 standard surface (find, collect, iter, filter) to SpecRegistry
  and ChangeRegistry. These are Group B — low risk, additive, no constructor
  changes needed.
entrance_criteria:
  - DR-050 approved
  - ADR-009 accepted
exit_criteria:
  - SpecRegistry exposes find(), collect(), iter(), filter()
  - ChangeRegistry exposes find(), iter(), filter()
  - SpecRegistry.get() emits DeprecationWarning
  - All existing tests pass
  - New unit tests for every added method
  - just lint + just pylint pass
verification:
  tests:
    - VT-050-01 (partial — Spec and Change registries)
    - VT-050-02 (regression)
  evidence: []
tasks:
  - id: 1.1
    description: Add find(), collect(), iter(), filter() to SpecRegistry
  - id: 1.2
    description: Deprecate SpecRegistry.get() with warning
  - id: 1.3
    description: Add find(), iter(), filter() to ChangeRegistry
  - id: 1.4
    description: Write tests for all new methods
risks:
  - description: get() deprecation breaks callers
    mitigation: alias calls find() internally; no removal
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-050.PHASE-01
```

# Phase 1 — Group B Registries (Spec + Change)

## 1. Objective

Add ADR-009 standard API surface to SpecRegistry and ChangeRegistry. These are
the lowest-risk registries to normalise: both are class-based with constructors
already close to the target pattern, and changes are purely additive.

## 2. Links & References

- **Delta**: [DE-050](../DE-050.md)
- **Design Revision**: [DR-050](../DR-050.md) §4 — Tier 1 code impact table
- **ADR**: ADR-009 §1-§3 — required surface and return conventions
- **Research**: [research.md](../research.md) — §1 SpecRegistry, §3 ChangeRegistry

## 3. Entrance Criteria

- [x] DR-050 authored
- [x] ADR-009 accepted

## 4. Exit Criteria / Done When

- [x] SpecRegistry: `find()`, `collect()`, `iter()`, `filter()` implemented
- [x] SpecRegistry: `get()` emits `DeprecationWarning`, delegates to `find()`
- [x] ChangeRegistry: `find()`, `iter()`, `filter()` implemented
- [x] All existing registry tests pass unchanged
- [x] New unit tests cover every added method (hit, miss, edge cases)
- [x] `just` passes (tests + both linters)

## 5. Verification

- Run: `just test` (full suite)
- Run: `just lint` + `just pylint`
- Inspect: deprecation warning emitted when `SpecRegistry.get()` called

## 6. Assumptions & STOP Conditions

- Assumptions: SpecRegistry's `_specs` dict is the canonical cache; `collect()`
  wraps it. ChangeRegistry's `collect()` already returns dict; `find()` delegates.
- STOP when: if `filter()` domain params are unclear for either registry, consult
  before guessing.

## 7. Tasks & Progress

| Status | ID  | Description                                                   | Parallel? | Notes                              |
| ------ | --- | ------------------------------------------------------------- | --------- | ---------------------------------- |
| [x]    | 1.1 | SpecRegistry: add `find()`, `collect()`, `iter()`, `filter()` | [P]       | done                               |
| [x]    | 1.2 | SpecRegistry: deprecate `get()` → `find()` with warning       |           | done                               |
| [x]    | 1.3 | ChangeRegistry: add `find()`, `iter()`, `filter()`            | [P]       | done                               |
| [x]    | 1.4 | Tests for SpecRegistry new methods                            |           | 16 new tests                       |
| [x]    | 1.5 | Tests for ChangeRegistry new methods                          |           | 7 new tests                        |
| [x]    | 1.6 | Lint + full test suite                                        |           | 2673 pass, ruff clean, pylint 9.55 |

### Task Details

- **1.1 SpecRegistry: standard surface**
  - **Files**: `supekku/scripts/lib/specs/registry.py`
  - **Approach**: `find(id)` delegates to `_specs.get(id)`. `collect()` returns
    `dict(self._specs)`. `iter(status=None)` yields from `_specs.values()` with
    optional status filter. `filter(status, category, tag)` — domain params TBD
    from existing usage patterns.
  - **Testing**: `supekku/scripts/lib/specs/registry_test.py`

- **1.2 SpecRegistry: deprecate get()**
  - **Approach**: `get()` calls `self.find()`, emits `warnings.warn("Use find()",
DeprecationWarning, stacklevel=2)`.

- **1.3 ChangeRegistry: standard surface**
  - **Files**: `supekku/scripts/lib/changes/registry.py`
  - **Approach**: `find(id)` calls `self.collect().get(id)`. `iter(status=None)`
    yields from `collect().values()`. `filter(status)` — status is the primary
    domain filter; `find_by_implements()` remains as a specialised method.
  - **Testing**: `supekku/scripts/lib/changes/registry_test.py`

## 8. Risks & Mitigations

| Risk                                 | Mitigation                                                   | Status |
| ------------------------------------ | ------------------------------------------------------------ | ------ |
| `get()` deprecation confuses callers | Alias delegates to `find()`; warning includes migration hint | open   |
| `filter()` param design unclear      | Check Group A filter patterns; keep minimal                  | open   |

## 9. Decisions & Outcomes

## 10. Findings / Research Notes

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (`just` passes — 2673 tests, ruff clean, pylint 9.55)
- [x] Notes updated
- [ ] Hand-off notes to Phase 2
