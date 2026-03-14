# Notes for DE-048

## Status: completed

## Implementation Summary

Single-phase delta. All code, tests, and verification complete.

### Changes Made

| File                                      | Change                                                                                                  |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `supekku/scripts/lib/core/config.py`      | Added `dirs` section to `DEFAULT_CONFIG` (16 keys)                                                      |
| `supekku/scripts/lib/core/paths.py`       | Added `_CONFIG_KEY_TO_CONSTANT` mapping, `_ORIGINAL_DEFAULTS` snapshot, `init_paths()`, `reset_paths()` |
| `supekku/scripts/lib/core/paths_test.py`  | 15 new tests: `TestInitPaths` (4), `TestResetPaths` (2), `TestCustomDirsHelpers` (9)                    |
| `supekku/scripts/lib/core/config_test.py` | 3 new tests + 1 assertion for `[dirs]` section                                                          |
| `supekku/cli/main.py`                     | `@app.callback()` with `_init_paths_from_config()` — loads config and calls `init_paths`                |
| `supekku/scripts/lib/test_base.py`        | `reset_paths()` added to `RepoTestCase.tearDown`                                                        |

### Design Decisions

- `init_paths(config)` mutates module-level constants via `globals()`. The `get_*_dir()` helpers resolve at call time, so they see overrides. Direct `from paths import SPECS_DIR` captures a snapshot — no production code does this (only tests).
- `_CONFIG_KEY_TO_CONSTANT` maps config keys to constant names; `_ORIGINAL_DEFAULTS` snapshots values at import time for `reset_paths()`.
- CLI callback uses `find_repo_root()` with `RuntimeError` catch — safe when not in a repo (e.g. `--help`, `install`).

### Invariants for Future Work

- If new directory constants are added to `paths.py`, they need entries in both `_CONFIG_KEY_TO_CONSTANT` and `DEFAULT_CONFIG["dirs"]`.
- No production code should `from paths import SPECS_DIR` directly — always use `get_*_dir()` helpers to benefit from config overrides.

## New Agent Instructions

### Next delta: DE-049

DE-049 (consolidate workspace directories under `.spec-driver/`) depends on DE-048 and is now unblocked.

**Required reading:**

- `change/deltas/DE-049-*/DE-049.md` — scope and motivation
- `change/deltas/DE-049-*/DR-049.md` — design revision
- `change/deltas/DE-049-*/IP-049.md` — implementation plan
- `backlog/improvements/IMPR-008-*/spike.md` — research context

**Key files (modified by DE-048, will be modified again by DE-049):**

- `supekku/scripts/lib/core/paths.py` — constants + `_CONFIG_KEY_TO_CONSTANT` + `_ORIGINAL_DEFAULTS`
- `supekku/scripts/lib/core/config.py` — `DEFAULT_CONFIG["dirs"]`
- `supekku/cli/main.py` — `@app.callback()` with `_init_paths_from_config()`
- `supekku/scripts/lib/test_base.py` — `reset_paths()` in tearDown

**Relevant memories:**

- `mem.signpost.spec-driver.file-map`
- `mem.pattern.spec-driver.core-loop`

**Advice:**

- DE-049 is significantly larger than DE-048 — directory moves, installer changes, symlinks, agent instruction updates. Plan phases carefully.
- The `globals()` pattern means changing default constant values in `paths.py` is the mechanism for changing the default layout. `DEFAULT_CONFIG["dirs"]` must stay in sync.
- ADR-004 acceptance may be a prerequisite — check before implementing.
