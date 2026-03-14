---
id: IP-044.PHASE-01
slug: 044-centralize_hardcoded_workspace_directory_paths-phase-01
name: "P01: Constants and helpers"
created: "2026-03-05"
updated: "2026-03-05"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-044.PHASE-01
plan: IP-044
delta: DE-044
objective: >-
  Add workspace directory constants and get_* helper functions to core/paths.py
  with comprehensive unit tests.
entrance_criteria:
  - DR-044 reviewed
  - Existing paths.py read and understood
exit_criteria:
  - All constants and helpers defined and exported
  - Unit tests cover every constant and helper
  - just lint + just pylint clean
  - Existing test suite still passes
verification:
  tests:
    - VT-044-paths
  evidence: []
tasks:
  - id: "1.1"
    summary: Add workspace root constants
  - id: "1.2"
    summary: Add subdirectory constants
  - id: "1.3"
    summary: Add get_* helper functions
  - id: "1.4"
    summary: Update __all__ exports
  - id: "1.5"
    summary: Write unit tests
  - id: "1.6"
    summary: Lint and verify
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-044.PHASE-01
```

# Phase 1 - Constants and helpers

## 1. Objective

Add all workspace directory constants and `get_*()` helper functions to
`supekku/scripts/lib/core/paths.py`, following the existing `SPEC_DRIVER_DIR` /
`get_spec_driver_root()` pattern. Write unit tests. No other files change in
this phase.

## 2. Links & References

- **Delta**: [DE-044](../DE-044.md)
- **Design Revision**: [DR-044 §4.1](../DR-044.md) — constant and helper definitions
- **Existing code**: `supekku/scripts/lib/core/paths.py`

## 3. Entrance Criteria

- [x] DR-044 reviewed
- [x] Existing `paths.py` read and understood

## 4. Exit Criteria / Done When

- [x] Constants defined: `SPECS_DIR`, `CHANGES_DIR`, `BACKLOG_DIR`, `MEMORY_DIR`
- [x] Subdirectory constants defined (see DR-044 §4.1)
- [x] Helper functions defined: `get_specs_dir`, `get_tech_specs_dir`, `get_product_specs_dir`, `get_decisions_dir`, `get_policies_dir`, `get_standards_dir`, `get_changes_dir`, `get_deltas_dir`, `get_revisions_dir`, `get_audits_dir`, `get_backlog_dir`, `get_memory_dir`
- [x] All exported in `__all__`
- [x] Unit tests pass (31 tests)
- [x] `just lint` + `just pylint` clean (pylint 10.00/10)

## 5. Verification

- `uv run pytest supekku/scripts/lib/core/paths_test.py -v`
- `just lint`
- `just pylint supekku/scripts/lib/core/paths.py`
- `just test` (full regression)

## 6. Assumptions & STOP Conditions

- Assumptions: The existing `get_*` helper pattern (auto-discover root when `None`) is the right approach
- STOP when: import cycle detected (unlikely — `paths.py` only imports `repo.py`)

## 7. Tasks & Progress

| Status | ID  | Description                                                                            | Parallel?    | Notes                                 |
| ------ | --- | -------------------------------------------------------------------------------------- | ------------ | ------------------------------------- |
| [x]    | 1.1 | Add workspace root constants (`SPECS_DIR`, `CHANGES_DIR`, `BACKLOG_DIR`, `MEMORY_DIR`) | —            | Done                                  |
| [x]    | 1.2 | Add subdirectory constants (`TECH_SPECS_SUBDIR`, `DELTAS_SUBDIR`, etc.)                | [P] with 1.1 | 12 constants                          |
| [x]    | 1.3 | Add `get_*` helper functions (12 functions per DR-044 §4.1)                            | —            | 12 helpers, all composing via parent  |
| [x]    | 1.4 | Update `__all__` exports                                                               | —            | 16 constants + 12 helpers added       |
| [x]    | 1.5 | Write unit tests for all constants and helpers                                         | —            | 31 tests in paths_test.py             |
| [x]    | 1.6 | Lint and full test suite verification                                                  | —            | 2571 passed, ruff clean, pylint 10/10 |

### Task Details

- **1.1–1.2 Constants**
  - 4 root constants + 12 subdirectory constants
  - Plain string values matching current directory names
  - Group with comments per DR-044 §4.1

- **1.3 Helper functions**
  - 12 functions, all following `get_spec_driver_root()` signature
  - Each composes root constant + subdir constant
  - Compose via existing helpers where natural (e.g. `get_tech_specs_dir` calls `get_specs_dir`)

- **1.5 Unit tests**
  - Test each constant has expected value
  - Test each helper returns correct path with explicit root
  - Test each helper with `root=None` (auto-discovery, may need mock)
