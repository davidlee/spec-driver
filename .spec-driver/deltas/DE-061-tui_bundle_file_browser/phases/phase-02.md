---
id: IP-061.PHASE-02
slug: 061-tui_bundle_file_browser-phase-02
name: Browser integration — layout, wiring, visibility, focus, CSS
created: '2026-03-08'
updated: '2026-03-08'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-061.PHASE-02
plan: IP-061
delta: DE-061
objective: >-
  Integrate BundleTree into BrowserScreen: left-column layout container,
  CSS for visibility toggling, tree↔preview wiring, focus management
  (f/Tab), tree refresh on file-watch events, state clear on type/artifact
  change. Full headless pilot tests.
entrance_criteria:
  - Phase 1 complete (ArtifactEntry.bundle_dir, BundleTree widget, PreviewPanel guard)
exit_criteria:
  - BrowserScreen composes #left-column with TypeSelector + BundleTree
  - Selecting a bundle artifact shows the tree; non-bundle hides it
  - Tree file selection updates preview panel
  - f focuses tree when visible; Tab from tree focuses artifact table
  - File-watch refresh repopulates tree for selected bundle artifact
  - Type change and non-bundle selection clear tree state
  - theme.tcss updated with left-column and bundle-tree rules
  - All VT-061-02 tests pass
  - Existing TUI tests still pass (VT-061-05)
  - Lint clean
verification:
  tests:
    - VT-061-02
    - VT-061-05
  evidence: []
tasks:
  - id: '2.1'
    description: BrowserScreen layout — left-column container
  - id: '2.2'
    description: theme.tcss — left-column, bundle-tree visibility, borders
  - id: '2.3'
    description: Wire artifact selection to tree show/hide/clear
  - id: '2.4'
    description: Wire BundleFileSelected to preview panel
  - id: '2.5'
    description: Focus management — f binding and Tab override
  - id: '2.6'
    description: Tree refresh on file-watch + re-resolve selected entry
risks:
  - description: Container wrapper may affect existing CSS or test queries
    mitigation: Run full TUI test suite after layout change
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-061.PHASE-02
```

# Phase 2 — Browser integration

## 1. Objective

Wire Phase 1 building blocks into BrowserScreen. The tree appears/disappears
based on selected artifact, files are previewable, focus model works, and
watch-triggered refresh keeps the tree current.

## 2. Links & References
- **Delta**: DE-061
- **Design Revision**: DR-061 §5 (DEC-061-02, DEC-061-03, DEC-061-06), §4
- **Phase 1 deliverables**: `ArtifactEntry.bundle_dir`, `BundleTree`, `PreviewPanel` non-md guard
- **Key files**: `browser.py`, `theme.tcss`, `app.py`

## 3. Entrance Criteria
- [x] Phase 1 complete

## 4. Exit Criteria / Done When
- [ ] `#left-column` container wraps TypeSelector + BundleTree
- [ ] CSS: `#left-column` borderless, each child has own border
- [ ] CSS: `.has-bundle` toggles tree visibility and height split
- [ ] `on_artifact_selected`: show tree for bundle, hide for non-bundle
- [ ] `on_type_selected`: clear tree and remove `.has-bundle`
- [ ] `on_bundle_file_selected`: update preview with file path
- [ ] `f` focuses tree when visible, no-op otherwise
- [ ] Tab from tree focuses `#artifact-table`
- [ ] `refresh_snapshot` re-resolves entry and repopulates tree
- [ ] Existing TUI tests pass (regression)
- [ ] New pilot tests for above behaviours
- [ ] Lint clean

## 5. Verification
- Textual headless pilot tests (extend `tui_test.py` or new file)
- `just test` + `just lint`

## 6. Assumptions & STOP Conditions
- Wrapping TypeSelector in Vertical doesn't break OptionList message bubbling
- CSS `display: none`/`display: block` toggles work on Tree widget
- STOP if layout container changes break existing tests fundamentally

## 7. Tasks & Progress

| Status | ID | Description | Notes |
| --- | --- | --- | --- |
| [ ] | 2.1 | BrowserScreen layout — left-column container | Foundation for 2.2–2.6 |
| [ ] | 2.2 | theme.tcss updates | Depends on 2.1 |
| [ ] | 2.3 | Wire artifact selection → tree show/hide/clear | Depends on 2.1 |
| [ ] | 2.4 | Wire BundleFileSelected → preview | Depends on 2.3 |
| [ ] | 2.5 | Focus management (f/Tab) | Depends on 2.1 |
| [ ] | 2.6 | Tree refresh + entry re-resolution | Depends on 2.3 |

### Task Details

- **2.1 — Layout container**
  - **Files**: `browser.py`
  - `compose()` yields `Vertical(TypeSelector, BundleTree, id="left-column")`
  - Import BundleTree. Tree starts hidden via CSS.

- **2.2 — CSS**
  - **Files**: `theme.tcss`
  - Move width rules from `#type-selector` to `#left-column`.
  - `#bundle-tree { display: none; }` by default.
  - `.has-bundle` variant: tree visible, height split (1fr/2fr).
  - Each widget keeps own border. Focus-within accent on bundle-tree.

- **2.3 — Artifact selection → tree**
  - **Files**: `browser.py`
  - `on_artifact_selected`: if `entry.bundle_dir`, show tree + add `.has-bundle`.
    Otherwise clear tree + remove class.
  - `on_type_selected`: always clear tree + remove class.

- **2.4 — BundleFileSelected → preview**
  - **Files**: `browser.py`
  - New handler: update preview with `message.path`, set border title to filename.

- **2.5 — Focus management**
  - **Files**: `browser.py`, `bundle_tree.py`
  - Screen binding `f` → `action_focus_files` (check tree visibility).
  - `BundleTree.key_tab` → focus `#artifact-table`.

- **2.6 — Tree refresh + re-resolve**
  - **Files**: `browser.py`
  - In `refresh_snapshot`: re-resolve `_selected_entry` via `find_entry(id)`.
    If fresh entry has `bundle_dir`, repopulate tree.
