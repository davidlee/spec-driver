---
id: IP-061.PHASE-03
slug: 061-tui_bundle_file_browser-phase-03
name: Track integration — per-row file paths, preview, navigation, hook fix
created: "2026-03-08"
updated: "2026-03-08"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-061.PHASE-03
plan: IP-061
delta: DE-061
objective: >-
  Wire track mode to bundle file paths: TrackPanel stores per-row file paths
  from event argv, TrackScreen uses them for preview and navigation,
  action_navigate_artifact gains optional file_path parameter,
  artifact_event.py uses hook cwd for deterministic path relativity.
entrance_criteria:
  - Phase 2 complete (browser integration, tree visibility, focus, refresh)
exit_criteria:
  - TrackPanel stores per-row file paths alongside artifact IDs
  - TrackPanel.file_path_for_row() accessor works
  - Row pruning and clear_and_replay clean _row_file_paths
  - TrackScreen row highlight uses file path for preview (with ID fallback)
  - TrackScreen row select navigates with file_path via action_navigate_artifact
  - action_navigate_artifact accepts optional file_path, browser selects file in tree
  - artifact_event.py uses hook_input cwd as relativization base
  - All VT-061-03 tests pass
  - Existing track tests pass (VT-061-05)
  - Lint clean
verification:
  tests:
    - VT-061-03
    - VT-061-05
  evidence: []
tasks:
  - id: "3.1"
    description: "TrackPanel: _row_file_paths storage, file_path_for_row(), pruning"
  - id: "3.2"
    description: "TrackScreen: file-path preview on row highlight (with fallback)"
  - id: "3.3"
    description: "TrackScreen: file-path navigation on row select"
  - id: "3.4"
    description: "app.py: action_navigate_artifact optional file_path parameter"
  - id: "3.5"
    description: "browser.py: navigate_to_artifact optional file_path → tree selection"
  - id: "3.6"
    description: "artifact_event.py: use hook_input cwd for path relativization"
risks:
  - description: Row key cleanup must track two dicts in lockstep
    mitigation: Test pruning and clear_and_replay explicitly
  - description: file_path parameter threading through app → browser → tree
    mitigation: Test end-to-end via pilot test
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-061.PHASE-03
```

# Phase 3 — Track integration

## 1. Objective

Wire track mode file paths through the stack: TrackPanel stores per-row file
paths from event argv, TrackScreen uses them for preview and navigation to
specific bundle files, and artifact_event.py is fixed to use deterministic
cwd-relative paths.

## 2. Links & References

- **Delta**: DE-061
- **Design Revision**: DR-061 §5 (DEC-061-04, DEC-061-06)
- **Phase 2 deliverables**: BrowserScreen with BundleTree, navigate_to_artifact
- **Key files**: `track_panel.py`, `track.py`, `app.py`, `browser.py`, `artifact_event.py`

## 3. Entrance Criteria

- [x] Phase 2 complete

## 4. Exit Criteria / Done When

- [x] `TrackPanel._row_file_paths` stores file paths per row
- [x] `TrackPanel.file_path_for_row()` returns file path for a row key
- [x] Row pruning and `clear_and_replay` clean `_row_file_paths`
- [x] Row highlight previews file path (with artifact ID fallback)
- [x] Row select navigates with `file_path` to specific bundle file
- [x] `action_navigate_artifact` accepts optional `file_path`
- [x] `navigate_to_artifact` selects file in BundleTree when `file_path` given
- [x] `artifact_event.py` uses `hook_input["cwd"]` as relativization base
- [x] Existing track tests pass (regression)
- [x] New tests for above behaviours
- [x] Lint clean

## 5. Verification

- Extend `track_test.py` for file path storage/retrieval/pruning/navigation
- Unit test for `artifact_event.py` cwd fix
- `just test` + `just lint`

## 6. Assumptions & STOP Conditions

- Event `argv[1]` reliably contains the file path (confirmed by existing hook code)
- `_resolve_event_path` helper may need creation or adaptation from existing preview logic
- STOP if `action_navigate_artifact` signature change breaks external callers

## 7. Tasks & Progress

| Status | ID  | Description                                         | Notes                      |
| ------ | --- | --------------------------------------------------- | -------------------------- |
| [x]    | 3.1 | TrackPanel: \_row_file_paths, accessor, pruning     | Done                       |
| [x]    | 3.2 | TrackScreen: file-path preview on highlight         | Done — with ID fallback    |
| [x]    | 3.3 | TrackScreen: file-path navigation on select         | Done                       |
| [x]    | 3.4 | app.py: action_navigate_artifact + file_path        | Done                       |
| [x]    | 3.5 | browser.py: navigate_to_artifact + file_path → tree | Done                       |
| [x]    | 3.6 | artifact_event.py: cwd fix                          | Done — uses hook_input cwd |

### Task Details

- **3.1 — TrackPanel file path storage**
  - **Files**: `widgets/track_panel.py`
  - Add `_row_file_paths: dict[str, str] = {}` alongside `_row_artifacts`
  - `file_path_for_row(row_key_value)` → accessor
  - `append_event`: extract `argv[1]` as file path, store in `_row_file_paths`
  - Pruning: `_row_file_paths.pop(last_key.value, None)` alongside artifact cleanup
  - `clear_and_replay`: `_row_file_paths.clear()` alongside `_row_artifacts.clear()`

- **3.2 — TrackScreen preview with file path**
  - **Files**: `track.py`
  - `_on_event_row_highlighted`: try file path first via `file_path_for_row`,
    resolve against snapshot root, fall back to artifact ID if not found/not file
  - `_update_preview_for_event`: similar — prefer file path from argv

- **3.3 — TrackScreen navigation with file path**
  - **Files**: `track.py`
  - `_on_event_row_selected`: pass `file_path` to `action_navigate_artifact`

- **3.4 — action_navigate_artifact + file_path**
  - **Files**: `app.py`
  - Add `file_path: str | None = None` parameter
  - Pass through to `navigate_to_artifact`

- **3.5 — navigate_to_artifact + tree selection**
  - **Files**: `browser.py`
  - Add `file_path: str | None = None` parameter
  - After row selection, if file_path provided and entry has bundle_dir,
    show tree and call `tree.select_file(resolved_path)`

- **3.6 — artifact_event.py cwd fix**
  - **Files**: `supekku/claude.hooks/artifact_event.py`
  - `build_event`: accept `cwd` kwarg, use as relativization base instead of `Path.cwd()`
  - Caller in `main()`: pass `hook_input["cwd"]` to `build_event`
