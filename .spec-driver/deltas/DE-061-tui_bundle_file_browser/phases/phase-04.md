---
id: IP-061.PHASE-04
slug: 061-tui_bundle_file_browser-phase-04
name: Track mode inline tree — BundleTree in TrackScreen on highlight
created: "2026-03-08"
updated: "2026-03-08"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-061.PHASE-04
plan: IP-061
delta: DE-061
objective: >-
  Add BundleTree to TrackScreen, driven by row highlight. Wrap SessionList +
  BundleTree in Vertical#track-left (mirroring #left-column). Refactor CSS
  to shared .bundle-column class. Parameterise BundleTree tab target. Tree
  shows on highlight for bundle artifacts, clears for non-bundle, refreshes
  on add_event. File selection updates track preview.
entrance_criteria:
  - Phase 3 complete (track file paths, preview, navigation)
exit_criteria:
  - BundleTree tab_target param; action renamed to focus_tab_target (DEC-061-07)
  - CSS refactored to .bundle-column shared class (DEC-061-08)
  - TrackScreen composes Vertical#track-left with SessionList + BundleTree
  - Session-list width rules moved to #track-left container
  - Row highlight shows tree for bundle artifact, hides for non-bundle
  - Skip-if-same optimisation on highlight; repopulate on add_event (DEC-061-09)
  - BundleFileSelected in tree updates #track-preview
  - f binding on TrackScreen to focus tree when visible
  - Tab from tree focuses #track-panel
  - All VT-061-06 tests pass
  - Existing tests pass (VT-061-05)
  - Lint clean
verification:
  tests:
    - VT-061-06
    - VT-061-05
  evidence: []
tasks:
  - id: "4.1"
    description: "BundleTree: tab_target param, rename action (DEC-061-07)"
  - id: "4.2"
    description: "theme.tcss: refactor .bundle-column, add #track-left (DEC-061-08)"
  - id: "4.3"
    description: "browser.py: add bundle-column class to #left-column compose"
  - id: "4.4"
    description: "TrackScreen: compose #track-left with SessionList + BundleTree"
  - id: "4.5"
    description: "TrackScreen: highlight-driven tree show/hide/clear"
  - id: "4.6"
    description: "TrackScreen: skip-if-same + event-driven refresh (DEC-061-09)"
  - id: "4.7"
    description: "TrackScreen: BundleFileSelected handler, f binding, focus model"
  - id: "4.8"
    description: Tests — VT-061-06
risks:
  - description: Layout change may break existing TrackScreen pilot tests
    mitigation: Run full test suite after compose change
  - description: Skip-if-same may miss edge cases beyond create/delete
    mitigation: Event-driven refresh covers the only real mutation source
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-061.PHASE-04
```

# Phase 4 — Track mode inline tree

## 1. Objective

Add BundleTree to TrackScreen, driven by row highlight (no Enter required).
Mirror BrowserScreen's left-column pattern. Refactor CSS to share
`.bundle-column` rules between both screens. Parameterise BundleTree's Tab
target so it works on both screens.

## 2. Links & References

- **Delta**: DE-061
- **Design Revision**: DR-061 §5 (DEC-061-07, DEC-061-08, DEC-061-09)
- **Phase 3 deliverables**: TrackPanel file paths, TrackScreen preview/navigation
- **Key files**: `bundle_tree.py`, `track.py`, `browser.py`, `theme.tcss`, `track_test.py`

## 3. Entrance Criteria

- [x] Phase 3 complete

## 4. Exit Criteria / Done When

- [x] BundleTree accepts `tab_target` param; action renamed
- [x] CSS uses `.bundle-column` shared class for both screens
- [x] `#track-left` wraps SessionList + BundleTree
- [x] `#session-list` width rules moved to `#track-left`
- [x] Row highlight → tree show/hide based on `entry.bundle_dir`
- [x] Skip-if-same on highlight; repopulate on `add_event` when bundle matches
- [x] `BundleFileSelected` → `#track-preview` update
- [x] `f` focuses tree when visible
- [x] Tab from tree focuses `#track-panel`
- [x] Existing TrackScreen tests pass (regression)
- [x] New VT-061-06 tests pass
- [x] Lint clean

