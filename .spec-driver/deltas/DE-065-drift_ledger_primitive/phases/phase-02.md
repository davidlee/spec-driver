---
id: IP-065.PHASE-02
slug: 065-drift_ledger_primitive-phase-02
name: Formatters, CLI, DE-063 integration
created: '2026-03-08'
updated: '2026-03-08'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-065.PHASE-02
plan: IP-065
delta: DE-065
objective: >-
  Build drift ledger formatters (pure functions), CLI commands (create/list/show),
  and integrate with DE-063 ID inference/dispatch system (PREFIX_TO_TYPE,
  resolvers, finders, show/view handlers).
entrance_criteria:
  - P01 complete (domain layer implemented and tested)
  - DR-065 §6 integration points understood
exit_criteria:
  - drift_formatters.py with list table and detail formatters
  - CLI create/list/show commands working
  - DE-063 integration: DL prefix inference, show/view dispatch
  - VT-065-formatters and VT-065-cli passing
  - ruff and pylint clean on all new/modified files
verification:
  tests:
    - VT-065-formatters
    - VT-065-cli
  evidence: []
tasks:
  - id: "2.1"
    description: create drift_formatters.py (list table, detail, JSON)
  - id: "2.2"
    description: add drift theme styles and column defs
  - id: "2.3"
    description: create drift ledger creation function
  - id: "2.4"
    description: add CLI commands (create/list/show drift)
  - id: "2.5"
    description: DE-063 integration (common.py, resolve.py, show.py, view.py)
  - id: "2.6"
    description: tests for formatters and CLI
