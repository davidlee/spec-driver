---
id: IP-044.PHASE-03
slug: 044-centralize_hardcoded_workspace_directory_paths-phase-03
name: 'P03: Test fixtures & verification'
created: '2026-03-05'
updated: '2026-03-05'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-044.PHASE-03
plan: IP-044
delta: DE-044
objective: >-
  Replace all hardcoded workspace directory strings in test fixtures with
  constants/helpers from core/paths.py. Run VA-044-grep final verification.
entrance_criteria:
  - P02 complete — production code uses constants
exit_criteria:
  - All test files use constants/helpers for workspace path construction
  - VA-044-grep passes (zero magic path-construction hits outside paths_test.py)
  - just test passes (full suite green)
  - just lint + just pylint clean
verification:
  tests:
    - VT-044-regression
    - VA-044-grep
  evidence:
    - 2625 passed, 3 skipped, 0 failures
    - ruff clean, pylint 9.56/10 (unchanged)
    - VA-044-grep clean — all remaining hits are legitimate exceptions
tasks:
  - id: '3.1'
    summary: Update spec-related test files (specs, decisions, policies, standards)
  - id: '3.2'
    summary: Update change-related test files (changes, creation, completion, coverage)
  - id: '3.3'
    summary: Update backlog and memory test files
  - id: '3.4'
    summary: Update CLI test files
  - id: '3.5'
    summary: Update remaining test files (workspace, validator, cross-refs, etc.)
  - id: '3.6'
    summary: VA-044-grep verification and final just check
risks:
  - description: Large file count causes merge conflicts with concurrent work
    mitigation: Commit in logical batches
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-044.PHASE-03
```

# Phase 3 - Test fixtures & verification

## 1. Objective

Replace all hardcoded workspace directory path strings in test fixtures with
constants/helpers from `core/paths.py`. Then run VA-044-grep to verify zero
magic path strings remain across the entire codebase.

## 2. Links & References
- **Delta**: [DE-044](../DE-044.md)
- **Design Revision**: [DR-044 §4.6](../DR-044.md)
- **Phase 2**: [phase-02.md](./phase-02.md) — production code complete

## 3. Entrance Criteria
- [x] P02 complete — production code uses constants (2606 tests green)

## 4. Exit Criteria / Done When
- [x] All test files use constants/helpers for workspace paths
- [x] VA-044-grep: zero path-construction hits outside `paths_test.py` + documented exceptions
- [x] `just` passes (2625 passed, ruff clean, pylint 9.56/10)

## 5. Verification
- `just test`: 2625 passed, 3 skipped, 0 failures
- `just lint`: ruff clean
- `just pylint`: 9.56/10 (unchanged from P02)
- VA-044-grep: all 4 patterns verified clean

## 6. Assumptions & STOP Conditions
- Assumptions: mechanical swap — import constant, replace string literal (confirmed)
- No STOP conditions triggered

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 3.1 | Spec-related tests | [P] | 8 files, ~39 replacements |
| [x] | 3.2 | Change-related tests | [P] | 9 files checked, 51 replacements in 7 |
| [x] | 3.3 | Backlog & memory tests | [P] | 8 files checked, 23 replacements in 4 |
| [x] | 3.4 | CLI tests | [P] | 11 files, 55 replacements |
| [x] | 3.5 | Remaining tests | [P] | 10 files checked, 39 replacements in 9 |
| [x] | 3.6 | VA-044-grep + final check | — | Clean — all remaining hits documented |

### Legitimate grep exceptions (not path construction)
- `paths_test.py` — tests the constants themselves (expected)
- `standards/registry_test.py:54` — `.registry` subdir, not a workspace path constant
- `cards/registry_test.py` — `kanban / "backlog"` is a kanban lane name
- `install.py:80,83` — `package_root / "memory"` is Python package dir (documented in P02)
- `install_test.py` — `tmp_path / "src" / "memory"` is test fixture for package source

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Large diff obscures review | Commit in logical batches | resolved |
| False positive grep hits | Manual review of each remaining hit | resolved |

## 9. Decisions & Outcomes
- `cards/registry_test.py` `/ "backlog"` hits intentionally left — these are kanban lane names, not the workspace `backlog/` directory
- `install_test.py` `tmp_path / "src" / "memory"` hits intentionally left — test-internal package source fixtures, not workspace paths

## 10. Findings / Research Notes
- ~207 replacements across ~39 test files
- All 5 batches executed in parallel via sub-agents
- `test_cli.py` was missed by initial batch assignment (integration test, not `*_test.py` pattern) — caught and fixed during VA-044-grep verification

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [ ] IP-044 progress tracking updated
- [ ] Delta closure checklist reviewed
