# IMPR-009 Research: TUI Dashboard

Research pass to inform design decisions before scoping a delta.

## 1. Registry API Surface

### Common interface (convention, no ABC/Protocol)

All registries follow the same pattern by convention. No base class — deliberate
per project doctrine (specific before generic).

| Method          | Signature                  | Returns           | Notes                                      |
| --------------- | -------------------------- | ----------------- | ------------------------------------------ |
| constructor     | `(root=None)`              | —                 | Most keyword-only; SpecRegistry positional |
| `collect()`     | `() → dict[str, Record]`   | dict keyed by ID  | Rescans filesystem each call               |
| `find(id)`      | `(str) → Record \| None`   | single record     | Calls `collect()` internally               |
| `iter(status=)` | `(str \| None) → Iterator` | filtered iterator | Optional status filter                     |
| `filter(...)`   | domain-specific kwargs     | `list[Record]`    | AND logic; params vary                     |
| `sync()`        | `() → None`                | —                 | Writes registry YAML                       |

### Universal model attributes

All record types expose: `id`, `title`/`name`, `status`, `path`.
Most also have: `tags`, `created`, `updated`, relationship lists.

### Divergences

| Registry                 | Divergence                                                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| **SpecRegistry**         | Eager-loads in `__init__` (caches `_specs`). Exposes `all_specs()` list, not `collect()` dict.                                  |
| **RequirementsRegistry** | Takes `registry_path: Path` not `root`. Eager-loads from YAML. Has `merge()`, `move_requirement()`. Complex lifecycle tracking. |
| **CardRegistry**         | Stateful — `create_card()` writes files. `next_id()` allocates. Requires `root` (no default).                                   |
| **BacklogRegistry**      | No class — pure functions only (`discover_backlog_items()`, `find_backlog_items_by_id()`, etc.).                                |
| **MemoryRegistry**       | Has `collect_bodies()` for body text. Optional `directory` override. Different filter params (`memory_type`).                   |
| **DecisionRegistry**     | Has `rebuild_status_symlinks()` — filesystem side-effects beyond YAML.                                                          |

### TUI implications

