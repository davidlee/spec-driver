---
id: IP-049.PHASE-03
slug: "049-consolidate_workspace_directories_under_spec_driver_with_backward_compat_symlinks-phase-03"
name: IP-049 Phase 03 — Installer + callers
created: "2026-03-06"
updated: "2026-03-06"
status: active
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-049.PHASE-03
plan: IP-049
delta: DE-049
objective: >-
  Update initialize_workspace() to create flat .spec-driver/ layout with
  backward-compat symlinks. Refactor install.py imports to use helpers instead
  of removed constants. Fix base.py hardcoded path filter. Update ~20 test
  files that import removed SPECS_DIR/CHANGES_DIR.
entrance_criteria:
  - Phase 2 committed (path model flattened, f6b5d97)
exit_criteria:
  - install.py uses helper calls instead of direct constant imports
  - initialize_workspace() creates flat layout under .spec-driver/
  - initialize_workspace() creates backward-compat symlinks per DEC-049-03
  - sync/adapters/base.py path filter updated for .spec-driver/
  - All test files updated — no imports of removed SPECS_DIR/CHANGES_DIR
  - CLI boots successfully (uv run spec-driver --help)
  - just lint passes (both ruff and pylint)
  - just test passes
verification:
  tests:
    - VT-049-install
    - VT-049-symlinks
  evidence:
    - initialize_workspace() creates dirs under .spec-driver/
    - Backward-compat symlinks created and resolve correctly
    - Full test suite passes
tasks:
  - id: "3.1"
    description: Fix install.py imports — replace SPECS_DIR/CHANGES_DIR with SPEC_DRIVER_DIR + subdirs
  - id: "3.2"
    description: Restructure directory creation in initialize_workspace() for flat layout
  - id: "3.3"
    description: Add symlink creation step to initialize_workspace()
  - id: "3.4"
    description: Replace direct constant usage with helper calls where appropriate
  - id: "3.5"
    description: Update base.py hardcoded path filter
  - id: "3.6"
    description: Update test file imports (~20 files)
  - id: "3.7"
    description: Write install tests (VT-049-install, VT-049-symlinks)
  - id: "3.8"
    description: Lint and test
