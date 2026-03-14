---
id: IP-063.PHASE-02
slug: 063-id-inference
name: 'P02: ID inference for show/view'
created: '2026-03-08'
updated: '2026-03-08'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-063.PHASE-02
plan: IP-063
delta: DE-063
objective: >-
  Add type-inferring ID resolution to show/view commands so bare IDs
  (DE-061, 61) resolve without specifying the entity subcommand.
entrance_criteria:
  - P01 complete
  - DR-063 §4a design agreed
exit_criteria:
  - InferringGroup custom Click Group dispatches bare IDs correctly
  - resolve_by_id() resolves prefixed, numeric, and ambiguous IDs
  - Hidden "inferred" command accepts output flags (--json, --path, --raw)
  - VT-063-01 and VT-063-02 tests passing
  - Existing show/view tests still passing
  - Lint clean
verification:
  tests:
    - VT-063-01
    - VT-063-02
  evidence: []
tasks:
  - id: "2.1"
    description: Add PREFIX_TO_TYPE mapping and resolve_by_id() to common.py
  - id: "2.2"
    description: Create InferringGroup in common.py
  - id: "2.3"
    description: Add hidden "inferred" command to show.py
  - id: "2.4"
    description: Add hidden "inferred" command to view.py
  - id: "2.5"
    description: Write VT-063-01 tests (resolve_by_id)
  - id: "2.6"
    description: Write VT-063-02 tests (CliRunner integration)
  - id: "2.7"
    description: Verify existing tests + lint
risks:
  - description: InferringGroup interaction with Typer internals
    mitigation: Integration tests via CliRunner validate full chain
  - description: _build_artifact_index perf for large repos
    mitigation: Single scan, same cost as existing resolve links
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-063.PHASE-02
```

# P02 — ID inference for show/view

## 1. Objective

Add type-inferring ID resolution to `show` and `view` commands so users can
write `spec-driver show DE-061` or `spec-driver show 61` without specifying
the entity subcommand.

## 2. Links & References

- **Delta**: DE-063
- **Design Revision**: DR-063 §4a
- **Issues**: ISSUE-045

## 3. Entrance Criteria

- [x] P01 complete
- [x] DR-063 §4a design agreed

## 4. Exit Criteria / Done When

- [ ] `PREFIX_TO_TYPE` mapping in `common.py`
- [ ] `resolve_by_id()` using `_build_artifact_index()` in `common.py`
- [ ] `InferringGroup` custom Click Group in `common.py`
- [ ] Hidden "inferred" command in `show.py` with --json/--path/--raw/--root
- [ ] Hidden "inferred" command in `view.py` with --root
- [ ] VT-063-01 tests passing (resolve_by_id)
- [ ] VT-063-02 tests passing (CliRunner integration)
- [ ] Existing show/view tests still passing
- [ ] Lint clean on all changed files

## 5. Verification

- Run: `just test`
- Run: `just lint` + `just pylint-files <changed files>`
- Evidence: test output showing VT-063-01 + VT-063-02 passing

## 6. Assumptions & STOP Conditions

- Assumption: Typer's `cls=` parameter works with custom Click Group subclasses
- Assumption: `_build_artifact_index()` from resolve.py is importable
- Assumption: `Table.add_row()` accepts `Text` objects (confirmed in P01)
- STOP if: `InferringGroup.resolve_command()` doesn't integrate cleanly with
  Typer's argument parsing pipeline

## 7. Tasks & Progress

| Status | ID  | Description                      | Parallel? | Notes                      |
| ------ | --- | -------------------------------- | --------- | -------------------------- |
| [ ]    | 2.1 | PREFIX_TO_TYPE + resolve_by_id() |           | common.py                  |
| [ ]    | 2.2 | InferringGroup                   |           | common.py                  |
| [ ]    | 2.3 | Hidden "inferred" in show.py     |           | After 2.1+2.2              |
| [ ]    | 2.4 | Hidden "inferred" in view.py     |           | After 2.1+2.2              |
| [ ]    | 2.5 | VT-063-01 tests                  | [P]       | Can start before 2.1 (TDD) |
| [ ]    | 2.6 | VT-063-02 tests                  |           | After 2.3+2.4              |
| [ ]    | 2.7 | Full test suite + lint           |           | After all                  |

### Task Details

- **2.1 PREFIX_TO_TYPE + resolve_by_id()**
  - **Files**: `supekku/cli/common.py`
  - **Approach**: Add reverse prefix mapping. `resolve_by_id()` uses
    `_build_artifact_index()` from `resolve.py` for O(1) lookup. Prefixed
    IDs resolve directly; numeric IDs try all prefixes and collect matches.
  - **Testing**: VT-063-01

- **2.2 InferringGroup**
  - **Files**: `supekku/cli/common.py`
  - **Approach**: Custom Click Group subclass overriding `resolve_command()`.
    Unknown subcommands stored in `ctx.obj["inferred_id"]`, routed to
    hidden "inferred" command.

- **2.3 Hidden "inferred" in show.py**
  - **Files**: `supekku/cli/show.py`
  - **Approach**: `@app.command("inferred", hidden=True)` accepting
    `--json`, `--path`, `--raw`, `--root`. Reads `ctx.obj["inferred_id"]`,
    calls `resolve_by_id()`, delegates to `emit_artifact()`.
  - **Change**: `app = typer.Typer(cls=InferringGroup, no_args_is_help=True)`

- **2.4 Hidden "inferred" in view.py**
  - **Files**: `supekku/cli/view.py`
  - **Approach**: Same pattern as show.py but calls `open_in_pager()`.

- **2.5 VT-063-01: resolve_by_id tests**
  - **Cases**: prefixed ID (DE-061), numeric ID (61), ambiguous numeric,
    unknown ID, card ID (T123), out-of-scope types (memory, requirement)

- **2.6 VT-063-02: CliRunner integration tests**
  - **Cases**: known subcommand passthrough, bare prefixed ID, bare numeric,
    ambiguous disambiguation, unknown error, no-args help, output flags

## 8. Risks & Mitigations

| Risk                        | Mitigation                         | Status |
| --------------------------- | ---------------------------------- | ------ |
| Typer cls= interaction      | CliRunner integration tests        | open   |
| \_build_artifact_index perf | Single scan, same as resolve links | open   |

## 9. Decisions & Outcomes

- DR-063 DEC-063-01: Custom Click Group — approved
- DR-063 DEC-063-04: Reuse \_build_artifact_index() — approved

## 10. Findings / Research Notes

(populated during execution)

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] ISSUE-042 closed as wontfix
- [ ] ISSUE-045, ISSUE-038, ISSUE-041 closable
