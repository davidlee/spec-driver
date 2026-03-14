---
id: IP-033.PHASE-03
slug: 033-memory_records_schema_and_command_surface-phase-03
name: IP-033 Phase 03 - CLI Surface
created: "2026-03-02"
updated: "2026-03-02"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-033.PHASE-03
plan: IP-033
delta: DE-033
objective: >-
  Add memory artifact commands to the existing CLI verb groups: create memory,
  list memories, show memory, find memory. Includes creation logic, formatters,
  and CLI integration tests.
entrance_criteria:
  - Phase 2 complete (MemoryRecord + MemoryRegistry passing tests)
  - Formatter pattern reviewed (decision_formatters.py as reference)
  - CLI patterns reviewed (create/list/show/find for ADRs as reference)
exit_criteria:
  - "create memory" generates a valid MEM-*.md file with schema-valid frontmatter
  - "list memories" displays records with status/type/tag filters and table/json/tsv output
  - "show memory MEM-XXX" displays details in human, JSON, path, and raw modes
  - "find memory" pattern-matches memory IDs
  - Memory formatters in formatters/memory_formatters.py (no display logic in CLI)
  - normalize_id supports "memory" / "MEM-" prefix
  - CLI integration tests passing
  - Unit tests for formatters and creation logic
  - Lint checks passing (ruff + pylint)
verification:
  tests:
    - VT-MEM-CLI-001 - CLI commands produce expected output for create/list/show/find
    - VT-MEM-FMT-001 - Memory formatters produce correct table/json/tsv output
    - VT-MEM-CREATE-001 - Creation logic generates valid frontmatter and file
  evidence:
    - Test run output showing all tests passing
    - Lint checks passing (ruff + pylint)
    - "uv run spec-driver list memories" and "uv run spec-driver create memory" smoke-tested
tasks:
  - id: "3.1"
    description: "Add MEM- prefix to ARTIFACT_PREFIXES in cli/common.py"
  - id: "3.2"
    description: "Create memory creation logic (memory/creation.py) — next ID, frontmatter, template"
  - id: "3.3"
    description: "Write creation tests (memory/creation_test.py)"
  - id: "3.4"
    description: "Create memory formatters (formatters/memory_formatters.py)"
  - id: "3.5"
    description: "Write formatter tests (formatters/memory_formatters_test.py)"
  - id: "3.6"
    description: "Add CLI commands: create memory, list memories, show memory, find memory"
  - id: "3.7"
    description: "Write CLI integration tests"
  - id: "3.8"
    description: "Lint and quality check"
