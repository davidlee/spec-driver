---
id: IP-033.PHASE-06
slug: 033-memory_records_schema_and_command_surface-phase-06
name: IP-033 Phase 06 - Semantic Memory ID Scheme
created: "2026-03-02"
updated: "2026-03-02"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-033.PHASE-06
plan: IP-033
delta: DE-033
objective: >-
  Replace sequential MEM-NNN IDs with semantic dot-separated IDs
  (mem.<type>.<domain>.<subject>[.<purpose>]) to improve readability,
  linkability, and grep-ability. Migrate existing records, update
  creation/registry/CLI/tests, and add ID validation.
entrance_criteria:
  - Phase 5 complete (formatters, real records, schema docs)
  - ID spec reviewed and accepted (id-spec.md in delta bundle)
exit_criteria:
  - Memory IDs use canonical form mem.<type>.<topic>... throughout
  - create memory accepts user-supplied ID (required arg or --id)
  - Registry discovers mem.*.md files (not MEM-*.md)
  - find/show accept shorthand (omitted mem. prefix) and canonical
  - Validation rejects malformed IDs; warns on type/memory_type mismatch
  - Existing MEM-001, MEM-002 migrated to semantic IDs
  - All tests updated and passing
  - Lint clean
verification:
  tests:
    - VT-MEM-ID-001 - ID validation (canonical, shorthand, rejection)
    - VT-MEM-ID-002 - Registry discovers new file naming
    - VT-MEM-ID-003 - Creation with user-supplied ID
  evidence:
    - create/list/show/find work with semantic IDs
    - Lint passing (ruff + pylint)
tasks:
  - id: "6.1"
    description: "ID validation module: canonical form, normalization, type extraction"
  - id: "6.2"
    description: "Rewrite creation.py: user-supplied ID, validation, file naming"
  - id: "6.3"
    description: "Update registry.py: glob pattern, file parsing for new naming"
  - id: "6.4"
    description: "Update CLI: create (--id required), find/show normalization, common.py prefix"
  - id: "6.5"
    description: "Migrate existing records (MEM-001, MEM-002) to semantic IDs"
  - id: "6.6"
    description: "Update all test fixtures and verify full suite"
  - id: "6.7"
    description: "Update schema examples, CLI reference doc, frontmatter-schema.md"
