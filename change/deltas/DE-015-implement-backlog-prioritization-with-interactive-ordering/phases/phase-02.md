---
id: IP-015.PHASE-02
slug: 015-implement-backlog-prioritization-with-interactive-ordering-phase-02
name: IP-015 Phase 02
created: '2025-11-04'
updated: '2025-11-04'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-015.PHASE-02
plan: IP-015
delta: DE-015
objective: >-
  Implement priority ordering and display logic so backlog items are shown in registry order with severity/ID fallback
entrance_criteria:
  - Phase 1 complete (registry infrastructure working)
  - Registry contains item ordering
exit_criteria:
  - Head-tail partition algorithm implemented and tested
  - Priority sort function implemented
  - list backlog command uses priority ordering by default
  - VT-015-001 and VT-015-003 tests passing
  - Lint checks pass
verification:
  tests:
    - VT-015-001
    - VT-015-003
  evidence:
    - list command output showing priority order
    - test results
tasks:
  - 2.1 Implement head-tail partition algorithm
  - 2.2 Implement priority sort function
  - 2.3 Update discover_backlog_items to use registry ordering
  - 2.4 Update formatters to display in priority order
  - 2.5 Write comprehensive tests
  - 2.6 Run lint and fix issues
risks:
  - Sort function complexity with multiple fallback levels (mitigate with clear tests)
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-015.PHASE-02
status: completed
started: '2025-11-04'
completed: '2025-11-04'
tasks_completed: 5
tasks_total: 5
last_updated: '2025-11-04'
notes: |
  Phase 2 complete: Priority ordering fully operational
  - priority.py: partition algorithm + sort function (10.00/10 pylint)
  - 18 comprehensive tests (VT-015-001, VT-015-003), all passing
  - list backlog: default priority ordering + --order-by-id flag
  - Quality: ruff ✓, all new code 10.00/10 pylint
  - Manual verification: priority order working correctly
  - All exit criteria satisfied ✓
```

# Phase 2 - Priority Ordering Logic

## 1. Objective

Implement the priority ordering and display logic so that backlog items are shown in registry order by default, with severity and ID as fallback ordering criteria. This phase adds the head-tail partition algorithm and sort functions but does NOT yet include interactive editing.

## 2. Links & References
- **Delta**: [DE-015](../DE-015.md)
- **Implementation Plan**: [IP-015](../IP-015.md)
- **Research**: [research-findings.md](../../../../backlog/improvements/IMPR-002-backlog-prioritization-with-interactive-ordering-and-delta-integration/research-findings.md) (sections on head-tail partitioning)
- **Phase 1**: [phase-01.md](./phase-01.md) (registry infrastructure - completed)

## 3. Entrance Criteria
- [x] Phase 1 complete (registry infrastructure working)
- [x] Registry file exists: `.spec-driver/registry/backlog.yaml`
- [x] Registry contains 18 backlog items in order

## 4. Exit Criteria / Done When
- [x] Head-tail partition algorithm implemented
- [x] Priority sort function implemented (registry order → severity → ID)
- [x] `list backlog` command displays items in priority order
- [x] VT-015-001 tests passing (partition algorithm) - 11/11 tests ✓
- [x] VT-015-003 tests passing (sort function) - 7/7 tests ✓
- [x] Lint checks passing - ruff ✓, pylint 10.00/10 on new modules ✓

## 5. Verification

**Tests (VT-015-001, VT-015-003):**
- Unit tests for head-tail partition algorithm
- Unit tests for priority sort function with fallbacks
- Edge cases: empty registry, all items filtered, partial ordering

**Commands:**
```bash
# Run tests
just test

# Lint checks
just lint
just pylint

