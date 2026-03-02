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

### Next steps

- Memory domain package (model, registry, selection/filtering logic)
- CLI commands (create memory, list memories, show memory, find memory)
- Formatters
- Runtime frontmatter parsing integration (frontmatter_schema.py currently does not enforce kind-specific fields at parse time — metadata validator is the enforcement path)
