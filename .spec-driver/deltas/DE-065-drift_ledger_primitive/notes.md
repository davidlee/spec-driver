# Notes for DE-065

## Status

Phase 1 (domain layer) complete. Phase 2 (formatters, CLI, DE-063 integration)
is next. Delta is `in-progress`.

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

## New Agent Instructions

### Task card

Delta: `.spec-driver/deltas/DE-065-drift_ledger_primitive/DE-065.md`
Notes: `.spec-driver/deltas/DE-065-drift_ledger_primitive/notes.md`

### Required reading

- DR-065: `.spec-driver/deltas/DE-065-drift_ledger_primitive/DR-065.md`
  - §6 (DE-063 CLI Integration) — extension points table
  - §7 (Model Design) — model shapes
  - §10 (Authoring & Creation) — creation template
- IP-065: `.spec-driver/deltas/DE-065-drift_ledger_primitive/IP-065.md`
- Phase 1 sheet: `.spec-driver/deltas/DE-065-drift_ledger_primitive/phases/phase-01.md`

### Key files (implemented in phase 1)

- `supekku/scripts/lib/drift/__init__.py`
- `supekku/scripts/lib/drift/models.py` — DriftLedger, DriftEntry, Source, Claim, DiscoveredBy
- `supekku/scripts/lib/drift/parser.py` — parse_ledger_body()
- `supekku/scripts/lib/drift/registry.py` — DriftLedgerRegistry
- `supekku/scripts/lib/core/paths.py` — DRIFT_SUBDIR, get_drift_dir()

### Key files (to modify/create in phase 2)

- `supekku/scripts/lib/formatters/drift_formatters.py` — NEW: pure format functions
- `supekku/scripts/drift.py` — NEW: thin CLI (create/list/show)
- `supekku/cli/common.py` — MODIFY: PREFIX_TO_TYPE, _ARTIFACT_RESOLVERS, _ARTIFACT_FINDERS
- `supekku/cli/resolve.py` — MODIFY: build_artifact_index() + _collect_drift_ledgers()
- `supekku/cli/show.py` — MODIFY: show_drift_ledger handler, show_handlers entry
- `supekku/cli/view.py` — MODIFY: view_drift_ledger handler

### Pattern references (for phase 2)

- Formatter pattern: `supekku/scripts/lib/formatters/backlog_formatters.py`
- Table rendering: `supekku/scripts/lib/formatters/table_utils.py` — use `add_row_with_truncation()` with `Text.from_markup()`
- CLI thin command pattern: `supekku/scripts/list_backlog.py` or similar
- ID inference registration: `supekku/cli/common.py` lines 515-530 (PREFIX_TO_TYPE)
- Resolver pattern: `supekku/cli/common.py` lines 466-482 (_ARTIFACT_RESOLVERS)
- InferringGroup: `supekku/cli/common.py` lines 594-618 (TyperGroup subclass, 3-tuple return)
- Cross-registry index: `supekku/cli/resolve.py` lines 145-163 (build_artifact_index)

### Relevant decisions

- DEC-065-02: entry data in fenced YAML blocks (not the pilot list-item format)
- DR-065 §10 creation template: frontmatter + `## Entries` heading, no template entry
- `--delta DE-NNN` flag on `create drift` recommended but open question
- Formatters must use Rich markup-aware truncation (DE-063 pattern)

### Loose ends

- Phase 2 sheet (`phases/phase-02.md`) needs to be created via `spec-driver create phase`
- `.spec-driver/drift/` directory doesn't exist yet — `create drift` should create it
- No `py.typed` or exports updated in `drift/__init__.py` yet
- Pilot DL-047 migration is phase 3, not phase 2

### Commit guidance

- `.spec-driver/**` changes from phase sheet creation should be committed
  promptly per doctrine (bias toward frequent small commits of workflow artefacts)
- Code changes and `.spec-driver` changes can go together or separately
