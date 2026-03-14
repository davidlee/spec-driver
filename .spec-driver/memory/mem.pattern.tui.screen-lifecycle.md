---
id: mem.pattern.tui.screen-lifecycle
name: "TUI screen lifecycle: install + push/switch"
kind: memory
status: active
memory_type: pattern
created: "2026-03-08"
updated: "2026-03-08"
tags:
  - tui
  - textual
  - screens
summary:
  "Screen lifecycle: install_screen + push/switch, not push/pop for persistent
  screens"
scope:
  globs:
    - supekku/tui/**
links:
  missing:
    - raw: DEC-054-01
---

# TUI screen lifecycle: install + push/switch

## Pattern

For screens that must **preserve state** across toggles (e.g. BrowserScreen ↔ TrackScreen):

1. `install_screen(screen, name="foo")` at mount time — registers without displaying
2. `push_screen("foo")` for the **initial** screen only
3. `switch_screen("bar")` to toggle — replaces top of stack, both stay mounted

**Do NOT** use `switch_screen` for the very first screen. Textual's default
blank screen has an empty `_result_callbacks` stack; `switch_screen` calls
`_pop_result_callback` on it → `IndexError`.

**Do NOT** use `push_screen`/`pop_screen` for toggling persistent screens.
`pop_screen` unmounts the screen — widget tree destroyed, scroll position
lost, event buffer gone. The screen must be rebuilt from scratch on re-push.

## Key files

- `supekku/tui/app.py` — `on_mount()` installs both, pushes browser
- [[DEC-054-01]] — design decision and rationale

## Verified

2026-03-08 — DE-054 Phase 2. Confirmed `push_screen` initial + `switch_screen`
toggle works; `switch_screen` initial crashes.
