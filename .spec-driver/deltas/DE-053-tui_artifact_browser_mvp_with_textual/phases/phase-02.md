---
id: IP-053.PHASE-02
slug: "053-tui_artifact_browser_mvp_with_textual-phase-02"
name: IP-053 Phase 02
created: "2026-03-07"
updated: "2026-03-07"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-053.PHASE-02
plan: IP-053
delta: DE-053
objective: >-
  Build the Textual TUI app consuming Phase 1 infrastructure: app shell,
  3-panel browser screen, type selector, artifact list with status filter,
  preview panel, theme.tcss, and headless pilot tests.
entrance_criteria:
  - Phase 1 complete (shared infrastructure committed — 4a203df)
  - Textual 8.0.2 available
  - DR-053 decisions DEC-053-11 through DEC-053-16 resolved
exit_criteria:
  - ArtifactGroup enum and ArtifactTypeMeta in core/artifact_view.py with tests
  - tui/app.py — App subclass with BrowserScreen, keybindings, CSS_PATH
  - tui/browser.py — BrowserScreen (Screen subclass) with 3-panel layout
  - tui/widgets/type_selector.py — OptionList with styled Text items, OptionSelected message
  - tui/widgets/artifact_list.py — DataTable with styled_text cells, Select status filter, ArtifactSelected message
  - tui/widgets/preview_panel.py — Markdown widget updated on artifact selection
  - tui/theme.tcss — layout chrome only, no hex/rgb colour literals
  - VT-053-pilot passing (headless pilot tests)
  - VT-053-tcss-lint passing (no colour literals in .tcss)
  - just passes (lint + test)
verification:
  tests:
    - VT-053-pilot
    - VT-053-tcss-lint
  evidence: []
tasks:
  - id: P02-T01
    description: Add ArtifactGroup and ArtifactTypeMeta to artifact_view.py
  - id: P02-T02
    description: Add artifact.group.* theme entries to theme.py
  - id: P02-T03
    description: Create tui package structure and theme.tcss
  - id: P02-T04
    description: Build type_selector widget
  - id: P02-T05
    description: Build artifact_list widget with status filter
  - id: P02-T06
    description: Build preview_panel widget
  - id: P02-T07
    description: Build BrowserScreen composing widgets with message wiring
  - id: P02-T08
    description: Build App subclass with screen, keybindings, CSS_PATH
  - id: P02-T09
    description: Write VT-053-pilot headless pilot tests
  - id: P02-T10
    description: Write VT-053-tcss-lint .tcss colour literal scanner
risks:
  - description: OptionList/Select dynamic rebuild causes flicker or state loss
    mitigation: Test in pilot; if problematic, batch updates or defer rebuild to next frame
  - description: Textual CSS layout doesn't match mockup proportions
    mitigation: Iterate .tcss; layout is chrome-only so changes are isolated
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-053.PHASE-02
```

# Phase 2 — TUI Core

## 1. Objective

Build the Textual TUI app on top of Phase 1 infrastructure. Delivers the
browsable 3-panel dashboard: type selector, artifact list with status filter,
and markdown preview. App launches headlessly for testing; CLI entry point is
Phase 3.

## 2. Links & References

- **Delta**: [DE-053](../DE-053.md)
- **Design Revision**: [DR-053](../DR-053.md)
  - DEC-053-01 (styled_text API)
  - DEC-053-03 (.tcss Textual-native tokens only)
  - DEC-053-10 (type selector flat OptionList, colour-grouped)
  - DEC-053-11 (ArtifactTypeMeta shared metadata)
  - DEC-053-12 (fuzzy search per-type only)
  - DEC-053-13 (Select widget for status filter)
  - DEC-053-14 (BrowserScreen as Screen subclass)
  - DEC-053-15 (built-in Footer widget)
  - DEC-053-16 (Textual Messages for inter-widget communication)
- **Phase 1**: [phase-01.md](./phase-01.md) — shared infrastructure
- **Spike findings**: [notes.md](../notes.md)

## 3. Entrance Criteria

- [x] Phase 1 complete (4a203df)
- [x] Textual 8.0.2 available and importable
- [x] DR-053 decisions DEC-053-11 through DEC-053-16 resolved
- [x] OptionList accepts styled Text objects (verified in preflight)
- [x] Select supports dynamic `set_options()` rebuild (verified in preflight)

## 4. Exit Criteria / Done When

- [x] `ArtifactGroup` + `ArtifactTypeMeta` in `core/artifact_view.py` with tests
- [x] 4 `artifact.group.*` theme entries added to `theme.py`
- [x] `supekku/tui/` package: app, browser, widgets, theme.tcss
- [x] App launches headlessly via `app.run_test()`
- [x] Type selector shows all 11 types with counts, colour-grouped
- [x] Selecting a type populates artifact list with styled rows
- [x] Status filter (Select) rebuilds per type, filters artifact list
- [x] Selecting an artifact shows markdown preview
- [x] VT-053-pilot passing (12 tests)
- [x] VT-053-tcss-lint passing (3 tests)
- [x] `just` passes (ruff clean, pylint 9.51/10, 2839 tests pass)

## 5. Verification

- `just test` — all existing + new tests
- `just lint` + `just pylint` — zero warnings
- VT-053-pilot: headless pilot tests covering widget composition, DataTable
  content, message dispatch, Markdown preview rendering
- VT-053-tcss-lint: regex scan of theme.tcss for `#[0-9a-fA-F]` and
  `rgb[a]?(` patterns — fail if found (POL-002)

