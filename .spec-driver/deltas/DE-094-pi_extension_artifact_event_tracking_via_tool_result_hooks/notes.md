# Notes for DE-094

## Implementation Notes (2026-03-14)

### What's done

**spec-driver-artifact-events.ts** — pi extension (~100 LOC)
- Hooks `tool_result` for read/edit/write tools
- `classifyPath()` — same 12 artifact patterns as `_ARTIFACT_PATTERNS` in Python
- `buildEvent()` — v1 event schema, identical fields to Python hook
- `writeLog()` — JSONL append to `.spec-driver/run/events.jsonl`
- `SYNC:` comments cross-referencing `artifact_event.py`

**No Unix socket** — Node.js `dgram` doesn't support `AF_UNIX` datagram sockets.
TUI falls back to log-tail mode automatically (watchfiles on `events.jsonl`).
This is sufficient — socket is a latency optimisation, not required.

**spec-driver-artifact-events.test.ts** — 29 tests
- Classification: all 13 artifact types + priority ordering (phase > delta, DR > delta)
- Non-artifact paths: 7 cases returning null
- Event schema: 5 tests (v1 fields, actions, relativization, no-id case)
- JSONL write: 2 tests (append semantics, recursive dir creation)
- Run via `node --experimental-strip-types`

**install.py** — test file exclusion
- `_collect_pi_sources()` now filters out `.test.` files
- Prevents test files from being installed to `.pi/extensions/`

### Surprises / adaptations
- Node.js `dgram` only supports `udp4`/`udp6`, not Unix domain sockets.
  Python's `socket.AF_UNIX, socket.SOCK_DGRAM` has no Node equivalent.
  Dropped socket emission; TUI log-tail fallback is automatic and sufficient.
- `import type` from `@mariozechner/pi-coding-agent` is stripped by Node's
  `--experimental-strip-types`, so tests run without the pi package installed.

### Commits
- `7e6c263` — feat(DE-094): pi artifact event extension + tests, exclude test files from install

### Verification
- 29 TS tests pass (classification, schema, JSONL write)
- 103 Python install tests pass (no regressions)
- 35 Python artifact_event tests pass
- Lint clean (ruff)
- Install pipeline correctly picks up new extension, excludes test file
