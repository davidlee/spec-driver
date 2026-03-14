---
id: IP-033.PHASE-02
slug: memory-domain-model-and-registry
name: IP-033 Phase 02 - Domain Model & Registry
created: '2026-03-02'
updated: '2026-03-02'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-033.PHASE-02
plan: IP-033
delta: DE-033
objective: >-
  Implement a MemoryRecord model and MemoryRegistry that can discover, parse,
  and index memory artifact files from the filesystem, following the established
  decisions/ registry pattern.
entrance_criteria:
  - Phase 1 complete (memory frontmatter metadata profile exists and validates)
  - DecisionRegistry / DecisionRecord pattern reviewed as reference architecture
  - Memory file storage convention agreed (or defaulted)
exit_criteria:
  - MemoryRecord dataclass loads all memory-specific frontmatter fields
  - MemoryRegistry discovers MEM-*.md files and parses them into MemoryRecords
  - Registry supports collect, find, iter, filter (by memory_type, status, tag)
  - to_dict serialization works for future YAML registry output
  - Unit tests passing for model and registry
  - Lint checks passing (ruff + pylint)
verification:
  tests:
    - VT-MEM-SCHEMA-001 (continued) - MemoryRecord round-trips frontmatter correctly
    - VT-MEM-REGISTRY-001 - Registry discovers and loads fixture files
    - VT-MEM-REGISTRY-002 - Registry filters by memory_type, status, tag
  evidence:
    - Test run output showing all unit tests passing
    - Lint checks passing (ruff + pylint)
tasks:
  - id: "2.1"
    description: "Create supekku/scripts/lib/memory/ package with __init__.py"
  - id: "2.2"
    description: "Implement MemoryRecord dataclass in models.py"
  - id: "2.3"
    description: "Write model tests (models_test.py) — construction, to_dict, edge cases"
  - id: "2.4"
    description: "Implement MemoryRegistry in registry.py — collect, find, iter, filter"
  - id: "2.5"
    description: "Create test fixtures (sample MEM-*.md files in tests/fixtures/)"
  - id: "2.6"
    description: "Write registry tests (registry_test.py) — discovery, parsing, filtering"
  - id: "2.7"
    description: "Lint and quality check"
risks:
  - description: Nested frontmatter objects (scope, priority, provenance) add parsing complexity
    mitigation: Keep model flat where sensible; use typed sub-dataclasses only where structure is validated
  - description: Memory storage location not yet decided
    mitigation: Default to memory/ at repo root; make configurable via registry constructor
