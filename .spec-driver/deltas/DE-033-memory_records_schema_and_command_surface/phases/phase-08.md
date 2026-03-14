---
id: IP-033.PHASE-08
slug: 033-memory_records_schema_and_command_surface-phase-08
name: IP-033 Phase 08 - Inline Link Parsing & Resolution
created: "2026-03-03"
updated: "2026-03-03"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-033.PHASE-08
plan: IP-033
delta: DE-033
objective: >-
  Implement [[...]] wikilink parsing in memory body content, resolution
  against known artifacts, frontmatter persistence of resolved links,
  CLI resolve command, sync integration, and formatter display.
  Verifies MEM-FR-004 (advisory cross-artifact links).
entrance_criteria:
  - Phase 6 complete (semantic IDs)
  - obs-link-spec reviewed (in delta bundle)
exit_criteria:
  - parse_links() extracts [[target]] and [[target|label]] from body text
  - Code fences and inline code skipped during parsing
  - resolve_parsed_link() resolves against artifact index
  - Self-links produce warnings, not errors
  - Memory shorthand (omit mem. prefix) resolves via normalization
  - links field in frontmatter schema validated
  - MemoryRecord.links round-trips through from_frontmatter/to_dict
  - "resolve links" CLI command writes frontmatter
  - "sync --memory-links" delegates to resolver
  - format_memory_details shows links section
  - format_memory_list_json includes links
  - Stale links cleared when body changes
  - VT-MEM-LINKS-001 verified
  - All tests pass, lint clean
verification:
  tests:
    - VT-MEM-LINKS-001 - Advisory cross-artifact links (MEM-FR-004)
  evidence:
    - 2087+ tests passing
    - ruff clean
    - pylint ≥ 9.61
tasks:
  - id: "8.0"
    description: "Shared artifact ID classifier — core/artifact_ids.py"
  - id: "8.1"
    description: "Link parser — memory/links.py parse_links()"
  - id: "8.2"
    description: "Link resolver — memory/links.py resolve_parsed_link() + resolve_all_links()"
  - id: "8.3"
    description: "Schema + model updates — links FieldMetadata + MemoryRecord.links"
  - id: "8.4"
    description: "CLI resolve command + sync --memory-links flag"
  - id: "8.5"
    description: "Formatter updates — _format_links() in memory_formatters.py"
  - id: "8.6"
    description: "VT-MEM-LINKS-001 integration verification + pylint cleanup"
risks:
  - description: "resolve.py pylint score (9.33) due to _build_artifact_index complexity"
    mitigation: "Refactor into per-registry helpers; deferred to 8.6 or follow-up"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-033.PHASE-08
