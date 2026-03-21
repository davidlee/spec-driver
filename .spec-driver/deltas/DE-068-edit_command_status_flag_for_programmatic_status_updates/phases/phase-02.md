---
id: IP-068.PHASE-02
slug: "068-edit_command_status_flag_for_programmatic_status_updates-phase-02"
name: CLI integration and edit drift
created: "2026-03-08"
updated: "2026-03-21"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-068.PHASE-02
plan: IP-068
delta: DE-068
objective: >-
  Add --status option to all existing edit subcommands, add new edit drift
  subcommand, wire up validation and frontmatter update, verify end-to-end.
entrance_criteria:
  - Phase 1 complete — shared primitive and enum expansion landed
exit_criteria:
  - all edit subcommands accept --status flag
  - edit drift subcommand exists and works
  - validation rejects invalid statuses for enum-covered entity types
  - just check passes (tests + both linters)
verification:
  tests:
    - VT-068-02
    - VT-068-03
  evidence: []
tasks:
  - id: "2.1"
    description: Add --status to existing edit subcommands
  - id: "2.2"
    description: Add edit drift subcommand
  - id: "2.3"
    description: CLI integration tests
  - id: "2.4"
    description: Final verification pass
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-068.PHASE-02
```

# Phase 2 — CLI integration and edit drift

## 1. Objective

Wire the shared primitive and validation into the CLI edit subcommands. Add `--status` to all existing edit entities, add the new `edit drift` subcommand, and verify the full surface end-to-end.

## 2. Links & References

- **Delta**: DE-068
- **Design Revision**: DR-068 §5.3 (CLI pattern), §5.4 (consolidation)
- **Specs**: PROD-013.FR-004

## 3. Entrance Criteria

- [x] Phase 1 complete — `update_frontmatter_status()` and `validate_status_for_entity()` available

## 4. Exit Criteria / Done When

- [x] All existing edit subcommands (spec, delta, revision, requirement, adr, policy, standard, card, plan, audit, memory, issue, problem, improvement, risk) accept `--status`
- [x] New `edit drift` subcommand works (resolves via `"drift_ledger"` key, validates via `"drift"` enum path)
- [x] `--status` skips editor launch (DEC-068-02)
- [x] Invalid status values rejected with helpful error message listing valid values
- [x] Empty/whitespace status values rejected
- [x] VT-068-02 and VT-068-03 tests pass
- [x] `just check` passes (tests + both linters)

## 5. Verification

- `just test` — full suite
- `just lint` + `just pylint-files` on edited files
- Manual smoke test: `spec-driver edit delta DE-068 --status in-progress`

## 6. Assumptions & STOP Conditions

- Assumption: all edit subcommands follow the same pattern (resolve artifact → open editor) — verified in DR research
- Assumption: `resolve_artifact("drift_ledger", ...)` works for drift ledgers — verified in `common.py:497`
- STOP: if any edit subcommand has non-standard resolution that doesn't fit the pattern

## 7. Tasks & Progress

| Status | ID  | Description                                 | Parallel? | Notes                                          |
| ------ | --- | ------------------------------------------- | --------- | ---------------------------------------------- |
| [x]    | 2.1 | Add `--status` to existing edit subcommands | [ ]       | 15 subcommands, uniform pattern                |
| [x]    | 2.2 | Add `edit drift` subcommand                 | [P]       | New subcommand, uses `"drift_ledger"` resolver |
| [x]    | 2.3 | CLI integration tests                       | [ ]       | 30 tests, all passing                          |
| [x]    | 2.4 | Final verification — `just check`           | [ ]       | 3397 passed, pylint 9.71                       |

### Task Details

- **2.1 Add `--status` to existing edit subcommands**
  - **Files**: `supekku/cli/edit.py`
  - **Design**: Per DR-068 §5.3 — add `status: Annotated[str | None, typer.Option("--status", ...)] = None` to each subcommand. When provided, validate then call `update_frontmatter_status()`, print confirmation, return without opening editor.
  - **Entity-to-enum mapping**: Most use `entity_type` directly as enum path prefix. Exceptions: revision/audit use `"revision.status"` / `"audit.status"` (aliases in registry). Drift uses `"drift.status"` for enum but `"drift_ledger"` for resolution.

- **2.2 Add `edit drift` subcommand**
  - **Files**: `supekku/cli/edit.py`
  - **Design**: New `@app.command("drift")` following existing pattern. Resolve via `resolve_artifact("drift_ledger", ...)`. Validate via `validate_status_for_entity("drift", status)`. Supports both `--status` and editor-open modes.

- **2.3 CLI integration tests**
  - **Files**: `supekku/cli/edit_test.py`
  - **Tests**:
    - `--status` updates frontmatter and skips editor (mock `subprocess.run`, verify not called)
    - `--status` with invalid value for enum-covered entity type → error exit with valid values listed
    - `--status ""` → error exit
    - `--status` without value → opens editor (default behaviour preserved)
    - `edit drift` resolves and opens editor / updates status
    - Representative coverage: test at least delta (change lifecycle), issue (backlog), drift (new subcommand), spec (no enum — accepts any)

- **2.4 Final verification**
  - Run `just check` (tests + both linters)
  - Run `just pylint-files` on all modified files
  - Manual smoke test of representative commands
