---
id: IP-081.PHASE-01
slug: 081-requirements_subsystem_sync_integrity_lifecycle_and_tags-phase-01
name: IP-081 Phase 01 — Implementation
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-081.PHASE-01
plan: IP-081
delta: DE-081
objective: >-
  Implement all three DE-081 objectives: coverage replacement semantics,
  deprecated/superseded lifecycle statuses, and inline requirement tag
  extraction. All tests pass, both linters clean.
entrance_criteria:
  - DR-081 approved with all design decisions resolved
exit_criteria:
  - Coverage evidence rebuilt fresh each sync (no accumulation)
  - Sync idempotency restored (NF-002)
  - deprecated/superseded statuses accepted; terminal statuses guarded from coverage overwrite
  - Inline [tag] syntax parsed and populates registry
  - filter(tag=...) works
  - All tests pass (just test)
  - Both linters clean (just lint, just pylint-files)
verification:
  tests:
    - VT-081-001
    - VT-081-002
    - VT-081-003
  evidence: []
tasks:
  - id: "1.1"
    description: Add deprecated/superseded constants to lifecycle.py
  - id: "1.2"
    description: Coverage replacement — clear and rebuild in _apply_coverage_blocks
  - id: "1.3"
    description: Terminal status guard in coverage derivation
  - id: "1.4"
    description: Extend _REQUIREMENT_LINE regex for [tag] syntax
  - id: "1.5"
    description: Add tag parameter to filter()
  - id: "1.6"
    description: Tests for all objectives
  - id: "1.7"
    description: Lint and verify
risks:
  - description: Regex change breaks existing parsing
    mitigation: Tag group is optional; full regression suite
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-081.PHASE-01
```

# Phase 1 — Implementation

## 1. Objective

Implement all three DE-081 objectives in a single phase. The changes are small,
tightly scoped to `requirements/`, and naturally tested together.

## 2. Links & References

- **Delta**: [DE-081](../DE-081.md)
- **Design Revision**: [DR-081](../DR-081.md) — DEC-081-01 through DEC-081-03
- **Specs**: SPEC-122.FR-002 (statuses), SPEC-122.NF-002 (idempotency), SPEC-122.FR-004 (extraction)
- **ADR-008**: Registry is derived; coverage replacement is correct

## 3. Entrance Criteria

- [x] DR-081 drafted with all design decisions resolved

## 4. Exit Criteria / Done When

- [ ] Coverage evidence rebuilt fresh each sync
- [ ] Sync idempotency: run twice → identical registry
- [ ] `deprecated`/`superseded` accepted as valid statuses
- [ ] Terminal statuses not overwritten by coverage derivation
- [ ] `[tag1, tag2]` syntax parsed from inline requirements
- [ ] `filter(tag="x")` returns tagged requirements
- [ ] `just test` passes
- [ ] `just lint` clean
- [ ] `just pylint-files` on changed files clean

## 5. Verification

- Run: `just test` (full suite — coverage tests are in registry_test.py)
- Run: `just lint` and `just pylint-files supekku/scripts/lib/requirements/lifecycle.py supekku/scripts/lib/requirements/registry.py supekku/scripts/lib/requirements/registry_test.py`
- Evidence: test output captured in notes

## 6. Assumptions & STOP Conditions

- Assumptions: No other code outside `requirements/` depends on the exact contents of `coverage_evidence` (it's a registry-derived field).
- STOP when: Existing tests fail in unexpected ways suggesting coverage_evidence is consumed elsewhere.

## 7. Tasks & Progress

| Status | ID  | Description                                                                           | Parallel? | Notes                       |
| ------ | --- | ------------------------------------------------------------------------------------- | --------- | --------------------------- |
| [ ]    | 1.1 | Add `deprecated`/`superseded` constants + `TERMINAL_STATUSES` to `lifecycle.py`       | [P]       | POL-002: named constants    |
| [ ]    | 1.2 | Clear + rebuild coverage fields in `_apply_coverage_blocks()`                         | [P]       | DEC-081-01                  |
| [ ]    | 1.3 | Guard terminal statuses from coverage-derived overwrite                               |           | Depends on 1.1              |
| [ ]    | 1.4 | Extend `_REQUIREMENT_LINE` regex for `[tag1, tag2]` syntax                            | [P]       | DEC-081-03                  |
| [ ]    | 1.5 | Populate `tags` in `_records_from_content()` and merge in `RequirementRecord.merge()` |           | Depends on 1.4              |
| [ ]    | 1.6 | Add `tag` parameter to `filter()`                                                     |           | Depends on 1.5              |
| [ ]    | 1.7 | Write tests for all objectives                                                        |           | TDD — interleave with above |
| [ ]    | 1.8 | Lint and verify                                                                       |           | Final gate                  |

### Task Details

- **1.1 — Lifecycle constants**
  - **Files**: `supekku/scripts/lib/requirements/lifecycle.py`
  - **Approach**: Add `STATUS_DEPRECATED = "deprecated"`, `STATUS_SUPERSEDED = "superseded"` to `VALID_STATUSES`. Add `TERMINAL_STATUSES = {STATUS_RETIRED, STATUS_DEPRECATED, STATUS_SUPERSEDED}`.

- **1.2 — Coverage replacement**
  - **Files**: `supekku/scripts/lib/requirements/registry.py` — `_apply_coverage_blocks()`
  - **Approach**: At method start, clear `coverage_evidence` and `coverage_entries` for all records. Then for each requirement in `coverage_map`, assign (not union) evidence. Line 813: `sorted(set(...) | artefacts)` → `sorted(artefacts)`.

- **1.3 — Terminal status guard**
  - **Files**: `supekku/scripts/lib/requirements/registry.py` — `_apply_coverage_blocks()` lines 816-818
  - **Approach**: Before `record.status = computed_status`, check `if record.status not in TERMINAL_STATUSES`.

- **1.4 — Tag regex**
  - **Files**: `supekku/scripts/lib/requirements/registry.py` — `_REQUIREMENT_LINE`
  - **Approach**: Add optional `(?:\[([^\]]*)\])?` group after category parentheses. Adjust group indices for title capture.

- **1.5 — Tag population**
  - **Files**: `supekku/scripts/lib/requirements/registry.py` — `_records_from_content()`, `RequirementRecord.merge()`
  - **Approach**: Extract tags from new capture group, split on comma, strip. In merge: `tags = sorted(set(self.tags) | set(other.tags))`.

- **1.6 — Tag filter**
  - **Files**: `supekku/scripts/lib/requirements/registry.py` — `filter()`
  - **Approach**: Add `tag: str | None = None` parameter. Filter: `tag in record.tags`.

- **1.7 — Tests**
  - **Files**: `supekku/scripts/lib/requirements/registry_test.py`
  - **New cases**: Coverage replacement (add/remove/re-sync), idempotency, terminal status guard, tag extraction (with/without category, multiple tags, no tags), tag filter.

## 8. Risks & Mitigations

| Risk                                                   | Mitigation                                                                          | Status |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------- | ------ |
| Regex group index shift breaks existing captures       | Careful: new group inserted between category and title; update all group references | Open   |
| Coverage clear affects requirements consumed elsewhere | Check for external consumers of coverage_evidence before changing                   | Open   |
