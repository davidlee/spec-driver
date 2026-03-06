---
id: IP-049.PHASE-02
slug: 049-consolidate_workspace_directories_under_spec_driver_with_backward_compat_symlinks-phase-02
name: IP-049 Phase 02 — Flatten path model and update config defaults
created: '2026-03-06'
updated: '2026-03-06'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-049.PHASE-02
plan: IP-049
delta: DE-049
objective: >-
  Flatten path constants/helpers to resolve under .spec-driver/ instead of
  grouping dirs. Update config defaults. Add warning for unknown [dirs] keys.
  Rewrite tests to match new invariants. No caller changes (phase 3).
entrance_criteria:
  - Phase 1 committed (structural migration complete)
exit_criteria:
  - SPECS_DIR and CHANGES_DIR constants eliminated
  - get_specs_dir() and get_changes_dir() removed
  - All leaf helpers resolve under get_spec_driver_root()
  - get_backlog_dir() and get_memory_dir() resolve under .spec-driver/
  - DEFAULT_CONFIG["dirs"] updated (specs/changes keys removed)
  - _CONFIG_KEY_TO_CONSTANT updated to match
  - init_paths() warns on unrecognized keys
  - paths_test.py rewritten for new invariants
  - config_test.py updated for new defaults
  - just lint passes
  - just test passes (may fail on callers — that's phase 3)
verification:
  tests:
    - VT-049-paths
  evidence:
    - Unit tests pass for flattened helper resolution
tasks:
  - id: "2.1"
    description: Flatten path constants — eliminate SPECS_DIR, CHANGES_DIR
  - id: "2.2"
    description: Rewrite helpers to resolve under get_spec_driver_root()
  - id: "2.3"
    description: Update _CONFIG_KEY_TO_CONSTANT and DEFAULT_CONFIG
  - id: "2.4"
    description: Add init_paths() warning for unknown keys
  - id: "2.5"
    description: Rewrite paths_test.py for new invariants
  - id: "2.6"
    description: Update config_test.py for new defaults
  - id: "2.7"
    description: Lint and test
risks:
  - description: Removing get_specs_dir/get_changes_dir breaks callers
    mitigation: Phase 3 handles callers; expect import errors until then
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-049.PHASE-02
```

# Phase 2 — Flatten path model and update config defaults

## 1. Objective

Eliminate the intermediate grouping layer (`SPECS_DIR`/`CHANGES_DIR` and their
helpers) from the path model. All leaf helpers resolve directly under
`get_spec_driver_root()`. Update config defaults and add a warning for
unrecognized `[dirs]` keys.

This phase changes only `paths.py`, `config.py`, and their tests. Callers that
import removed symbols will break — that's Phase 3.

## 2. Links & References
- **Delta**: DE-049
- **DR-049**: §4 (path model before/after), §7 DEC-049-01 (flatten), DEC-049-02 (leaf resolution), DEC-049-06 (config keys)
- **Predecessor**: Phase 1 (structural migration, commits 843f9b1..981abac)

## 3. Entrance Criteria
- [x] Phase 1 committed (structural migration complete)

## 4. Exit Criteria / Done When
- [ ] `SPECS_DIR` and `CHANGES_DIR` constants removed from `paths.py`
- [ ] `get_specs_dir()` and `get_changes_dir()` removed from `paths.py`
- [ ] All leaf helpers resolve as `get_spec_driver_root() / SUBDIR`
- [ ] `get_backlog_dir()` / `get_memory_dir()` resolve under `.spec-driver/`
- [ ] `DEFAULT_CONFIG["dirs"]` updated — `specs`/`changes` keys removed
- [ ] `_CONFIG_KEY_TO_CONSTANT` updated — `specs`/`changes` entries removed
- [ ] `init_paths()` emits `warnings.warn()` for unrecognized keys
- [ ] `paths_test.py` rewritten for new invariants
- [ ] `config_test.py` updated if needed
- [ ] `just lint` clean
- [ ] `just test` — paths/config tests pass (caller failures expected → P3)

## 5. Verification
- `uv run pytest supekku/scripts/lib/core/paths_test.py -v`
- `uv run pytest supekku/scripts/lib/core/config_test.py -v` (if changed)
- `just lint`

## 6. Assumptions & STOP Conditions
- **Assumption**: Callers that import `SPECS_DIR`, `CHANGES_DIR`, `get_specs_dir`, `get_changes_dir` will break — fixed in Phase 3
- **STOP**: If more than ~5 callers import the removed symbols, consider whether to deprecate-then-remove instead

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 2.1 | Flatten path constants | No | Remove SPECS_DIR, CHANGES_DIR |
| [ ] | 2.2 | Rewrite helpers | No | Leaf helpers → get_spec_driver_root(); remove get_specs_dir/get_changes_dir |
| [ ] | 2.3 | Update config mapping + defaults | No | _CONFIG_KEY_TO_CONSTANT, DEFAULT_CONFIG |
| [ ] | 2.4 | Add unknown-key warning to init_paths | No | warnings.warn() |
| [ ] | 2.5 | Rewrite paths_test.py | No | New structural invariants |
| [ ] | 2.6 | Update config_test.py | No | If defaults changed |
| [ ] | 2.7 | Lint and test | No | just lint; targeted pytest |

### Task Details

- **2.1 Flatten path constants**
  - Remove `SPECS_DIR` and `CHANGES_DIR` constants
  - Remove from `__all__`
  - `BACKLOG_DIR` and `MEMORY_DIR` keep their string values but change resolution anchor

- **2.2 Rewrite helpers**
  - Remove `get_specs_dir()` and `get_changes_dir()`
  - `get_tech_specs_dir()` → `get_spec_driver_root(repo_root) / TECH_SPECS_SUBDIR`
  - Same pattern for `get_product_specs_dir`, `get_decisions_dir`, `get_policies_dir`, `get_standards_dir`
  - `get_deltas_dir()` → `get_spec_driver_root(repo_root) / DELTAS_SUBDIR`
  - Same for `get_revisions_dir`, `get_audits_dir`
  - `get_backlog_dir()` → `get_spec_driver_root(repo_root) / BACKLOG_DIR`
  - `get_memory_dir()` → `get_spec_driver_root(repo_root) / MEMORY_DIR`

- **2.3 Update config mapping + defaults**
  - Remove `"specs": "SPECS_DIR"` and `"changes": "CHANGES_DIR"` from `_CONFIG_KEY_TO_CONSTANT`
  - Remove `"specs"` and `"changes"` from `DEFAULT_CONFIG["dirs"]`
  - Snapshot `_ORIGINAL_DEFAULTS` will auto-update (computed at import time)

- **2.4 Add unknown-key warning to init_paths()**
  - For any key in `config["dirs"]` not in `_CONFIG_KEY_TO_CONSTANT`, emit:
    `warnings.warn(f"Unknown [dirs] key '{key}' in config — ignored", UserWarning, stacklevel=2)`

- **2.5 Rewrite paths_test.py**
  - Remove `TestWorkspaceRootConstants` tests for SPECS_DIR/CHANGES_DIR
  - Remove `TestSpecsHelpers.test_get_specs_dir` and `TestChangesHelpers.test_get_changes_dir`
  - Rewrite all leaf helper assertions: `repo_root / ".spec-driver" / subdir`
  - Rewrite `TestHelperComposition`: all leaf helpers are children of `get_spec_driver_root()`
  - Update `TestInitPaths`: remove specs/changes overrides, test warning on unknown keys
  - Update `TestCustomDirsHelpers`: remove specs/changes-based assertions

- **2.6 Update config_test.py** — if `DEFAULT_CONFIG["dirs"]` changes affect existing tests

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Callers break on removed symbols | Expected — Phase 3 scope | Accepted |
| _ORIGINAL_DEFAULTS stale after constant removal | Computed at import time from new constants | Clear |

## 9. Decisions & Outcomes
*(Updated during execution)*

## 10. Findings / Research Notes
*(Updated during execution)*

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Hand-off notes to Phase 3
