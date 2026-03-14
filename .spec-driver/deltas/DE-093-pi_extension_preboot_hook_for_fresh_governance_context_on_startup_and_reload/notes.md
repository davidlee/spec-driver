# Notes for DE-093

## Implementation Notes (2026-03-14)

### What's done

**preboot.py** — dual output

- `write_preboot_file()` now writes to both `.agents/spec-driver-boot.md` (Claude Code)
  and `.pi/APPEND_SYSTEM.md` (pi auto-discovery)
- Extracted `_write_if_changed()` helper; content-diffing on both outputs
- Docstring updated to reference both agents and DE-093

**pi extension** — `supekku/pi.extensions/spec-driver-preboot.ts`

- ~10 LOC; hooks `session_shutdown` → runs `spec-driver admin preboot ctx.cwd`
- Source lives in `supekku/pi.extensions/` (package source), installed to `.pi/extensions/` by `spec-driver install`

**install.py** — pi config installer

- `_install_pi_config()` copies `supekku/pi.extensions/*` → `.pi/extensions/`
- Installer-owned, overwritten on every install (same semantics as claude.hooks)
- Wired into `initialize_workspace()` alongside `_install_claude_config()`

**pyproject.toml** — wheel packaging

- `force-include` for `supekku/pi.extensions` (no .py files, wouldn't be picked up otherwise)

**flake.nix** — Nix wrapper (belt)

- `jailed-pi` and `jailed-pi-research` wrapped with host-side preboot before jail entry
- Fixed name collision (raw + wrapper both producing `bin/jailed-pi`)
- Fixed `lib.getExe` warning → `lib.getExe'` + `meta.mainProgram`

**.gitignore** — `.pi/APPEND_SYSTEM.md` (generated)

**preboot_test.py** — 3 new tests for pi output (existence, parity, skip-when-unchanged)

**memories** — 2 captured

- `mem.fact.pi.append-system-md-discovery` — `.pi/APPEND_SYSTEM.md` auto-discovery
- `mem.fact.pi.session-shutdown-hook-timing` — `/reload` event ordering

### Surprises / adaptations

- pi doesn't resolve `@` includes in AGENTS.md — Claude Code syntax is literal text to pi.
  Used `.pi/APPEND_SYSTEM.md` (pi-native auto-discovery) instead.
- `APPEND_SYSTEM.md` discovery is undocumented in pi README; found in `resource-loader.js`.
- System prompt survives compaction (only messages replaced) — preboot content persists
  without per-turn re-injection.
- `hatch` includes non-.py files under the package dir if .py files are present in the
  same dir, but `pi.extensions/` has only `.ts` — needed `force-include`.

### Commits

- `c9b6561` — feat(DE-093): preboot hook for pi — belt and suspenders
- `0c16582` — fix(DE-093): resolve jailed-pi name collision and getExe warning
- `6132f94` — mem(DE-093): pi APPEND_SYSTEM.md discovery and session_shutdown hook timing
- `8304e69` — feat(DE-093): install pi extensions via spec-driver install
- `f89f6e5` — feat(DE-093): add \_install_pi_config tests and .pi/APPEND_SYSTEM.md gitignore entry

### Verification

- Nix flake builds successfully after collision fix
- pi confirmed loading preboot governance context (ADRs, policies, standards) into system prompt
- Tests not yet run against source (installed spec-driver is Nix-built, doesn't reflect changes)
- User to test `spec-driver install` in a fresh session

### Rough edges / follow-ups

- ~~No test for `_install_pi_config()` in install_test.py yet~~ — **done** (`f89f6e5`):
  `TestInstallPiConfig` (6 unit tests) + `TestInitializeWorkspacePiConfig` (2 integration tests)
- ~~`.pi/APPEND_SYSTEM.md` should probably also be in a default `.gitignore` entry~~ —
  **done** (`f89f6e5`): `_ensure_gitignore_entry(target_root, ".pi/APPEND_SYSTEM.md")`
  added to `initialize_workspace()`, with 2 tests (`TestInitializeWorkspaceGitignorePiAppend`)
- No test for the `.ts` file being included in the wheel build
- The `artifact_event.py` equivalent for pi (tool-call observation via RPC events)
  is deferred to future work (DE-092 or successor)
