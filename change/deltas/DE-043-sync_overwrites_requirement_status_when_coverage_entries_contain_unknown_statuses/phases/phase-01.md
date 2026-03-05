---
id: IP-043.PHASE-01
slug: 043-code-fix-and-tests
name: IP-043 Phase 01 - Code fix and tests
created: '2026-03-05'
updated: '2026-03-05'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-043.PHASE-01
plan: IP-043
delta: DE-043
objective: >-
  Add validation at the sync boundary so unknown coverage statuses are warned
  and excluded from status derivation; refactor derivation to reference the
  canonical vocabulary.
entrance_criteria:
  - DR-043 reviewed and approved
  - Existing tests passing (just check)
exit_criteria:
  - Unknown coverage statuses excluded from derivation with warning
  - _compute_status_from_coverage() references canonical set
  - VALID_COVERAGE_STATUSES alias exported from verification.py
  - All tests pass (just check)
  - VT-043-001, VT-043-002, VT-043-003 verified
verification:
  tests:
    - VT-043-001
    - VT-043-002
    - VT-043-003
  evidence: []
tasks:
  - id: '1.1'
    description: Add VALID_COVERAGE_STATUSES alias to verification.py
  - id: '1.2'
    description: Write tests for unknown status filtering (TDD)
  - id: '1.3'
    description: Add validation in _apply_coverage_blocks()
  - id: '1.4'
    description: Refactor _compute_status_from_coverage() to use canonical set
  - id: '1.5'
    description: Verify all checks pass
risks:
  - description: Extraction loop duplication makes the filter insertion repetitive
    mitigation: Consider extracting a shared helper if the pattern is identical across all four loops
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-043.PHASE-01
```

# Phase 1 – Code fix and tests

## 1. Objective

Add validation at the sync boundary (`_apply_coverage_blocks()`) so unknown
coverage statuses are warned and excluded from status derivation. Refactor
`_compute_status_from_coverage()` to reference the canonical `VALID_COVERAGE_STATUSES`
set. Write comprehensive tests.

## 2. Links & References

- **Delta**: [DE-043](../DE-043.md)
- **Design Revision**: [DR-043 §4](../DR-043.md) – Code Impact Summary
- **Specs**: PROD-008.FR-001, PROD-009.FR-001, PROD-009.FR-003
- **Key Files**:
  - `supekku/scripts/lib/blocks/verification.py` (VALID_STATUSES)
  - `supekku/scripts/lib/requirements/registry.py` (_apply_coverage_blocks, _compute_status_from_coverage)
  - `supekku/scripts/lib/requirements/registry_test.py` (existing tests)

## 3. Entrance Criteria

- [x] DR-043 reviewed
- [x] Existing tests passing (`just check`) — 2603 passed, baseline 9.56/10

## 4. Exit Criteria / Done When

- [ ] `VALID_COVERAGE_STATUSES` alias exported from `verification.py`
- [ ] `_apply_coverage_blocks()` warns and excludes entries with unknown statuses
- [ ] `_compute_status_from_coverage()` references canonical set, not string literals
- [ ] Invalid entries still stored on `record.coverage_entries` for transparency
- [ ] All tests pass (`just check`)

## 5. Verification

- `just test` — all unit tests pass
- `just lint` + `just pylint` — zero warnings
- VT-043-001: test that unknown status entry is excluded from derivation, warning on stderr
- VT-043-002: test that `_compute_status_from_coverage` filters unknown statuses
- VT-043-003: existing `test_compute_status_from_coverage` still passes (regression)

## 6. Assumptions & STOP Conditions

- **Assumption**: The four extraction loops in `_apply_coverage_blocks()` have
  identical structure and can be treated uniformly
- **STOP when**: The extraction loops have diverged in structure and a shared
  helper would require significant refactoring

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 1.1 | Add `VALID_COVERAGE_STATUSES` alias to `verification.py` | | DEC-043-02 |
| [ ] | 1.2 | Write tests for unknown status filtering (TDD) | | VT-043-001, VT-043-002 |
| [ ] | 1.3 | Add validation in `_apply_coverage_blocks()` | | DR-043 §4 |
| [ ] | 1.4 | Refactor `_compute_status_from_coverage()` to use canonical set | | DR-043 §4 |
| [ ] | 1.5 | Run `just check` and verify all gates pass | | |

### Task Details

- **1.1 – Add `VALID_COVERAGE_STATUSES` alias**
  - **Files**: `supekku/scripts/lib/blocks/verification.py`
  - **Approach**: Add `VALID_COVERAGE_STATUSES = VALID_STATUSES` after line 24.
    Add to `__all__`. Preserves backward compat for existing `VALID_STATUSES` imports.

- **1.2 – Write tests (TDD)**
  - **Files**: `supekku/scripts/lib/requirements/registry_test.py`
  - **Cases**:
    - Entry with `status: "deferred"` excluded from derivation; requirement
      status unchanged
    - Warning printed to stderr naming the invalid status and source file
    - `_compute_status_from_coverage` with mix of valid + unknown: only valid
      entries counted
    - `_compute_status_from_coverage` with all unknown: returns None
    - Existing test cases still pass (regression)

- **1.3 – Add validation in `_apply_coverage_blocks()`**
  - **Files**: `supekku/scripts/lib/requirements/registry.py`
  - **Approach**: In each extraction loop, after extracting `status`, check
    against `VALID_COVERAGE_STATUSES`. If invalid: warn to stderr, skip
    appending to `coverage_map`. Entry is still stored in raw block data
    (which flows to `record.coverage_entries` separately).
  - **Design note**: Per DR-043, invalid entries are excluded from `coverage_map`
    (which feeds derivation) but still appear in `record.coverage_entries`
    (for visibility). The `coverage_entries` assignment at line 678 uses the
    entries from `coverage_map`, so we need to also build a separate
    "all entries" collection. OR: simpler — just let the invalid entries into
    `coverage_map` but filter them in `_compute_status_from_coverage()`. Let
    the warning happen at ingestion but the filtering at derivation.
    **Decision needed during implementation.**

- **1.4 – Refactor `_compute_status_from_coverage()`**
  - **Files**: `supekku/scripts/lib/requirements/registry.py`
  - **Approach**: Import `VALID_COVERAGE_STATUSES`. Change the set
    comprehension to filter: `statuses = {e.get("status") for e in entries if e.get("status") in VALID_COVERAGE_STATUSES}`.
    Remove hardcoded string literals in favor of constants where possible
    (secondary — only if it improves clarity without bloating imports).

- **1.5 – Verify**
  - Run `just check` (tests + lint + pylint)
  - Confirm no regressions

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Four identical extraction loops → repetitive filter insertion | Consider extracting shared helper if warranted | Monitor |
| Filtering at ingestion vs derivation is a design fork | Resolve during 1.3; prefer simplest approach that satisfies DR intent | Open |

## 9. Decisions & Outcomes

*(Record during implementation)*

## 10. Findings / Research Notes

*(Record during implementation)*

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] IP-043 progress tracking updated
- [ ] Hand-off notes to Phase 2