```

# Phase 02 — Domain Model & Registry

## 1. Objective

Build the `supekku/scripts/lib/memory/` domain package with a `MemoryRecord` model and `MemoryRegistry` that can discover, load, and query memory artifact files. This is the prerequisite for CLI commands (Phase 3), selection/filtering (Phase 4), and formatters (Phase 5).

## 2. Links & References

- **Delta**: [DE-033](../DE-033.md)
- **Design Revision**: [DR-033](../DR-033.md) — §4 code impacts, §12 requirements
- **Implementation Plan**: [IP-033](../IP-033.md)
- **Requirements**: MEM-FR-001 (schema), MEM-FR-003 (selection), MEM-FR-004 (advisory links)
- **Reference Implementation**: `supekku/scripts/lib/decisions/registry.py` (DecisionRecord + DecisionRegistry)
- **Phase 1 Output**: `supekku/scripts/lib/core/frontmatter_metadata/memory.py` (validated schema)

## 3. Entrance Criteria

- [x] Phase 1 complete — memory metadata profile validates, 28 tests pass
- [x] DecisionRegistry pattern reviewed as reference architecture
- [x] Memory file storage convention agreed — `memory/` at repo root (configurable via constructor)

## 4. Exit Criteria / Done When

- [x] `MemoryRecord` dataclass with all memory-specific fields (20 attrs incl. scope, priority, provenance)
- [x] `MemoryRegistry` discovers `MEM-*.md` files, parses frontmatter, builds index
- [x] `find(id)`, `iter(status=)`, `filter(memory_type=, tag=, status=)` methods work
- [x] `to_dict(root)` serialization for future YAML registry output
- [x] Unit tests passing — 30 tests (11 model + 19 registry)
- [x] Lint passing — ruff clean, pylint 9.98/10 (only `too-many-instance-attributes` on dataclass, same as DecisionRecord)

## 5. Verification

- `uv run pytest supekku/scripts/lib/memory/ -v`
- `uv run ruff check supekku/scripts/lib/memory/`
- `uv run pylint --indent-string "  " supekku/scripts/lib/memory/`

## 6. Assumptions & STOP Conditions

- **Assumption**: Memory files use standard YAML frontmatter (same as all other artifacts).
- **Assumption**: `MEM-` prefix for memory IDs (consistent with other artifact families).
- **Assumption**: Memory file location defaults to `memory/` at repo root. Configurable later.
- **STOP**: If frontmatter parsing reveals incompatibilities with the metadata validator, revisit Phase 1 schema.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                     | Parallel? | Notes                                                         |
| ------ | --- | ------------------------------- | --------- | ------------------------------------------------------------- |
| [x]    | 2.1 | Create memory package structure |           | `__init__.py`                                                 |
| [x]    | 2.2 | Implement MemoryRecord model    |           | Dataclass with from_frontmatter + to_dict                     |
| [x]    | 2.3 | Write model tests               | [P]       | 11 tests: construction, to_dict, from_frontmatter, edge cases |
| [x]    | 2.4 | Implement MemoryRegistry        |           | collect, find, iter, filter                                   |
| [x]    | 2.5 | Create test fixtures            | [P]       | Inline YAML fixtures in registry_test.py                      |
| [x]    | 2.6 | Write registry tests            |           | 19 tests: discovery, parsing, filtering, integration          |
| [x]    | 2.7 | Lint and quality check          |           | ruff clean, pylint 9.98/10                                    |

### Task Details

- **2.2 MemoryRecord model**
  - **Fields**: id, name, slug, status, memory_type (required); confidence, verified, review_by, summary, tags, owners, requires_reading, scope, priority, provenance, audience, visibility, relations, path (optional)
  - **Nested types**: Consider `MemoryScope`, `MemoryPriority` sub-dataclasses for type safety, or keep as dicts if simpler
  - **Method**: `to_dict(root)` for YAML serialization (mirrors DecisionRecord pattern)
  - **Method**: `from_frontmatter(path, frontmatter)` classmethod for construction from parsed YAML

- **2.4 MemoryRegistry**
  - **Constructor**: `root` (repo root), derives `directory` (default: `root / "memory"`)
  - **collect()**: Glob `MEM-*.md`, parse frontmatter, build dict[id, MemoryRecord]
  - **find(id)**: Lookup by ID
  - **iter(status=, memory_type=)**: Iterator with optional filters
  - **filter(memory_type=, tag=, status=, ...)**: Multi-criteria filter
  - **Note**: Deterministic ordering (MEM-FR-003) is Phase 4 scope — keep filter/iter simple here

## 8. Risks & Mitigations

| Risk                                                     | Mitigation                                                                          | Status |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------ |
| Nested scope/priority/provenance adds parsing complexity | Use typed sub-dataclasses or validated dicts; keep model close to frontmatter shape | Open   |
| Storage location not finalized                           | Default to `memory/`; accept path override in constructor                           | Open   |

## 9. Decisions & Outcomes

- `_parse_date` extracted as module-level function in `models.py` (not a method on MemoryRecord or MemoryRegistry). Reduces coupling; potential consolidation target with DecisionRegistry.parse_date in future.
- Test fixtures are inline YAML strings in `registry_test.py` rather than separate fixture files. Simpler, self-contained, no fixture directory maintenance.
- `MemoryRegistry.directory` is configurable via constructor kwarg, defaulting to `root / "memory"`.

## 10. Findings / Research Notes

- DecisionRegistry uses `load_markdown_file()` from `supekku/scripts/lib/core/` for frontmatter parsing — reused here.
- DecisionRecord uses `@dataclass` with `field(default_factory=list)` for optional lists — same pattern adopted.
- `parse_date` is duplicated across DecisionRegistry, PolicyRegistry, StandardRegistry. Extracted as `_parse_date` module function in models.py — future consolidation opportunity into `core/`.
- Added `memory` to KNOWN_LEAF_PACKAGES in `package_utils_test.py` (21→22 leaf packages).
- pylint `too-many-instance-attributes` warning is expected for rich data models (DecisionRecord has same). Not suppressed.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: 30 tests passing, ruff clean, pylint 9.98/10
- [x] IP-033 updated with Phase 2 outcomes
- [x] Notes.md updated
- [x] Hand-off notes to Phase 3 (CLI surface)
