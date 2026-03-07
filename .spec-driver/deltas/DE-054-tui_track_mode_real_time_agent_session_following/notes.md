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
  file offset internally. Call it *before* `start()` — the bootstrap drain
  in `start()` reads from that offset forward.
- `EventListener.start(app)` posts `TrackEvent` messages to the app. The app
  must bridge these to the active TrackScreen (events arrive at the app level,
  not the screen level, because the listener is owned by the app).
- The listener's `stop()` is async — must be awaited. It handles transport
  close, task cancel, and socket unlink (if owned).
- `DISPLAY_BUFFER_LIMIT = 500` is exported from `event_listener.py` for the
  TrackScreen's in-memory buffer cap.

