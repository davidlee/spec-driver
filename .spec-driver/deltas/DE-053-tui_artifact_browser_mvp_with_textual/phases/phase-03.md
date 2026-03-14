---
id: IP-053.PHASE-03
slug: "053-tui_artifact_browser_mvp_with_textual-phase-03"
name: IP-053 Phase 03
created: "2026-03-07"
updated: "2026-03-07"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-053.PHASE-03
plan: IP-053
delta: DE-053
objective: >-
  Wire TUI into CLI entry point, add file watching with per-registry
  invalidation, handle edge cases ($EDITOR unset, import guard), run VH smoke
  gate, and scope follow-up delta for BacklogRegistry normalisation.
entrance_criteria:
  - Phase 2 complete (TUI core committed — 2c63db6)
  - watchfiles available in [tui] extra
  - ArtifactSnapshot.refresh() and BrowserScreen.refresh_snapshot() APIs exist
exit_criteria:
  - spec-driver tui command launches TUI when [tui] extra installed
  - spec-driver tui gives helpful install message when textual not installed
  - File changes trigger per-registry refresh within ~1s
  - $EDITOR unset produces helpful error (not crash)
  - VT-053-edge-cases passing
  - VH-053-smoke passed (manual gate)
  - Follow-up delta scoped for BacklogRegistry normalisation
  - just passes (lint + test)
verification:
  tests:
    - VT-053-edge-cases
  evidence:
    - VH-053-smoke
tasks:
  - id: P03-T01
    description: CLI entry point — tui command in main.py with import guard
  - id: P03-T02
    description: File watching — watchfiles.awatch integration with per-registry invalidation
  - id: P03-T03
    description: Editor integration — $EDITOR launch via app.suspend(), helpful error if unset
  - id: P03-T04
    description: VT-053-edge-cases tests
  - id: P03-T05
    description: VH-053-smoke manual verification gate
  - id: P03-T06
    description: Scope follow-up delta for BacklogRegistry normalisation
