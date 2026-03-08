# Notes for DE-065

## Status

All 3 phases complete. Delta closed.

## Completed

- DE-065 scoped from IMPR-007
- DR-065 drafted, adversarially reviewed (2 passes), revised
  - Key revision: DEC-065-02/03 changed from regex parser to fenced YAML blocks
  - DEC-065-06 added typed substructures (Source, Claim, DiscoveredBy)
  - IMPR-007 "binding" language softened to "authoritative starting point"
  - `backlog` added to RESOLUTION_PATHS (pilot divergence from schema draft)
  - DE-063 CLI integration points documented in DR-065 §6
- IP-065 planned with 3 phases
- Phase 1 implemented: models, parser, registry, paths.py, 65 tests, linters clean
- Pre-existing PROB-001 test failure fixed
- Phase 2 implemented: formatters, CLI, DE-063 integration, 41 new tests

### Phase 2 details

- `drift_formatters.py`: list table (via `format_list_table`), detail view, JSON
  - Used `format_list_table()` from table_utils (generic helper) rather than hand-rolling table setup
  - Extracted `_entry_to_dict()` to keep McCabe complexity down on JSON serializer
- `drift/creation.py`: `create_drift_ledger()` with sequential ID allocation
  - Scans existing DL-*.md files for max ID, increments
  - Creates `.spec-driver/drift/` directory on demand
  - Template matches DR-065 §10 exactly
- CLI commands added directly in `create.py`, `list.py`, `show.py` (not a separate drift.py — CLI commands live in the verb-grouped modules, not per-artifact modules)
- DE-063 integration: 6 extension points wired per DR-065 §6 table
  - `PREFIX_TO_TYPE["DL"] = "drift_ledger"`
  - `_resolve_drift_ledger`, `_find_drift_ledgers` in common.py
  - `_collect_drift_ledgers` in resolve.py → build_artifact_index()
  - `show_drift` + show_handlers entry in show.py
  - `view_drift` in view.py
- Theme: drift ledger + entry status styles, `drift.id` style
- Column defs: `DRIFT_COLUMNS` in column_defs.py
- ID inference works: `spec-driver show DL-001` resolves via prefix

### Phase 2 commits

- `a53cde3` docs(DE-065): create phase 2 sheet
- `46fe97d` feat(DE-065): add drift formatters, CLI commands, DE-063 integration (P02)

## Verification

- `just check` green: 3285 tests pass, ruff clean, formatter clean
- New files score 10.00/10 on pylint
- Pre-existing pylint warnings in CLI modules unchanged (import-outside-toplevel pattern, duplicate-code across similar show/view commands)

## New Agent Instructions

### Task card

Delta: `.spec-driver/deltas/DE-065-drift_ledger_primitive/DE-065.md`
Notes: `.spec-driver/deltas/DE-065-drift_ledger_primitive/notes.md`

### Next: Phase 3 — Migration & close

Create phase 3 sheet:
  `uv run spec-driver create phase "Migration and close" --plan IP-065`

Tasks:
1. Migrate pilot DL-047 from `drift/` to `.spec-driver/drift/`
   - Convert entry format from pilot list-item to fenced YAML blocks
   - Update any references to old path
2. End-to-end verification: `create drift`, `list drift`, `show drift DL-047`
3. Delta closure: `spec-driver complete delta DE-065`

### Key files (phase 2 — all implemented)

- `supekku/scripts/lib/formatters/drift_formatters.py` — list table, detail, JSON
- `supekku/scripts/lib/drift/creation.py` — create_drift_ledger()
- `supekku/cli/common.py` — PREFIX_TO_TYPE, resolver, finder for drift_ledger
- `supekku/cli/resolve.py` — _collect_drift_ledgers in build_artifact_index
- `supekku/cli/create.py` — `create drift` command
- `supekku/cli/list.py` — `list drift` command
- `supekku/cli/show.py` — `show drift` command + show_handlers entry
- `supekku/cli/view.py` — `view drift` command
- `supekku/scripts/lib/formatters/column_defs.py` — DRIFT_COLUMNS
- `supekku/scripts/lib/formatters/theme.py` — drift status/entry styles

### Adaptations from DR-065

- DR-065 listed `supekku/scripts/drift.py` as a new thin CLI file. Instead, commands were added to the existing verb-grouped modules (create.py, list.py, show.py) — this follows the actual codebase pattern where all CLI commands live in verb modules, not artifact modules.
- `format_list_table()` generic helper was used instead of hand-building table setup (existed from a prior refactor, not known when DR-065 was drafted)

### Phase 3 details

- Migrated pilot DL-047 from `drift/` to `.spec-driver/drift/`
- Converted all 21 entries from list-item format to fenced YAML blocks (DEC-065-02)
- `analysis` field content moved outside YAML fence as freeform markdown
- `evidence` field kept inside fence as YAML list
- Parser roundtrips all 21 entries correctly
- `list drift` and `show drift DL-047` both work
- Old `drift/` directory removed
- Delta closed without `--force`

### Phase 3 commits

- `55d1632` feat(DE-065): migrate pilot DL-047 to fenced YAML format (P03)

### Loose ends

- `drift/__init__.py` exports are still empty (`__all__: list[str] = []`) — acceptable for now, consumers import from submodules directly
- Pilot DL-047 migration is phase 3
- `--delta` flag on `create drift` is implemented (optional `--delta DE-NNN`)
- No `ARTIFACT_PREFIXES` entry for drift (DL IDs don't use numeric-only normalization — DL-047 is always fully qualified). This is correct per current design.