```

# Phase 8 — Inline Link Parsing & Resolution

## 1. Objective

Implement `[[...]]` wikilink parsing in memory body content per obs-link-spec,
resolve targets against project artifact registries, persist results in
frontmatter `links` field, and provide CLI + sync integration.

## 2. Links & References

- **Obs-link-spec**: `obs-link-spec.md` (delta bundle)
- **Phase 8 plan**: `phase8-exploration-summary.md` (delta bundle)
- **ID classifier**: `supekku/scripts/lib/core/artifact_ids.py`
- **Link module**: `supekku/scripts/lib/memory/links.py`
- **CLI**: `supekku/cli/resolve.py`
- **Delta**: DE-033
- **Requirement**: MEM-FR-004

## 3. Entrance Criteria

- [x] Phase 6 complete
- [x] obs-link-spec reviewed

## 4. Exit Criteria / Done When

- [x] `core/artifact_ids.py` — shared ID classification (34 tests)
- [x] `memory/links.py` — parser + resolver + serializer (43 tests)
- [x] `frontmatter_metadata/memory.py` — links FieldMetadata (5 tests)
- [x] `memory/models.py` — links field round-trip (4 tests)
- [x] `memory/__init__.py` — exports updated
- [x] `formatters/memory_formatters.py` — \_format_links() (6 tests)
- [x] `cli/resolve.py` — resolve links command (8 tests)
- [x] `cli/main.py` — resolve group registered
- [x] `cli/sync.py` — --memory-links flag
- [x] 2087 tests pass (up from 1984)
- [x] ruff clean
- [x] pylint cleanup on resolve.py (8.54 → 10.00 — extracted per-registry collectors, top-level imports)
- [x] VT-MEM-LINKS-001 status updated to verified in IP-033
- [x] IP-033 phase overview updated

## 5. Verification

```bash
uv run pytest supekku/ -q --tb=short        # 2087 passed
just lint                                     # All checks passed
just pylint                                   # 9.61/10
uv run spec-driver resolve links --dry-run    # CLI works
uv run spec-driver resolve --help             # Shows links subcommand
```

## 7. Tasks & Progress

| Status | ID  | Description                   | Notes                                                                                             |
| ------ | --- | ----------------------------- | ------------------------------------------------------------------------------------------------- |
| [x]    | 8.0 | Shared artifact ID classifier | `core/artifact_ids.py`: 10 patterns, classify + is_artifact_id. 34 tests.                         |
| [x]    | 8.1 | Link parser                   | `memory/links.py`: parse_links(), code fence/inline skipping, dedup. 23 parser tests.             |
| [x]    | 8.2 | Link resolver                 | Same file: resolve_parsed_link(), resolve_all_links(), links_to_frontmatter(). 20 resolver tests. |
| [x]    | 8.3 | Schema + model                | links FieldMetadata (out/missing arrays), MemoryRecord.links field. 9 tests.                      |
| [x]    | 8.4 | CLI + sync                    | `cli/resolve.py` resolve links [--dry-run], sync --memory-links. 8 CLI tests.                     |
| [x]    | 8.5 | Formatter                     | \_format_links(), wired into details + JSON. 6 formatter tests.                                   |
| [x]    | 8.6 | Verification                  | pylint 10.00 (extracted collectors + top-level imports), IP-033 updated.                          |

## 8. Outstanding Work

### Pylint cleanup (8.6, blocking completion)

`resolve.py` scores 9.33/10 due to:

- `_build_artifact_index` too complex (McCabe 13) — needs extraction into per-registry helpers
- `import-outside-toplevel` x6 — lazy imports are intentional (registry dependencies optional) but pylint flags them
- `broad-exception-caught` x4 — used to gracefully skip missing registries
- `too-many-locals` x2 — follows from monolithic function

**Recommended fix**: Extract `_collect_memory_artifacts()`, `_collect_decisions()`, `_collect_specs()`, `_collect_changes()` helper functions. Move `load_markdown_file`/`dump_markdown_file` imports to top level in `_resolve_memory_links`.

### `links.py` minor

- `resolve_parsed_link` has 7 return statements (max 6) — could combine early-return paths

### IP-033 updates (blocking completion)

- Update VT-MEM-LINKS-001 status: `planned` → `verified`
- Add Phase 8 to phase overview table
- Update progress tracking section

### Follow-up (out of scope)

- Update `blocks/revision.py` and `blocks/verification.py` to import from `core/artifact_ids.py`
- `[[slug]]` resolution (deferred per obs-link-spec adjustments)
- `mem:` URI scheme (dropped — `mem.` prefix sufficient)

## 9. Decisions

- Dropped `mem:` URI scheme — canonical `mem.` dot prefix is unambiguous
- Dropped `[[slug]]` resolution — semantic IDs are the primary mechanism
- Resolution rule: classify_artifact_id() for SPEC/ADR/DE etc, normalize_memory_id() for dotted targets
- Self-links: skip with warning (not error)
- Frontmatter `links.out` always overwritten from body (no merge) for determinism
- Stale links cleared when body no longer contains them

## 10. Files Changed

### New

- `supekku/scripts/lib/core/artifact_ids.py` + `_test.py` — shared ID classification
- `supekku/scripts/lib/memory/links.py` + `_test.py` — parser, resolver, serializer
- `supekku/cli/resolve.py` + `_test.py` — CLI command
- `change/deltas/DE-033-.../phase8-exploration-summary.md` — research notes

### Modified

- `supekku/scripts/lib/core/frontmatter_metadata/memory.py` + `_test.py` — links field
- `supekku/scripts/lib/memory/models.py` + `_test.py` — links attribute
- `supekku/scripts/lib/memory/__init__.py` — exports
- `supekku/scripts/lib/formatters/memory_formatters.py` + `_test.py` — \_format_links
- `supekku/cli/main.py` — resolve group
- `supekku/cli/sync.py` — --memory-links flag