## 6. Assumptions & STOP Conditions

- **Assumption**: Textual's `Screen` + `Footer` + `OptionList` + `DataTable` +
  `Select` + `Markdown` compose without layout conflicts at reasonable terminal
  sizes (80x24 minimum).
- **Assumption**: `OptionList.OptionSelected` and `Select.Changed` messages
  bubble to the screen handler as expected.
- **STOP**: If Textual widget composition hits a blocking layout or event issue
  not resolvable via CSS/message wiring, consult before workarounds.
- **STOP**: If pilot tests cannot inspect widget state reliably (e.g. DataTable
  rows not queryable), reassess VT strategy.

## 7. Tasks & Progress

| Status | ID      | Description                                                | Parallel? | Notes                           |
| ------ | ------- | ---------------------------------------------------------- | --------- | ------------------------------- |
| [x]    | P02-T01 | `ArtifactGroup` + `ArtifactTypeMeta` in `artifact_view.py` | [P]       | DEC-053-11, 16 tests            |
| [x]    | P02-T02 | `artifact.group.*` theme entries in `theme.py`             | [P]       | 4 group colours                 |
| [x]    | P02-T03 | `tui/` package structure + `theme.tcss`                    |           | POL-002 compliant               |
| [x]    | P02-T04 | `tui/widgets/type_selector.py`                             |           | styled Text + TypeSelected msg  |
| [x]    | P02-T05 | `tui/widgets/artifact_list.py` + status filter             |           | DataTable + Select + Input      |
| [x]    | P02-T06 | `tui/widgets/preview_panel.py`                             | [P]       | Markdown widget                 |
| [x]    | P02-T07 | `tui/browser.py` — BrowserScreen                           |           | Message wiring, Screen subclass |
| [x]    | P02-T08 | `tui/app.py` — App subclass                                |           | snapshot param for testability  |
| [x]    | P02-T09 | VT-053-pilot headless tests                                |           | 12 tests, mock snapshot         |
| [x]    | P02-T10 | VT-053-tcss-lint                                           | [P]       | 3 tests, hex+rgb scan           |

### Task Details

- **P02-T01: ArtifactGroup + ArtifactTypeMeta**
  - **Files**: `supekku/scripts/lib/core/artifact_view.py`, `artifact_view_test.py`
  - **Approach**: Add `ArtifactGroup` enum (GOVERNANCE, CHANGE, DOMAIN,
    OPERATIONAL). Add `ArtifactTypeMeta` frozen dataclass (singular, plural,
    group). Add `ARTIFACT_TYPE_META` dict mapping all 11 `ArtifactType` members.
    Add convenience properties on `ArtifactType` (`.meta`, `.singular`,
    `.plural`, `.group`).
  - **Testing**: All types have metadata. Properties return correct values.
    Every `ArtifactType` has a corresponding `ARTIFACT_TYPE_META` entry (no
    missing keys).

- **P02-T02: Group theme entries**
  - **Files**: `supekku/scripts/lib/formatters/theme.py`, `theme_test.py`
  - **Approach**: Add `artifact.group.governance`, `.change`, `.domain`,
    `.operational` to `SPEC_DRIVER_THEME`. Choose colours distinct from
    per-type ID styles.
  - **Testing**: `resolve_style()` returns a style for each group key.

- **P02-T03: TUI package structure + theme.tcss**
  - **Files**: `supekku/tui/__init__.py`, `supekku/tui/theme.tcss`
  - **Approach**: Create package with `__init__.py`. Write `.tcss` with layout
    rules for 3-panel composition: type selector ~20%, artifact list ~35%,
    preview ~45%. Borders, padding, focus indicators. Textual-native tokens
    only — no hex/rgb colour literals (POL-002).

- **P02-T04: Type selector widget**
  - **Files**: `supekku/tui/widgets/__init__.py`, `supekku/tui/widgets/type_selector.py`
  - **Approach**: Subclass or compose `OptionList`. On mount, populate with
    `Option(styled_text(f"{meta.plural} ({count})", group_style), id=art_type.value)`
    for each `ArtifactType` in enum order (preserves group ordering).
    Post `TypeSelected(artifact_type)` message on `OptionSelected`.
    Expose `refresh_counts(counts: dict[ArtifactType, int])` for watch-triggered
    updates.

- **P02-T05: Artifact list widget + status filter**
  - **Files**: `supekku/tui/widgets/artifact_list.py`
  - **Approach**: Composite widget: `Select` (status filter) + `DataTable`
    (artifact rows) in a Vertical container. On `TypeSelected`, rebuild
    `Select` options from distinct statuses in current entries. On
    `Select.Changed` or type change, repopulate DataTable rows using
    `column_labels()` for headers and `styled_text()` for cell content.
    Post `ArtifactSelected(entry: ArtifactEntry)` on row selection.
    Fuzzy filter input (DEC-053-12): `Input` widget with on-change filtering
    of current DataTable contents.

- **P02-T06: Preview panel widget**
  - **Files**: `supekku/tui/widgets/preview_panel.py`
  - **Approach**: Wrap Textual `Markdown` widget. On `ArtifactSelected`,
    read `entry.path` with `Path.read_text()` and update markdown content.
    Handle missing/unreadable files gracefully (show error message in panel).

- **P02-T07: BrowserScreen**
  - **Files**: `supekku/tui/browser.py`
  - **Approach**: `Screen` subclass. `compose()` yields Horizontal container
    with type selector, artifact list, preview panel. Message handlers:
    `on_type_selected` → update artifact list. `on_artifact_selected` → update
    preview. Receives `ArtifactSnapshot` (or reference to it) for data access.

- **P02-T08: App subclass**
  - **Files**: `supekku/tui/app.py`
  - **Approach**: `App` subclass. `CSS_PATH = "theme.tcss"`. Creates
    `ArtifactSnapshot` at init. Pushes `BrowserScreen` as default screen.
    Mounts `Footer`. Declares keybindings: `q` quit, `e` edit (Phase 3
    wiring), `/` search focus, `?` help (placeholder). `ENABLE_COMMAND_PALETTE = False`.

- **P02-T09: VT-053-pilot**
  - **Files**: `supekku/tui/tui_test.py`
  - **Approach**: Headless pilot tests via `app.run_test(size=(120, 40))`.
    Tests: app mounts without error; type selector has 11 items; selecting a
    type populates DataTable; selecting a row updates Markdown preview;
    status Select rebuilds on type change; Footer visible; keybinding dispatch.
  - **Fixture**: Mock `ArtifactSnapshot` with known test data to avoid
    filesystem dependency.

- **P02-T10: VT-053-tcss-lint**
  - **Files**: `supekku/tui/tcss_lint_test.py`
  - **Approach**: Read `theme.tcss`, scan for `#[0-9a-fA-F]{3,8}` and
    `rgba?\(` patterns. Fail with diagnostic if found. POL-002 enforcement.

## 8. Risks & Mitigations

| Risk                                         | Mitigation                                                    | Status   |
| -------------------------------------------- | ------------------------------------------------------------- | -------- |
| OptionList/Select dynamic rebuild flicker    | Batch updates; test in pilot                                  | open     |
| Layout doesn't fit 80x24 minimum             | Iterate .tcss proportions; test with `run_test(size=(80,24))` | open     |
| Message bubbling not reaching screen handler | Verified: Textual messages bubble by default                  | low risk |
| Pilot can't inspect DataTable row content    | Spike confirmed Pilot API works for DataTable                 | low risk |

## 9. Decisions & Outcomes

Decisions inherited from DR-053 (DEC-053-01, -03, -10 through -16).
No phase-specific decisions expected unless STOP conditions trigger.

## 10. Findings / Research Notes

**Preflight API verification (2026-03-07)**:

- `OptionList.Option(prompt: VisualType)` accepts Rich `Text` — verified with
  styled text, styles preserved in rendered output.
- `Select.__init__(options: Iterable[tuple[RenderableType, SelectType]])` —
  accepts Rich renderables. `set_options()` for dynamic rebuild. `Changed`
  message on selection.
- Both widgets confirmed compatible with `styled_text()` approach.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: `just` passes (2839 tests, ruff clean, pylint 9.51)
- [x] Notes updated with findings
- [x] Hand-off notes to Phase 3
