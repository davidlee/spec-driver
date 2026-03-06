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
