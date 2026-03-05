---
id: IP-041.PHASE-03
slug: 041-cli_completeness_fill_obvious_command_gaps-phase-03
name: "IP-041 Phase 03 — List improvements + final verification"
created: '2026-03-04'
updated: '2026-03-04'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-041.PHASE-03
plan: IP-041
delta: DE-041
objective: >-
  Add list plans command, backfill --filter on 6 list commands that lack it,
  add --truncate to list cards, create format_plan_list_table() formatter,
  and complete delta verification.
entrance_criteria:
  - Phase 2 complete (all show/view/edit/find subcommands wired and tested)
  - Existing test suite passing (just check)
  - DR-041 §4.8 reviewed
exit_criteria:
  - list plans subcommand with --json/--format/--filter/--status/--truncate flags
  - format_plan_list_table() formatter with tests
  - --filter added to list deltas, list adrs, list policies, list standards, list memories
  - --filter and --truncate added to list cards
  - Integration tests for new/modified list commands (VT-list-filters)
  - All IP-041 verification artifacts status updated
  - just check green (tests + both linters)
verification:
  tests:
    - VT-format-plan-list
    - VT-list-plans
    - VT-list-filters
  evidence:
    - VA-lint
tasks:
  - id: "3.1"
    description: "format_plan_list_table() formatter + tests (VT-format-plan-list)"
    status: complete
  - id: "3.2"
    description: "Plan discovery function for list plans"
    status: complete
  - id: "3.3"
    description: "Wire list plans subcommand with full baseline flags"
    status: pending
  - id: "3.4"
    description: "Add --filter to list deltas"
    status: pending
  - id: "3.5"
    description: "Add --filter to list adrs, list policies, list standards, list memories"
    status: pending
  - id: "3.6"
    description: "Add --filter and --truncate to list cards"
    status: pending
  - id: "3.7"
    description: "Integration tests for list changes (VT-list-filters)"
    status: pending
  - id: "3.8"
    description: "Update IP-041 verification statuses + final just check"
    status: pending
risks:
  - description: list.py is already 2158 lines; adding more commands increases maintenance burden
    likelihood: low
    impact: low
    mitigation: Each addition is mechanical and small; consider extraction if it crosses 2500
  - description: Plan discovery may be slow scanning all delta dirs
    likelihood: low
    impact: low
    mitigation: Delta dirs are typically <50; glob is fast enough
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-041.PHASE-03
```

# Phase 03 — List improvements + final verification

## 1. Objective

Complete the delta's list-command improvements: add `list plans` as a new
subcommand, backfill the `--filter` flag on 6 commands that lack it, add
`--truncate` to `list cards`, and close out all verification artifacts.

## 2. Links & References
- **Delta**: [DE-041](../DE-041.md)
- **Design Revision**: [DR-041](../DR-041.md) §4.8, §4.10
- **Specs**: PROD-010 (CLI UX), PROD-013 (CLI Artifact File Access)
- **Existing pattern**: `list changes` has the canonical `--filter` implementation

## 3. Entrance Criteria
- [x] Phase 2 complete (all show/view/edit/find subcommands wired and tested)
- [ ] Existing test suite passing (`just check`)
- [ ] DR-041 §4.8 reviewed

## 4. Exit Criteria / Done When
- [ ] `list plans` with `--json/--format/--filter/--status/--truncate`
- [ ] `format_plan_list_table()` tested
- [ ] `--filter` on: deltas, adrs, policies, standards, memories
- [ ] `--filter` + `--truncate` on: cards
- [ ] Integration tests for all modified list commands
- [ ] IP-041 verification statuses updated
- [ ] `just check` green

## 5. Verification
```bash
# Formatter tests
uv run pytest supekku/scripts/lib/formatters/change_formatters_test.py -k plan_list -v

# List command integration tests
uv run pytest supekku/cli/list_test.py -k "plan or filter" -v