## 5. Verification

- Extend `track_test.py` with VT-061-06 tests
- `just test` + `just lint`

## 6. Assumptions & STOP Conditions

- Textual screen-scoped `query_one` isolates the two `#bundle-tree` instances
- `SessionList` message bubbling unaffected by Vertical wrapper
- STOP if layout container changes break existing TrackScreen tests fundamentally

## 7. Tasks & Progress

| Status | ID  | Description                                         | Notes                           |
| ------ | --- | --------------------------------------------------- | ------------------------------- |
| [x]    | 4.1 | BundleTree: tab_target param, rename action         | DEC-061-07                      |
| [x]    | 4.2 | theme.tcss: .bundle-column refactor, #track-left    | DEC-061-08                      |
| [x]    | 4.3 | browser.py: add bundle-column class to #left-column | Minimal — one kwarg             |
| [x]    | 4.4 | TrackScreen: compose #track-left + BundleTree       | Layout change                   |
| [x]    | 4.5 | TrackScreen: highlight-driven tree show/hide        | Wire \_on_event_row_highlighted |
| [x]    | 4.6 | TrackScreen: skip-if-same + event refresh           | DEC-061-09                      |
| [x]    | 4.7 | TrackScreen: BundleFileSelected, f binding, Tab     | Focus model                     |
| [x]    | 4.8 | Tests — VT-061-06                                   | 8 pilot tests, all passing      |

### Task Details

- **4.1 — BundleTree tab_target**
  - **Files**: `widgets/bundle_tree.py`
  - Add `tab_target: str = "#artifact-table"` constructor param
  - Rename `BINDINGS` action to `focus_tab_target`
  - Rename method to `action_focus_tab_target`
  - Use `self._tab_target` in action body
  - Update existing browser_bundle_test.py if it references the action name

- **4.2 — CSS refactor**
  - **Files**: `theme.tcss`
  - Replace `#left-column.has-bundle` selectors with `.bundle-column.has-bundle`
  - Combine `#type-selector` and `#session-list` height override in one rule
  - Add `#track-left` sizing rules (width: 1fr, min-width: 20, max-width: 25, height: 100%)
  - Move width/min-width/max-width from `#session-list` to `#track-left`
  - Keep `#session-list` chrome (border, background, padding, height: 100%)

- **4.3 — browser.py bundle-column class**
  - **Files**: `browser.py`
  - `Vertical(id="left-column", classes="bundle-column")` in compose

- **4.4 — TrackScreen layout**
  - **Files**: `track.py`
  - Import BundleTree
  - `compose()`: wrap SessionList + BundleTree in `Vertical(id="track-left", classes="bundle-column")`
  - BundleTree gets `tab_target="#track-panel"`
  - `on_mount`: set `#session-list` border title (unchanged)

- **4.5 — Highlight-driven tree**
  - **Files**: `track.py`
  - In `_on_event_row_highlighted`: resolve artifact entry via snapshot
  - If `entry.bundle_dir` and different from `tree.bundle_dir`: `show_bundle` + add `.has-bundle`
  - If `entry.bundle_dir` and same: `select_file` for the specific file path
  - If no bundle: `clear_bundle` + remove `.has-bundle`

- **4.6 — Skip-if-same + event refresh**
  - **Files**: `track.py`
  - In `add_event`: after existing logic, check if new event touches the
    currently displayed bundle. If so, repopulate tree.

- **4.7 — Focus model**
  - **Files**: `track.py`
  - `BundleFileSelected` handler: update `#track-preview`
  - `Binding("f", "focus_files")` on TrackScreen
  - `action_focus_files`: focus tree if visible

- **4.8 — Tests**
  - **Files**: `track_test.py`
  - TrackScreen composes BundleTree in #track-left
  - Highlight bundle event row → tree visible with correct files
  - Highlight non-bundle event row → tree hidden
  - Same-bundle highlight skips repopulation (mock show_bundle call count)
  - add_event with matching bundle → tree repopulated
  - BundleFileSelected → preview updated
  - f focuses tree when visible
  - Tab from tree focuses #track-panel
  - Existing tests still pass
