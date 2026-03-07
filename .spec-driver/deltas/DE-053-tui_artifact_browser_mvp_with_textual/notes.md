# Notes for DE-053

## 2026-03-07 — Preflight spike: Textual + theme integration

### Status: preflight complete, DR-053 next

### What was done

- Confirmed DE-050 (registry normalisation) is completed — all 8 class-based
  registries implement `collect/find/iter/filter`. BacklogRegistry remains
  function-based (no class).
- Verified Textual 8.0.2 available (delta's `>=3.0` pin is fine). Rich 14.2.0
  present via typer.
- Ran headless spike testing three DataTable styling approaches:
  1. Rich markup strings → **dead** (DataTable stores as literal text)
  2. `Text.from_markup()` with theme style names → **dead** (Textual doesn't
     resolve Rich Theme styles; colours absent from render)
  3. Pre-resolved `Text` objects via `SPEC_DRIVER_THEME.styles` → **works**
     (colours confirmed in rendered output)
- Tested `Markdown` widget with raw file content → works cleanly for preview.
- Confirmed 163 CSS rules extractable from theme, but unnecessary for cell
  content — pre-resolved Text objects carry their own styles.

### Design decisions resolved

- **Formatter integration**: Option C — build DataTable rows directly from
  registry records + resolved theme styles. Formatters' `format_*_list_table()`
  functions are not reusable for TUI. The `get_*_status_style()` helpers are
  the bridge (return style names → resolve against `SPEC_DRIVER_THEME.styles`).
- **Preview panel**: `Markdown` widget with raw `Path.read_text()`. No
  formatter output needed.
- **Theme mapping**: Runtime style resolution on Text objects, not CSS
  generation. Hand-written `.tcss` for layout/chrome only.

### Open questions

- **Q1: Adapter location** — `tui/` (scoped) vs `core/` (reusable). The
  normalisation shim for BacklogRegistry could benefit `core/`, but
  specific-first doctrine says `tui/` unless reuse is proven.
- **Q4: Type selector grouping** — 12-13 artifact types. Flat list vs grouped
  by category (governance / change / domain). UX decision.

### Testing strategy (critical — agent cannot interact with TUI)

- **VT (unit)**: Registry adapter normalisation, view model mapping, styled
  text helper, theme style resolution.
- **VT (integration)**: Textual headless pilot tests via `app.run_test()` —
  verify widget composition, DataTable row content, Markdown rendering,
  keybinding dispatch. Pilot API supports programmatic input and screenshot
  export.
- **VH (human)**: Manual smoke test gates — launch, browse, search, editor
  integration (`$EDITOR` via `app.suspend()`), file watch live reload. These
  cannot be automated headlessly.
- **Harness**: `textual.app.App.run_test(size=(w,h))` async context manager
  provides `Pilot` object for simulating keys/clicks and inspecting widget
  state. Confirmed working in spike.

### Risks updated post-spike

| Risk | Status | Notes |
|---|---|---|
| Rich markup in Textual | **Resolved** | Pre-resolved Text objects are the path |
| DataTable vs formatter mismatch | **Resolved** | Skip formatters, build rows directly |
| Textual version pin | **Low risk** | 8.0.2 available, `>=3.0` pin is fine |
| BacklogRegistry divergence | **Known** | Adapter shim needed, small scope |
| CardRegistry lane≠status | **Known** | Map lane to status slot in adapter |

### Commits

No code committed — spike was throwaway. Findings recorded here.

## 2026-03-07 — DR review, reconciliation, follow-up scoping

### DR-053 review (two rounds)

Two adversarial review passes surfaced 9 + 3 findings. All resolved. Key
changes from the original draft:

- Artifact projection layer moved to `core/artifact_view.py` (reusable, no
  TUI imports) — risk of parallel implementation outweighs premature
  generalisation
- Shared `column_defs.py` extracted from formatters (POL-001 compliance)
- `resolve_style()` / `styled_text()` promoted to public API in `theme.py`
- `.tcss` uses Textual-native tokens only — intentionally not palette-matched,
  no runtime bridge
- Error isolation boundary in adapter (stderr redirect, per-registry catch)
- Snapshot-on-load caching with watch-triggered per-registry invalidation
- Bounded dep ranges: `textual>=8.0,<9.0`, `watchfiles>=1.0,<2.0`
- BacklogRegistry shim in adapter + follow-up delta as exit criteria
- Type selector: flat OptionList, colour-grouped, no headings
- Expanded VT: error states, edge cases, tcss lint (POL-002)
- Accessibility: explicit MVP non-goal
- DE-053 reconciled with DR-053 (no competing truths)

### BacklogRegistry follow-up delta

DE-053 exit criteria requires a follow-up delta to normalise BacklogRegistry
from function-based to class-based (`collect/find/iter/filter`).

Related backlog items to evaluate as potential riders:
- ISSUE-016, ISSUE-024, ISSUE-026, ISSUE-034, ISSUE-043, ISSUE-045
- IMPR-010

These form a cluster around "backlog subsystem undercooked". Not all should
ride the normalisation delta — triage when scoping.

## 2026-03-07 — Phase 1 complete: Shared infrastructure

### What was done

- **T01**: `resolve_style()` and `styled_text()` added to `formatters/theme.py`
  as public API. 21 tests including style key regression inventory.
- **T02**: `column_defs.py` created with `ColumnDef` dataclass and definitions
  for all 11 artifact/view types. All 9 existing formatter modules refactored
  to consume `column_labels()` instead of inline column lists. 15 tests
  including regression against formatter column expectations. 261 existing
  formatter tests pass unchanged.
- **T03**: `core/artifact_view.py` created with `ArtifactEntry` dataclass,
  `ArtifactSnapshot` cache, per-registry adapters for all 11 types,
  BacklogRegistry function-based shim, error isolation (try/except + stderr
  redirect). 13 tests. Verified against real workspace: 496 artifacts across
  11 types loaded successfully.
- **T04**: TDD throughout — tests written before or alongside implementation.

### Files created/modified

New:
- `supekku/scripts/lib/formatters/theme_test.py` (21 tests)
- `supekku/scripts/lib/formatters/column_defs.py`
- `supekku/scripts/lib/formatters/column_defs_test.py` (15 tests)
- `supekku/scripts/lib/core/artifact_view.py`
- `supekku/scripts/lib/core/artifact_view_test.py` (13 tests)

Modified:
- `supekku/scripts/lib/formatters/theme.py` (additive: 2 functions)
- All 9 `*_formatters.py` files (import + column_labels() substitution)

### Verification

- `just` passes: ruff clean, pylint 9.52/10, 2805 tests pass
- No STOP conditions triggered
- No surprises — column_defs extraction was cleaner than feared

### Commits

Uncommitted. Ready to commit when user approves.

### Handoff to Phase 2

Phase 1 infrastructure is ready. Phase 2 (TUI core) can now:
- Import `styled_text()` from `formatters/theme.py`
- Import `column_labels()` and `*_COLUMNS` from `formatters/column_defs.py`
- Import `ArtifactSnapshot`, `ArtifactType`, `ArtifactEntry` from
  `core/artifact_view.py`
- Build the Textual app consuming this foundation

## 2026-03-07 — Phase 2 complete: TUI core

### What was done

- **T01**: `ArtifactGroup` enum + `ArtifactTypeMeta` dataclass added to
  `core/artifact_view.py` (DEC-053-11). Convenience properties on
  `ArtifactType` (`.singular`, `.plural`, `.group`, `.meta`). 16 new tests.
- **T02**: 4 `artifact.group.*` theme entries added to `theme.py`. Added to
  existing style key regression test.
- **T03**: `supekku/tui/` package created with `__init__.py`, `widgets/__init__.py`,
  `theme.tcss` (Textual-native tokens only, POL-002 compliant).
- **T04**: `tui/widgets/type_selector.py` — `TypeSelector(OptionList)` with
  styled `Text` labels, `TypeSelected` message, `refresh_counts()`.
- **T05**: `tui/widgets/artifact_list.py` — `ArtifactList(Vertical)` with
  `Select` status filter (DEC-053-13), `Input` fuzzy search (DEC-053-12),
  `DataTable` with `cursor_type="row"`, `ArtifactSelected` message.
- **T06**: `tui/widgets/preview_panel.py` — `PreviewPanel(Markdown)` with
  `show_artifact(path)`, graceful error handling.
- **T07**: `tui/browser.py` — `BrowserScreen(Screen)` (DEC-053-14) composing
  all 3 widgets. Message handlers for `TypeSelected` and `ArtifactSelected`
  (DEC-053-16).
- **T08**: `tui/app.py` — `SpecDriverApp(App)` with `CSS_PATH`, keybindings,
  `snapshot` parameter for testability. Pushes `BrowserScreen` on mount.
  Built-in `Footer` (DEC-053-15).
- **T09**: VT-053-pilot — 12 headless pilot tests covering app mount, type
  selection, artifact selection with preview, status filter, fuzzy search,
  keybindings (quit, search focus).
- **T10**: VT-053-tcss-lint — 3 tests scanning theme.tcss for hex/rgb literals.

### Surprises & adaptations

- **Textual MRO handler dispatch**: `on_mount` handlers fire on ALL classes in
  the MRO, not just the most-derived override. This broke test isolation when
  `TestApp(SpecDriverApp)` tried to override `on_mount`. Fixed by adding
  `snapshot` parameter to `SpecDriverApp.__init__` — cleaner API anyway.
- **DataTable cursor_type**: Default is `"cell"`, not `"row"`.
  `DataTable.RowSelected` only fires with `cursor_type="row"`.
- **Select.BLANK vs Select.NULL**: `Select.BLANK` is `False` (not a valid
  value to assign). Use `select.clear()` to reset and `select.is_blank()` to
  check state.
- **app.query_one vs screen.query_one**: `app.query_one()` searches the app's
  own DOM, not pushed screens. Must use `app.screen.query_one()` or
  `self.screen.query_one()` to find widgets on the active screen.

### Dependencies added

- `pytest-asyncio>=1.0` — dev dependency for async test support. Required by
  Textual's headless pilot testing pattern.
- `[project.optional-dependencies] tui` — `textual>=8.0,<9.0`,
  `watchfiles>=1.0,<2.0`. Pulled forward from Phase 3 scope because `uv sync`
  removed textual when it wasn't declared. Dev group includes `spec-driver[tui]`.
- `supekku/tui` added to pytest `testpaths`.
- `asyncio_mode = "auto"` added to pytest config.

### Files created

- `supekku/tui/__init__.py`
- `supekku/tui/app.py`
- `supekku/tui/browser.py`
- `supekku/tui/theme.tcss`
- `supekku/tui/tui_test.py` (12 tests)
- `supekku/tui/tcss_lint_test.py` (3 tests)
- `supekku/tui/widgets/__init__.py`
- `supekku/tui/widgets/type_selector.py`
- `supekku/tui/widgets/artifact_list.py`
- `supekku/tui/widgets/preview_panel.py`

### Files modified

- `supekku/scripts/lib/core/artifact_view.py` (ArtifactGroup, ArtifactTypeMeta)
- `supekku/scripts/lib/core/artifact_view_test.py` (+16 tests)
- `supekku/scripts/lib/formatters/theme.py` (+4 group style entries)
- `supekku/scripts/lib/formatters/theme_test.py` (+4 parametrized cases)
- `supekku/scripts/lib/specs/package_utils_test.py` (22→23 leaf packages)
- `pyproject.toml` (tui extra, pytest-asyncio, testpaths, asyncio_mode)

### DR updates

- DEC-053-11 through DEC-053-16 added (preflight design review, all decided)
- Cross-type fuzzy search captured as follow-up in DE-053

### Verification

- `just` passes: ruff clean, pylint 9.51/10, 2839 tests pass, 3 skipped
- VT-053-pilot: 12/12 pass
- VT-053-tcss-lint: 3/3 pass

### Commits

Uncommitted. Ready to commit when user approves.

### Follow-ups

- CLI entry point (`spec-driver tui` command) — Phase 3
- File watching (`watchfiles.awatch` integration) — Phase 3
- Edge cases (`$EDITOR` unset, import guard) — Phase 3
- Refactor `list.py` `_PLURAL_TO_SINGULAR` to consume `ArtifactTypeMeta` —
  follow-up (not DE-053 scope)
- Cross-type fuzzy search — follow-up (DEC-053-12)
