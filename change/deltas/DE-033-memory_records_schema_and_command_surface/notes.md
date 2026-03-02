# Notes for DE-033

## Phase 1 Slice: Memory Frontmatter Metadata Schema

### Completed

1. **Base kind enum** (`base.py`): Added `"memory"` to `kind` field `enum_values`, alphabetically ordered.

2. **Memory metadata profile** (`memory.py`): Created `MEMORY_FRONTMATTER_METADATA` extending base with memory-specific fields:
   - `memory_type` (required enum): concept, fact, pattern, signpost, system, thread
   - `confidence` (optional enum): low, medium, high
   - `verified` / `review_by` (optional ISO-8601 dates)
   - `requires_reading` (optional string array): pre-reading artifact paths/IDs
   - `scope` (optional object): globs, paths, commands, languages, platforms
   - `priority` (optional object): severity enum + weight int
   - `provenance` (optional object): sources array with kind/ref/note
   - `audience` (optional enum array): human, agent
   - `visibility` (optional enum array): pre, on_demand

3. **Registry** (`__init__.py`): Imported and registered `MEMORY_FRONTMATTER_METADATA` under `"memory"` key.

4. **Tests** (`memory_test.py`): 28 dual-validation tests covering:
   - Valid: minimal, all fields, all enum values, partial objects, empty arrays
   - Invalid: missing required, bad enums, bad date formats, wrong types, empty strings in arrays

5. **Schema CLI**: `schema show frontmatter.memory` works for both `--format json-schema` and `--format yaml-example`. Memory appears in `schema list frontmatter`.

6. **Docs**: Updated `supekku/about/frontmatter-schema.md` with Memory Records section.

### Design decisions

- `memory_type` (not `type`) avoids Python builtin collision and is clearer in frontmatter context.
- JAMMS `time.verified/review_by` mapped to top-level `verified`/`review_by` for consistency with existing date fields.
- JAMMS `owner.contact` maps to existing base `owners` array — no new field needed.
- JAMMS `policy.audience/visibility` flattened to top-level arrays, matching spec-driver's flat field convention.
- JAMMS `relations.requires_reading` promoted to top-level `requires_reading` array for direct filtering.
- JAMMS `relations.supersedes/superseded_by` handled by existing base `relations` array.
- MEM-NFR-001 satisfied: no YAML block metadata defined for v1.

### Next steps (from Phase 1)

- ~~Memory domain package (model, registry, selection/filtering logic)~~ → Phase 2 complete
- CLI commands (create memory, list memories, show memory, find memory)
- Formatters
- Runtime frontmatter parsing integration (frontmatter_schema.py currently does not enforce kind-specific fields at parse time — metadata validator is the enforcement path)

## Phase 2: Domain Model & Registry

### Completed

1. **Package**: Created `supekku/scripts/lib/memory/` with `__init__.py`, `models.py`, `registry.py`.

2. **MemoryRecord** (`models.py`): Dataclass with 20 fields mirroring memory frontmatter schema.
   - `from_frontmatter(path, fm)` classmethod — constructs from parsed YAML dict.
   - `to_dict(root)` — serializes for YAML registry output, relativizes paths, omits empty optionals.
   - `_parse_date()` module-level helper for date string/object parsing.

3. **MemoryRegistry** (`registry.py`): Discovery and query engine for MEM-*.md files.
   - `collect()` — globs MEM-*.md, parses frontmatter, returns dict[id, MemoryRecord].
   - `find(id)` — lookup by ID.
   - `iter(status=)` — iterate with optional status filter.
   - `filter(memory_type=, status=, tag=)` — multi-criteria AND filter.
   - Constructor accepts `directory` kwarg, defaulting to `root / "memory"`.

4. **Tests**: 30 tests total (11 model + 19 registry). All passing.

5. **Lint**: ruff clean, pylint 9.98/10.

6. **Side-effect**: Updated `KNOWN_LEAF_PACKAGES` in `package_utils_test.py` (21→22).

### Design decisions

- `_parse_date` is a module-level function (not a method). Reduces coupling. Consolidation with DecisionRegistry.parse_date is a future opportunity.
- Test fixtures are inline YAML in `registry_test.py`. No separate fixture files — simpler, self-contained.
- Memory file storage convention: `memory/` at repo root, configurable via `MemoryRegistry(directory=...)`.

### Observations

- `parse_date` logic is duplicated across DecisionRegistry, PolicyRegistry, StandardRegistry. Worth extracting to `core/` in a future cleanup delta.
- The `too-many-instance-attributes` pylint warning on MemoryRecord is expected (same as DecisionRecord). Not suppressed.

### Next steps

- Phase 3: CLI surface — phase sheet created at `phases/phase-03.md`
- Phase 4: Selection & deterministic filtering/ordering
- Phase 5: Formatters refinement & docs
- Phase 6: Verification & skills

## Handover — Phase 3 pickup

Phase 3 sheet is at `phases/phase-03.md` with 8 tasks. Start with `/preflight DE-033/3.1`.

Key context for the next agent:

1. **Reference implementations are well-established**:
   - Creation: `decisions/creation.py` → `ADRCreationOptions`, `create_adr()`, `generate_next_adr_id()`
   - Formatters: `formatters/decision_formatters.py` → `format_decision_details()`, `format_decision_list_table()`
   - CLI: `cli/create.py` (`create_adr`), `cli/list.py` (`list_adrs`), `cli/show.py` (`show_adr`), `cli/find.py` (`find_adr`)

2. **Shared utilities already handle most plumbing**:
   - `normalize_id()` in `cli/common.py` — just needs `"memory": "MEM-"` added to `ARTIFACT_PREFIXES`
   - `table_utils.py` — `create_table`, `render_table`, `format_as_json`, `format_as_tsv`
   - `matches_regexp()` in `cli/common.py` for `--regexp` filtering

3. **Watch for file size**: `list.py` is ~2000 lines. Keep memory list command thin (~50 lines).

4. **Note on Phase 5 overlap**: The phase sheet includes formatters as task 3.4/3.5. This overlaps with the original Phase 5 ("Formatters & Docs"). Phase 5 may reduce to just docs and refinement once Phase 3 formatters are done. Revisit Phase 5 scope after Phase 3.

5. **Commits so far**:
   - `d1bca98` — Phase 1: memory frontmatter metadata schema
   - `df69d6c` — Phase 2: MemoryRecord model and MemoryRegistry
