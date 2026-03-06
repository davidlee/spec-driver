# Notes for DE-045

## Phase 1 (complete)

- `compute_backlinks()` and `expand_link_graph()` added to `memory/links.py` as pure functions
- Graph formatters (table/tree/json) added to `memory_formatters.py`
- `emit_artifact` extended with `body_only` mode in `cli/common.py`
- `show_memory` migrated to use `emit_artifact` (zero regression)
- 32 new tests

## Phase 2 (complete)

- `MemoryRegistry.collect_bodies()` added for shared body extraction (3 tests)
- `list memories --links-to <id>` wired via `compute_backlinks()` — backlink filter bypasses normal filter pipeline, returns source memories sorted by ID
- `show memory --links-depth N [--tree] [--json]` wired via `expand_link_graph()` — graph expansion mode short-circuits before `emit_artifact`
- `show memory --body-only/-b` already wired from phase 1 migration
- 16 new CLI integration tests
- VA walkthrough confirmed all DE-045 §6 acceptance criteria

### Design notes

- `--links-to` normalizes shorthand IDs via `normalize_memory_id` before computing backlinks
- `--links-depth` builds bodies/names/types dicts from registry then delegates to pure `expand_link_graph` — the CLI stays thin
- Graph expansion mode in `show_memory` is handled before `emit_artifact` dispatch since it has different output semantics (graph, not single artifact)
