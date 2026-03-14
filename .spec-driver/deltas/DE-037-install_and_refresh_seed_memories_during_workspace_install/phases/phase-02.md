---
id: IP-037.PHASE-02
slug: 037-install_and_refresh_seed_memories_during_workspace_install-phase-02
name: IP-037 Phase 02
created: '2026-03-04'
updated: '2026-03-04'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-037.PHASE-02
plan: IP-037
delta: DE-037
objective: >-
  Implement two-bucket memory install behavior in install.py: seed (create-only)
  and spec-driver (replace/refresh with pruning). Dual discovery for dev/installed contexts.
entrance_criteria:
  - Phase 0 complete (corpus classified, seed stubs authored)
  - pyproject.toml force-include configured
exit_criteria:
  - install.py has memory install step with dual discovery
  - seed bucket creates missing files only, never overwrites
  - spec-driver bucket replaces/refreshes from package source
  - managed-set pruning removes spec-driver IDs absent from source
  - unmanaged memories are never touched
  - all new behavior covered by tests (VT-037-001 through VT-037-003)
  - existing install tests still pass
verification:
  tests:
    - VT-037-001 seed create-only
    - VT-037-002 spec-driver managed refresh
    - VT-037-003 unmanaged preservation
  evidence: []
tasks:
  - id: "2.1"
    description: Write tests for memory install behavior (TDD)
  - id: "2.2"
    description: Implement _find_memory_source, _classify_memory, _install_memories
  - id: "2.3"
    description: Integrate _install_memories into initialize_workspace
  - id: "2.4"
    description: Verify all tests pass, lint clean
risks:
  - description: Managed replacement could accidentally target user files
    mitigation: Strict namespace classifier; only mem.*.spec-driver.* touched
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-037.PHASE-02
```

# Phase 1 — Installer Semantics

## 1. Objective

Implement two-bucket memory install in `install.py`: seed (create-only) and spec-driver (replace/refresh with pruning).

## 2. Links & References

- **Delta**: DE-037
- **Phase 0**: phase-01.md (classification complete)
- **Files**: `supekku/scripts/install.py`, `supekku/scripts/lib/install_test.py`

## 3. Entrance Criteria

- [x] Phase 0 complete
- [x] pyproject.toml force-include configured

## 4. Exit Criteria / Done When

- [x] `_find_memory_source()` discovers memories in dev and installed contexts
- [x] `_classify_memory()` correctly classifies by namespace
- [x] Seed: create-if-missing, never overwrite
- [x] Spec-driver: replace/refresh from source
- [x] Pruning: remove managed IDs absent from source (with notice)
- [x] Unmanaged memories untouched
- [x] Tests pass, lint clean

## 5. Verification

- `uv run pytest supekku/scripts/lib/install_test.py -x -q`
- `uv run ruff check supekku/scripts/install.py`

## 6. Assumptions & STOP Conditions

- Memory destination: `target_root / "memory"`
- Seed auto-applies (create-only is non-destructive); managed prompts per category
- STOP: if memory source structure differs from expected

## 7. Tasks & Progress

| Status | ID  | Description                                   | Parallel? | Notes                                                                 |
| ------ | --- | --------------------------------------------- | --------- | --------------------------------------------------------------------- |
| [x]    | 2.1 | Write tests for memory install behavior (TDD) |           | 27 new tests                                                          |
| [x]    | 2.2 | Implement memory install functions            |           | \_classify_memory, \_find_memory_source, \_install_memories + helpers |
| [x]    | 2.3 | Integrate into initialize_workspace           |           | Added after agent docs, before skills                                 |
| [x]    | 2.4 | Verify all tests pass, lint clean             |           | 2205 pass, ruff clean, pylint clean on new code                       |

## 8. Risks & Mitigations

| Risk                                   | Mitigation                  | Status |
| -------------------------------------- | --------------------------- | ------ |
| Managed replacement targets user files | Strict namespace classifier | open   |

## 9. Decisions & Outcomes

- `2026-03-04` - Seed auto-applies (non-destructive); managed uses prompt_for_category pattern
- `2026-03-04` - Pruning emits notice per removed file

## 10. Findings / Research Notes

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
