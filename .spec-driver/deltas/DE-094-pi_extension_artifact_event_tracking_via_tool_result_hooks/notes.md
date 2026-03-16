# Notes for DE-094

## Implementation Notes (2026-03-16)

### What's done

**spec-driver-artifact-events.ts** — pi extension (~120 LOC)

- Hooks `tool_result` for read/edit/write tools
- Hooks `session_start` to set `SPEC_DRIVER_SESSION` env var (propagates
  session ID to CLI calls via bash tool — mirrors Claude Code `startup.sh`)
- `classifyPath()` — same 12 artifact patterns as `_ARTIFACT_PATTERNS` in Python
- `buildEvent()` — v1 event schema with session ID from `ctx.sessionManager`
- `writeLog()` — JSONL append to `.spec-driver/run/events.jsonl`
- `sendSocket()` — `spawnSync("python3", ...)` for AF_UNIX SOCK_DGRAM to `tui.sock`
- `SYNC:` comments cross-referencing `artifact_event.py`

**spec-driver-artifact-events.test.ts** — 31 tests

- Classification: all 13 artifact types + priority ordering (phase > delta, DR > delta)
- Non-artifact paths: 7 cases returning null
- Event schema: 6 tests (v1 fields, actions, relativization, no-id case, sessionId)
- JSONL write: 2 tests (append semantics, recursive dir creation)
- Run via `node --experimental-strip-types`

**install.py** — test file exclusion

- `_collect_pi_sources()` now filters out `.test.` files
- Prevents test files from being installed to `.pi/extensions/`

### Surprises / adaptations

- Node.js `dgram` only supports `udp4`/`udp6`, not Unix domain sockets.
  Initially solved by `pi.exec("python3", ...)` (async fire-and-forget).
- `pi.exec` socket sends didn't reach the socket-owning TUI — async
  fire-and-forget was unreliable. Replaced with `spawnSync("python3", ...)`
  for synchronous delivery matching the Python hook's in-process `sendto()`.
- `python3` must be on PATH inside bubblewrap jails — added to `projectPkgs`
  in `flake.nix`.
- Session ID available via `ctx.sessionManager.getSessionId()` — wired into
  `buildEvent()` for TS extension events and propagated via env var for CLI.
- `import type` from `@mariozechner/pi-coding-agent` is stripped by Node's
  `--experimental-strip-types`, so tests run without the pi package installed.

### Commits

- `7e6c263` — feat(DE-094): pi artifact event extension + tests, exclude test files from install
- `f4a3173` — feat(DE-094): restore socket emission via pi.exec python3 dgram
- `e85f4bfc` — fix(DE-094): add python3 to jail extraPkgs for unix socket send
- `8b5ba965` — fix(DE-094): replace pi.exec with spawnSync for socket send reliability
- `806ee5f0` — fix(DE-094): add session ID from ctx.sessionManager, update docs
- `dba1c8e6` — fix(DE-094): set SPEC_DRIVER_SESSION env var on session_start for CLI events

### Verification

- 31 TS tests pass (classification, schema, JSONL write, sessionId)
- 103 Python install tests pass (no regressions)
- 35 Python artifact_event tests pass
- Lint clean (ruff)
- Install pipeline correctly picks up new extension, excludes test file
- **Live TUI verification**: JSONL events, socket datagrams, and session IDs
  all confirmed working in both socket-owning and polling TUI instances

### Rough edges / follow-ups

- No test for the `.ts` file being included in the wheel build
- `artifact_event.py` equivalent for pi (tool-call observation via RPC events)
  is deferred to future work (DE-092 or successor)
