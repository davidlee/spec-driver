---
id: IP-069.PHASE-01
slug: "069-complete_formatter_migration_to_format_list_table_generic_helper-phase-01"
name: "IP-069 Phase 01: Foundation"
created: "2026-03-08"
updated: "2026-03-08"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-069.PHASE-01
plan: IP-069
delta: DE-069
objective: >-
  Create cell_helpers module, add governance_5col_widths to table_utils,
  eliminate no_truncate param, and backport helpers into already-migrated formatters.
entrance_criteria:
  - DR-069 approved
exit_criteria:
  - cell_helpers.py exists with format_tags_cell and format_date_cell
  - cell_helpers_test.py passes with edge case coverage
  - governance_5col_widths in table_utils.py
  - no_truncate removed from add_row_with_truncation
  - PACKAGES_COLUMN added to column_defs.py
  - 4 already-migrated formatters (decision, policy, standard, memory) use cell_helpers
  - 3 governance formatters (decision, policy, standard) use governance_5col_widths
  - grep -r no_truncate supekku/ returns zero hits
  - just check passes
verification:
  tests:
    - cell_helpers_test.py
    - decision_formatters_test.py
    - policy_formatters_test.py
    - standard_formatters_test.py
    - memory_formatters_test.py
    - table_utils_test.py
  evidence:
    - VT-069-cell-helpers
    - VA-069-no-truncate
