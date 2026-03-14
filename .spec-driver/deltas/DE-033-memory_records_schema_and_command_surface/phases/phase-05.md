---
id: IP-033.PHASE-05
slug: 033-memory_records_schema_and_command_surface-phase-05
name: IP-033 Phase 05 - Formatters, Docs, and Validation
created: '2026-03-02'
updated: '2026-03-02'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-033.PHASE-05
plan: IP-033
delta: DE-033
objective: >-
  Complete memory formatter coverage, fix theme gaps, author real memory
  records to validate display and behavior, update schema docs and YAML
  example, and produce a CLI reference document to support external skills
  authoring.
entrance_criteria:
  - Phase 3 complete (CLI surface working)
  - Phase 4 complete (selection and filtering working)
  - Formatter module exists with list/detail/JSON functions
exit_criteria:
  - Detail formatter renders all non-empty model fields
  - Theme includes all valid memory statuses (incl. deprecated)
  - ≥2 real memory records committed and visible in list/show output
  - Frontmatter schema doc updated to match implementation
  - schema show yaml-example includes scope/priority/provenance
  - CLI reference doc authored (memory commands + valid frontmatter)
  - Formatter tests cover full-field detail, truncate, TSV columns
  - Lint + tests passing
verification:
  tests:
    - VT-MEM-FMT-001 - Full-field detail formatter coverage
  evidence:
    - Real memory records displayed via list/show/tsv/json
    - schema show frontmatter.memory --format yaml-example output
    - Lint checks passing (ruff + pylint)
tasks:
  - id: "5.1"
    description: "Extend detail formatter to render all non-empty model fields"
  - id: "5.2"
    description: "Theme gap: add deprecated + superseded + obsolete memory statuses"
  - id: "5.3"
    description: "Formatter tests: full-field detail, truncate, TSV column consistency"
  - id: "5.4"
    description: "Create ≥2 real memory records to validate display and selection behavior"
  - id: "5.5"
    description: "Update frontmatter-schema.md and schema show yaml-example"
  - id: "5.6"
    description: "Author CLI reference doc for memory commands (skills input)"
risks:
  - description: "Detail formatter complexity — rendering nested dicts (scope, priority, provenance)"
    mitigation: "Follow decision_formatters.py pattern; keep it flat with key: value lines"
  - description: "yaml-example requires schema module changes"
    mitigation: "Check schema generation code first; may be config-only"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-033.PHASE-05
```

# Phase 5 - Formatters, Docs, and Validation

## 1. Objective

Complete the memory artifact surface by: filling formatter gaps, fixing theme
holes, validating with real records, updating schema documentation, and
producing a CLI reference document to support external skills authoring.

## 2. Links & References

- **Delta**: DE-033
- **DR Sections**: DR-033 §9 (code_impacts for formatters)
- **Requirement**: MEM-FR-002 (CLI), MEM-NFR-001 (schema discoverability)
- **Frontmatter schema**: `supekku/about/frontmatter-schema.md` (lines 408-439)
- **Reference pattern**: `decision_formatters.py` (full-field detail rendering)

## 3. Entrance Criteria

- [x] Phase 3 complete (CLI surface working)
- [x] Phase 4 complete (selection and filtering working)
- [x] Formatter module exists with list/detail/JSON

## 4. Exit Criteria / Done When

- [x] Detail formatter renders all non-empty fields (verified, review_by, owners, scope, priority, provenance, relations, audience, visibility, requires_reading)
- [x] Theme covers deprecated, superseded, obsolete statuses
- [x] ≥2 real memory records committed and validated
- [x] Frontmatter schema doc accurate and current
- [x] `schema show frontmatter.memory --format yaml-example` includes richer example
- [x] CLI reference doc authored (all memory commands + frontmatter reference)
- [x] Formatter tests comprehensive
- [x] Lint + tests passing

## 5. Verification

- `uv run pytest supekku/scripts/lib/formatters/memory_formatters_test.py -v`
- `uv run spec-driver list memories` / `show memory MEM-001` with real records
- `uv run spec-driver schema show frontmatter.memory --format yaml-example`
- `just lint` + `just pylint`

## 6. Assumptions & STOP Conditions

- Assumptions: yaml-example generation can be enriched via schema definition changes
- STOP when: schema module changes would affect other artifact families

## 7. Tasks & Progress

| Status | ID  | Description                                                 | Notes                                                                                     |
| ------ | --- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [x]    | 5.1 | Extend detail formatter — render all non-empty model fields | 5 helpers, 5 new tests (21 total)                                                         |
| [x]    | 5.2 | Theme: add deprecated/superseded/obsolete memory statuses   | 3 entries, pylint 10/10                                                                   |
| [x]    | 5.3 | Formatter tests: full-field detail, truncate, TSV columns   | +6 tests (27 total): truncate, TSV cols/content/no-confidence, JSON ISO dates, null dates |
| [x]    | 5.4 | Create ≥2 real memory records, validate display             | MEM-001 (Skinny CLI), MEM-002 (Formatter SoC); validated table/tsv/json/detail            |
| [x]    | 5.5 | Update frontmatter-schema.md + schema yaml-example          | Doc verified accurate; swapped example order so yaml-example shows full fields            |
| [x]    | 5.6 | Author CLI reference doc (memory commands + frontmatter)    | `memory-cli-reference.md` in delta bundle; covers 4 commands + all frontmatter            |

### Task Details

- **5.1 Detail formatter**
  - **Files**: `supekku/scripts/lib/formatters/memory_formatters.py`
  - `_format_detail_lines` currently renders 10 fields. Missing: `verified`, `review_by`, `owners`, `requires_reading`, `audience`, `visibility`, `scope`, `priority`, `provenance`, `relations`.
  - Render nested dicts (scope, priority, provenance) as flattened key-value or indented sub-lines.
  - Only render non-empty fields (existing pattern).

- **5.2 Theme gaps**
  - **Files**: `supekku/scripts/lib/formatters/theme.py`
  - Add: `memory.status.deprecated`, `memory.status.superseded`, `memory.status.obsolete`
  - These are valid statuses per `_EXCLUDED_STATUSES` in selection.py.

- **5.3 Formatter tests**
  - **Files**: `supekku/scripts/lib/formatters/memory_formatters_test.py`
  - Add `test_full_record_detail` covering all fields
  - Add `test_truncate_table` for truncate=True path
  - Add TSV column count/content assertion
  - Verify JSON date serialization produces ISO strings

- **5.4 Real memory records**
  - Create at least 2 records in `memory/` with meaningful scope, priority, tags
  - Validate: `list memories`, `show memory MEM-001`, `list memories --path ...`, `list memories --format tsv`
  - Verify table alignment, detail view completeness, JSON structure

- **5.5 Schema docs**
  - **Files**: `supekku/about/frontmatter-schema.md` (lines 408-439), schema definition module
  - Verify memory section accuracy vs actual implementation
  - Enrich yaml-example to show scope/priority/provenance (currently shows minimal fields only)
  - Add v1 note about block metadata deferral (already present at line 439, verify)

- **5.6 CLI reference doc**
  - **Location**: TBD (likely `supekku/about/` or delta notes)
  - Cover: `create memory`, `list memories`, `show memory`, `find memory`
  - Include: all options, scope matching semantics, valid frontmatter fields
  - Purpose: input for skills authoring in external repo

## 8. Risks & Mitigations

| Risk                                         | Mitigation                              | Status    |
| -------------------------------------------- | --------------------------------------- | --------- |
| Nested dict rendering complexity             | Follow decision_formatters flat pattern | mitigated |
| Schema example changes affect other families | Scope change to memory schema only      | open      |

## 9. Decisions & Outcomes

- `2026-03-02` - Detail formatter follows decision_formatters.py sectioned-helpers pattern: `_format_dates`, `_format_scope`, `_format_priority`, `_format_provenance`, `_format_relations`. Each returns `list[str]`, flattened in `_format_detail_lines`.
- `2026-03-02` - Nested dicts (scope, priority, provenance) rendered as header + indented sub-lines (e.g. `Scope:\n  paths: ...`). Keeps output scannable without over-engineering.
- `2026-03-02` - Theme uses `#cc241d` (red) for deprecated/superseded/obsolete, matching all other artifact families.

