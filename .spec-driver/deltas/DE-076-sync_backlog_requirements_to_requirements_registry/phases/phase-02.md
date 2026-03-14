---
id: IP-076.PHASE-02
slug: 076-sync_backlog_requirements_to_requirements_registry-phase-02
name: IP-076 Phase 02 — Backlog requirement sync and CLI filtering
created: "2026-03-09"
updated: "2026-03-09"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-076.PHASE-02
plan: IP-076
delta: DE-076
objective: >-
  Add heading regex for dotted backlog format, source_kind/source_type fields,
  backlog sync loop, CLI --source-kind filter, and Source column in formatter.
entrance_criteria:
  - Phase 1 complete and committed
exit_criteria:
  - _REQUIREMENT_HEADING regex matches dotted backlog format
  - RequirementRecord has source_kind/source_type with to_dict/from_dict/merge support
  - sync() accepts backlog_registry, iterates items, extracts requirements
  - CLI --source-kind filter works (single and multi-value)
  - Source column in table output
  - All VT artifacts verified
  - All existing tests pass (regression)
  - Linters pass (ruff + pylint)
verification:
  tests:
    - VT-REGEX-076-001
    - VT-SYNC-076-002
    - VT-UPSERT-076-003
    - VT-FILTER-076-004
    - VT-COMPAT-076-005
    - VT-COVERAGE-076-006
  evidence: []
tasks:
  - id: T1
    name: Add _REQUIREMENT_HEADING regex
  - id: T2
    name: Add source_kind/source_type to RequirementRecord
  - id: T3
    name: Add backlog sync loop to sync()
  - id: T4
    name: Add --source-kind CLI filter
  - id: T5
    name: Add Source column to formatter
  - id: T6
    name: Wire up cli/sync.py
risks:
  - id: R1
    description: Backlog items with non-standard requirement format
    mitigation: Graceful skip with warning log
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-076.PHASE-02
entrance_criteria:
  - item: "Phase 1 complete and committed"
    completed: true
exit_criteria:
  - item: "_REQUIREMENT_HEADING regex matches dotted backlog format"
    completed: true
  - item: "RequirementRecord has source_kind/source_type with serialization"
    completed: true
  - item: "sync() accepts backlog_registry, iterates items, extracts requirements"
    completed: true
  - item: "CLI --source-kind filter works"
    completed: true
  - item: "Source column in table output"
    completed: true
  - item: "All VT artifacts verified"
    completed: true
  - item: "All existing tests pass (regression)"
    completed: true
  - item: "Linters pass"
    completed: true
```

# Phase 2 — Backlog requirement sync and CLI filtering

## 1. Objective

Implement the core feature: backlog items with dotted-format requirements (`### FR-016.001: Title`) are discovered by the requirements registry sync, tracked with source provenance, and filterable in the CLI.

## 2. Links & References

- **Delta**: [DE-076](../DE-076.md)
- **Design Revision**: [DR-076](../DR-076.md) — DEC-076-02, DEC-076-03, DEC-076-05, DEC-076-07, DEC-076-08
- **Requirements**: ISSUE-016.FR-016.001, FR-016.002, FR-016.004, NF-016.001
- **Primary Spec**: SPEC-122

## 3. Entrance Criteria

- [x] Phase 1 complete and committed (cleanup refactor)

## 4. Exit Criteria / Done When

- [x] `_REQUIREMENT_HEADING` regex matches `### FR-016.001:`, `### NF-013.001:`, rejects `### FR-001:`
- [x] `RequirementRecord` has `source_kind`/`source_type` with `to_dict`/`from_dict`/`merge` support
- [x] `sync()` accepts `backlog_registry`, iterates items, calls `_records_from_content`, upserts with provenance
- [x] `--source-kind` filter on `list requirements` (multi-value, `""` passes all)
- [x] Source column in table output
- [x] All VT artifacts have passing tests (18 new tests)
- [x] `just` passes (3510 tests + lint)

## 5. Verification

- **VT-REGEX-076-001**: Unit tests for `_REQUIREMENT_HEADING` — match/reject cases
- **VT-SYNC-076-002**: Sync with mock backlog items → records appear with correct UIDs and `source_kind`
- **VT-UPSERT-076-003**: `_upsert_record` sets `source_kind`/`source_type` after merge
- **VT-FILTER-076-004**: CLI filter tests — single value, multi-value, empty passes all
- **VT-COMPAT-076-005**: Existing sync tests pass; `sync_from_specs` alias works; round-trip serialization
- **VT-COVERAGE-076-006**: Coverage tracking with backlog-sourced requirement UIDs
- Run `just` (tests + lint + pylint)

## 6. Assumptions & STOP Conditions

- **Assumption**: Backlog items use `### FR-NNN.MMM: Title` heading format for requirements
- **Assumption**: `BacklogRegistry` is importable from requirements registry without circular deps
- **STOP when**: Circular import detected between requirements and backlog packages
- **STOP when**: More than 2 backlog items have requirements in a format neither regex handles