tasks:
  - id: "1.1"
    summary: Create cell_helpers.py + tests
  - id: "1.2"
    summary: Add governance_5col_widths to table_utils.py
  - id: "1.3"
    summary: Remove no_truncate from add_row_with_truncation + fix tests and CLI
  - id: "1.4"
    summary: Add PACKAGES_COLUMN to column_defs.py
  - id: "1.5"
    summary: Backport cell_helpers into decision_formatters
  - id: "1.6"
    summary: Backport cell_helpers + governance_5col_widths into policy_formatters
  - id: "1.7"
    summary: Backport cell_helpers + governance_5col_widths into standard_formatters
  - id: "1.8"
    summary: Backport cell_helpers into memory_formatters
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-069.PHASE-01
```

# Phase 1 — Foundation

## 1. Objective

Create shared infrastructure (cell helpers, governance column widths), eliminate the `no_truncate` inconsistency, and backport helpers into the 4 already-migrated formatters. This establishes the reusable building blocks that Phase 2 migrations depend on.

## 2. Links & References

- **Delta**: DE-069
- **Design Revision**: DR-069 §4.1 (cell_helpers), §4.2 (governance_5col_widths), §4.3 (no_truncate), §4.5 (backport)
- **Specs**: SPEC-120, SPEC-146

## 3. Entrance Criteria

- [x] DR-069 approved

## 4. Exit Criteria / Done When

- [x] `cell_helpers.py` exists with `format_tags_cell` and `format_date_cell`
- [x] `cell_helpers_test.py` passes with edge case coverage (12 tests)
- [x] `governance_5col_widths` in `table_utils.py`
- [x] `no_truncate` removed from `add_row_with_truncation`
- [x] `PACKAGES_COLUMN` added to `column_defs.py`
- [x] Decision, policy, standard formatters use `cell_helpers` + `governance_5col_widths`
- [x] Memory formatter uses `cell_helpers`
- [x] `grep -r no_truncate supekku/` returns zero hits
- [x] `just check` passes (3414 passed, 0 failed)

## 5. Verification

- `pytest supekku/scripts/lib/formatters/cell_helpers_test.py` — new helper tests
- `pytest supekku/scripts/lib/formatters/` — all formatter regression
- `grep -r no_truncate supekku/` — must return empty
- `just check` — full suite

## 6. Assumptions & STOP Conditions

- Assumptions: existing formatter tests provide adequate regression coverage for backport changes
- STOP when: any existing formatter test fails after backport — investigate before proceeding

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                           | Parallel? | Notes                                             |
| ------ | --- | --------------------------------------------------------------------- | --------- | ------------------------------------------------- |
| [x]    | 1.1 | Create `cell_helpers.py` + `cell_helpers_test.py`                     |           | 12 tests, all passing                             |
| [x]    | 1.2 | Add `governance_5col_widths` to `table_utils.py`                      | [P]       | Extracted from decision/policy/standard           |
| [x]    | 1.3 | Remove `no_truncate` from `add_row_with_truncation` + fix tests + CLI | [P]       | 2 test sites, 3 CLI sites, 2 formatter signatures |
| [x]    | 1.4 | Add `PACKAGES_COLUMN` to `column_defs.py`                             | [P]       | Done                                              |
| [x]    | 1.5 | Backport into `decision_formatters.py`                                |           | cell_helpers + governance_5col_widths             |
| [x]    | 1.6 | Backport into `policy_formatters.py`                                  | [P]       | cell_helpers + governance_5col_widths             |
| [x]    | 1.7 | Backport into `standard_formatters.py`                                | [P]       | cell_helpers + governance_5col_widths             |
| [x]    | 1.8 | Backport into `memory_formatters.py`                                  | [P]       | cell_helpers only (custom widths kept)            |

### Task Details

- **1.1 Create `cell_helpers.py` + tests**
  - **Files**: `supekku/scripts/lib/formatters/cell_helpers.py`, `supekku/scripts/lib/formatters/cell_helpers_test.py`
  - **Design**: Per DR-069 §4.1. Two pure functions. `format_tags_cell(tags, style="#d79921")` → Rich markup string. `format_date_cell(date, missing="—", fmt="%Y-%m-%d")` → formatted string.
  - **Testing**: Empty/None tags, single tag, multiple tags, custom style. None date, valid date, custom missing sentinel, custom format.
  - **Export**: Add to `formatters/__init__.py`

- **1.2 Add `governance_5col_widths` to `table_utils.py`**
  - **Design**: Per DR-069 §4.2. Extract from `decision_formatters._calculate_column_widths` (byte-identical in policy/standard). ID(10), Title(flex), Tags(20), Status(12), Updated(10).
  - **Testing**: Existing tests cover width calculation indirectly via formatter tests.

- **1.3 Remove `no_truncate` from `add_row_with_truncation`**
  - **Files**: `table_utils.py`, `table_utils_test.py`, `cli/list.py`
  - **Design**: Per DR-069 §4.3. Remove param; `max_widths=None` is the sole truncation-skip mechanism. Update 2 test call sites (pass `max_widths=None`). Update 3 CLI call sites: `no_truncate=not truncate` → `truncate=truncate`.
  - **Note**: Also rename `no_truncate` → `truncate` in `spec_formatters` and `change_formatters` signatures — but those bodies change in Phase 2, so only rename the param + invert logic in the signature here; the migration itself is Phase 2.

- **1.4 Add `PACKAGES_COLUMN` to `column_defs.py`**
  - **Design**: Add `PACKAGES_COLUMN = ColumnDef(label="Packages", field="packages")` for spec_formatters consistency.
  - **Testing**: Covered by existing `column_defs_test.py` patterns.

- **1.5–1.8 Backport into already-migrated formatters**
  - **Design**: Replace inline `", ".join(tags)` + markup → `format_tags_cell(tags)`. Replace inline `.strftime(...)` + fallback → `format_date_cell(date)` / `format_date_cell(date, missing="N/A")`. Replace local `_calculate_column_widths` → `governance_5col_widths` (decision/policy/standard only).
  - **Testing**: Run each formatter's existing test suite after change. No new tests needed — behaviour is identical.

## 8. Risks & Mitigations

| Risk                              | Mitigation                                         | Status |
| --------------------------------- | -------------------------------------------------- | ------ |
| Backport breaks stable formatters | Test suite exists for all 4; run after each change | open   |

## 9. Decisions & Outcomes

- 2026-03-08 — All design decisions settled in DR-069 (DEC-069-01 through DEC-069-05)