risks:
  - description: watchfiles async watcher conflicts with Textual event loop
    mitigation: watchfiles.awatch is asyncio-native; test in pilot if feasible, otherwise VH gate
  - description: app.suspend() + subprocess does not restore terminal state
    mitigation: Textual docs confirm suspend/resume pattern; VH gate covers real terminal
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-053.PHASE-03
```

# Phase 3 — Integration & Close

## 1. Objective

Wire the TUI into the CLI, add file watching and editor integration, cover
edge cases with tests, pass the manual smoke gate, and scope the follow-up
delta. This completes DE-053.

## 2. Links & References

- **Delta**: [DE-053](../DE-053.md)
- **Design Revision**: [DR-053](../DR-053.md)
  - DEC-053-07 (snapshot-on-load with watch-triggered invalidation)
  - DEC-053-08 (BacklogRegistry shim + follow-up delta)
  - DEC-053-09 (bounded dependency ranges)
- **Phase 2**: [phase-02.md](./phase-02.md) — TUI core
- **Spike findings**: [notes.md](../notes.md)

## 3. Entrance Criteria

- [x] Phase 2 complete (2c63db6)
- [x] `watchfiles` available (`[tui]` extra)
- [x] `ArtifactSnapshot.refresh(art_type)` API exists
- [x] `BrowserScreen.refresh_snapshot(art_type)` API exists

## 4. Exit Criteria / Done When

- [x] `spec-driver tui` command works (import guard + launch)
- [x] File watching triggers per-registry refresh
- [x] `$EDITOR` unset → helpful error on `e` keybinding
- [x] VT-053-edge-cases passing (16/16)
- [x] VH-053-smoke passed
- [x] Follow-up delta scoped (DE-057 — BacklogRegistry normalisation)
- [x] `just` passes (2855 tests, ruff clean, pylint 9.51)

## 5. Verification

- `just test` — all existing + new tests
- `just lint` + `just pylint` — zero warnings
- VT-053-edge-cases: import guard, $EDITOR unset, empty registries
- VH-053-smoke: launch, browse all types, filter, search, edit, watch

## 6. Assumptions & STOP Conditions

- **Assumption**: `watchfiles.awatch` integrates cleanly with Textual's asyncio
  event loop via `asyncio.create_task`.
- **Assumption**: `app.suspend()` + subprocess editor works on Linux terminals.
- **STOP**: If watchfiles watcher deadlocks or corrupts Textual event loop,
  consult before workarounds.
- **STOP**: If `app.suspend()` does not restore terminal state reliably,
  consult before alternative approaches.

## 7. Tasks & Progress

| Status | ID      | Description                                      | Parallel? | Notes             |
| ------ | ------- | ------------------------------------------------ | --------- | ----------------- |
| [x]    | P03-T01 | CLI entry point (`tui` command + import guard)   |           | main.py           |
| [x]    | P03-T02 | File watching (watchfiles.awatch integration)    |           | app.py            |
| [x]    | P03-T03 | Editor integration (`$EDITOR` + `app.suspend()`) | [P]       | app.py keybinding |
| [x]    | P03-T04 | VT-053-edge-cases tests                          |           | 16 tests          |
| [x]    | P03-T05 | VH-053-smoke manual verification                 |           | passed + polish   |
| [x]    | P03-T06 | Scope follow-up delta (BacklogRegistry)          |           | DE-057            |

### Task Details

- **P03-T01: CLI entry point**
  - **Files**: `supekku/cli/main.py`
  - **Approach**: Add `tui` command. Import guard: try importing
    `supekku.tui.app`, catch `ImportError`, print helpful message with
    install command (`uv pip install -e ".[tui]"`). On success, instantiate
    `SpecDriverApp(root=root)` and call `app.run()`.
  - **Testing**: VT-053-edge-cases covers import guard scenario.

- **P03-T02: File watching**
  - **Files**: `supekku/tui/app.py` or `supekku/tui/browser.py`
  - **Approach**: `asyncio.create_task` launching a watcher coroutine that
    calls `watchfiles.awatch(root)`. Map changed file paths to
    `ArtifactType` using directory conventions (via `paths.py` getters).
    On change, call `snapshot.refresh(art_type)` then
    `screen.refresh_snapshot(art_type)`. Watcher task cancelled on app exit.
  - **Testing**: VH gate (live filesystem changes are hard to test headlessly).

- **P03-T03: Editor integration**
  - **Files**: `supekku/tui/browser.py`
  - **Approach**: On `e` keybinding, check `$EDITOR` env var. If unset, show
    notification/error. If set, use `app.suspend()` context manager +
    `subprocess.run([$EDITOR, path])`. Terminal restores on resume.
  - **Testing**: VT-053-edge-cases covers $EDITOR unset. VH covers real edit.

- **P03-T04: VT-053-edge-cases**
  - **Files**: `supekku/tui/edge_cases_test.py` (or similar)
  - **Approach**: Test import guard (mock missing textual), $EDITOR unset
    (mock env), empty snapshot (all types return []). Use pilot where
    feasible, unit tests otherwise.

- **P03-T05: VH-053-smoke**
  - Manual verification gate. Checklist:
    - [ ] `spec-driver tui` launches
    - [ ] All artifact types visible with correct counts
    - [ ] Status filter works
    - [ ] Fuzzy search filters list
    - [ ] `e` opens $EDITOR on selected artifact
    - [ ] File change on disk triggers refresh
    - [ ] `q` exits cleanly
    - [ ] No visual glitches at 80x24 minimum

- **P03-T06: Scope follow-up delta**
  - Use `spec-driver scope delta` to create BacklogRegistry normalisation
    delta. Reference ISSUE-016, -024, -026, -034, -043, -045, IMPR-010.

## 8. Risks & Mitigations

| Risk                                           | Mitigation                                    | Status |
| ---------------------------------------------- | --------------------------------------------- | ------ |
| watchfiles/asyncio conflict                    | watchfiles async API is asyncio-native        | open   |
| app.suspend() terminal restore                 | Textual docs confirm pattern; VH gate         | open   |
| Path-to-ArtifactType mapping misses edge cases | Use paths.py getters for directory resolution | open   |

## 9. Decisions & Outcomes

Decisions inherited from DR-053. No phase-specific decisions expected.

## 10. Findings / Research Notes

**From Phase 2 handoff** (save debugging time):

- `DataTable` needs `cursor_type="row"` for `RowSelected` events
- `Select.clear()` to reset; `select.is_blank()` to check blank state
- `app.screen.query_one()` not `app.query_one()` for pushed screens
- Textual dispatches `on_*` handlers across entire MRO
- `SpecDriverApp` takes `snapshot=` param for test injection
- `watchfiles` async API compatible with asyncio

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated with findings
- [ ] IP-053 progress tracking updated
- [ ] DE-053 closed via `spec-driver complete delta DE-053`
