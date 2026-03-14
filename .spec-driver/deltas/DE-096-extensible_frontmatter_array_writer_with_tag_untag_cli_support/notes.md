# DE-096 Implementation Notes

## 2026-03-14 – Design exploration

### CompactDumper findings
- `yaml.safe_dump` with custom representer is idempotent and deterministic
- Flow-style heuristic: all scalars AND total rendered width < 80 chars → flow; otherwise block
- Empty lists emit as `[]` (flow) which matches project convention
- Relations (list-of-dicts) stay block-style — correct behaviour

### Date quoting
- Double-quoted `"2025-01-15"` → loaded as string → re-dumped as single-quoted `'2025-01-15'`
- Unquoted `2025-01-15` → loaded as `datetime.date` → re-dumped unquoted
- Both stable after normalisation; single-quote is canonical post-normalisation

### Adversarial review findings
- `update_frontmatter_status` returns `bool` — callers check `False` for "no status field". Preserved in wrapper.
- `FieldUpdateResult` return type — computed from dict diff. Preserved.
- Code-fenced YAML blocks in body: out of scope, body is passthrough.
- Client repo migration: backlog item required before delta closure.

## 2026-03-14 – Phase 1 complete

### Changes
- **`frontmatter_writer.py`**: Full rewrite. `CompactDumper` (flow for short scalar lists, block otherwise). `update_frontmatter(path, mutator)` core primitive. `add/remove_frontmatter_list_items()` convenience functions. `update_frontmatter_status`/`update_frontmatter_fields` reimplemented as round-trip wrappers.
- **`spec_utils.py`**: `dump_markdown_file` switched to `dump_frontmatter_yaml` (CompactDumper). Lazy import to avoid circular dependency.
- **`edit.py`**: Fixed `_verify_memory` to pass plain date strings (not pre-quoted `"'2026-03-09'"`).
- **`complete_delta_test.py`**: Added mock for `update_frontmatter_status` — test was using MagicMock paths that don't support real file I/O.

### Surprises
- `python-frontmatter` library parses double-quoted dates as strings but `yaml.safe_load` parses unquoted dates as `datetime.date`. Both round-trip correctly.
- `policy.path` is a string in some registries, not a `Path`. `_apply_tags` needed `Path(path)` coercion.
- `update_frontmatter_fields` callers passed pre-quoted strings like `"'2026-03-09'"`. With YAML round-trip this double-escapes. Fixed the one production caller (`_verify_memory`).

### Commits
- `85816b6` — Phase 1: CompactDumper + writer + list ops + dump_markdown_file
- `0846840` — Phase 2: --tag/--untag on all 17 edit commands

### Verification
- 4040 passed, 4 skipped, 1 deselected (pre-existing `test_raises_not_found_for_missing_backlog`)
- 59 writer tests (CompactDumper + update_frontmatter + list ops + backward-compat wrappers)
- pylint 10.00/10 on touched files

## Outstanding — Phase 3

### Not yet done
- [ ] One-time normalisation of all `.spec-driver/**/*.md` frontmatter
- [ ] Backlog item for client repo migration strategy
- [ ] Phase sheet updates
- [ ] Audit and closure

### Normalisation approach
Write a script that walks all `.spec-driver/**/*.md`, calls `load_markdown_file` → `dump_markdown_file` (which now uses CompactDumper). Body untouched. One atomic commit.

### Gotcha for next agent
- The user has already run prettier over all markdown. Body content may have changed formatting. The normalisation commit should only touch frontmatter YAML — `dump_markdown_file` already handles this correctly since it preserves body as-is.
- `_FLOW_LIST_WIDTH_LIMIT = 80` in frontmatter_writer.py controls the flow/block heuristic threshold. This is a tuning knob if output doesn't look right on real files.
