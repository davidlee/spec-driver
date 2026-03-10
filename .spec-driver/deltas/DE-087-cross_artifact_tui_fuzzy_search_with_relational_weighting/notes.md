# Notes for DE-087

## Phase 01 — Search core

### 2026-03-10: Implementation complete

**New files created:**
- `supekku/tui/search/__init__.py` — package exports
- `supekku/tui/search/index.py` — `SearchEntry` dataclass, `build_search_index()`, field extraction
- `supekku/tui/search/scorer.py` — `score_entry()`, `search()`, weight constants
- `supekku/tui/search/index_test.py` — 17 tests (VT-087-002)
- `supekku/tui/search/scorer_test.py` — 15 tests (VT-087-001, VT-087-003)

**Other changes:**
- `supekku/scripts/lib/specs/package_utils_test.py` — added `supekku/tui/search` to KNOWN_LEAF_PACKAGES

## Phase 02 — TUI overlay

### 2026-03-10: Implementation complete

**New files:**
- `supekku/tui/widgets/search_overlay.py` — `SearchOverlay(ModalScreen)` with `_SearchInput` key forwarding
- `supekku/tui/widgets/search_overlay_test.py` — 5 tests (lifecycle, keybindings)

**Modified files:**
- `supekku/tui/app.py` — added `ArtifactEntry` import, `action_global_search()`, rebound `/` → `global_search`, added `Ctrl+F` → `focus_search`
- `supekku/tui/tui_test.py` — updated keybinding test: `test_search_focus_binding` → `test_search_overlay_binding` + `test_filter_focus_binding`

**Integration approach:**
- `push_screen(SearchOverlay, callback)` — overlay dismisses with `ArtifactEntry | None`
- Callback calls `action_navigate_artifact(entry.id)` which already handles type switching and row selection
- Index built fresh on each overlay mount via `build_search_index(root=)`
- No changes to `BrowserScreen` — navigation goes through existing `App.action_navigate_artifact`

---

**Key design points (Phase 01):**
- Index builder is fully self-contained — instantiates own registries, no ArtifactSnapshot coupling
- Reuses `_REGISTRY_FACTORIES` and `adapt_record` from `artifact_view.py` (code reuse, not state sharing)
- Tags produce per-tag entries (`tag.0`, `tag.1`) for correct per-tag scoring
- Broad exception catches at registry/record boundaries match `_collect_safe` pattern in `artifact_view.py`
- All 32 new tests passing, 3805 total tests passing, both linters clean

## Phase 03 — Verification, edge cases, and closure

### 2026-03-10: VA-087-001 walkthrough

**Walkthrough results (human-verified):**

| Scenario | Result | Notes |
| --- | --- | --- |
| Partial ID → correct artifact | PASS | Works across types |
| Tag name → matching artifacts | PASS | |
| Referenced artifact ID → referencing artifacts | PASS | Below own-ID matches as designed |
| Empty query → no results | PASS | Blank on open |
| Escape → overlay dismisses | PASS | Clean dismiss |
| Enter on result → browser navigates | PASS | After fix (see below) |
| Ctrl+F → per-type search | PASS | Unaffected |

**Issues found and fixed:**

1. **Performance: exponential fuzzy matcher** — Textual's `Matcher.match()` is
   combinatorial on long queries with scattered character positions (46s for
   "specification" across 574 entries). Replaced with linear O(n) subsequence
   scorer (`_fuzzy_score`): substring bonus, prefix bonus, compactness scoring.
   Sub-millisecond for all query lengths.

2. **Navigation: screen transition race** — `action_navigate_artifact` called
   `switch_screen("browser")` after modal dismiss, re-pushing the already-active
   browser and causing a remount. Fixed: guard with `isinstance` check + defer
   callback via `call_later`.

3. **Preview focus** — Added `preview.focus()` after search navigation so
   keyboard scrolling works immediately.

**UX improvements added:**

- PageUp/PageDown key forwarding from search input to results table
- Ctrl+Delete / Ctrl+Backspace for word deletion in search input
- Search index cached on app, invalidated on file changes (406ms → 0ms on reopen)
- Per-type colour styling on IDs and type labels in search results

**Backlog items created:**
- IMPR-013: TUI requirements type performance
- IMPR-014: Search overlay relation context display
- IMPR-015: Browser all-types view in primary navigation

**Test results:** 3826 passed, 4 skipped, both linters clean.