A generic artifact browser panel needs an adapter layer. The common subset
(`collect()` → dict, universal attrs) covers ~80% of the list view. The
remaining 20% (RequirementsRegistry's path-based init, BacklogRegistry's
function-based API, SpecRegistry's eager caching) needs per-type wiring.

**Related**: ISSUE-019 documents this drift in detail — three different ID
lookup patterns (`get()` vs `find()` vs none), plus BacklogRegistry being
function-based while others are class-based. Its proposed hybrid approach
(normalise on `find(id)`, build artifact resolver in `core/`) would directly
reduce TUI adapter complexity. If ISSUE-019 lands first (or concurrently), the
TUI adapter layer shrinks significantly. If not, the TUI adapters become
additional evidence for the normalisation case.

**Decision**: Don't create a Registry Protocol yet. Write thin per-type adapters
in the TUI layer that normalise to a common view model. Extract a Protocol only
if/when 3+ adapters are identical. Track ISSUE-019 as a simplification
opportunity.

---

## 2. Formatter Infrastructure

### Architecture

All formatters are **pure functions** returning **strings** (not Rich
Renderables). The pipeline:

1. Formatter builds string with Rich markup (`[style]text[/style]`)
2. `create_table()` → Rich `Table` object
3. `table.add_row()` with markup strings
4. `render_table()` → `Console(theme=SPEC_DRIVER_THEME).capture()` → string

### Key components

- **`theme.py`**: `SPEC_DRIVER_THEME` — a `rich.theme.Theme` with 70+ named
  styles. Status-to-style helpers per artifact type.
- **`table_utils.py`**: `format_list_table()` is the generic dispatcher. Takes
  `prepare_row` (Rich markup), `prepare_tsv_row` (plain), `to_json` callables.
  Handles terminal width, truncation, format selection.
- **Per-domain modules**: `decision_formatters.py`, `change_formatters.py`, etc.
  Each follows the same pattern: `_prepare_X_row()`, `_prepare_X_tsv_row()`,
  `format_X_list_json()`, `format_X_list_table()`.

### Output formats

- **table**: Rich Table rendered to string (default)
- **tsv**: Plain text, no markup
- **json**: `{"items": [...]}` with custom serialisation per type
- **raw/text**: Some formatters return plain strings directly

### Textual compatibility

**Problem**: Formatters return strings, not Rich objects. `render_table()`
captures to string immediately via `Console.capture()`.

**Options (in order of preference)**:

1. **Option A (minimal, do first)**: Use `Text.from_markup(string)` in Textual
   widgets. Textual supports Rich markup. Theme style names need to be mapped
   to Textual CSS or registered. Quick to try, may be sufficient for MVP.

2. **Option B (dual-path)**: Extract `_build_X_table()` functions that return
   Rich `Table` objects before `render_table()` is called. TUI uses the object;
   CLI continues to render to string. Small refactor, backwards-compatible.

3. **Option C (future)**: Textual-native widgets with CSS styling. Full rewrite
   of display layer. Unnecessary for MVP.

**Recommendation**: Start with Option A. If markup rendering is insufficient
(e.g. DataTable needs structured data not strings), move to Option B for
specific formatters as needed.

### Theme reuse

`SPEC_DRIVER_THEME` style names (e.g. `adr.status.accepted`) can be mapped to
Textual CSS classes. The colour palette in `theme.py` is the single source of
truth for styling — Textual CSS should derive from it, not duplicate it.

---

## 3. Paths & Configuration

### Current state (`core/paths.py`)

- 30+ getter functions: `get_*_dir(repo_root=None) → Path`
- All paths are **hardcoded constants** — no config override mechanism
- `_resolve_root()` uses `find_repo_root()` for auto-detection
- Clean, well-contained module (189 lines)

### workflow.toml parsing (`core/config.py`)

- `load_workflow_config(repo_root) → dict` — single entry point
- Deep-merges user config over `DEFAULT_CONFIG`
- Currently used in only 3 places: `install.py`, `skills/sync.py`, `complete_delta.py`
- **No `[dirs]` section yet** — that's IMPR-008's scope

### IMPR-008 relationship

IMPR-008 (`idea` status) plans to:

1. Add `[dirs]` config section to workflow.toml
2. Make `paths.py` resolve from config instead of constants
3. Provide migration tooling

**For IMPR-009**: Use `paths.py` getters as-is. They already abstract directory
locations. When IMPR-008 lands (making those getters config-aware), the TUI
inherits configurability for free. No hardcoded paths in TUI code.

---

## 4. CLI Dispatch & Hook Points

### Current architecture

- Typer (Click-based) with flat command registration
- No middleware, no pre/post hooks, no event loop
- Each command is independent and self-contained
- `main.py` registers commands; no common wrapper

### Event emission options

**Option A (minimal, recommended for MVP)**:
Add a `core/events.py` module with:

- `emit_event(cmd, artifacts, status)` — appends JSONL + sends to socket
- Session ID from `SPEC_DRIVER_SESSION` env var
- Called explicitly at end of commands that mutate state

Pros: No framework changes. Opt-in per command. Zero cost when disabled.
Cons: Must add call sites manually to each command.

**Option B (Typer callback wrapper)**:
Wrap command functions with a decorator that emits post-execution events.

```python
@emit_on_complete
def create_delta(...): ...
```

Pros: Consistent, less manual wiring.
Cons: Typer's callback model is limited; may need custom subclass.

**Option C (filesystem-based, zero code changes)**:
Use `watchfiles` on the artifact directories. Infer command from file changes.
Pros: Works without modifying CLI at all.
Cons: No command context, no session attribution, can't distinguish create vs
edit vs sync.

**Recommendation**: Option A for MVP. It's explicit, testable, and doesn't
require framework-level changes. Option B can come later as a refinement.

**Best hook point for Option A**: `Workspace.sync_all_registries()` already
orchestrates across all registries — a single post-sync event there covers
most state-changing operations.

---

## 5. Dependencies

### Current (`pyproject.toml`)

```
jinja2>=3.1.0
pyyaml>=6.0.3
python-frontmatter>=1.1.0
typer>=0.15.0
```

Rich is transitive via typer, not declared explicitly.

### TUI additions needed

| Package           | Purpose                           | Size                 |
| ----------------- | --------------------------------- | -------------------- |
| `textual>=3.0`    | TUI framework                     | ~2MB (includes Rich) |
| `watchfiles>=1.0` | File watching (Rust-backed, fast) | ~1MB                 |

### Optional extra vs core dependency

**Recommendation**: Make TUI an optional extra.

```toml
[project.optional-dependencies]
tui = ["textual>=3.0", "watchfiles>=1.0"]
```

Entry point: `spec-driver tui` checks for import availability, gives helpful
error if not installed. Event emission (JSONL + socket) uses only stdlib and
stays in core.

---

## 6. Textual Fit Assessment

### Widget mapping

| TUI feature      | Textual widget             | Notes                      |
| ---------------- | -------------------------- | -------------------------- |
| Type selector    | `OptionList` or `ListView` | Sidebar with counts        |
| Artifact list    | `DataTable`                | Sortable, filterable       |
| Markdown preview | `MarkdownViewer`           | Built-in, handles most MD  |
| Search           | `Input` + `OptionList`     | Modal overlay              |
| Track/event log  | `RichLog`                  | Append-only, scrollable    |
| Editor launch    | `app.suspend()`            | Textual 1.0+ supports this |

### Async architecture

Textual is fully async (built on `asyncio`). This is ideal for:

- Socket listener (non-blocking `asyncio.DatagramProtocol`)
- File watching (`watchfiles` has async API)
- Background registry refresh

### CSS theming

Textual uses CSS for styling. The 70+ styles in `SPEC_DRIVER_THEME` can be
mapped to Textual CSS classes. A `theme.tcss` file derived from `theme.py`
keeps the single source of truth.

---

## 7. Design Decisions to Make Before Scoping

| #   | Decision                   | Options                                        | Recommendation                               |
| --- | -------------------------- | ---------------------------------------------- | -------------------------------------------- |
| 1   | Optional extra vs core dep | `[tui]` extra / always installed               | Optional extra                               |
| 2   | Formatter reuse strategy   | Markup strings / Rich objects / Textual-native | Markup strings first, Rich objects if needed |
| 3   | Event emission approach    | Explicit calls / decorator / filesystem        | Explicit calls (Option A)                    |
| 4   | Registry abstraction       | Protocol / per-type adapters / none            | Per-type adapters, no Protocol               |
| 5   | Theme source of truth      | theme.py generates .tcss / duplicate / shared  | Generate .tcss from theme.py                 |
| 6   | Track mode transport       | Socket only / log only / hybrid                | Hybrid (socket + JSONL)                      |
| 7   | IMPR-008 dependency        | Block on it / use paths.py as-is               | Use paths.py as-is                           |

---

## 8. Risk Register

| Risk                                                  | Likelihood | Impact | Mitigation                                        |
| ----------------------------------------------------- | ---------- | ------ | ------------------------------------------------- |
| Rich markup doesn't render cleanly in Textual widgets | Medium     | Medium | Spike early; fall back to Option B (Rich objects) |
| 13 artifact types make generic browser unwieldy       | Low        | Medium | Group by category; progressive disclosure         |
| Event emission adds latency to CLI commands           | Low        | High   | Fire-and-forget socket; async JSONL append        |
| Textual version churn breaks TUI                      | Medium     | Low    | Pin to stable minor; TUI is optional extra        |
| IMPR-008 path changes break TUI                       | Low        | Low    | Use paths.py getters exclusively; no hardcoding   |

---

## References

- ISSUE-019 — Registry API drift: inconsistent ID lookup patterns
- `supekku/scripts/lib/core/paths.py` — path constants and getters
- `supekku/scripts/lib/core/config.py` — workflow.toml loader
- `supekku/scripts/lib/formatters/theme.py` — Rich theme definition
- `supekku/scripts/lib/formatters/table_utils.py` — generic table infrastructure
- `supekku/cli/main.py` — CLI entry point and command registration
- `backlog/improvements/IMPR-008*/IMPR-008.md` — configurable paths (idea)
- ADR-006 — consolidate workspace under `.spec-driver/`
- [Textual docs](https://textual.textualize.io/)
- [watchfiles docs](https://watchfiles.helpmanual.io/)
