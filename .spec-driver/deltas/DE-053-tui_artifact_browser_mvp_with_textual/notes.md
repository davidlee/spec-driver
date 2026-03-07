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
