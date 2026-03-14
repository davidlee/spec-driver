---
id: IP-068.PHASE-01
slug: "068-edit_command_status_flag_for_programmatic_status_updates-phase-01"
name: Shared primitive and enum expansion
created: "2026-03-08"
updated: "2026-03-08"
status: in-progress
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-068.PHASE-01
plan: IP-068
delta: DE-068
objective: >-
  Extract shared frontmatter status update primitive, expand ENUM_REGISTRY
  with backlog and drift status entries, consolidate existing duplicate callers.
entrance_criteria:
  - DR-068 design decisions settled
exit_criteria:
  - update_frontmatter_status() exists in core/frontmatter_writer.py with tests
  - ENUM_REGISTRY includes backlog kinds, drift, revision/audit aliases
  - completion.py and complete_delta.py delegate to shared primitive
  - existing completion tests pass
  - just lint passes
verification:
  tests:
    - VT-068-01
  evidence: []
tasks:
  - id: "1.1"
    description: Create frontmatter_writer module with update_frontmatter_status()
  - id: "1.2"
    description: Expand ENUM_REGISTRY with backlog, drift, and alias entries
  - id: "1.3"
    description: Consolidate completion.py and complete_delta.py onto shared primitive
  - id: "1.4"
    description: Add validate_status_for_entity() helper
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-068.PHASE-01
```

# Phase 1 — Shared primitive and enum expansion

## 1. Objective

Extract the duplicated frontmatter status update logic into a shared primitive, expand the enum registry to cover all entity types that have status definitions, and consolidate existing callers.

## 2. Links & References

- **Delta**: DE-068
- **Design Revision**: DR-068 §5.1 (primitive), §5.2 (validation dispatch)
- **Specs**: PROD-013.FR-004

## 3. Entrance Criteria

- [x] DR-068 design decisions settled (DEC-068-01 through DEC-068-03)

## 4. Exit Criteria / Done When

- [ ] `core/frontmatter_writer.py` exists with `update_frontmatter_status()`
- [ ] `validate_status_for_entity()` helper exists (in frontmatter_writer or enums module)
- [ ] `ENUM_REGISTRY` includes: `issue.status`, `problem.status`, `improvement.status`, `risk.status`, `drift.status`, `revision.status`, `audit.status`
- [ ] `completion.py:_update_artifact_frontmatter_status()` delegates to shared primitive
- [ ] `complete_delta.py:update_delta_frontmatter()` delegates to shared primitive
- [ ] VT-068-01 tests pass
- [ ] Existing completion tests pass (regression)
- [ ] `just lint` passes

## 5. Verification

- `just test` — all tests including new frontmatter_writer_test.py
- `just lint` — zero warnings
- Regression: `complete_delta` and `complete_revision` test suites

## 6. Assumptions & STOP Conditions

- Assumption: unquoted `status: value` format is universal (verified)
- Assumption: `startswith("status:")` line matching is safe within frontmatter blocks (battle-tested in production)
- STOP: if any existing frontmatter uses quoted status values or multi-line status fields

## 7. Tasks & Progress

| Status | ID  | Description                                       | Parallel? | Notes          |
| ------ | --- | ------------------------------------------------- | --------- | -------------- |
| [ ]    | 1.1 | Create `core/frontmatter_writer.py` + tests       | [ ]       | DR-068 §5.1    |
| [ ]    | 1.2 | Expand `ENUM_REGISTRY` in `core/enums.py`         | [P]       | DR-068 §5.2    |
| [ ]    | 1.3 | Consolidate `completion.py` + `complete_delta.py` | [ ]       | Depends on 1.1 |
| [ ]    | 1.4 | Add `validate_status_for_entity()` + tests        | [P]       | DR-068 §5.2    |

### Task Details

- **1.1 Create `core/frontmatter_writer.py`**
  - **Files**: `supekku/scripts/lib/core/frontmatter_writer.py`, `supekku/scripts/lib/core/frontmatter_writer_test.py`
  - **Design**: Extract from `completion.py:_update_artifact_frontmatter_status()`. Add empty/whitespace rejection. Write status unquoted, updated date single-quoted.
  - **Tests**: Round-trip content preservation, `updated:` date bump, missing status field returns False, empty input raises ValueError, idempotent update

- **1.2 Expand `ENUM_REGISTRY`**
  - **Files**: `supekku/scripts/lib/core/enums.py`, `supekku/scripts/lib/core/enums_test.py`
  - **Design**: Add entries from `backlog/models.py` (4 kinds), `drift/models.py` (LEDGER_STATUSES), and alias entries for `revision.status`/`audit.status` pointing to CHANGE_STATUSES
  - **Tests**: `get_enum_values()` returns correct values for each new path

- **1.3 Consolidate existing callers**
  - **Files**: `supekku/scripts/lib/changes/completion.py`, `supekku/scripts/complete_delta.py`
  - **Design**: Replace inline implementations with calls to `update_frontmatter_status()`. Remove ~40 lines of duplicate code.
  - **Tests**: Existing completion test suites must pass unchanged (regression)

- **1.4 Add `validate_status_for_entity()`**
  - **Files**: `supekku/scripts/lib/core/frontmatter_writer.py` (or enums.py — co-locate with ENUM_REGISTRY)
  - **Design**: Per DR-068 §5.2 — empty rejection, enum lookup, strict rejection where enum exists, silent acceptance otherwise
  - **Tests**: Valid status accepted, invalid rejected with message listing valid values, unknown entity type accepted silently, empty rejected