risks:
  - description: CLI files already large (list.py ~2000 lines)
    mitigation: Keep memory commands thin; all logic in domain/formatters
  - description: create memory needs a template body — design not yet specified
    mitigation: Follow ADR creation pattern; simple body template with section headers
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-033.PHASE-03
```

# Phase 03 — CLI Surface

## 1. Objective

Add memory commands to the four existing CLI verb groups (`create`, `list`, `show`, `find`), keeping CLI files thin by delegating to creation logic in `memory/creation.py` and display logic in `formatters/memory_formatters.py`.

## 2. Links & References

- **Delta**: [DE-033](../DE-033.md)
- **Design Revision**: [DR-033](../DR-033.md) — §4 code impacts (create.py, list.py, show.py, find.py)
- **Implementation Plan**: [IP-033](../IP-033.md)
- **Requirements**: MEM-FR-002 (CLI surface), MEM-FR-003 (selection/filtering — basic filter support here, deterministic ordering is Phase 4)
- **Phase 2 Output**: `supekku/scripts/lib/memory/` (MemoryRecord + MemoryRegistry)
- **Reference CLI**: `supekku/cli/create.py` (`create_adr`), `supekku/cli/list.py` (`list_adrs`), `supekku/cli/show.py` (`show_adr`), `supekku/cli/find.py` (`find_adr`)
- **Reference Formatter**: `supekku/scripts/lib/formatters/decision_formatters.py`

## 3. Entrance Criteria

- [x] Phase 2 complete — MemoryRecord + MemoryRegistry, 30 tests passing
- [x] Formatter pattern reviewed (decision_formatters.py)
- [x] CLI patterns reviewed (create/list/show/find for ADRs)

## 4. Exit Criteria / Done When

- [x] `create memory` generates valid `MEM-*.md` with frontmatter + body template
- [x] `list memories` with `--status`, `--type`, `--tag`, `--format`, `--json`, `--regexp`, `--truncate`
- [x] `show memory MEM-XXX` with `--json`, `--path`, `--raw`
- [x] `find memory` with pattern matching
- [x] `normalize_id("memory", "1")` returns `"MEM-001"`
- [x] Formatters: `format_memory_details`, `format_memory_list_table`, `format_memory_list_json`
- [x] Tests and lint passing (1849 pass, ruff clean, pylint 10.00)

## 5. Verification

- `uv run pytest supekku/scripts/lib/memory/ supekku/scripts/lib/formatters/memory_formatters_test.py -v`
- `uv run ruff check supekku/cli/ supekku/scripts/lib/memory/ supekku/scripts/lib/formatters/`
- `uv run pylint --indent-string "  " supekku/scripts/lib/memory/ supekku/scripts/lib/formatters/memory_formatters.py`
- Smoke test: `uv run spec-driver create memory "Test Memory" --type fact`
- Smoke test: `uv run spec-driver list memories`

## 6. Assumptions & STOP Conditions

- **Assumption**: Memory creation follows the ADR pattern (auto-increment ID, slug from name, write file to `memory/` directory).
- **Assumption**: `create memory` requires `--type` (memory_type) as a required option, defaulting body template to a simple markdown structure.
- **Assumption**: Formatter output follows the same table/json/tsv pattern as decisions.
- **STOP**: If `list.py` exceeds ~2100 lines after adding memory commands, refactor list commands into sub-modules before proceeding.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                          | Parallel? | Notes                                             |
| ------ | --- | ------------------------------------ | --------- | ------------------------------------------------- |
| [x]    | 3.1 | Add MEM- prefix to ARTIFACT_PREFIXES |           | `cli/common.py` + test assertion added            |
| [x]    | 3.2 | Memory creation logic                |           | `memory/creation.py`: 3 dataclasses, 3 functions  |
| [x]    | 3.3 | Creation tests                       | [P]       | 13 tests (id gen, frontmatter, create, errors)    |
| [x]    | 3.4 | Memory formatters                    |           | `formatters/memory_formatters.py` + theme entries |
| [x]    | 3.5 | Formatter tests                      | [P]       | 16 tests (details, table, json, tsv, edge cases)  |
| [x]    | 3.6 | CLI commands                         |           | create, list, show, find — all 4 wired            |
| [x]    | 3.7 | CLI integration tests                |           | 22 tests in `cli/memory_test.py`                  |
| [x]    | 3.8 | Lint and quality check               |           | 1849 pass, ruff clean, pylint 10.00               |

### Task Details

- **3.1 ARTIFACT_PREFIXES**
  - Add `"memory": "MEM-"` to `ARTIFACT_PREFIXES` dict in `supekku/cli/common.py`
  - This enables `normalize_id("memory", "1")` → `"MEM-001"`

- **3.2 Memory creation logic** (`memory/creation.py`)
  - `MemoryCreationOptions` dataclass: name, memory_type, status (default "active"), tags, summary
  - `MemoryCreationResult` dataclass: memory_id, path
  - `generate_next_memory_id(registry)` — scan existing, return next MEM-NNN
  - `build_memory_frontmatter(options, memory_id)` — dict for YAML frontmatter
  - `create_memory(registry, options)` — orchestrate: next ID, slug, write file, return result
  - Follow `decisions/creation.py` pattern closely

- **3.4 Memory formatters** (`formatters/memory_formatters.py`)
  - `format_memory_details(record)` → multi-line human-readable detail view
  - `format_memory_list_table(records, format_type, truncate)` → table/tsv/json output
  - `format_memory_list_json(records)` → JSON array
  - Columns for table: ID, Status, Type, Name, Confidence, Tags
  - Follow `decision_formatters.py` pattern

- **3.6 CLI commands**
  - `create.py`: `create_memory(name, --type, --status, --tag, --summary, --root)`
  - `list.py`: `list_memories(--status, --type, --tag, --regexp, --format, --json, --truncate, --root)`
  - `show.py`: `show_memory(memory_id, --json, --path, --raw, --root)`
  - `find.py`: `find_memory(pattern, --root)`
  - Each command: thin orchestration, delegate to domain + formatters

## 8. Risks & Mitigations

| Risk                                             | Mitigation                                                 | Status                                           |
| ------------------------------------------------ | ---------------------------------------------------------- | ------------------------------------------------ |
| list.py is already ~2000 lines                   | Memory list command is ~50 lines if kept thin              | Resolved — 2067 lines, under 2100 threshold      |
| create memory needs a sensible body template     | Minimal template: `# {name}\n\n## Summary\n\n## Context\n` | Resolved — inline body, no Jinja template needed |
| memory_type is required but not a CLI positional | Use `--type` required option (consistent with schema)      | Resolved                                         |

## 9. Decisions & Outcomes

- `build_memory_frontmatter` takes `(memory_id, options)` not individual args — avoids pylint too-many-arguments, cleaner API
- Memory body template is inline (`# {name}\n\n## Summary\n\n## Context\n`) — no Jinja template file. Simpler than ADR pattern; can add template later if needed.
- `create memory --type` is required (not positional) — consistent with schema where `memory_type` is required
- `--tag` is repeatable (`list[str]`) on create, single value on list (consistent with other list commands)
- Added memory theme entries for status styling (active/draft/review/archived) + `memory.id`
- Singular alias `list memory` registered via existing `_PLURAL_TO_SINGULAR` machinery

## 10. Findings / Research Notes

- ADR CLI pattern: create calls `creation.py` impl, list uses registry + formatters, show uses registry + formatter/json, find uses registry + pattern match
- `ARTIFACT_PREFIXES` in `cli/common.py` already supports MEM-style prefix normalization — just needs the entry
- Formatter pattern: `format_*_details` (single record), `format_*_list_table` (multiple, supports table/tsv/json format*type), `format*\*\_list_json` (dedicated JSON)
- `table_utils.py` provides `create_table`, `render_table`, `format_as_json`, `format_as_tsv` shared helpers

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: 1849 tests pass, ruff clean, pylint 10.00
- [ ] IP-033 updated with Phase 3 outcomes
- [x] Notes.md updated
- [ ] Hand-off notes to Phase 4 (selection & ordering) and Phase 5 (formatters refinement)
