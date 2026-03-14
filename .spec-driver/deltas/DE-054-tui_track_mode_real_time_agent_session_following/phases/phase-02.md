---
id: IP-054.PHASE-02
slug: 054-tui_track_mode_real_time_agent_session_following-phase-02
name: IP-054 Phase 02 — TrackScreen and app integration
created: "2026-03-07"
updated: "2026-03-07"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-054.PHASE-02
plan: IP-054
delta: DE-054
objective: >-
  Build TrackScreen, TrackPanel, SessionList widgets. Integrate EventListener
  into SpecDriverApp with toggle keybinding and cross-screen artifact navigation.
  Add theme styles and layout CSS.
entrance_criteria:
  - Phase 1 complete (EventListener passes VT-054-01..04)
  - just green
exit_criteria:
  - VT-054-05 through VT-054-08 passing
  - VH-054-01 and VH-054-02 attested
  - just passes (lint + test)
verification:
  tests:
    - VT-054-05
    - VT-054-06
    - VT-054-07
    - VT-054-08
  evidence:
    - VH-054-01
    - VH-054-02
tasks:
  - id: P02-T1
    description: Theme style keys for track view (theme.py)
  - id: P02-T2
    description: TrackPanel widget (RichLog, event formatting)
  - id: P02-T3
    description: SessionList widget (session discovery, colour assignment, filtering)
  - id: P02-T4
    description: TrackScreen (2-panel layout, message handling, event buffer)
  - id: P02-T5
    description: ArtifactSnapshot.find_entry() cross-type lookup
  - id: P02-T6
    description: BrowserScreen.navigate_to_artifact() method
  - id: P02-T7
    description: App integration (toggle binding, listener lifecycle, navigate action)
  - id: P02-T8
    description: TrackScreen layout CSS (theme.tcss)
  - id: P02-T9
    description: Tests VT-054-05..08
  - id: P02-T10
    description: VH-054-01 and VH-054-02 manual attestation
