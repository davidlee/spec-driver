---
id: IP-054.PHASE-01
slug: 054-tui_track_mode_real_time_agent_session_following-phase-01
name: IP-054 Phase 01 — EventListener infrastructure
created: '2026-03-07'
updated: '2026-03-07'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-054.PHASE-01
plan: IP-054
delta: DE-054
objective: >-
  Implement the EventListener abstraction: socket probe, bind/log-tail mode
  selection, JSONL replay with bounded read, bootstrap drain sequence, and
  TrackEvent message posting. Fully testable without Textual widgets.
entrance_criteria:
  - DR-054 reviewed and findings incorporated
  - DE-052 completed (events.py emitter exists)
  - DE-053 completed (watchfiles is a dependency)
exit_criteria:
  - event_listener.py passes VT-054-01 through VT-054-04
  - just passes (lint + test)
verification:
  tests:
    - VT-054-01
    - VT-054-02
    - VT-054-03
    - VT-054-04
  evidence: []
tasks:
  - id: P01-T1
    description: JSONL replay — read last N lines, parse, skip malformed
  - id: P01-T2
    description: Socket probe — detect live/stale/absent socket
  - id: P01-T3
    description: Socket-mode listener — pre-bound SOCK_DGRAM, asyncio protocol, TrackEvent posting
  - id: P01-T4
    description: Log-tail-mode listener — directory watch, offset tracking, line parsing
  - id: P01-T5
    description: Bootstrap drain — record offset at replay EOF, drain after listener start
  - id: P01-T6
    description: EventListener public API — start/stop/replay_events, mode selection
  - id: P01-T7
    description: Tests for VT-054-01 through VT-054-04