# Full suite
just check
```

## 6. Assumptions & STOP Conditions

**Assumptions**:
- Plan files (IP-*.md) have frontmatter with id, name, status, kind fields
- The `--filter` backfill follows the exact pattern from `list changes` (substring match on id/slug/name)
- Card formatter can accept a truncate parameter following the same convention as other formatters
- `format_plan_list_table` follows existing table formatter patterns (rich Table)

**STOP when**:
- Plan frontmatter is too inconsistent to display in a table (would need registry-level normalization)
- Card formatter truncate requires changing the Card model

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 3.1 | format_plan_list_table() + tests | [ ] | Foundation for list plans |
| [x] | 3.2 | Plan discovery function | [P] | `PlanSummary` + `discover_plans()` in `changes/registry.py`; 10 tests |
| [ ] | 3.3 | Wire list plans subcommand | [ ] | After 3.1 + 3.2 |
| [ ] | 3.4 | --filter on list deltas | [P] | Mechanical; independent |
| [ ] | 3.5 | --filter on adrs/policies/standards/memories | [P] | Mechanical; independent |
| [ ] | 3.6 | --filter + --truncate on list cards | [P] | Mechanical; independent |
| [ ] | 3.7 | Integration tests (VT-list-filters) | [ ] | After 3.3–3.6 |
| [ ] | 3.8 | IP verification update + final check | [ ] | After 3.7 |

### Task Details

- **3.1 format_plan_list_table()**
  - **Design**: DR-041 §4.10. Follow `format_change_list_table` pattern. Rich Table with columns: ID, Status, Name, Delta, Phases. Accept `format_type` (table/json/tsv) and `truncate` params.
  - **Files**: `supekku/scripts/lib/formatters/change_formatters.py`
  - **Testing**: VT-format-plan-list in `change_formatters_test.py`

- **3.2 Plan discovery function**
  - **Design**: Scan `change/deltas/*/IP-*.md`, parse frontmatter, return list of dicts. Can live in `change_formatters.py` as a helper or in a thin domain function. Reuse frontmatter loading from `load_markdown_file`.
  - **Files**: `supekku/scripts/lib/changes/creation.py` or new function in `common.py`
  - **Note**: `_find_plans()` in `common.py` yields `ArtifactRef` — may be reusable but returns refs not full data. Likely need a dedicated `discover_plans()` that loads frontmatter for table display.

- **3.3 Wire list plans**
  - **Design**: DR-041 §4.8. Follow `list_revisions` pattern. Params: `--status`, `--filter`, `--regexp`, `--format`, `--json`, `--truncate`. ~40-60 lines.
  - **Files**: `supekku/cli/list.py`

- **3.4 --filter on list deltas**
  - **Design**: Add `substring` param with `--filter`/`-f`. Add substring check in filter loop before regexp check. Update docstring. Pattern: copy from `list changes` lines 490-496 (param) and 592-599 (filter logic).
  - **Files**: `supekku/cli/list.py` (list_deltas function)

- **3.5 --filter on adrs/policies/standards/memories**
  - **Design**: Same mechanical pattern as 3.4, applied to 4 commands. Each needs: param declaration, filter logic insertion, docstring update.
  - **Files**: `supekku/cli/list.py` (4 functions)

- **3.6 --filter + --truncate on list cards**
  - **Design**: Add `substring` param (--filter) and `truncate: TruncateOption` param. Pass truncate to card formatter (requires updating `format_card_list_table` signature). Add substring filter in card loop.
  - **Files**: `supekku/cli/list.py` (list_cards), `supekku/scripts/lib/formatters/card_formatters.py`

- **3.7 Integration tests**
  - **Design**: CliRunner tests. For each modified command, test that `--filter` narrows results and that `--filter nonexistent` returns empty. For list plans, test basic output and `--json`.
  - **Files**: `supekku/cli/list_test.py`

- **3.8 Final verification**
  - Update IP-041 verification block statuses (VT-backlog-find, VT-plan-resolve, etc. → verified).
  - `just check` green.
  - Update IP-041 progress tracking: Phase 3 complete.

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| list.py exceeds maintainable size | Each change is small and follows proven patterns; track line count | Monitor |
| Plan discovery O(n) over delta dirs | Typically <50 delta dirs; acceptable | Accepted |
| Card formatter truncate param changes API | Backward-compatible: default to no-truncate | Planned |

## 9. Decisions & Outcomes
- `2026-03-04` — Phase scope: all list improvements from DR-041 §4.8 + delta closure verification.
- `2026-03-04` — Tasks 3.4–3.6 are mechanical and independent; can be done in parallel or batched.

## 10. Findings / Research Notes

**Pre-phase analysis**:
- `--filter` already exists on 8 list commands (specs, changes, requirements, revisions, backlog, issues, problems, improvements, risks)
- Missing from 6: deltas, adrs, policies, standards, memories, cards
- `--truncate` exists on 14/15 list commands; missing from cards only
- Card formatter `format_card_list_table` takes `(cards, format_type)` — needs `truncate` param added
- All commands with `--filter` use identical pattern: `substring.lower()` matched against `id.lower()`, `slug.lower()`, `name.lower()`
- `list_deltas` already has `--regexp`; `--filter` is the simpler complement

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] IP-041 updated with Phase 3 results
- [ ] Delta closure checklist
