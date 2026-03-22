---
id: IP-031-P01
status: completed
kind: phase
plan: IP-031
delta: DE-031
---

# Phase 1: Install `.claude/` settings & hooks

## Objective

Add installer step to copy Claude-specific config (settings.json, hooks) from package source into the target workspace's `.claude/` directory.

## Entry Criteria

- [x] Delta DE-031 accepted and in-progress
- [x] Source files exist: `supekku/claude.settings.json`, `supekku/.claude/hooks/*`
- [x] Installer patterns understood (see `copy_directory_if_changed`, `_install_hooks`)

## Tasks

| #   | Task                                               | Status |
| --- | -------------------------------------------------- | ------ |
| 1.1 | Write tests for `_install_claude_config`           | done   |
| 1.2 | Implement `_install_claude_config` in `install.py` | done   |
| 1.3 | Wire into `initialize_workspace()`                 | done   |
| 1.4 | Verify: `just` passes (tests + lint)               | done   |

## Design Decisions

- **Settings**: installer-owned, overwrite on reinstall (defines hook wiring, must match package)
- **Hooks**: installer-owned, overwrite on reinstall (operational bootstrap, not user-customizable)
- **chmod**: hooks get `+x` after copy
- **workflow.toml gating**: deferred (follow-up)

## Exit Criteria

- [x] `.claude/settings.json` installed from `supekku/claude.settings.json`
- [x] `.claude/hooks/*` installed from `supekku/.claude/hooks/*` with executable bit
- [x] Dry-run reports without writing
- [x] Idempotent on re-run
- [x] VT-031-003 verified (9 tests: 7 unit + 2 integration)
- [x] `just` green (76 install tests pass, pylint 9.56 unchanged)
