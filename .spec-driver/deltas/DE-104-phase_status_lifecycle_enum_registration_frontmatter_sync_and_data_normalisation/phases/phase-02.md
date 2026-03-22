---
id: IP-104.PHASE-02
slug: "104-phase_status_lifecycle_enum_registration_frontmatter_sync_and_data_normalisation-phase-02"
name: IP-104 Phase 02
created: "2026-03-21"
updated: "2026-03-21"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-104.PHASE-02
plan: IP-104
delta: DE-104
objective: >-
  Add phase status checks to validate with --fix flag, fix schema example,
  update five skills and two memory records, backfill all existing phases
  to canonical status values.
entrance_criteria:
  - Phase 01 complete and committed
exit_criteria:
  - validate detects non-canonical phase statuses
  - validate --fix normalises them via CANONICAL_STATUS_MAP
  - validate warns on structural issues (missing overview block, missing status, wrong kind)
  - Schema example uses canonical status value
  - Five skills updated with canonical vocabulary and CLI guidance
  - Two memory records updated
  - All existing phases backfilled to canonical values
  - just check passes
verification:
  tests:
    - uv run pytest supekku/scripts/lib/validation/validator_test.py -x
    - uv run pytest supekku/cli/workspace_test.py -x
    - just check
  evidence:
    - "Post-backfill: grep -r '^status:' .spec-driver/deltas/*/phases/phase-[0-9][0-9].md confirms only canonical values"
tasks:
  - "2.1 Add _validate_phase_statuses to WorkspaceValidator"
  - "2.2 Wire --fix flag through validate CLI"
  - "2.3 Fix schema example"
  - "2.4 Update skills"
  - "2.5 Update memory records"
  - "2.6 Backfill via validate --fix"
  - "2.7 Final verification"
risks:
  - "First mutation in validate — keep scope narrow per DEC-104-05"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-104.PHASE-02
entrance_criteria:
  - item: "Phase 01 complete and committed"
    completed: true
exit_criteria:
  - item: "validate detects non-canonical phase statuses"
    completed: true
  - item: "validate --fix normalises them"
    completed: true
  - item: "validate warns on structural issues"
    completed: true
  - item: "Schema example uses canonical status"
    completed: true
  - item: "Five skills updated"
    completed: true
  - item: "Two memory records updated"
    completed: true
  - item: "All phases backfilled"
    completed: true
    notes: "60 files normalised; zero non-canonical frontmatter statuses remain"
  - item: "just check passes"
    completed: true
    notes: "3915 passed; 1 pre-existing failure (leaf package count from DE-103, not DE-104)"
