---
id: mem.system.tui.architecture
name: "TUI app architecture: screens, widgets, listener, watcher"
kind: memory
status: active
memory_type: system
created: "2026-03-08"
updated: "2026-03-08"
tags:
  - tui
  - textual
  - architecture
summary:
  How SpecDriverApp composes screens, EventListener, file watcher, and test
  harness
scope:
  globs:
    - supekku/tui/**
links:
  missing:
    - raw: DEC-053-14
    - raw: DEC-054-01
---

# TUI app architecture: screens, widgets, listener, watcher

## Component map

```
SpecDriverApp (supekku/tui/app.py)
├── BrowserScreen (browser.py)         — 3-panel artifact browser
│   ├── TypeSelector (widgets/type_selector.py)   — OptionList, ArtifactType
│   ├── ArtifactList (widgets/artifact_list.py)    — DataTable + search + status filter
│   ├── PreviewPanel (widgets/preview_panel.py)    — markdown/non-md preview
│   └── BundleTree (widgets/bundle_tree.py)        — Tree widget for bundle dirs
├── TrackScreen (track.py)             — 2-panel live event view
│   ├── SessionList (widgets/session_list.py)      — OptionList, session filter
│   └── TrackPanel (widgets/track_panel.py)        — DataTable, event rows
├── EventListener (event_listener.py)  — socket or log-tail, posts TrackEvent
├── file watcher (asyncio.Task)        — watchfiles, refreshes registries
└── theme.tcss                         — layout CSS for both screens
```

## Data flow

- **Events**: CLI → `.spec-driver/run/events.jsonl` + `tui.sock` → EventListener → `TrackEvent` message → App.on_track_event → TrackScreen.add_event
- **Artifacts**: registries → ArtifactSnapshot (with bundle_dir detection) → BrowserScreen widgets
- **Navigation**: TrackPanel row select → TrackScreen → App.action_navigate_artifact → switch to browser + BrowserScreen.navigate_to_artifact
- **File watch**: watchfiles → App.\_watch_files → BrowserScreen.refresh_snapshot

## Test harness

- `_make_app(snapshot, listen=False)` — mock snapshot, no listener
- `app.run_test(size=(120, 40))` — Textual pilot for headless testing
- `action_toggle_track()` — switch screens in tests
- Mock snapshot: `MagicMock(spec=ArtifactSnapshot)` with `.entries`, `.counts_by_type`, `.all_entries`, `.find_entry`

## Key constructor params

- `watch=True` — file watcher (disable in tests if not testing watch)
- `listen=True` — event listener (disable with `listen=False` in tests)

## See also

- [[mem.pattern.tui.screen-lifecycle]] — install/switch pattern
- [[DEC-053-14]], [[DEC-054-01]] — screen design decisions
