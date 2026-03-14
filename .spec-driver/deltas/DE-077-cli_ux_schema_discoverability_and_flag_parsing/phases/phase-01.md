---
id: IP-077.PHASE-01
slug: "077-cli_ux_schema_discoverability_and_flag_parsing-phase-01"
name: "IP-077 Phase 01: Implementation"
created: "2026-03-09"
updated: "2026-03-09"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-077.PHASE-01
plan: IP-077
delta: DE-077
objective: >-
  Create hints.py module, update create commands with schema hints,
  fix --from-backlog flag parsing, write tests
entrance_criteria:
  - DR-077 drafted
exit_criteria:
  - hints.py exists with ARTIFACT_SCHEMA_MAP and format_schema_hints()
  - All create commands emit schema hints
  - --from-backlog is a boolean flag; backlog ID via positional
  - Unit tests pass for both features
  - Lint clean on changed files
verification:
  tests:
    - VT-077-schema-hints
    - VT-077-from-backlog
  evidence: []
tasks:
  - id: "1.1"
    description: Create supekku/cli/hints.py
  - id: "1.2"
    description: Update create commands to emit schema hints
  - id: "1.3"
    description: Convert --from-backlog to boolean flag
  - id: "1.4"
    description: Write tests
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-077.PHASE-01
```

# Phase 1 — Implementation

## 1. Objective

Create the schema hints helper, wire it into all create commands, fix `--from-backlog` greedy parsing, and write tests for both changes.

## 2. Links & References

- **Delta**: DE-077
- **Design Revision**: DR-077 (sections 4, 7)
- **Specs**: SPEC-110, PROD-010
- **Issues**: ISSUE-023, ISSUE-043

## 3. Entrance Criteria

- [x] DR-077 drafted and reviewed

## 4. Exit Criteria / Done When

- [ ] `supekku/cli/hints.py` exists with `ARTIFACT_SCHEMA_MAP` and `format_schema_hints()`
- [ ] All applicable create commands call `print_schema_hints()` before exit
- [ ] `--from-backlog` is a boolean flag; positional `name` carries backlog ID
- [ ] `_validate_backlog_id` callback removed
- [ ] Unit tests for `format_schema_hints()` cover all mapped artifact kinds + unmapped kind
- [ ] CLI runner tests verify hint output for at least delta, revision, audit
- [ ] `--from-backlog` tests updated for boolean flag shape
- [ ] `just lint` clean on changed files

## 5. Verification

- `pytest supekku/cli/hints_test.py` — unit tests for hints module
- `pytest supekku/cli/create_test.py` — updated CLI tests
- `just lint` — ruff clean
- `just pylint-files supekku/cli/hints.py supekku/cli/create.py`

## 6. Assumptions & STOP Conditions

- Assumptions: All frontmatter schema kinds in the map exist in the registry
- STOP when: Typer boolean flag doesn't behave as expected with positional args

## 7. Tasks & Progress

| Status | ID  | Description                              | Parallel? | Notes                    |
| ------ | --- | ---------------------------------------- | --------- | ------------------------ |
| [ ]    | 1.1 | Create `supekku/cli/hints.py`            | [P]       | Pure function + constant |
| [ ]    | 1.2 | Wire hints into create commands          |           | After 1.1                |
| [ ]    | 1.3 | Convert `--from-backlog` to boolean flag | [P]       | Independent of 1.1       |
| [ ]    | 1.4 | Write/update tests                       |           | After 1.1–1.3            |

### Task Details

- **1.1 Create hints.py**
  - `ARTIFACT_SCHEMA_MAP` dict constant per DR-077
  - `format_schema_hints(artifact_kind: str) -> list[str]` pure function
  - Files: `supekku/cli/hints.py`

- **1.2 Wire hints into create commands**
  - Add `print_schema_hints()` wrapper that calls `format_schema_hints()` + `typer.echo()`
  - Call before `raise typer.Exit(EXIT_SUCCESS)` in: delta, plan, phase, revision, audit, spec, adr, policy, standard, memory
  - Backlog entries (issue/problem/improvement/risk) and card/drift — skip (no meaningful schemas)
  - Files: `supekku/cli/create.py`

- **1.3 Convert --from-backlog**
  - Change type annotation from `str | None` to `bool`
  - Remove `callback=_validate_backlog_id`
  - Remove `_validate_backlog_id` function and `_BACKLOG_ID_RE` (if only used there — check first)
  - Add inline validation in command body: if `from_backlog` and `name` doesn't match backlog pattern
  - Files: `supekku/cli/create.py`

- **1.4 Tests**
  - `supekku/cli/hints_test.py` — new file
  - `supekku/cli/create_test.py` — update `CreateDeltaFromBacklogValidationTest`
  - Files: `supekku/cli/hints_test.py`, `supekku/cli/create_test.py`

## 8. Risks & Mitigations

| Risk                            | Mitigation                               | Status |
| ------------------------------- | ---------------------------------------- | ------ |
| `_BACKLOG_ID_RE` used elsewhere | Grep before removing; relocate if shared | Open   |
