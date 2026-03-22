# Notes for DE-114

## New Agent Instructions

### Task Card

**DE-114** — God-file structural splits: list.py, common.py, requirements/registry.py, creation.py, workflow_metadata.py

### Status

Phase 01 (CLI layer) and Phase 02 (Lib: creation + workflow_metadata) are **complete**. Phase 03 is next.

### Required Reading

1. **Delta**: `.spec-driver/deltas/DE-114-god_file_structural_splits_list_py_common_py_requirements_registry_py_creation_py_workflow_metadata_py/DE-114.md`
2. **Design Revision**: `DR-114.md` — §4c (registry split) is the active section for P03.
3. **Implementation Plan**: `IP-114.md` — 3 phases, P01+P02 complete.
4. **Phase 01 sheet**: `phases/phase-01.md` — done (CLI layer).
5. **Phase 02 sheet**: `phases/phase-02.md` — done (creation + workflow_metadata).

### What's Done

**Phase 01 — CLI layer:**
- `cli/common.py` (1,124→316) + `artifacts.py` (651) + `ids.py` (104) + `io.py` (138). Re-exports in slim `common.py`.
- `cli/list.py` (3,195→package) with 10 files (48–527 lines each).

**Phase 02 — Lib layer:**
- `changes/creation.py` (1,056→276) + `_creation_utils.py` (41) + `revision_creation.py` (98) + `delta_creation.py` (170) + `audit_creation.py` (102) + `phase_creation.py` (497).
- `blocks/workflow_metadata.py` (1,485→251) + 7 schema files: `state_schema.py` (227), `handoff_schema.py` (301), `review_index_schema.py` (261), `review_findings_schema.py` (268), `sessions_schema.py` (111), `notes_bridge_schema.py` (69), `phase_bridge_schema.py` (72).
- All re-exports in slim files for backward compatibility.
- All 4,585 tests pass.

### What's Next (Phase 03)

Split `requirements/registry.py` (1,511 lines → 5 files). This is the hardest split — standalone function extraction with `records` dict passed by reference. Per DR-114 §4c:

**registry.py → 5 files:**
- `models.py`: `RequirementRecord`, `SyncStats` (~120)
- `parser.py`: `_records_from_content`, `_records_from_frontmatter`, etc. (~280)
- `sync.py`: all `_apply_*`, `_upsert_record`, iteration helpers (~500)
- `coverage.py`: `_apply_coverage_blocks`, `_check_coverage_drift`, etc. (~200)
- `registry.py` (slim): `RequirementsRegistry` core (~350)

**Import graph** (acyclic): registry→sync→parser→models, registry→coverage→models

**Test split**: `registry_test.py` (2,787 lines, 17 classes) splits to mirror source.

### Key Decisions

- **DEC-114-02**: Re-exports for zero-change migration. Follow-up backlog issue to remove them.
- **DEC-114-03**: Sync internals receive mutable `records` dict by reference — identical semantics.
- **DEC-114-05**: Single-consumer helpers move with their schema files.
- P02 deviation: Finding chain placed in `review_findings_schema.py` (sole consumer), not `review_index_schema.py` as DR table suggested.
- P02: `delta_creation.py` uses deferred import of `_render_plan` to avoid circular dependency.

### Relevant Governance

- POL-001: maximise code reuse, minimise sprawl
- STD-003: utility module placement rule
- DE-116 (upcoming): registry protocol enforcement — P03 registry split must not obstruct

### Key Files (P03 targets)

- `supekku/scripts/lib/requirements/registry.py` (1,511 lines — split target)
- `supekku/scripts/lib/requirements/registry_test.py` (2,787 lines — split target)

### Worktree State

Clean. All changes committed.

### Advice

- The full call graph for registry.py is in DR-114 §4c — use it.
- Extracted functions receive `records: dict[str, RequirementRecord]` by reference.
- `sync()` stays as a class method that delegates to imported standalone functions.
- The import graph is acyclic by design. Verify with a quick grep after splitting.
- Run `uv run spec-driver create phase "<name>" --plan IP-114` to create the P03 sheet.
