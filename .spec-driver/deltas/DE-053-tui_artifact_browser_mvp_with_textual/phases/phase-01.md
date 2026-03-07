---
id: IP-053.PHASE-01
slug: 053-tui_artifact_browser_mvp_with_textual-phase-01
name: IP-053 Phase 01
created: '2026-03-07'
updated: '2026-03-07'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-053.PHASE-01
plan: IP-053
delta: DE-053
objective: >-
  Build shared infrastructure: theme style API, shared column metadata,
  and reusable artifact projection layer. No TUI dependency.
entrance_criteria:
  - DR-053 approved (all decisions decided, no open questions)
  - DE-050 completed (normalised registry API available)
exit_criteria:
  - resolve_style() and styled_text() in theme.py with tests
  - column_defs.py with defs for all artifact types, existing formatters refactored to consume it
  - core/artifact_view.py with ArtifactEntry model, all registry adapters, error isolation, snapshot caching
  - All VT-053-adapter, VT-053-column-defs, VT-053-styled-text passing
  - just passes (lint + test)
verification:
  tests:
    - VT-053-adapter
    - VT-053-column-defs
    - VT-053-styled-text
  evidence: []
tasks:
  - id: P01-T01
    description: Add resolve_style() and styled_text() to theme.py
  - id: P01-T02
    description: Create column_defs.py and refactor formatters
  - id: P01-T03
    description: Build core/artifact_view.py
  - id: P01-T04
    description: Write tests for all three modules
