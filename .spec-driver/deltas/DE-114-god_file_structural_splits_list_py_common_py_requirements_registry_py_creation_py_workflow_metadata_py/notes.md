# Notes for DE-114

## New Agent Instructions

### Task Card

**DE-114** — God-file structural splits: list.py, common.py, requirements/registry.py, creation.py, workflow_metadata.py

### Status

Phase 01 (CLI layer) is **complete**. Phase 02 is next.

### Required Reading

1. **Delta**: `.spec-driver/deltas/DE-114-god_file_structural_splits_list_py_common_py_requirements_registry_py_creation_py_workflow_metadata_py/DE-114.md`
2. **Design Revision**: `DR-114.md` (same directory) — 3 adversarial passes, zero blockers. §4d (creation split) and §4e (workflow_metadata split) are the active sections.
3. **Implementation Plan**: `IP-114.md` (same directory) — 3 phases, P01 complete.
4. **Phase 01 sheet**: `phases/phase-01.md` — done, for reference only.

### What's Done (Phase 01)

- `cli/common.py` (1,124 lines) → `common.py` (316) + `artifacts.py` (651) + `ids.py` (104) + `io.py` (138). Re-exports in slim `common.py` for backward compat.
- `cli/list.py` (3,195 lines) → `cli/list/` package with 10 files (48–527 lines each). Singular aliases restored in `__init__.py`.
- `package_utils_test.py` updated (`cli` is now parent, `cli/list` is leaf).
- All 4,585 tests pass.

### What's Next (Phase 02)

Split `changes/creation.py` and `blocks/workflow_metadata.py`. Per DR-114:

**creation.py (1,056 lines → 6 files)**:

- `_creation_utils.py`: shared helpers (~40 lines)
- `revision_creation.py`: `create_revision` (~75)
- `delta_creation.py`: `create_delta` (~140)
- `audit_creation.py`: `create_audit` (~80)
- `phase_creation.py`: all phase logic (~320)
- `creation.py` (slim): `create_plan`, `_render_plan`, `create_requirement_breakout` + re-exports (~400)
- 4 importers: `cli/create.py`, `creation_test.py`, 2 deferred in `core/events_test.py`
- Test: extract phase tests to `phase_creation_test.py`

**workflow_metadata.py (1,485 lines → 8 files)**:

- Move single-consumer helpers to their schema files (see DR-114 §4e table)
- Only `_timestamps_block` stays in slim shared file (used by STATE + HANDOFF)
- 4 importers in `workflow/` modules
- Re-exports from slim `workflow_metadata.py`

### Key Decisions

- **DEC-114-02**: Re-exports for zero-change migration. Follow-up backlog issue to remove them.
- **DEC-114-05**: Single-consumer helpers move with their schema files, not into shared.
- Phase ordering: P02 targets are independent of each other. Do either first.

### Relevant Governance

- POL-001: maximise code reuse, minimise sprawl
- STD-003: utility module placement rule
- DE-116 (upcoming): registry protocol enforcement — P03 registry split must not obstruct

### Key Files

- `supekku/scripts/lib/changes/creation.py` (1,056 lines — split target)
- `supekku/scripts/lib/changes/creation_test.py` (823 lines — partial split)
- `supekku/scripts/lib/blocks/workflow_metadata.py` (1,485 lines — split target)
- `supekku/cli/create.py` (importer of creation.py)
- `supekku/scripts/lib/workflow/{review_io,handoff_io,state_io,bridge}.py` (importers of workflow_metadata)

### Worktree State

Clean. All `.spec-driver` and code changes committed. Phase 01 sheet is complete but phase not yet formally closed via CLI (do that at start of next session or when creating P02 sheet).

### Advice

- The creation.py split is straightforward — each `create_*` function is self-contained with shared utils.
- The workflow_metadata split requires care with helper placement (see DR-114 §4e verified usage table).
- After P02, P03 (requirements/registry.py) is the hard one — standalone function extraction with full call graph in DR-114 §4c.
- Run `uv run spec-driver create phase "<name>" --plan IP-114` to create the P02 sheet.