risks:
  - description: macOS socket probe errno may differ
    mitigation: Defensive fallback to log-tail on unexpected OSError
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-054.PHASE-01
```

# Phase 1 — EventListener infrastructure

## 1. Objective

Implement `supekku/tui/event_listener.py` — the async event listener that
bridges DE-052's event emission to the TUI. Supports two transport modes
(socket, log-tail) behind a uniform interface, with JSONL replay on startup
and a bootstrap drain to close the replay-to-live gap.

This phase produces no visible UI changes — it delivers the plumbing that
Phase 2's TrackScreen consumes.

## 2. Links & References

- **Delta**: DE-054
- **Design Revision Sections**: DEC-054-02 (socket probe/fallback),
  DEC-054-03 (replay), DEC-054-05 (EventListener abstraction)
- **Implementation Reference**: `supekku/scripts/lib/core/events.py`
  (emitter — the other end of the socket)

## 3. Entrance Criteria

- [x] DR-054 reviewed (adversarial, all findings incorporated)
- [x] DE-052 completed (events.py, socket emitter)
- [x] DE-053 completed (watchfiles dependency available)

## 4. Exit Criteria / Done When

- [ ] `event_listener.py` implements: replay, probe, socket-mode, log-tail-mode,
      bootstrap drain, start/stop lifecycle
- [ ] `event_listener_test.py` covers VT-054-01 through VT-054-04
- [ ] `just` green (lint + test)

## 5. Verification

- `just test` — unit tests for replay, probe, socket, log-tail
- `just lint` + `just pylint` — zero warnings on new files
- VT-054-01: Replay parses JSONL, respects N-line bound, skips malformed,
  handles missing/empty file
- VT-054-02: Socket listener receives datagrams, posts TrackEvent, discards
  probes (v:0), handles malformed JSON
- VT-054-03: Probe detects live (sendto succeeds), stale (ECONNREFUSED),
  absent (FileNotFoundError)
- VT-054-04: Log-tail detects appended lines via directory watch, parses
  events, skips malformed

## 6. Assumptions & STOP Conditions

- Assumptions:
  - `asyncio.get_running_loop()` is available when called from Textual
    app context (confirmed by existing `asyncio.create_task` usage in app.py)
  - `watchfiles.awatch` on the run directory detects `events.jsonl` appends
    within ~300ms (observed on Linux)
  - Event volume is low enough that synchronous file read for replay is fine
- STOP when:
  - `create_datagram_endpoint(sock=...)` doesn't work as expected in Textual's
    loop — escalate to `/consult`
  - `watchfiles` directory watch misses appended lines on the target platform

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID     | Description              | Parallel? | Notes                             |
| ------ | ------ | ------------------------ | --------- | --------------------------------- |
| [x]    | P01-T1 | JSONL replay             | [P]       | Pure function, no async           |
| [x]    | P01-T2 | Socket probe             | [P]       | Pure function, no async           |
| [x]    | P01-T3 | Socket-mode listener     |           | Pre-bound sock= approach works    |
| [x]    | P01-T4 | Log-tail-mode listener   | [P]       | Directory watch + offset tracking |
| [x]    | P01-T5 | Bootstrap drain          |           | \_drain_from_offset reused by T4  |
| [x]    | P01-T6 | EventListener public API |           | Composes T1-T5                    |
| [x]    | P01-T7 | Tests VT-054-01..04      |           | 24 tests, all passing             |

### Task Details

- **P01-T1: JSONL replay**
  - **Design**: DEC-054-03. Read file, split newlines, take last 200 lines.
    Parse each as JSON, skip malformed. Record file offset at EOF for
    bootstrap drain (T5). Return `list[dict]`.
  - **Files**: `supekku/tui/event_listener.py`
  - **Testing**: VT-054-01 — valid JSONL, malformed lines, empty file,
    missing file, >200 lines (verify bound)

- **P01-T2: Socket probe**
  - **Design**: DEC-054-02. `_probe_socket(path) -> bool`. sendto `{"v":0}`
    to test socket. `True` = live (sendto succeeds). `False` = stale
    (ECONNREFUSED) or absent (FileNotFoundError). `True` on other OSError
    (defensive).
  - **Files**: `supekku/tui/event_listener.py`
  - **Testing**: VT-054-03 — three states (live, stale, absent)

- **P01-T3: Socket-mode listener**
  - **Design**: DEC-054-05. Pre-bind `AF_UNIX`/`SOCK_DGRAM` socket. Register
    with `loop.create_datagram_endpoint(protocol, sock=sock)`.
    `_EventProtocol.datagram_received` parses JSON, discards `v:0` probes,
    posts `TrackEvent` to app. Cleanup: close transport, unlink socket file.
  - **Files**: `supekku/tui/event_listener.py`
  - **Testing**: VT-054-02 — receive valid event, receive malformed JSON,
    receive probe (discarded), transport cleanup

- **P01-T4: Log-tail-mode listener**
  - **Design**: DEC-054-02/05. `watchfiles.awatch(.spec-driver/run/)` filtered
    to `events.jsonl`. On change, seek to last-known offset, read new lines,
    parse, post `TrackEvent`. Track offset via `file.tell()`.
  - **Files**: `supekku/tui/event_listener.py`
  - **Testing**: VT-054-04 — append lines to temp file, verify events posted,
    verify malformed lines skipped

- **P01-T5: Bootstrap drain**
  - **Design**: DEC-054-03 bootstrap sequence. After listener starts, read
    from replay's recorded offset to current EOF. Parse and post any events
    emitted during the gap. Then hand off to live mode.
  - **Files**: `supekku/tui/event_listener.py`
  - **Testing**: Part of VT-054-01 (replay returns offset) and VT-054-04
    (drain reads from offset)

- **P01-T6: EventListener public API**
  - **Design**: DEC-054-05. `replay_events() -> list[dict]`,
    `start(app) -> None`, `stop() -> None`. Constructor takes `run_dir: Path`.
    `start()` probes socket, selects mode, runs bootstrap drain.
  - **Files**: `supekku/tui/event_listener.py`
  - **Testing**: Integration-level: replay + start + event posting verified
    end-to-end

- **P01-T7: Tests**
  - **Files**: `supekku/tui/event_listener_test.py`
  - **Coverage**: VT-054-01 through VT-054-04

## 8. Risks & Mitigations

| Risk                                             | Mitigation                                                 | Status |
| ------------------------------------------------ | ---------------------------------------------------------- | ------ |
| macOS socket probe errno                         | Defensive OSError fallback to log-tail                     | open   |
| `create_datagram_endpoint` with pre-bound socket | Verified approach in DR-054; STOP if it fails              | open   |
| watchfiles misses appends to events.jsonl        | Watch directory not file; verified ~300ms latency on Linux | open   |

## 9. Decisions & Outcomes

## 10. Findings / Research Notes

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied — 24 tests passing, `just` green (2925 passed)
- [x] Verification evidence: VT-054-01..04 covered by event_listener_test.py
- [x] Hand-off to Phase 2: EventListener ready for app integration