risks:
  - description: Large number of test files to update — tedious but mechanical
    mitigation: Changes are import-only (SPECS_DIR→SPEC_DRIVER_DIR, CHANGES_DIR→SPEC_DRIVER_DIR)
  - description: base.py path filter change could affect sync behavior
    mitigation: Verify with existing base_test.py
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-049.PHASE-03
```

# Phase 3 — Installer + callers

## 1. Objective

Fix the broken CLI by updating `install.py` to use the flattened path model.
Restructure `initialize_workspace()` to create the flat `.spec-driver/` layout
with backward-compat symlinks. Update `base.py` hardcoded path filter. Fix all
remaining test file imports of removed `SPECS_DIR`/`CHANGES_DIR`.

## 2. Links & References

- **Delta**: DE-049
- **DR-049**: §4 (code impact — install.py, base.py), §7 DEC-049-03 (symlinks)
- **Predecessor**: Phase 2 (flatten path model, commit f6b5d97)
- **Notes**: Phase 2 hand-off section in notes.md

## 3. Entrance Criteria

- [x] Phase 2 committed (f6b5d97)

## 4. Exit Criteria / Done When

- [x] `install.py` imports fixed — no `SPECS_DIR`/`CHANGES_DIR`
- [x] `initialize_workspace()` creates flat layout under `.spec-driver/`
- [x] `initialize_workspace()` creates backward-compat symlinks per DEC-049-03
- [x] `install.py` uses helpers where possible (DE-048 invariant)
- [x] `sync/adapters/base.py` path filter updated
- [x] All test files updated — no imports of `SPECS_DIR`/`CHANGES_DIR`
- [x] CLI boots (`uv run spec-driver --help`)
- [x] `just lint` clean
- [x] `just test` passes (2629 passed, 3 skipped)

## 5. Verification

- `uv run pytest supekku/scripts/install_test.py -v` (if exists)
- `uv run pytest supekku/scripts/lib/sync/adapters/base_test.py -v`
- `just lint && just test`

## 6. Assumptions & STOP Conditions

- **Assumption**: Test file changes are mechanical — replacing `SPECS_DIR` with `SPEC_DRIVER_DIR` and `CHANGES_DIR` with `SPEC_DRIVER_DIR` in fixture path composition
- **STOP**: If any test reveals that fixture paths depend on the old grouping semantics (not just constants), escalate

## 7. Tasks & Progress

| Status | ID  | Description                         | Parallel? | Notes                                                           |
| ------ | --- | ----------------------------------- | --------- | --------------------------------------------------------------- |
| [x]    | 3.1 | Fix install.py imports              | No        | Removed SPECS_DIR/CHANGES_DIR, added STANDARDS_SUBDIR + helpers |
| [x]    | 3.2 | Restructure directory creation      | No        | All content dirs under .spec-driver/                            |
| [x]    | 3.3 | Add symlink creation step           | No        | `_create_compat_symlinks()` — idempotent, targeted              |
| [x]    | 3.4 | Replace constant usage with helpers | No        | `get_memory_dir()`, `get_backlog_dir()`                         |
| [x]    | 3.5 | Update base.py path filter          | No        | `"/.spec-driver/"` replaces old strings                         |
| [x]    | 3.6 | Update test file imports            | Yes       | ~34 files (not ~20 — second sweep found 12 more)                |
| [x]    | 3.7 | Write install/symlink tests         | No        | 3 new tests: creation, idempotency, resolution                  |
| [x]    | 3.8 | Lint and test                       | No        | ruff clean, pylint 9.55, 2629 pass                              |

### Task Details

- **3.1 Fix install.py imports**
  Remove `SPECS_DIR` and `CHANGES_DIR` from the import block. These no longer
  exist in `paths.py`. Keep `SPEC_DRIVER_DIR` and all `*_SUBDIR` constants
  that are still used for directory creation.

- **3.2 Restructure directory creation**
  Change directory list from `f"{CHANGES_DIR}/{DELTAS_SUBDIR}"` etc. to
  `f"{SPEC_DRIVER_DIR}/{DELTAS_SUBDIR}"` etc. All content dirs become children
  of `.spec-driver/`.

- **3.3 Add symlink creation step**
  After directory creation, create backward-compat symlinks:
  - `specify/` — real dir with symlinks: tech, product, decisions, policies, standards
  - `change/` — real dir with symlinks: deltas, revisions, audits
  - `backlog/` → `.spec-driver/backlog/` (direct symlink)
  - `memory/` → `.spec-driver/memory/` (direct symlink)
    Idempotent: skip if symlink already exists and points to correct target.

- **3.4 Replace constant usage with helpers**
  - `target_root / MEMORY_DIR` → `get_memory_dir(target_root)` for memory install
  - `target_root / BACKLOG_DIR / "backlog.md"` → `get_backlog_dir(target_root) / "backlog.md"`

- **3.5 Update base.py path filter**
  Replace `"/specify/" in path_str or "/change/" in path_str` with
  `"/.spec-driver/" in path_str`. The old compat symlinks should also be
  skipped — they're symlinks and already caught by the symlink check above.

- **3.6 Update test file imports**
  ~20 test files import `SPECS_DIR` or `CHANGES_DIR` for fixture path composition.
  Replace with `SPEC_DRIVER_DIR`. The fixture paths change from e.g.
  `tmp / SPECS_DIR / TECH_SPECS_SUBDIR` to `tmp / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR`.

- **3.7 Write install/symlink tests**
  Test that `initialize_workspace()`:
  - Creates content dirs under `.spec-driver/`
  - Creates backward-compat symlinks that resolve correctly
  - Is idempotent (second run doesn't error)

## 8. Risks & Mitigations

| Risk                               | Mitigation                         | Status   |
| ---------------------------------- | ---------------------------------- | -------- |
| Many test files to update          | Mechanical changes, parallelizable | Open     |
| base.py filter change affects sync | Existing base_test.py covers it    | Open     |
| Symlink creation on Windows        | Not a target platform              | Accepted |

## 9. Decisions & Outcomes

- Test file scope was ~34 files, not ~20 as estimated. Initial grep only caught
  direct `core.paths` imports; a second sweep found files using the constants
  from other import paths or in body-only references.
- `STANDARDS_SUBDIR` was added to `install.py` imports — it was missing from
  the old directory creation list (pre-existing gap).

## 10. Findings / Research Notes

- `_create_compat_symlinks()` uses `readlink()` equality for idempotency.
  Skips real directories to avoid clobbering existing workspace content.
- `base.py` filter simplification: the symlink check above the path-string
  check already catches compat symlinks, so `"/.spec-driver/"` is sufficient
  for real content dirs.
- Several test files needed `parents=True` on `.mkdir()` calls because the
  `.spec-driver` parent dir doesn't exist in fresh tmp dirs.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (2629 pass, ruff clean, pylint 9.55)
- [x] Notes updated (notes.md — Phase 3 section)
- [x] Hand-off notes to Phase 4 (in notes.md)