risks:
  - description: common.py or show.py may have changed since DR-065 was written
    mitigation: read current code before integrating
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-065.PHASE-02
```

# Phase 2 — Formatters, CLI, DE-063 integration

## 1. Objective

Build the display and CLI layers for drift ledgers: pure formatters, thin CLI
commands (create/list/show), and integration with the DE-063 ID inference and
dispatch system so `spec-driver show DL-047` works via prefix lookup.

## 2. Links & References

- **Delta**: DE-065
- **Design Revision**: DR-065 §6 (DE-063 integration), §10 (creation template)
- **Pattern references**:
  - Formatter: `supekku/scripts/lib/formatters/backlog_formatters.py`
  - Table utils: `supekku/scripts/lib/formatters/table_utils.py`
  - Column defs: `supekku/scripts/lib/formatters/column_defs.py`
  - CLI create: `supekku/cli/create.py`
  - CLI list: `supekku/cli/list.py`
  - ID inference: `supekku/cli/common.py` (PREFIX_TO_TYPE, resolvers, finders)
  - Artifact index: `supekku/cli/resolve.py` (build_artifact_index)
  - Show dispatch: `supekku/cli/show.py` (show_handlers)
  - View dispatch: `supekku/cli/view.py`

## 3. Entrance Criteria

- [x] P01 complete (models, parser, registry implemented, 65 tests)
- [x] DR-065 §6 integration points read and understood

## 4. Exit Criteria / Done When

- [x] `drift_formatters.py` with `format_drift_list_table()` and `format_drift_details()`
- [x] Column defs and theme styles for drift ledgers
- [x] Drift creation function in `supekku/scripts/lib/drift/creation.py`
- [x] CLI `create drift`, `list drift`, `show drift` commands working
- [x] DE-063 integration: `DL` prefix in PREFIX_TO_TYPE, resolver, finder
- [x] `show_handlers` and `view` dispatch include drift_ledger
- [x] `build_artifact_index()` collects drift ledgers
- [x] All tests pass (`just test`) — 3285 passed
- [x] Both linters clean — ruff 0 errors, new files pylint 10.00/10

## 5. Verification

- `just test` — all unit tests
- `just lint` — ruff
- `just pylint-files` on new/modified files

## 6. Assumptions & STOP Conditions

- Assumptions:
  - Phase 1 domain layer is stable and tested
  - DE-063 dispatch tables are additive (append-only extension)
  - `format_list_table` from table_utils is the right abstraction for drift list
- STOP when:
  - DE-063 tables have changed shape requiring refactor
  - Creation requires template infrastructure not yet available

## 7. Tasks & Progress

| Status | ID  | Description                                      | Parallel? | Notes                                  |
| ------ | --- | ------------------------------------------------ | --------- | -------------------------------------- |
| [x]    | 2.1 | `drift_formatters.py` — list table, detail, JSON | [P]       | used format_list_table() generic       |
| [x]    | 2.2 | theme styles + column defs for drift             | [P]       | done                                   |
| [x]    | 2.3 | `drift/creation.py` — create_drift_ledger()      | [P]       | done                                   |
| [x]    | 2.4 | CLI commands: create/list/show drift             | —         | in verb modules, not separate drift.py |
| [x]    | 2.5 | DE-063 integration: common, resolve, show, view  | —         | all 6 extension points                 |
| [x]    | 2.6 | tests: VT-065-formatters, VT-065-cli             | —         | 41 tests, all passing                  |

### Task Details

- **2.1 drift_formatters.py**
  - `format_drift_list_table(ledgers, format_type, truncate)` — table/json/tsv
  - `format_drift_details(ledger)` — full detail view for show command
  - `format_drift_details_json(ledger)` — JSON serialization
  - Use `format_list_table()` from table_utils for list, `add_row_with_truncation()`
  - Rich-aware truncation via `Text.from_markup()`

- **2.2 theme + column defs**
  - Add `DRIFT_COLUMNS` to `column_defs.py`
  - Add drift status styles to `theme.py` + `get_drift_status_style()`
  - Drift ID style: `drift.id`

- **2.3 creation**
  - `create_drift_ledger(name, delta_ref=None, repo_root=None) -> Path`
  - Next-ID allocation: scan existing DL-\*.md, pick max+1
  - Template per DR-065 §10
  - Creates `.spec-driver/drift/` directory if needed

- **2.4 CLI commands**
  - `create drift` in create.py — thin, delegates to creation.py
  - `list drift` in list.py — thin, registry + filter + format
  - `show drift` in show.py — thin, resolve + emit_artifact

- **2.5 DE-063 integration**
  - `PREFIX_TO_TYPE["DL"] = "drift_ledger"`
  - `_resolve_drift_ledger()` in common.py
  - `_find_drift_ledgers()` in common.py
  - `_collect_drift_ledgers()` in resolve.py
  - `show_drift_ledger` handler + show_handlers entry in show.py
  - `view_drift_ledger` handler in view.py

## 8. Risks & Mitigations

| Risk                                        | Mitigation                                           | Status   |
| ------------------------------------------- | ---------------------------------------------------- | -------- |
| common.py is already large                  | Minimal additions following exact existing pattern   | resolved |
| list.py exceeding 150 lines (already large) | Drift list command is small, follow existing pattern | resolved |

## 9. Decisions & Outcomes

- 2026-03-08: CLI commands added to verb modules (create.py, list.py, show.py) instead of separate drift.py — matches actual codebase pattern where all commands live in verb-grouped modules
- 2026-03-08: Used `format_list_table()` generic helper instead of hand-rolling table setup — cleaner than backlog_formatters.py pattern
- 2026-03-08: Extracted `_entry_to_dict()` from `format_drift_details_json()` to reduce McCabe complexity from 11 to acceptable levels
- 2026-03-08: `--delta` flag implemented as optional on `create drift` (DR-065 open question resolved: yes, explicit flag)

## 10. Findings / Research Notes

- DE-063 extension points are purely additive — adding to dispatch tables is mechanical and low-risk
- `format_list_table()` in table_utils.py is the right abstraction for new list formatters — eliminates boilerplate
- Pre-existing pylint warnings in CLI modules (import-outside-toplevel, duplicate-code) are endemic to the pattern, not introduced by drift additions

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (3285 tests, ruff clean, pylint 10.00/10 on new files)
- [x] Phase sheet updated with outcomes
- [x] Hand-off notes to phase 3 (in notes.md)