risks:
  - description: Formatter refactor to consume column_defs breaks existing CLI output
    mitigation: Run existing formatter tests after refactor; diff CLI output before/after
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-053.PHASE-01
```

# Phase 1 — Shared Infrastructure

## 1. Objective

Build the reusable foundation that both TUI and CLI consume. Three modules,
no TUI dependency, fully testable independently.

## 2. Links & References
- **Delta**: [DE-053](../DE-053.md)
- **Design Revision**: [DR-053](../DR-053.md)
  - DEC-053-01 (styled_text API)
  - DEC-053-02 (column defs extraction)
  - DEC-053-04 (artifact view in core/)
  - DEC-053-06 (error isolation)
  - DEC-053-07 (snapshot caching)
  - DEC-053-08 (BacklogRegistry shim)
- **Spike findings**: [notes.md](../notes.md)

## 3. Entrance Criteria
- [x] DR-053 approved (all decisions decided, no open questions)
- [x] DE-050 completed (normalised registry API available)
- [x] Spike validated styling approach

## 4. Exit Criteria / Done When
- [x] `resolve_style()` and `styled_text()` added to `formatters/theme.py`
- [x] `formatters/column_defs.py` created with defs for all artifact types
- [x] Existing `*_formatters.py` refactored to consume `column_defs.py`
- [x] Existing CLI output unchanged (verified by existing tests — 2805 pass)
- [x] `core/artifact_view.py` created with `ArtifactEntry`, per-registry
      adapters, BacklogRegistry shim, error isolation, snapshot caching
- [x] VT-053-adapter passing (13 tests)
- [x] VT-053-column-defs passing (15 tests)
- [x] VT-053-styled-text passing (21 tests)
- [x] `just` passes (ruff clean, pylint 9.52/10, 2805 tests pass)

## 5. Verification
- `just test` — all existing + new tests
- `just lint` + `just pylint` — zero warnings
- Manual: `uv run spec-driver list specs`, `list adrs`, etc. — confirm CLI
  output unchanged after column_defs refactor

## 6. Assumptions & STOP Conditions
- **Assumption**: Existing formatter tests are sufficient to catch regression
  from column_defs extraction. If not, add targeted regression tests.
- **Assumption**: BacklogRegistry shim is ~30 lines wrapping existing functions.
  If it grows significantly, STOP and reassess whether normalisation should
  happen first.
- **STOP**: If column_defs extraction requires touching >50% of formatter
  function signatures, consult before proceeding — the refactor may be too
  invasive for this phase.

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | P01-T01 | Add `resolve_style()` / `styled_text()` to `theme.py` | [P] | 21 tests, TDD |
| [x] | P01-T02 | Create `column_defs.py` + refactor formatters | | All 9 formatters refactored, 261 formatter tests pass |
| [x] | P01-T03 | Build `core/artifact_view.py` | [P] | 13 tests, verified against real workspace (496 artifacts) |
| [x] | P01-T04 | Write VT-053-adapter, VT-053-column-defs, VT-053-styled-text | | TDD throughout; 49 new tests total |

### Task Details

- **P01-T01: Theme style API**
  - **Files**: `supekku/scripts/lib/formatters/theme.py`
  - **Approach**: Add two public functions. `resolve_style(name: str) -> Style | None`
    looks up `SPEC_DRIVER_THEME.styles`. `styled_text(value: str, style_name: str) -> Text`
    builds a `Text` object with the resolved style applied. Handle missing
    style gracefully (return unstyled Text).
  - **Testing**: VT-053-styled-text — resolve known style keys, handle missing
    keys, regression test for all style keys consumed by TUI (inventory test).

- **P01-T02: Column defs extraction**
  - **Files**: `supekku/scripts/lib/formatters/column_defs.py` (new),
    `*_formatters.py` (refactor)
  - **Approach**: For each artifact type, define a dict/dataclass with: field
    names (attribute path on the record), display labels, width hints. Refactor
    `_prepare_*_row()` functions to read column metadata from `column_defs`
    instead of inline definitions. Existing `format_*_list_table()` signatures
    and output must not change.
  - **Testing**: VT-053-column-defs — all artifact types have defs, formatter
    output unchanged (snapshot/comparison tests against existing output).
  - **Risk**: If formatter column logic is deeply entangled with per-row
    formatting (conditional display, prefix stripping), extraction may not be
    clean. Assess per-formatter; extract what's clean, document what isn't.

- **P01-T03: Artifact view layer**
  - **Files**: `supekku/scripts/lib/core/artifact_view.py` (new)
  - **Approach**:
    - `ArtifactEntry` dataclass: `id`, `title`, `status`, `path`,
      `artifact_type`, `error: str | None`
    - Per-registry adapter functions: `_adapt_{type}(record) -> ArtifactEntry`
    - `BacklogRegistry` shim: wrap `discover_backlog_items()` in a function
      returning `dict[str, ArtifactEntry]`
    - `ArtifactSnapshot` class: calls `collect()` once per registry at init,
      caches results. `refresh(artifact_type)` re-collects single registry.
      `all_entries(type_filter, status_filter)` reads from cache.
    - Error isolation: each registry `collect()` wrapped in try/except +
      stderr redirect. Failures produce entries with `error` field set.
  - **Testing**: VT-053-adapter — per-registry normalisation (at least one
    record per type), BacklogRegistry shim, error isolation (mock a registry
    raising), snapshot caching (collect called once, refresh re-collects target
    only), CardRegistry lane→status mapping.

- **P01-T04: Test suite**
  - TDD where practical (write test → implement → verify).
  - For the formatter refactor (T02), existing tests are the primary
    regression gate. Add targeted tests if coverage is thin.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Formatter refactor breaks CLI output | Existing tests + manual output diff | open |
| Column defs extraction too invasive | STOP if >50% of signatures change; consult | open |
| BacklogRegistry shim grows beyond ~30 lines | Reassess; may need normalisation first | open |

## 9. Decisions & Outcomes

Decisions inherited from DR-053. No phase-specific decisions expected unless
STOP conditions trigger.

## 10. Findings / Research Notes

(Populated during execution.)

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence: `just` passes (2805 tests, ruff clean, pylint 9.52)
- [x] Notes updated with findings
- [ ] Hand-off notes to Phase 2
