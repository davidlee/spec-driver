# Notes for DE-054

## Phase 1 — EventListener infrastructure

- Made event constants public in `events.py` (`LOG_FILENAME`, `SOCKET_FILENAME`,
  etc.) so the listener can import them — single source of truth for paths.
- `_drain_from_offset()` is shared between log-tail mode and bootstrap drain.
- `TrackEvent` message class defined in `event_listener.py` (single consumer).
- Socket probe sends `{"v":0}` — listener discards v:0 events as probes.
- 24 unit tests covering replay, protocol, probe (live/stale/absent), drain,
  and EventListener lifecycle (bind, receive, stop/cleanup).
- `ruff format` auto-reformatted the `awatch()` call in `_tail_log` — the
  formatter-applied line break is intentional, not a manual edit.

### Design notes for Phase 2

- `EventListener.get_replay_events()` returns `list[dict]` and records the
  file offset internally. Call it _before_ `start()` — the bootstrap drain
  in `start()` reads from that offset forward.
- `EventListener.start(app)` posts `TrackEvent` messages to the app. The app
  must bridge these to the active TrackScreen (events arrive at the app level,
  not the screen level, because the listener is owned by the app).
- The listener's `stop()` is async — must be awaited. It handles transport
  close, task cancel, and socket unlink (if owned).
- `DISPLAY_BUFFER_LIMIT = 500` is exported from `event_listener.py` for the
  TrackScreen's in-memory buffer cap.

## Phase 2 — TrackScreen and app integration

### What's done

- **T1**: 13 `track.*` style keys in `SPEC_DRIVER_THEME` (theme.py)
- **T2**: `TrackPanel(DataTable)` — cursor_type="row", 5 columns, styled
  cells, row pruning at 500, artifact-to-row mapping via `_row_artifacts`
  dict (row keys are sequential `evt-N` to avoid duplicate key errors)
- **T3**: `SessionList(OptionList)` — discovers sessions from events,
  sorted by recency, colour via md5 hash, "All sessions" option,
  posts `SessionSelected` message
- **T4**: `TrackScreen(Screen)` — 2-panel compose, event buffer (capped 500),
  session filter, wires DataTable.RowSelected → navigate
- **T5**: `ArtifactSnapshot.find_entry()` — dict key lookup across all types,
  skips error entries. 4 tests.
- **T6**: `BrowserScreen.navigate_to_artifact()` — uses `find_entry()`,
  `get_option_index()` for type switch, `move_cursor()` for row selection
- **T7**: App integration — `install_screen` + `push_screen("browser")` for
  initial screen, `switch_screen` for toggle. Listener lifecycle via
  `_start_listener` async task. `on_track_event` bridges to TrackScreen.
  `action_navigate_artifact` switches to browser + navigates. `listen=False`
  constructor param for tests.
- **T8**: TrackScreen CSS — horizontal layout, session-list 20-25col,
  track-panel 4fr, same border/focus conventions as BrowserScreen
- **T9**: 20 track tests + 4 find_entry tests. All VTs passing.

### Surprises / adaptations

- **DEC-054-07 revised**: DataTable instead of RichLog. RichLog has no
  per-line selection, making click-to-navigate impossible without a custom
  cursor. DataTable gives row selection for free. DR updated.
- **DEC-054-01 revised**: `install_screen` + `switch_screen` instead of
  push/pop. Push/pop destroys TrackScreen widget tree on pop, losing state.
  DR updated. Initial screen uses `push_screen` (not `switch_screen`)
  because `switch_screen` on the default blank screen triggers an IndexError
  in Textual's `_pop_result_callback`.
- **Row key uniqueness**: Multiple events can reference the same artifact
  (e.g. two commands touching DE-052). DataTable requires unique row keys.
  Solved with sequential `evt-N` keys and a separate `_row_artifacts` dict
  mapping row key → artifact ID.
- **pylint too-many-instance-attributes (9/7)** on SpecDriverApp: inherent
  to app being the integration point for browser, track, watcher, and
  listener. Pre-existing pattern, not worth extracting.

### Rough edges / follow-ups

- `_ACTIVE_THRESHOLD_SECONDS` (10min active/recent distinction per
  DEC-054-04) removed to keep lint clean — not yet used. Add when
  active/recent visual distinction is implemented.
- No dedup between socket events and drain events (accepted in DEC-054-03).
- Session list rebuilds fully on every event — fine at spec-driver's
  command frequency, would need throttling for high-throughput.

### Verification

- `just` green: 2949 passed, 3 skipped
- ruff: zero warnings
- pylint on edited files: 9.70+ (all messages pre-existing)
- Uncommitted work
