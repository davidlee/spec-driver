---
id: IP-063.PHASE-01
slug: 063-truncation-fix
name: "P01: Truncation fix"
created: "2026-03-08"
updated: "2026-03-08"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-063.PHASE-01
plan: IP-063
delta: DE-063
objective: >-
  Fix markup-aware truncation in table_utils.py so list --truncate renders
  correct status values instead of corrupted Rich markup fragments.
entrance_criteria:
  - IP-063 approved
  - DR-063 §4b design agreed
exit_criteria:
  - add_row_with_truncation uses Text.from_markup() for display-width measurement
  - Dead truncate_text() removed
  - VT-063-03 tests passing
  - Lint clean (ruff + pylint on changed files)
  - Existing list tests still passing
verification:
  tests:
    - VT-063-03
  evidence: []
tasks:
  - id: "1.1"
    description: Implement markup-aware truncation in add_row_with_truncation
  - id: "1.2"
    description: Remove dead truncate_text() and update imports
  - id: "1.3"
    description: Write VT-063-03 tests
  - id: "1.4"
    description: Verify existing list tests pass, lint clean
risks:
  - description: Text.from_markup() edge cases with malformed markup
    mitigation: Rich treats unrecognized tags as literal text — no crash risk; test explicitly
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-063.PHASE-01
```

# P01 — Truncation fix

## 1. Objective

Fix `add_row_with_truncation()` in `table_utils.py` to use Rich's
`Text.from_markup()` for display-width measurement, so `list --truncate`
renders status as human-readable values instead of corrupted markup fragments.

## 2. Links & References

- **Delta**: DE-063
- **Design Revision**: DR-063 §4b
- **Issues**: ISSUE-038, ISSUE-041

## 3. Entrance Criteria

- [x] IP-063 approved
- [x] DR-063 §4b design agreed

## 4. Exit Criteria / Done When

- [ ] `add_row_with_truncation` uses `Text.from_markup()` + `Text.truncate()`
- [ ] `max_width <= 3` edge case guarded (truncate without ellipsis)
- [ ] Dead `truncate_text()` removed from `table_utils.py`
- [ ] VT-063-03 tests written and passing
- [ ] Existing list/table tests still passing
- [ ] Lint clean on changed files

## 5. Verification

- Run: `just test` (full suite)
- Run: `just lint` + `just pylint-files supekku/scripts/lib/formatters/table_utils.py`
- Evidence: test output showing VT-063-03 passing

## 6. Assumptions & STOP Conditions

- Assumption: `Table.add_row()` accepts `Text` objects (Rich docs confirm)
- Assumption: No callers of `truncate_text()` outside table_utils.py (grep confirmed)
- STOP if: `Text.from_markup()` handles any input differently from expected
  (e.g. double-encoding, style inheritance issues)

## 7. Tasks & Progress

| Status | ID  | Description                       | Parallel? | Notes                      |
| ------ | --- | --------------------------------- | --------- | -------------------------- |
| [ ]    | 1.1 | Implement markup-aware truncation |           | DR-063 §4b target impl     |
| [ ]    | 1.2 | Remove dead `truncate_text()`     |           | After 1.1                  |
| [ ]    | 1.3 | Write VT-063-03 tests             |           | Can start before 1.1 (TDD) |
| [ ]    | 1.4 | Verify existing tests + lint      |           | After 1.1 + 1.2            |

### Task Details

- **1.1 Implement markup-aware truncation**
  - **Files**: `supekku/scripts/lib/formatters/table_utils.py`
  - **Approach**: Replace `truncate_text(value, max_width)` call in
    `add_row_with_truncation` with `Text.from_markup(value)` +
    `Text.truncate()` + `Text.append("...")`. Add `max_width <= 3` guard.
  - **Testing**: VT-063-03

- **1.2 Remove dead `truncate_text()`**
  - **Files**: `supekku/scripts/lib/formatters/table_utils.py`
  - **Approach**: Remove function definition. Update `__all__` if exported.
    Remove from test file if tested standalone.

- **1.3 Write VT-063-03 tests**
  - **Files**: `tests/formatters/test_table_utils.py` (or wherever existing tests live)
  - **Cases**: plain text (no truncation needed), plain text (truncation needed),
    short markup (no truncation), long markup (truncation preserves style),
    `max_width <= 3`, mixed markup/plain row, empty string

- **1.4 Verify existing tests + lint**
  - **Commands**: `just test`, `just lint`,
    `just pylint-files supekku/scripts/lib/formatters/table_utils.py`

## 8. Risks & Mitigations

| Risk             | Mitigation                               | Status |
| ---------------- | ---------------------------------------- | ------ |
| Malformed markup | Rich treats as literal — test explicitly | open   |

## 9. Decisions & Outcomes

- DR-063 DEC-063-02: Use `Text.from_markup()` — approved
- DR-063 DEC-063-05: Remove dead `truncate_text()` — approved

## 10. Findings / Research Notes

(populated during execution)

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Hand-off notes to P02
