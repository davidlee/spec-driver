# Notes for DE-049

## How to build context on the design

### Required reading (in order)

1. **IMPR-008 spike** — the research foundation. Covers surface analysis (path
   references, registry entries, symlink feasibility, config resolution, test
   fixture impact) and estimates.
   `backlog/improvements/IMPR-008-configurable_workspace_directory_layout_with_migration_support/spike.md`

2. **DE-048 notes** — predecessor delta. Established `init_paths(config)` /
   `reset_paths()`, `[dirs]` config section, `_CONFIG_KEY_TO_CONSTANT` mapping.
   Key invariants for DE-049 documented here.
   `change/deltas/DE-048-configurable_workspace_directory_paths_via_workflow_toml/notes.md`

3. **DE-049 delta** — scope, motivation, objectives, risks.
   `change/deltas/DE-049-consolidate_workspace_directories_under_spec_driver_with_backward_compat_symlinks/DE-049.md`

4. **DR-049** — the design under review. Six design decisions, code impact
   table, verification alignment, config override semantics.
   `change/deltas/DE-049-consolidate_workspace_directories_under_spec_driver_with_backward_compat_symlinks/DR-049.md`

### Key source files

| File | Why |
|---|---|
| `supekku/scripts/lib/core/paths.py` | Path constants, helpers, `init_paths()`/`reset_paths()`, `_CONFIG_KEY_TO_CONSTANT` |
| `supekku/scripts/lib/core/config.py` | `DEFAULT_CONFIG["dirs"]`, `load_workflow_config()`, merge logic |
| `supekku/scripts/install.py` | `initialize_workspace()` — directory creation, memory install, agent docs. **Imports constants directly (violates DE-048 invariant)** |
| `supekku/scripts/lib/changes/registry.py` | Only real production caller of `get_changes_dir()` (line 45) |
| `supekku/scripts/lib/deletion/executor.py` | Dead assignment of `get_changes_dir()` (line 299) |
| `supekku/scripts/lib/sync/adapters/base.py` | Hardcoded `"/specify/"` and `"/change/"` string check (line 92) — only production hardcoded path |
| `supekku/scripts/lib/core/paths_test.py` | Structural invariant tests that must be rewritten |

### Relevant memories

- `mem.pattern.installer.boot-architecture` — installer + agent boot reference architecture
- `mem.signpost.spec-driver.file-map` — current workspace file map (will need updating post-implementation)

### Key design decisions to evaluate

- **DEC-049-01**: Flatten path model — eliminate `SPECS_DIR`/`CHANGES_DIR` intermediate grouping
- **DEC-049-02**: Leaf helpers resolve directly against `get_spec_driver_root()`
- **DEC-049-03**: Targeted symlinks inside real compat dirs (not broad dir-to-dir)
- **DEC-049-04**: `config/` grouping deferred to follow-up
- **DEC-049-05**: Migration via `git mv` then symlink; this repo first
- **DEC-049-06**: Config override model — grouping keys removed, subdir keys reparented

### Known resolved issues from adversarial review

**Round 1:**
1. Symlink leakiness — resolved by targeted symlinks (DEC-049-03)
2. This repo's migration unaddressed — resolved by git mv approach (DEC-049-05)
3. Config override semantics change silently — documented in DEC-049-06
4. Parent-child test assertions wrong by design — noted in DEC-049-01 consequences
5. `deletion/executor.py` caller is dead code — corrected in code impact table

**Round 2:**
6. `install.py` imports constants directly (violates DE-048 invariant) — added to code impact table
7. `sync/adapters/base.py:92` hardcodes `"/specify/"` and `"/change/"` — added to code impact table
8. `contracts/` shown in "After" diagram but not in scope — removed from diagram (stays at repo root)
9. ~400 derived symlinks should be deleted before `git mv` — added as step 0 in migration sequence
10. `get_backlog_dir()`/`get_memory_dir()` resolution anchor change not in code impact table — added with callers
11. `init_paths()` should warn on unrecognized `[dirs]` keys — added to DEC-049-06 and code impact table
12. Decision status symlinks not mentioned — included in step 0 cleanup
13. DEC-049-04/06 tension noted — flagged as known follow-up interaction

---

## Phase 1 — Structural migration (complete)

### What's done

Three commits, clean sequence:
1. `843f9b1` — Deleted 388 derived symlinks (spec index dirs, alias symlinks, contract mirror symlinks, decision status symlinks, registry_v2.json)
2. `4d5649a` — `git mv` of 526 files: all content from `specify/`, `change/`, `backlog/`, `memory/` into `.spec-driver/`
3. `981abac` — Created 10 backward-compat symlinks per DEC-049-03

### Observations

- No conflicts with existing `.spec-driver/` subdirs (as predicted in preflight)
- All `git mv` renames detected at 100% similarity — clean history preservation
- `by-language/` survived derived symlink deletion (real dir, not a symlink) — moved naturally during 1.2
- Symlink structure matches DR-049 §4 exactly

### Verification