## 7. Tasks & Progress

| Status | ID  | Description                                            | Parallel? | Notes                         |
| ------ | --- | ------------------------------------------------------ | --------- | ----------------------------- |
| [x]    | T1  | Add `_REQUIREMENT_HEADING` regex + tests               | [P]       | DEC-076-03, DEC-076-08        |
| [x]    | T2  | Add `source_kind`/`source_type` to `RequirementRecord` | [P]       | DEC-076-02                    |
| [x]    | T3  | Add backlog sync loop to `sync()`                      | [ ]       | Depends on T1, T2. DEC-076-07 |
| [x]    | T4  | Add `--source-kind` CLI filter                         | [ ]       | Depends on T2. DEC-076-05     |
| [x]    | T5  | Add Source column to formatter                         | [P]       | DEC-076-02                    |
| [x]    | T6  | Wire up `cli/sync.py`                                  | [ ]       | Depends on T3                 |
| [x]    | T7  | Full test + lint pass                                  | [ ]       | After T1–T6                   |

### Task Details

- **T1: `_REQUIREMENT_HEADING` regex**
  - **Approach**: New regex matching `^\s*#{1,4}\s*(FR|NF)-(\d{3})\.(\d{3})\s*[:\-–]\s*(.+)$`. Captures: kind, artifact-num, seq-num, title. Label: `FR-{artifact-num}.{seq-num}`. Only matches dotted format — no overlap with spec bullet format (DEC-076-08).
  - **Files**: `supekku/scripts/lib/requirements/registry.py` (regex + `_records_from_content`)
  - **Testing**: VT-REGEX-076-001 — match `### FR-016.001: Title`, `### NF-013.001: Title`; reject `### FR-001: Title`, `- FR-016.001: Title`
  - **TDD**: Write tests first

- **T2: `source_kind`/`source_type` on `RequirementRecord`**
  - **Approach**: Add `source_kind: str = ""` and `source_type: str = ""` fields. Update `to_dict()` to include them. Update `from_dict()` to default missing fields to `""`. Update `merge()` — incoming value wins (sync is authoritative, DEC-076-05).
  - **Files**: `supekku/scripts/lib/requirements/registry.py`
  - **Testing**: VT-UPSERT-076-003 (merge semantics), VT-COMPAT-076-005 (round-trip)
  - **TDD**: Write tests first

- **T3: Backlog sync loop**
  - **Approach**: Add `backlog_registry: BacklogRegistry | None = None` param to `sync()`. Iterate `backlog_registry.iter()`, call `load_markdown_file(item.path)` for `(frontmatter, body)`, call `_records_from_content(item.id, frontmatter, body, item.path, repo_root)`, upsert each record with `source_kind=item.kind, source_type="backlog"`. Import `BacklogRegistry` under `TYPE_CHECKING`.
  - **Files**: `supekku/scripts/lib/requirements/registry.py`
  - **Testing**: VT-SYNC-076-002 — mock BacklogRegistry with test fixture items

- **T4: `--source-kind` CLI filter**
  - **Approach**: Add `--source-kind` option (multi-value, `list[str]`). Filter: if `source_kind` values provided, include records where `record.source_kind in values` OR `record.source_kind == ""` (empty passes all, DEC-076-05).
  - **Files**: `supekku/cli/list.py`
  - **Testing**: VT-FILTER-076-004 — `--source-kind issue`, `--source-kind spec --source-kind issue`, default (no filter)

- **T5: Source column in formatter**
  - **Approach**: Add `source` column to `REQUIREMENT_COLUMNS` in `column_defs.py`. Update table formatter in `requirement_formatters.py` to display `source_kind`.
  - **Files**: `supekku/scripts/lib/formatters/column_defs.py`, `supekku/scripts/lib/formatters/requirement_formatters.py`
  - **Testing**: Formatter unit tests

- **T6: Wire up `cli/sync.py`**
  - **Approach**: In `_sync_requirements`, construct `BacklogRegistry(root=root)` and pass to `req_registry.sync(backlog_registry=...)`.
  - **Files**: `supekku/cli/sync.py`
  - **Testing**: Integration — run sync, verify backlog requirements appear

## 8. Risks & Mitigations

| Risk                                          | Mitigation                                                           | Status   |
| --------------------------------------------- | -------------------------------------------------------------------- | -------- |
| Circular import (requirements ↔ backlog)     | Import BacklogRegistry under TYPE_CHECKING; runtime import in sync() | open     |
| Backlog items with unusual requirement format | Graceful skip; warning log                                           | open     |
| Code fence false positives (pre-existing)     | Out of scope; noted in DR-076                                        | accepted |

## 9. Decisions & Outcomes

- DEC-076-03: Two regexes, format-specific
- DEC-076-05: Sync backfills source_kind; CLI treats "" as pass-all
- DEC-076-07: BacklogRegistry for iteration, load_markdown_file for body
- DEC-076-08: Heading regex dotted-only, no overlap with bullet regex