risks:
  - description: "Blast radius in test fixtures (~271 MEM- references across 7 test files)"
    mitigation: "Mechanical replacement; run full suite after each file"
  - description: "Shorthand normalization ambiguity (e.g., system.auth vs mem.system.auth)"
    mitigation: "Simple rule: if no mem. prefix, prepend it. No registry lookup needed for normalization."
  - description: "Type segment vs memory_type mismatch"
    mitigation: "Warn on create, don't block. Frontmatter memory_type remains authoritative per spec."
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-033.PHASE-06
```

# Phase 6 — Semantic Memory ID Scheme

## 1. Objective

Replace sequential `MEM-NNN` IDs with semantic dot-separated IDs
(`mem.<type>.<domain>.<subject>[.<purpose>]`) per the ID spec in the delta
bundle. This improves human readability, makes IDs greppable by domain, and
prepares for `[[obsidian]]` link resolution in a future phase.

## 2. Links & References

- **ID Spec**: `id-spec.md` (delta bundle)
- **Delta**: DE-033
- **Existing code**: `creation.py`, `registry.py`, `common.py`, `find.py`, `show.py`
- **Test files**: `memory_test.py`, `registry_test.py`, `selection_test.py`, `models_test.py`, `creation_test.py`, `memory_formatters_test.py`, `frontmatter_metadata/memory_test.py`

## 3. Entrance Criteria

- [x] Phase 5 complete
- [x] ID spec reviewed

## 4. Exit Criteria / Done When

- [x] ID validation function: `validate_memory_id(raw) -> canonical | error`
- [x] `normalize_memory_id(raw) -> canonical` (prepend `mem.` if missing)
- [x] `extract_type_from_id(id) -> str | None` (second segment)
- [x] `create memory` requires user-supplied ID (positional), `--name` for display name
- [x] Warn (don't block) if ID type segment disagrees with `--type`
- [x] Registry discovers `mem.*.md` files
- [x] File naming: `mem.<full.id>.md` (e.g., `mem.pattern.cli.skinny.md`)
- [x] `find memory` and `show memory` accept shorthand (e.g., `pattern.cli.skinny`)
- [x] `common.py` prefix table updated (memory removed from ARTIFACT_PREFIXES)
- [x] MEM-001, MEM-002 migrated
- [x] 1984 tests pass (up from 1946)
- [x] Ruff clean, pylint 9.68

## 5. Verification

- `uv run pytest supekku/ -v --tb=short`
- `uv run spec-driver create memory mem.test.smoke --type fact`
- `uv run spec-driver list memories`
- `uv run spec-driver show memory mem.pattern.cli.skinny`
- `uv run spec-driver find memory "mem.pattern.*"`
- `just lint` + `just pylint`

## 6. Assumptions & STOP Conditions

- Assumptions:
  - ID charset is `[a-z0-9-]+` per segment, separated by `.`
  - 3–6 segments recommended; 2 minimum (`mem.<type>`)
  - Hyphens allowed within segments (e.g., `oauth-migration`)
  - File naming uses the full canonical ID as filename stem
- STOP when:
  - Changes would affect non-memory ID normalization in `common.py`
  - Changes require modifications to other artifact registries

## 7. Tasks & Progress

| Status | ID  | Description                     | Notes                                                                                                      |
| ------ | --- | ------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [x]    | 6.1 | ID validation module            | `memory/ids.py`: validate, normalize, extract_type, filename_from_id. 35 tests.                            |
| [x]    | 6.2 | Rewrite creation.py             | User-supplied ID, normalize on create, type mismatch warning, filename_from_id. 13 tests.                  |
| [x]    | 6.3 | Update registry.py              | `mem.*.md` glob, frontmatter-first ID, filename-stem fallback. 21 tests (2 new).                           |
| [x]    | 6.4 | Update CLI commands             | create takes semantic ID positional + --name, find/show shorthand normalization, common.py prefix removed. |
| [x]    | 6.5 | Migrate existing records        | MEM-001 → mem.pattern.cli.skinny, MEM-002 → mem.pattern.formatters.soc. Cross-refs updated.                |
| [x]    | 6.6 | Update test fixtures            | ~195 MEM- refs replaced across 7 test files. 1984 tests pass.                                              |
| [x]    | 6.7 | Update docs and schema examples | frontmatter metadata examples updated, **init**.py exports ids functions.                                  |

### Task Details

- **6.1 ID validation module** (`supekku/scripts/lib/memory/ids.py`)
  - `MEMORY_ID_PATTERN = r'^mem\.[a-z0-9-]+(\.[a-z0-9-]+){1,5}$'`
  - `validate_memory_id(raw: str) -> str` — returns canonical or raises ValueError
  - `normalize_memory_id(raw: str) -> str` — prepend `mem.` if missing, lowercase
  - `extract_type_from_id(memory_id: str) -> str | None` — second segment
  - `filename_from_id(memory_id: str) -> str` — `{id}.md`
  - Tests first (TDD)

- **6.2 Rewrite creation.py**
  - `create_memory` takes user-supplied ID instead of auto-generating
  - Remove `generate_next_memory_id` (or deprecate)
  - `MemoryCreationOptions` gains `memory_id: str` field
  - File naming: `{canonical_id}.md` (dots in filename are fine)
  - Warn if `extract_type_from_id(id)` != `memory_type`
  - Uniqueness check against registry

- **6.3 Update registry.py**
  - `self.directory.glob("MEM-*.md")` → `self.directory.glob("mem.*.md")`
  - `_parse_memory_file`: relax filename regex, use frontmatter `id` as primary
  - Fallback: derive ID from filename stem if frontmatter missing

- **6.4 Update CLI commands**
  - `create memory`: change `NAME` positional to `ID`, add `--name` option (or keep NAME and add `--id`)
  - `find memory`: pattern matching on dot-separated IDs (`mem.pattern.*`)
  - `show memory`: `normalize_memory_id` on input
  - `common.py`: remove `"memory": "MEM-"` from `ARTIFACT_PREFIXES` (no longer numeric shorthand)

- **6.5 Migrate existing records**
  - `MEM-001-skinny_cli_pattern.md` → `mem.pattern.cli.skinny.md`
  - `MEM-002-formatter_separation_of_concerns.md` → `mem.pattern.formatters.soc.md`
  - Update frontmatter `id` fields
  - Update `relations` cross-references

- **6.6 Update test fixtures**
  - Mechanical: replace `MEM-001` → `mem.fact.test.alpha` (or similar test IDs)
  - Replace `MEM-002`, `MEM-003`, etc. with distinct semantic IDs
  - Update file naming in test helpers/fixtures
  - Run suite after each file

- **6.7 Update docs and schema examples**
  - `frontmatter_metadata/memory.py` examples: `MEM-042` → `mem.signpost.auth.prereading`, `MEM-001` → `mem.fact.example`
  - `frontmatter-schema.md` memory section: update ID format, add canonical form description
  - `memory-cli-reference.md` (delta bundle): update command examples, add ID format section, update `create memory` syntax
  - `supekku/about/glossary.md`: update Memory Records entry if it references MEM-NNN
  - Phase 5 real records: update body/frontmatter cross-references if needed

## 8. Risks & Mitigations

| Risk                           | Mitigation                                 | Status |
| ------------------------------ | ------------------------------------------ | ------ |
| Test fixture churn (~271 refs) | Mechanical replacement, run suite per file | open   |
| Shorthand ambiguity            | Simple prefix rule, no registry lookup     | open   |
| Type mismatch                  | Warn only, frontmatter authoritative       | open   |

## 9. Decisions & Outcomes

- Canonical form: `mem.<type>.<domain>.<subject>[.<purpose>]`
- Charset: `[a-z0-9-]+` per segment, `.` separator, lowercase enforced
- File naming: `<canonical_id>.md` (e.g., `mem.pattern.cli.skinny.md`)
- Type segment is a hint; `memory_type` in frontmatter is authoritative
- No auto-generation; user supplies ID at creation time

## 10. Findings / Research Notes

- `common.py` `ARTIFACT_PREFIXES` table used by `normalize_id()` for numeric shorthand — memory entry must be removed since new IDs aren't numeric
- `find.py` uses fnmatch patterns — works naturally with dot-separated IDs
- `registry.py` glob is the main discovery mechanism; changing the pattern is straightforward
- `_parse_memory_file` currently derives ID from filename regex — needs to become frontmatter-first
