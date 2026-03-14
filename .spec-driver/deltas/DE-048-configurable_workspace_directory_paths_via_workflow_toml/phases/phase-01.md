---
id: IP-048.PHASE-01
slug: 048-config-dirs-wiring
name: Config [dirs] wiring and paths initialization
created: '2026-03-06'
updated: '2026-03-06'
status: done
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-048.PHASE-01
plan: IP-048
delta: DE-048
objective: >-
  Add [dirs] config section to workflow.toml, implement init_paths/reset_paths
  in paths.py, wire CLI startup, and update test base — with full test coverage.
entrance_criteria:
  - DR-048 reviewed
  - Existing tests green (just)
  - core/paths.py and core/config.py read and understood
exit_criteria:
  - init_paths(config) and reset_paths() implemented and tested
  - "[dirs] section in DEFAULT_CONFIG with all directory name defaults"
  - CLI entry point calls init_paths after config load
  - RepoTestCase.tearDown calls reset_paths
  - All VT gates satisfied
  - just green (zero lint warnings, all tests pass)
verification:
  tests:
    - core/paths_test.py
    - core/config_test.py
  evidence:
    - VT-048-config
    - VT-048-custom
    - VT-048-regression
tasks:
  - id: 1.1
    description: Add [dirs] section to DEFAULT_CONFIG in config.py
  - id: 1.2
    description: Implement init_paths(config) and reset_paths() in paths.py
  - id: 1.3
    description: Write paths_test.py (init, reset, custom dirs, fallback)
  - id: 1.4
    description: Update config_test.py for [dirs] parsing
  - id: 1.5
    description: Wire init_paths() into CLI entry point
  - id: 1.6
    description: Add reset_paths() to RepoTestCase.tearDown
  - id: 1.7
    description: Run just — verify full regression
risks:
  - description: Mutable module state complicates test parallelism
    mitigation: reset_paths() in tearDown; tests are already sequential
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-048.PHASE-01
```

# Phase 1 — Config [dirs] wiring and paths initialization

## 1. Objective

Wire `[dirs]` config section into `paths.py` helpers so workspace directory
names can be overridden via `workflow.toml`. Non-breaking — all defaults match
current layout.

## 2. Links & References

- **Delta**: [DE-048](../DE-048.md)
- **Design Revision**: [DR-048](../DR-048.md) — code impacts and design decisions
- **Spike**: [IMPR-008 spike](../../../../backlog/improvements/IMPR-008-configurable_workspace_directory_layout_with_migration_support/spike.md) — Q5 (config resolution), Q8 (test fixtures)

## 3. Entrance Criteria

- [x] DR-048 reviewed
- [x] Existing tests green (`just`)
- [x] `core/paths.py` and `core/config.py` read and understood

## 4. Exit Criteria / Done When

- [x] `init_paths(config)` and `reset_paths()` implemented
- [x] `[dirs]` section in `DEFAULT_CONFIG` with matching defaults
- [x] CLI entry point calls `init_paths()` after config load
- [x] `RepoTestCase.tearDown` calls `reset_paths()`
- [x] `paths_test.py` covers: init, reset, custom dirs, fallback, partial override
- [x] `config_test.py` covers: `[dirs]` parsing, partial overrides, missing section
- [x] `just` green

## 5. Tasks & Progress

| Status | ID  | Description                                                      | Notes                                                                                   |
| ------ | --- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| [x]    | 1.1 | Add `[dirs]` section to `DEFAULT_CONFIG` in `config.py`          | 16 keys added, defaults match paths.py constants                                        |
| [x]    | 1.2 | Implement `init_paths(config)` and `reset_paths()` in `paths.py` | `_CONFIG_KEY_TO_CONSTANT` mapping + `_ORIGINAL_DEFAULTS` snapshot; `globals()` override |
| [x]    | 1.3 | Write `paths_test.py`                                            | 15 new tests: TestInitPaths (4), TestResetPaths (2), TestCustomDirsHelpers (9)          |
| [x]    | 1.4 | Update `config_test.py` for `[dirs]` parsing                     | 3 new tests + 1 assertion added to structure test                                       |
| [x]    | 1.5 | Wire `init_paths()` into CLI entry point                         | `@app.callback()` in main.py; uses `find_repo_root()` with RuntimeError fallback        |
| [x]    | 1.6 | Add `reset_paths()` to `RepoTestCase.tearDown`                   | No conftest.py exists; tearDown is sufficient                                           |
| [x]    | 1.7 | Run `just` — full regression                                     | 2651 passed, 3 skipped, pylint 9.56/10 (unchanged)                                      |

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - `_merge_defaults()` in config.py handles `[dirs]` automatically (it
    already merges nested dicts one level deep)
  - CLI has a single entry point where config is loaded before commands run
  - No tests currently call `init_paths()`, so adding `reset_paths()` in
    tearDown is purely defensive

- **STOP when**:
  - CLI entry point architecture is unclear — escalate before guessing
  - Existing tests break in unexpected ways — investigate before proceeding
