# Notes for DE-093

## Implementation Notes (2026-03-14)

### What's done
- `preboot.py`: extended `write_preboot_file()` to dual-output
  - `.agents/spec-driver-boot.md` (Claude Code, existing)
  - `.pi/APPEND_SYSTEM.md` (pi, new — auto-discovered by pi as append-system-prompt)
  - Extracted `_write_if_changed()` helper; both outputs use content-diffing
- `.pi/extensions/spec-driver-preboot.ts`: hooks `session_shutdown` → runs `spec-driver admin preboot ctx.cwd`
- `flake.nix`: wraps `jailed-pi` and `jailed-pi-research` with host-side preboot before jail entry
- `.gitignore`: added `.pi/APPEND_SYSTEM.md` (generated file)
- `preboot_test.py`: 3 new tests for pi output (existence, parity, skip-when-unchanged)

### Key discovery: pi doesn't resolve `@` includes in AGENTS.md
The root `AGENTS.md` uses Claude Code `@path` syntax, which pi reads as literal text.
Used `.pi/APPEND_SYSTEM.md` (pi's native auto-discovery for appended system prompt)
instead of trying to modify AGENTS.md. This cleanly separates the two agents' context paths.

### Key discovery: `session_shutdown` is the correct hook for `/reload` freshness
pi's reload sequence: `session_shutdown` (awaited) → `resourceLoader.reload()` → `session_start`.
The extension must hook `session_shutdown` not `session_start` to ensure preboot runs
before AGENTS.md is re-read. Verified from pi source (`agent-session.js` lines 1784-1801).

### Surprises / adaptations
- pi's `APPEND_SYSTEM.md` discovery was not documented in README — found by reading
  `resource-loader.js` source. Looks for `.pi/APPEND_SYSTEM.md` (project) or
  `~/.pi/agent/APPEND_SYSTEM.md` (global).
- System prompt survives compaction (only messages are replaced) — so preboot content
  stays in context without needing per-turn re-injection.

### Commits
- `c9b6561` — feat(DE-093): preboot hook for pi — belt and suspenders

### Verification
- Tests not yet run (installed spec-driver is Nix-built, doesn't reflect source changes).
  User will test in a new session.

### Follow-ups
- Consider a memory for the `APPEND_SYSTEM.md` discovery path and the
  `session_shutdown` hook timing — both are non-obvious and would save future agents time.
- The preboot docstring now references DE-093 alongside DE-091 for traceability.
