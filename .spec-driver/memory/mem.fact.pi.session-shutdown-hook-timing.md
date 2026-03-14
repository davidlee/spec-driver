---
id: mem.fact.pi.session-shutdown-hook-timing
name: pi session_shutdown fires before /reload resource re-read
kind: memory
status: active
memory_type: fact
created: "2026-03-14"
updated: "2026-03-14"
verified: "2026-03-14"
confidence: high
tags:
  - pi
  - extension
  - hooks
  - reload
summary:
  session_shutdown is awaited before resourceLoader.reload() — the correct
  hook for pre-reload file generation
scope:
  globs:
    - .pi/extensions/**
provenance:
  sources:
    - "@mariozechner/pi-coding-agent/dist/core/agent-session.js (reload method, lines 1784-1801)"
    - DE-093
---

# pi session_shutdown fires before /reload resource re-read

pi's `/reload` sequence in `AgentSession.reload()`:

1. `await extensionRunner.emit({ type: "session_shutdown" })` — **awaited**
2. `settingsManager.reload()`
3. `await resourceLoader.reload()` — re-reads AGENTS.md, APPEND_SYSTEM.md, skills, etc.
4. `_buildRuntime()` — rebuilds tools and system prompt
5. `await extensionRunner.emit({ type: "session_start" })`

**Consequence:** to regenerate a file before pi re-reads it on `/reload`, hook `session_shutdown`, not `session_start`. `session_start` fires after the re-read — too late.

**Gotcha:** `session_shutdown` also fires on actual process exit. Any hook must be idempotent and fast. spec-driver preboot (~100ms) is both.

Used by `.pi/extensions/spec-driver-preboot.ts` ([[DE-093]]).