risks:
  - description: RichLog max_lines with wrap
    mitigation: wrap=False enforced, single-line events
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-054.PHASE-02
```

# Phase 2 — TrackScreen and app integration

## 1. Objective

Build the visible Track view: TrackPanel (event stream), SessionList (session
filter), TrackScreen (composition), and integrate into SpecDriverApp with `t`
toggle, EventListener lifecycle, and cross-screen artifact navigation. Add
theme style keys and layout CSS.

## 2. Links & References

- **Delta**: DE-054
- **Design Revision Sections**: DEC-054-01 (TrackScreen), DEC-054-04 (sessions),
  DEC-054-06 (navigation), DEC-054-07 (TrackPanel)
- **Phase 1 output**: `supekku/tui/event_listener.py` (EventListener)
- **Existing TUI**: `supekku/tui/app.py`, `browser.py`, `widgets/`

## 3. Entrance Criteria

- [ ] Phase 1 complete — EventListener VTs passing
- [ ] `just` green

## 4. Exit Criteria / Done When

- [ ] `t` toggles between BrowserScreen and TrackScreen
- [ ] TrackScreen shows live events from socket (or log-tail)
- [ ] Session list shows discovered sessions with stable colours
- [ ] Session filtering works (specific session + "all" mode)
- [ ] Clicking an event with artifacts navigates to browser
- [ ] VT-054-05..08 passing
- [ ] VH-054-01 attested (live events between terminals)
- [ ] VH-054-02 attested (second instance graceful degradation)
- [ ] `just` green

## 5. Verification

- `just test` — unit + pilot tests
- `just lint` + `just pylint` — zero warnings
- VT-054-05: Session filter — "all" returns all, specific ID returns subset
- VT-054-06: Session discovery — unique sessions from events, recency order
- VT-054-07: Cross-screen navigation — find_entry resolves artifact,
  browser navigates to correct type + row
- VT-054-08: TrackScreen pilot — widget composition, event rendering in
  DataTable, session selection updates filter, row selection triggers navigation
- VH-054-01: Manual smoke — CLI commands in one terminal, TUI track view
  in another, events appear in real time
- VH-054-02: Start second TUI — first keeps working on socket, second
  falls back to log-tail, both show events

## 6. Assumptions & STOP Conditions

- Assumptions:
  - `install_screen` + `switch_screen` preserves both screens' widget state
    (confirmed via Textual API verification)
  - `DataTable` accepts `Text` objects in cells (confirmed — same pattern
    as `artifact_list.py`)
  - 8-colour palette is sufficient for session differentiation
- STOP when:
  - `switch_screen` unexpectedly unmounts a screen — escalate
  - `DataTable.RowSelected` doesn't fire on row click — escalate

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID      | Description                          | Parallel? | Notes                                    |
| ------ | ------- | ------------------------------------ | --------- | ---------------------------------------- |
| [x]    | P02-T1  | Theme style keys                     | [P]       | 13 track.\* keys added                   |
| [x]    | P02-T2  | TrackPanel widget                    | [P]       | DataTable, not RichLog (DEC-054-07 rev)  |
| [x]    | P02-T3  | SessionList widget                   | [P]       | OptionList + SessionSelected msg         |
| [x]    | P02-T4  | TrackScreen                          |           | 2-panel compose, event buffer            |
| [x]    | P02-T5  | ArtifactSnapshot.find_entry()        | [P]       | Cross-type dict lookup                   |
| [x]    | P02-T6  | BrowserScreen.navigate_to_artifact() |           | Type switch + row cursor                 |
| [x]    | P02-T7  | App integration                      |           | install+push, toggle, navigate, listener |
| [x]    | P02-T8  | TrackScreen layout CSS               |           | Horizontal split, border conventions     |
| [x]    | P02-T9  | Tests VT-054-05..08                  |           | 20 tests + 4 find_entry tests            |
| [x]    | P02-T10 | VH manual attestation                |           | VH-054-01 + VH-054-02 attested           |

### Task Details

- **P02-T1: Theme style keys**
  - **Design**: DEC-054-04, DEC-054-07. Add to `SPEC_DRIVER_THEME`:
    `track.timestamp`, `track.cmd`, `track.artifact`,
    `track.status.ok`, `track.status.error`,
    `track.session.0` through `track.session.7`
  - **Files**: `supekku/scripts/lib/formatters/theme.py`

- **P02-T2: TrackPanel widget**
  - **Design**: DEC-054-07. `TrackPanel(Static)` wrapping a
    `DataTable(cursor_type="row")` with 5 columns (timestamp, session, cmd,
    artifact, status). `append_event(event: dict)` adds a styled row;
    prunes oldest row when `row_count > DISPLAY_BUFFER_LIMIT`.
    `clear_and_replay(events, session_filter)` for filter changes. Row key
    stores first artifact ID for navigation.
  - **Files**: `supekku/tui/widgets/track_panel.py`

- **P02-T3: SessionList widget**
  - **Design**: DEC-054-04. `SessionList(OptionList)`. Maintains
    `dict[str|None, SessionInfo]` (last_ts, count). `register_event(event)`
    updates metadata. Rebuilds option list ordered by recency. Colour via
    `md5(session_id) % 8` → `track.session.N` style key. Posts
    `SessionSelected(session_id: str | None)` message. "all" option always
    first.
  - **Files**: `supekku/tui/widgets/session_list.py`

- **P02-T4: TrackScreen**
  - **Design**: DEC-054-01. `TrackScreen(Screen)`. Compose: SessionList +
    TrackPanel in horizontal layout. Maintains in-memory event buffer
    (list[dict], capped at 500). Handles `TrackEvent` → append to buffer,
    register with SessionList, append to TrackPanel (if passes filter).
    Handles `SessionSelected` → clear TrackPanel, replay filtered events
    from buffer.
  - **Files**: `supekku/tui/track.py`

- **P02-T5: ArtifactSnapshot.find_entry()**
  - **Design**: DEC-054-06. Scan `entries` across all ArtifactTypes. Return
    first match by ID, or None. O(n) over total artifacts — acceptable for
    user-initiated navigation.
  - **Files**: `supekku/scripts/lib/core/artifact_view.py`,
    `supekku/scripts/lib/core/artifact_view_test.py`

- **P02-T6: BrowserScreen.navigate_to_artifact()**
  - **Design**: DEC-054-06. Given artifact_id, call
    `snapshot.find_entry(id)`. If found: switch type selector, populate
    list, select matching row in DataTable. If not found: return False
    (caller shows notification).
  - **Files**: `supekku/tui/browser.py`

- **P02-T7: App integration**
  - **Design**: DEC-054-01, DEC-054-05, DEC-054-06. Add `Binding("t",
"toggle_track", "Track")`. `action_toggle_track`: `switch_screen`
    between `"browser"` and `"track"`. `on_mount`: install both screens,
    create EventListener, replay events into TrackScreen, start listener
    task. `action_navigate_artifact(id)`: switch to browser, call
    `browser.navigate_to_artifact(id)`, notify on failure.
  - **Files**: `supekku/tui/app.py`

- **P02-T8: TrackScreen layout CSS**
  - **Design**: DEC-054-01. Horizontal split: SessionList (~20-25 cols) +
    TrackPanel (remaining). Same border/focus styling conventions as
    BrowserScreen (DEC-053-03).
  - **Files**: `supekku/tui/theme.tcss`

- **P02-T9: Tests**
  - **Files**: `supekku/tui/track_test.py`,
    `supekku/scripts/lib/core/artifact_view_test.py` (find_entry addition)
  - **Coverage**: VT-054-05 (session filtering), VT-054-06 (session
    discovery), VT-054-07 (cross-screen navigation / find_entry),
    VT-054-08 (TrackScreen pilot)

- **P02-T10: VH attestation**
  - VH-054-01: Run `uv run spec-driver list specs` (or similar) in one
    terminal while TUI track view is open in another. Verify event appears
    within ~1s.
  - VH-054-02: Start second TUI instance. Verify first keeps receiving
    socket events. Verify second falls back to log-tail and still shows
    events.

## 8. Risks & Mitigations

| Risk                                     | Mitigation                                                     | Status |
| ---------------------------------------- | -------------------------------------------------------------- | ------ |
| DataTable row pruning at cap             | remove_row on oldest; 500-row cap is small                     | open   |
| Screen state across switch_screen        | install_screen preserves mounted state (verified)              | open   |
| TrackEvent delivery to non-active screen | App bridges events to TrackScreen regardless of stack position | open   |

## 9. Decisions & Outcomes

- DEC-054-01 revised: install_screen + push/switch instead of push/pop (state preservation)
- DEC-054-07 revised: DataTable instead of RichLog (row selection for navigation)
- Event buffer lives on TrackScreen, widgets synced on first mount
- Newest-first sort order (user preference, sort by timestamp descending)
- Sequential row keys (`evt-N`) with separate artifact mapping (avoids duplicate key errors)

## 10. Findings / Research Notes

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] VH-054-01 attested — live events appear <200ms in track view
- [x] VH-054-02 attested — second TUI falls back to log-tail, both receive events
- [x] Verification evidence stored
- [ ] Delta ready for `/close-change`