## 10. Findings / Research Notes

- `format_as_json` uses `default=str` — date serialization is safe (str(date) → ISO format)
- TSV outputs 6 columns (id, status, memory_type, name, confidence, updated); table has 7 (includes tags) — minor inconsistency, note for 5.3
- `schema show frontmatter.memory --format yaml-example` currently shows minimal fields only — needs enrichment in 5.5
- No `memory/` directory exists yet in repo — first real records will create it in 5.4

## Implementation State (handover)

### Completed (5.1–5.2)

- **`memory_formatters.py`** — `_format_detail_lines` refactored with 5 section helpers:
  - `_format_dates(record)` — verified, review_by, created, updated (skip if None)
  - `_format_scope(scope)` — header + indented paths/globs/commands/languages/platforms
  - `_format_priority(priority)` — header + severity/weight
  - `_format_provenance(provenance)` — header + sources with kind/ref/note
  - `_format_relations(relations)` — header + type → target (annotation)
  - Also added inline: owners, audience, visibility, requires_reading as comma-joined lists
  - All sections skip cleanly when empty
- **`theme.py`** — added `memory.status.deprecated`, `.superseded`, `.obsolete` (`#cc241d` red)
- **`memory_formatters_test.py`** — 21 tests (was 16): added `test_full_record` (all fields), `test_empty_scope_omitted`, `test_empty_priority_omitted`, `test_empty_provenance_omitted`, `test_empty_relations_omitted`
- **Full suite**: 1940 passed, 3 skipped. Ruff clean. Pylint 10/10 on changed files.

### Completed (5.3–5.6)

- **5.3** Formatter tests: +6 tests (27 total). Added: `test_truncate_table`, `test_tsv_column_count`, `test_tsv_column_content`, `test_tsv_no_confidence`, `test_date_serialization_iso`, `test_null_dates_in_json`.
- **5.4** Created MEM-001 (Skinny CLI Pattern) and MEM-002 (Formatter Separation of Concerns) with scope, priority, provenance, relations, audience, visibility. Validated across all 4 display paths (table, tsv, json, detail).
- **5.5** Frontmatter schema doc verified accurate. Swapped example order in `frontmatter_metadata/memory.py` so `yaml-example` shows the full-field example by default (was minimal).
- **5.6** CLI reference doc authored at `memory-cli-reference.md` in delta bundle. Covers all 4 commands, all options, scope matching semantics, ordering, full frontmatter reference with nested objects.

### Phase 5 Summary

- **Tests**: 1946 passed, 3 skipped. 27 formatter tests.
- **Lint**: ruff clean, pylint 10/10 on all changed files.
- **Files changed**: `memory_formatters_test.py`, `frontmatter_metadata/memory.py`
- **Files created**: `memory/MEM-001-skinny_cli_pattern.md`, `memory/MEM-002-formatter_separation_of_concerns.md`, `memory-cli-reference.md`
