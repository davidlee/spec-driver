---
id: IP-061.PHASE-01
slug: 061-tui_bundle_file_browser-phase-01
name: Data model, BundleTree widget, PreviewPanel guard
created: "2026-03-08"
updated: "2026-03-08"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-061.PHASE-01
plan: IP-061
delta: DE-061
objective: >-
  Add bundle_dir field to ArtifactEntry, implement BundleTree widget with
  full test coverage, add non-markdown preview guard to PreviewPanel.
  No BrowserScreen integration yet — pure building blocks.
entrance_criteria:
  - DR-061 accepted
exit_criteria:
  - ArtifactEntry.bundle_dir populated correctly by adapt_record
  - BundleTree widget populates, selects, clears, sorts correctly
  - BundleTree skips symlinks and hidden files, respects depth limit
  - PreviewPanel shows placeholder for non-markdown files
  - All new tests pass
  - Lint clean (ruff + pylint on touched files)
verification:
  tests:
    - VT-061-01 (BundleTree widget)
    - VT-061-04 (PreviewPanel non-markdown)
  evidence: []
tasks:
  - id: "1.1"
    description: Add bundle_dir to ArtifactEntry + _detect_bundle_dir
  - id: "1.2"
    description: BundleTree widget with BundleFileSelected message
  - id: "1.3"
    description: PreviewPanel non-markdown guard
risks:
  - description: Textual Tree API may not support cursor_line or data on nodes as expected
    mitigation: Spike early; if API differs, adapt widget design
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-061.PHASE-01
```

# Phase 1 — Data model, BundleTree widget, PreviewPanel guard

## 1. Objective

Build the three independent components needed before browser integration:

- `ArtifactEntry.bundle_dir` field with ID-based detection
- `BundleTree` widget (Textual `Tree` subclass)
- `PreviewPanel` non-markdown file guard

All three are testable in isolation without TUI integration.

## 2. Links & References

- **Delta**: DE-061
- **Design Revision**: DR-061 §5 (DEC-061-01, DEC-061-05), §6
- **Key files**: `artifact_view.py`, `widgets/preview_panel.py`

## 3. Entrance Criteria

- [x] DR-061 reviewed and accepted
- [x] All entrance criteria met

## 4. Exit Criteria / Done When

- [x] `_detect_bundle_dir(record_id, path)` returns correct `Path | None`
- [x] `ArtifactEntry.bundle_dir` populated in `adapt_record`
- [x] `BundleTree.show_bundle()` populates tree from directory
- [x] `BundleTree` emits `BundleFileSelected` on leaf node select
- [x] `BundleTree` skips dotfiles, symlinks; depth-limited
- [x] `BundleTree.clear_bundle()` resets state
- [x] Sort: dirs first, primary file first among files, then alpha
- [x] `BundleTree._select_primary()` cursors the primary file node
- [x] `PreviewPanel.show_artifact()` shows placeholder for non-.md files
- [x] Tests for all of the above (26 new tests)
- [x] `just lint` clean on touched files (ruff + pylint 10/10)

## 5. Verification

- `just test` — new test files:
  - `supekku/scripts/lib/core/artifact_view_test.py` (extend with `_detect_bundle_dir` tests)
  - `supekku/tui/widgets/bundle_tree_test.py`
  - `supekku/tui/widgets/preview_panel_test.py` (extend)
- `just lint` + `just pylint-files` on touched files

## 6. Assumptions & STOP Conditions

- Textual `Tree[Path]` supports `.data` attribute on nodes and `NodeSelected` message
- `cursor_line` property is settable on Tree widget
- STOP if Tree widget API is fundamentally incompatible — `/consult` before workaround

## 7. Tasks & Progress

| Status | ID  | Description                                       | Parallel? | Notes                             |
| ------ | --- | ------------------------------------------------- | --------- | --------------------------------- |
| [x]    | 1.1 | `_detect_bundle_dir` + `ArtifactEntry.bundle_dir` | [P]       | Pure function + dataclass field   |
| [x]    | 1.2 | `BundleTree` widget                               | [P]       | New file `widgets/bundle_tree.py` |
| [x]    | 1.3 | `PreviewPanel` non-markdown guard                 | [P]       | Small edit to existing widget     |

### Task Details

- **1.1 — `_detect_bundle_dir` + `ArtifactEntry.bundle_dir`**
  - **Files**: `supekku/scripts/lib/core/artifact_view.py`
  - **Approach**: Add `bundle_dir: Path | None = None` to frozen dataclass.
    Add `_detect_bundle_dir(record_id: str, path: Path) -> Path | None` —
    returns `path.parent` if `parent.name.startswith(record_id)` and parent
    is a directory. Call in `adapt_record`.
  - **Testing**: Test with paths like `deltas/DE-061-slug/DE-061.md` (→ bundle),
    `decisions/ADR-001-title.md` (→ None), nonexistent paths (→ None).

- **1.2 — `BundleTree` widget**
  - **Files**: `supekku/tui/widgets/bundle_tree.py` (new),
    `supekku/tui/widgets/__init__.py` (export)
  - **Approach**: Per DR-061 §6. `Tree[Path]` subclass, `BundleFileSelected`
    message, `show_bundle(bundle_dir, primary_path)`, `_populate` with
    symlink/depth/dotfile guards, `_sort_key`, `_select_primary`, `clear_bundle`.
  - **Testing**: Use `tmp_path` fixtures to create mock bundle directories.
    Test: population, node data, selection message, sort order, symlink skip,
    depth limit, dotfile skip, empty directory, clear.

- **1.3 — `PreviewPanel` non-markdown guard**
  - **Files**: `supekku/tui/widgets/preview_panel.py`
  - **Approach**: Before reading file content, check `path.suffix`. If not
    `.md`/`.markdown`, update markdown widget with placeholder text and return.
  - **Testing**: Extend existing preview tests with `.txt`, `.yaml`, no-extension cases.

## 8. Risks & Mitigations

| Risk              | Mitigation                                              | Status |
| ----------------- | ------------------------------------------------------- | ------ |
| Tree API mismatch | Spike `Tree[Path]` constructor and `NodeSelected` early | open   |

## 9. Decisions & Outcomes

(populated during execution)

## 10. Findings / Research Notes

(populated during execution)