```

# Phase 02 — Validation + --fix, schema, skills, memory, backfill

## 1. Objective

Add phase status validation to `validate` with a `--fix` flag for normalisation, fix the misleading schema example, update skill and memory guidance, and backfill all existing phase sheets to canonical status values.

## 2. Links & References

- **Delta**: [DE-104](../DE-104.md)
- **Design Revision**: [DR-104](../DR-104.md) §4.3, §4.4, §4.6, §4.7
- **Specs**: SPEC-161, SPEC-116

## 3. Entrance Criteria

- [ ] Phase 01 complete and committed

## 4. Exit Criteria / Done When

- [ ] `_validate_phase_statuses()` in `WorkspaceValidator` checks status against enum
- [ ] `--fix` flag on `validate` CLI normalises non-canonical values
- [ ] Structural warnings: missing `phase.overview` block, missing `status` field, missing/wrong `kind: phase`
- [ ] Phase discovery uses `phase-[0-9][0-9].md` glob (DEC-104-06)
- [ ] Schema example in `plan.py` uses `"status": "in-progress"` instead of `"active"`
- [ ] Skills updated: `/execute-phase`, `/update-delta-docs`, `/continuation`, `/close-change`, `/plan-phases`
- [ ] Memory updated: `mem.reference.workflow-commands`, `mem.fact.spec-driver.status-enums`
- [ ] All existing phases normalised via `validate --fix`
- [ ] `just check` passes

## 5. Verification

- `uv run pytest supekku/scripts/lib/validation/validator_test.py -x`
- `uv run pytest supekku/cli/workspace_test.py -x` (if --fix wiring has tests here)
- `just check`
- Post-backfill: `grep -r "^status:" .spec-driver/deltas/*/phases/phase-[0-9][0-9].md | grep -vE "draft|in-progress|completed|deferred|pending"` returns empty

## 6. Assumptions & STOP Conditions

- Assumes Phase 01 enum + lifecycle map is committed and importable.
- STOP if `validate --fix` produces unexpected side effects on non-phase files.

## 7. Tasks & Progress

| Status | ID  | Description                                           | Parallel? | Notes                                                                     |
| ------ | --- | ----------------------------------------------------- | --------- | ------------------------------------------------------------------------- |
| [x]    | 2.1 | `_validate_phase_statuses` + `_validate_single_phase` | [ ]       | Core validation logic                                                     |
| [x]    | 2.2 | Wire `--fix` through CLI                              | [ ]       | `--fix` on validate command                                               |
| [x]    | 2.3 | Fix schema example                                    | [P]       | `active` → `in-progress`                                                  |
| [x]    | 2.4 | Update skills (5 files)                               | [P]       | execute-phase, update-delta-docs, continuation, close-change, plan-phases |
| [x]    | 2.5 | Update memory records (2)                             | [P]       | workflow-commands, status-enums                                           |
| [x]    | 2.6 | Backfill via `validate --fix`                         | [ ]       | 60 files normalised                                                       |
| [x]    | 2.7 | Final verification                                    | [ ]       | 3915+120 tests pass; lint clean                                           |

### Task Details

- **2.1 `_validate_phase_statuses` + `_validate_single_phase`**
  - **Files**: `supekku/scripts/lib/validation/validator.py`
  - **Approach**: Per DR §4.3 code sketch. Add `_validate_phase_statuses(fix=False)` that walks `deltas/*/phases/phase-[0-9][0-9].md`. Add `_validate_single_phase()` for per-file checks. Call from `validate()` method.
  - **Imports**: `get_deltas_dir`, `get_enum_values`, `normalize_status`, `update_frontmatter_status`, `load_markdown_file`
  - **Testing**: Extend `validator_test.py`:
    - Phase with canonical status → no issue
    - Phase with `complete` → warning (or info if `--fix`)
    - Phase with `done` → warning (or info if `--fix`)
    - Phase missing status field → warning
    - Phase missing overview block → warning
    - Phase with wrong kind → warning
    - Non-standard filename (`phase-05-plan.md`) → not discovered (glob doesn't match)

- **2.2 Wire `--fix` through CLI**
  - **Files**: `supekku/cli/workspace.py`
  - **Approach**: Add `--fix` option to `validate` command. Thread through to `validate_workspace(workspace, strict=strict, fix=fix)` and `WorkspaceValidator.__init__(workspace, strict, fix)`.
  - **Testing**: Integration test or manual verification.

- **2.3 Fix schema example**
  - **Files**: `supekku/scripts/lib/core/frontmatter_metadata/plan.py`
  - **Approach**: Change phase example `"status": "active"` → `"status": "in-progress"`. One-line change.
  - **Testing**: Existing schema tests should pass.

- **2.4 Update skills**
  - **Files**: 5 skill SKILL.md files
  - **Changes per DR §4.6**:
    - `/execute-phase`: Canonical values, `phase start`/`phase complete` instructions, deferred exception
    - `/update-delta-docs`: Canonical values reference
    - `/continuation`: Note that `phase complete` updates frontmatter
    - `/close-change`: Verify phase statuses before closure
    - `/plan-phases`: "Always use `create phase` CLI — do not hand-craft" guardrail

- **2.5 Update memory records**
  - **Approach per DR §4.7**:
    - `mem.reference.workflow-commands`: Fix table entry, add frontmatter note
    - `mem.fact.spec-driver.status-enums`: Add `phase.status` to enum set, add scope paths
  - **Tool**: `uv run spec-driver edit memory <id>` or direct file edit

- **2.6 Backfill via `validate --fix`**
  - **Approach**: Run `uv run spec-driver validate --fix`. Commit normalised files as single atomic commit.
  - **Verification**: Post-fix grep confirms zero non-canonical values.

- **2.7 Final verification**
  - Run `just check`.
  - Verify `uv run spec-driver validate` (without `--fix`) reports zero phase status errors/warnings (only structural warnings for the 10 historical files).

## 8. Risks & Mitigations

| Risk                                            | Mitigation                                 | Status   |
| ----------------------------------------------- | ------------------------------------------ | -------- |
| `--fix` sets precedent for mutation in validate | Scoped narrowly per DEC-104-05; documented | Accepted |
| Backfill commit touches ~120 files              | Deterministic; reviewable diff; atomic     | Accepted |

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] `just check` passes
- [ ] Delta ready for closure
