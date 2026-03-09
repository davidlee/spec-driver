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

