---
id: IP-087.PHASE-02
slug: 087-cross_artifact_tui_fuzzy_search_with_relational_weighting-phase-02
name: TUI overlay — widget, keybindings, browser integration
created: '2026-03-10'
updated: '2026-03-10'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-087.PHASE-02
plan: IP-087
delta: DE-087
objective: >-
  Build the search overlay widget, rebind keybindings, and integrate result
  selection with BrowserScreen.navigate_to_artifact(). Functional end-to-end
  search in the TUI.
entrance_criteria:
  - Phase 01 complete — search core tests passing
exit_criteria:
  - Search overlay opens on / with empty input
  - Typing filters results across all artifact types in real-time
  - Results show type badge, ID, title sorted by score
  - Enter navigates to selected artifact in browser
  - Escape dismisses overlay
  - Ctrl+F focuses per-type inline search
  - just check green
verification:
  tests: []
  evidence:
    - VA-087-001
tasks:
  - id: "2.1"
    summary: Search overlay widget (ModalScreen)
  - id: "2.2"
    summary: Keybinding changes in app.py
  - id: "2.3"
    summary: Browser integration — overlay mounting and result handling
  - id: "2.4"
    summary: Overlay widget tests
risks:
  - description: Textual ModalScreen API may not support needed focus patterns
    mitigation: Verify API before building; fall back to Screen with overlay CSS
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-087.PHASE-02
```

# Phase 02 — TUI overlay

## 1. Objective

Build the search overlay widget, change keybindings, and wire result selection to browser navigation. After this phase the feature is functionally complete.

## 2. Links & References

- **Delta**: [DE-087](../DE-087.md)
- **Design Revision**: [DR-087](../DR-087.md) — DEC-087-03 (overlay UX), DEC-087-04 (keybindings)
- **Phase 01**: [phase-01.md](./phase-01.md) — provides `build_search_index`, `search`, `SearchEntry`
- **Existing code**: `supekku/tui/app.py`, `supekku/tui/browser.py`, `supekku/tui/widgets/artifact_list.py`

## 3. Entrance Criteria

- [x] Phase 01 complete — search core tests passing, `just check` green

## 4. Exit Criteria / Done When

- [x] `/` opens search overlay with empty input focused
- [x] Real-time filtering across all artifact types as user types
- [x] Results display: `[Type]  ID  Title`
- [x] Up/Down navigates results; Enter selects → overlay closes, browser navigates
- [x] Escape dismisses overlay without action
- [x] `Ctrl+F` focuses per-type inline search (existing `_SearchInput`)
- [x] `just check` green — 3811 tests passing

## 5. Verification

- Widget tests where feasible (Textual's `App.run_test()` for basic lifecycle)
- VA-087-001: Manual walkthrough documented in notes.md

## 6. Assumptions & STOP Conditions

- **Assumption**: Textual's `ModalScreen` (or `Screen` with modal CSS) supports the needed overlay pattern
- **Assumption**: `BrowserScreen.navigate_to_artifact()` works correctly for all artifact types (already tested by DE-053/DE-061)
- **STOP**: If Textual's modal/focus management doesn't support the overlay pattern cleanly, consult

## 7. Tasks & Progress

| Status | ID  | Description           | Parallel? | Notes                                               |
| ------ | --- | --------------------- | --------- | --------------------------------------------------- |
| [x]    | 2.1 | Search overlay widget | [ ]       | ModalScreen + \_SearchInput key forwarding          |
| [x]    | 2.2 | Keybinding changes    | [P]       | / → global_search, Ctrl+F → focus_search            |
| [x]    | 2.3 | Browser integration   | [ ]       | push_screen callback → action_navigate_artifact     |
| [x]    | 2.4 | Tests                 | [ ]       | 5 overlay tests + updated tui_test keybinding tests |

### Task Details

- **2.1 Search overlay widget**
  - **File**: `supekku/tui/widgets/search_overlay.py`
  - **Design**: Textual `ModalScreen` (or `Screen` subclass). Composes: `Input` (search box) + `DataTable` (results). On `Input.Changed` → call `search()` from Phase 01 scorer, update table. On `DataTable.RowSelected` → post result message and dismiss. On Escape → dismiss.
  - **Styling**: Type badge column styled per `ArtifactGroup`. Use `styled_text` from theme.
  - **Index**: Call `build_search_index(root=)` on mount. Not cached across open/close.

- **2.2 Keybinding changes**
  - **File**: `supekku/tui/app.py`
  - **Changes**: `Binding("slash", ...)` → `Binding("slash", "global_search", ...)`. Add `Binding("ctrl+f", "focus_search", ...)`. New `action_global_search` method pushes the overlay screen.
  - **Key display**: `/` shows "Search", `Ctrl+F` shows "Filter".

- **2.3 Browser integration**
  - **File**: `supekku/tui/browser.py` (and/or `app.py`)
  - **Design**: When overlay posts a result, `app.action_navigate_artifact(artifact_id)` is called (already exists). Overlay dismisses itself before or after posting.
  - **Root passing**: Overlay needs `root: Path` for `build_search_index`. Pass from `SpecDriverApp._root`.

- **2.4 Tests**
  - **File**: `supekku/tui/widgets/search_overlay_test.py`
  - **Coverage**: Overlay mounts, input triggers search, result selection posts message, escape dismisses. Use Textual's `app.run_test()` pattern.

## 8. Risks & Mitigations

| Risk                                               | Mitigation                                                            | Status |
| -------------------------------------------------- | --------------------------------------------------------------------- | ------ |
| Textual ModalScreen API gaps                       | Verify API first; fall back to Screen + CSS overlay                   | Open   |
| Focus management between overlay input and results | Test with `app.run_test()`; handle key forwarding like `_SearchInput` | Open   |

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] VA-087-001 walkthrough documented
- [ ] Hand-off notes to Phase 03