Manual spot-checks pass:
- `specify/tech/SPEC-110/SPEC-110.md` resolves
- `change/deltas/DE-049-*/DE-049.md` resolves
- `backlog/improvements/IMPR-008-*/spike.md` resolves
- `memory/` lists memory files
- `git status` clean

**No code tests run** — Phase 1 is pure structural, no code changes. Expect test failures starting Phase 2 when path defaults change.

### Migration script

`supekku/scripts/migrate_to_consolidated_layout.sh` (`3280914`) — captures the
Phase 1 steps as a reusable shell script with `--dry-run`, idempotency, and
verification. Placement TBD — move to a proper home when migration/deployment
strategy is formalized.

## Phase 2 — Flatten path model and config (complete)

### What's done

One commit: `f6b5d97`
- `paths.py`: removed `SPECS_DIR`, `CHANGES_DIR`, `get_specs_dir()`, `get_changes_dir()`.
  All leaf helpers now resolve under `get_spec_driver_root()`. `init_paths()` warns
  on unrecognized `[dirs]` keys.
- `config.py`: removed `specs`/`changes` from `DEFAULT_CONFIG["dirs"]`
- `changes/registry.py`: refactored to leaf helper dispatch (`_KIND_TO_DIR_HELPER`)
- `deletion/executor.py`: removed dead `get_changes_dir` import and assignment
- `paths_test.py`: fully rewritten (40 tests)
- `config_test.py`: 2 tests updated

### Adaptation

Pulled `changes/registry.py` and `deletion/executor.py` fixes from Phase 3 scope —
import chain via `__init__.py` blocked test collection without them.

### Verification

69 tests pass. Both linters clean. Net -96 lines.

### Hand-off to Phase 3

~20 test files still import `SPECS_DIR`, `CHANGES_DIR` for fixture path composition.
These need updating to use `SPEC_DRIVER_DIR` instead. The `sync/adapters/base.py`
hardcoded path filter also needs updating. `install.py` needs restructuring.

## Phase 3 — Installer + callers (complete)

### What's done

Uncommitted. All changes in working tree.

**Production code:**
- `install.py`: removed `SPECS_DIR`/`CHANGES_DIR` imports, replaced with
  `SPEC_DRIVER_DIR` + subdirs. Directory creation restructured for flat
  `.spec-driver/` layout. Added `_create_compat_symlinks()` — creates targeted
  symlinks per DEC-049-03 (idempotent, won't clobber real dirs). Replaced
  `target_root / MEMORY_DIR` and `target_root / BACKLOG_DIR` with helper calls
  (`get_memory_dir()`, `get_backlog_dir()`).
- `sync/adapters/base.py:92`: path filter updated from
  `"/specify/" or "/change/"` to `"/.spec-driver/"`.

**Test files updated (~34 files total):**
- 22 test files: replaced `SPECS_DIR`/`CHANGES_DIR` imports with `SPEC_DRIVER_DIR`
  in import lines and all fixture path constructions.
- 12 additional test files discovered via second grep sweep (not in original
  `paths` import — used constants from other import paths or had body-only refs).
- `cli/memory_test.py`: added `parents=True` to `.mkdir()` calls (`.spec-driver`
  parent must exist before `memory/` subdir).
- `scripts/lib/memory/registry_test.py`: same `.mkdir(parents=True)` fix, updated
  assertion string from `"memory/"` to `".spec-driver/memory/"`.
- `scripts/lib/deletion/executor_test.py`: removed stale `change_dir` assertion
  (attribute removed in Phase 2).
- `scripts/lib/install_test.py`: updated expected directory list for flat layout,
  added 3 new tests (VT-049-symlinks: creation, idempotency, resolution).
- Formatter and requirements test assertions updated for `.spec-driver/` paths.
- Several line-length fixes from longer `SPEC_DRIVER_DIR` constant name.

### Scope vs plan

The phase sheet estimated ~20 test files. Actual count was ~34 — the initial
grep only caught files importing directly from `core.paths`. A second sweep
found 12 more files importing the constants via other paths or using them only
in function bodies.

### Observations

- `_create_compat_symlinks()` is ~40 lines, clean. Uses `readlink()` for
  idempotency checks. Won't clobber real directories (skips if `link.exists()`
  and not a symlink).
- The `STANDARDS_SUBDIR` was missing from the old `install.py` import — added
  as part of the flat layout restructuring.
- `base.py` filter change is minimal: the symlink check above it already
  catches compat symlinks, so `"/.spec-driver/"` catches the real content dirs.

### Verification

- `uv run ruff check` — clean
- `uv run pytest` — 2629 passed, 3 skipped (net +3 tests from new symlink tests)
- `just pylint` — 9.55/10 (±0.00 from previous)
- `just` — all green
- CLI boots: `uv run spec-driver --help` works

### Hand-off to Phase 4

Phase 4 (regression + cleanup):
- Full regression already passes (`just` green)
- Agent instruction files may reference old paths — check and update
- Memory files (`mem.signpost.spec-driver.file-map` etc.) need updating
- Consider whether `STANDARDS_SUBDIR` was previously missing from installer
  (pre-existing gap or introduced by this delta?)
