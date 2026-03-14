# Notes for DE-080

## Implementation (2026-03-09)

### Changes

1. **`config.py`**: Renamed `DEFAULT_CONFIG["cards"]` → `["kanban"]`, merged `["docs"]` keys (`artefacts_root`, `plans_root`) into `["kanban"]`. Updated `_SECTION_COMMENTS`. Added `_migrate_legacy_keys()` compat shim called by `_merge_defaults()`.

2. **Templates**: `glossary.md` — card explanation now renders unconditionally; kanban-specific details (root, id_prefix) remain gated on `config.kanban.enabled`. `workflow.md` — updated variable paths from `config.cards.*`/`config.docs.*` to `config.kanban.*`.

3. **Tests**: Updated all `config_test.py` and `install_test.py` assertions to use `kanban` key. Added 3 new tests for legacy `[cards]`/`[docs]` → `[kanban]` migration.

4. **Project `workflow.toml`**: Renamed `[cards]`/`[docs]` to `[kanban]` with merged keys.

5. **Memory**: Updated `mem.reference.spec-driver.workflow-config.md` to document `[kanban]` section and compat note.

### Verification

- `just check` passes (3507 tests, 0 failures, ruff clean)
- Regenerated agent docs via `spec-driver install` — glossary renders card explanation with `kanban.enabled = false`