# Manual verification
uv run spec-driver sync --backlog
uv run spec-driver list backlog
# Verify items appear in registry order (not chronological)
```

**Evidence:**
- Test output showing all tests passing
- `list backlog` output showing priority-based order
- Comparison: registry order vs. display order

## 6. Assumptions & STOP Conditions

**Assumptions:**
- Registry ordering is maintained by Phase 1 sync command
- Items without priority (not in registry) fall back to severity → ID
- Current display uses chronological (ID) ordering by default

**STOP when:**
- Sort algorithm produces unexpected ordering
- Performance issues with large backlogs (>100 items)
- Test coverage gaps discovered

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Implement head-tail partition algorithm | [ ] | Core merge logic |
| [x] | 2.2 | Implement priority sort function | [ ] | Registry → severity → ID |
| [x] | 2.3 | Update list backlog to use priority ordering | [ ] | Modify CLI display |
| [x] | 2.4 | Write comprehensive tests (VT-015-001, VT-015-003) | [P] | Can parallel with 2.3 |
| [x] | 2.5 | Run lint and fix issues | [ ] | Final cleanup |

### Task Details

**2.1 - Implement head-tail partition algorithm** ✅
- **Design**: Algorithm from research findings (lines 186-274)
  - `build_partitions(all_items, filtered_items)` → returns (prefix, [(head, [tail])])
  - Each partition is (shown_item, [unshown_followers])
  - Prefix contains items before first shown item
- **Files**: `supekku/scripts/lib/backlog/priority.py` (new module) ✓
- **Testing**: 11 comprehensive tests (VT-015-001) all passing ✓
- **Observations**:
  - Implemented stateless partition algorithm with proper tail handling
  - Fixed edge case: trailing unshown items attach to last partition
  - Merge function correctly reorders heads with tails following atomically
  - All partition tests pass including roundtrip verification
  - Pylint: 10.00/10 ✓

**2.2 - Implement priority sort function** ✅
- **Design**: `sort_by_priority(items: list[BacklogItem], ordering: list[str]) -> list[BacklogItem]`
  - Create index map from ordering list
  - Sort with key: (registry_index or 999999, severity_rank, id)
  - Severity rank: p1=0, p2=1, p3=2, none=3
- **Files**: `supekku/scripts/lib/backlog/priority.py:116-153` ✓
- **Testing**: 7 comprehensive tests (VT-015-003) all passing ✓
- **Observations**:
  - Pure function with triple-level fallback: registry → severity → ID
  - Case-insensitive severity matching
  - Items not in registry get large position value (999999)
  - All edge cases covered: empty registry, partial registry, same severity
  - Pylint: 10.00/10 ✓

**2.3 - Update list backlog to use priority ordering** ✅
- **Design**: Modify `list_backlog()` in CLI to:
  - Load registry ordering
  - Sort discovered items using sort_by_priority()
  - Display sorted items (existing formatter)
  - Add --order-by-id/-o flag for chronological fallback
- **Files**: `supekku/cli/list.py:1192-1289` ✓
- **Testing**: Manual verification successful ✓
- **Observations**:
  - CLI stays thin - delegates to load_backlog_registry() and sort_by_priority()
  - Default behavior now uses priority ordering (registry → severity → ID)
  - --order-by-id flag provides opt-out to chronological ordering
  - Import ordering fixed with ruff ✓
  - Pre-existing pylint warnings in file unchanged (8.51/10)
  - Manual test: items display in registry order (IMPR-001, IMPR-002 first) ✓

**2.4 - Write comprehensive tests**
- **Design**: `supekku/scripts/lib/backlog/priority_test.py` (new file)
  - VT-015-001: partition algorithm tests
  - VT-015-003: sort function tests
  - Edge cases: empty registry, all filtered, no severity
- **Files**: `supekku/scripts/lib/backlog/priority_test.py`
- **Testing**: `just test`
- **Parallel**: Yes, can write tests alongside implementation

**2.5 - Run lint and fix issues**
- **Design**: Run both linters, fix all issues
- **Commands**: `just lint`, `just pylint`
- **Testing**: Both must pass with zero warnings

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Sort function produces unexpected ordering | Comprehensive test coverage with all fallback scenarios | Planned |
| Performance degradation with large backlogs | Profile with 500 item test; optimize if needed | Accepted |
| Registry out of sync with filesystem | Document that sync should be run before list | Accepted |

## 9. Decisions & Outcomes
- **2025-11-04** - Implement partition algorithm in Phase 2 (not Phase 3) for better code organization
- **2025-11-04** - Create new `priority.py` module for ordering logic (separation of concerns)

## 10. Findings / Research Notes

**From research-findings.md:**
- Head-tail partitioning algorithm (lines 186-274)
- Partition structure: `(shown_item, [unshown_followers])`
- Merge algorithm: reorder heads, tails move atomically
- Storage: flat ordered list (position = priority)

**Current list backlog behavior:**
- `supekku/cli/list.py:1168-1245`
- Uses `discover_backlog_items()` which returns items sorted by ID
- Formatter: `format_backlog_list_table()` in formatters/backlog_formatters.py
- Current display columns: ID, Kind, Status, Title, Severity

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] All tests passing (VT-015-001, VT-015-003)
- [ ] Lint checks passing
- [ ] Manual verification: list backlog shows priority order
- [ ] Phase tracking updated
- [ ] Hand-off notes prepared for Phase 3
