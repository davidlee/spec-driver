---
id: IP-037.PHASE-03
slug: 037-install_and_refresh_seed_memories_during_workspace_install-phase-03
name: IP-037 Phase 03
created: '2026-03-04'
updated: '2026-03-04'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-037.PHASE-03
plan: IP-037
delta: DE-037
objective: >-
  Complete dry-run/reporting integration tests, verify all VT/VA artefacts,
  finalize notes and documentation.
entrance_criteria:
  - Phase 1 complete (installer semantics implemented)
exit_criteria:
  - VT-037-001 through VT-037-004 covered by passing tests
  - VA-037-001 classification report complete
  - Integration tests for initialize_workspace with memories
  - All tests pass, lint clean
verification:
  tests:
    - VT-037-004 dry-run category reporting
  evidence:
    - Integration test results
tasks:
  - id: '3.1'
    description: Add integration and dry-run reporting tests
  - id: '3.2'
    description: Verify all VT/VA artefacts satisfied
  - id: '3.3'
    description: Update notes and phase sheets
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-037.PHASE-03
```

# Phase 2+3 — UX, Safety & Verification

## 1. Objective
Integration-level tests for dry-run/reporting; verify all VT/VA artefacts; close out.

## 3. Entrance Criteria
- [x] Phase 1 complete

## 4. Exit Criteria / Done When
- [x] VT-037-001: seed create-only — covered by TestInstallMemoriesSeed (3 tests)
- [x] VT-037-002: managed refresh — covered by TestInstallMemoriesManaged (5 tests)
- [x] VT-037-003: unmanaged preservation — covered by TestInstallMemoriesUnmanaged (2 tests)
- [x] VT-037-004: dry-run reporting — covered by TestInstallMemoriesReporting (4 tests)
- [x] VA-037-001: classification report — in notes.md
- [x] Integration tests — covered by TestInitializeWorkspaceMemories (3 tests)
- [x] 2210 tests pass, ruff clean

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 3.1 | Add integration and dry-run reporting tests | | 5 new tests |
| [x] | 3.2 | Verify all VT/VA artefacts satisfied | | All covered |
| [x] | 3.3 | Update notes and phase sheets | | |

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated
