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
