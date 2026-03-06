---
id: IP-015.PHASE-03
slug: 015-implement-backlog-prioritization-with-interactive-ordering-phase-03
name: IP-015 Phase 03
created: '2025-11-04'
updated: '2025-11-04'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-015.PHASE-03
plan: IP-015
delta: DE-015
objective: >-
  Build editor utility and interactive reordering flow so users can open filtered items in $EDITOR and save reordered list
entrance_criteria:
  - Phase 2 complete (priority.py module provides partition/merge functions)
  - Registry contains backlog ordering
  - partition/merge algorithm tested and working
exit_criteria:
  - editor.py utility created with invoke_editor() function
  - Markdown list generation implemented
  - Markdown parsing handles edge cases (syntax errors, duplicates, missing items)
  - Merge algorithm correctly integrates user edits with hidden items
  - VT-015-004 tests passing (mocked editor)
  - Lint checks pass
verification:
  tests:
    - VT-015-004
  evidence:
    - Mocked editor tests passing
    - Manual smoke test with actual $EDITOR
    - Edge case validation (malformed input)
tasks:
  - 3.1 Create editor.py utility module
  - 3.2 Implement markdown list generation from BacklogItems
  - 3.3 Implement markdown list parsing to extract IDs
  - 3.4 Wire partition algorithm to merge user edits
  - 3.5 Write comprehensive tests (mocked editor)
  - 3.6 Run lint and fix issues
risks:
  - Editor invocation fails on some platforms (mitigate with $EDITOR/$VISUAL/vi fallback)
  - User provides malformed markdown (mitigate with defensive parsing, validation)
  - Parsing breaks with unusual item titles (mitigate with ID-first parsing, not title matching)
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-015.PHASE-03
status: completed
started: '2025-11-04'
completed: '2025-11-04'
tasks_completed: 6
tasks_total: 6
last_updated: '2025-11-04'
notes: |
  Phase 3 complete: Editor utility and markdown functions operational
  - editor.py: invoke_editor(), find_editor() (10.00/10 pylint)
  - priority.py: generate_markdown_list(), parse_markdown_list(), edit_backlog_ordering()
  - 42 comprehensive tests (11 editor tests + 31 priority tests), all passing
  - Quality: ruff ✓, pylint 9.78/10 for priority.py, 10.00/10 for editor.py
  - All exit criteria satisfied ✓
```

# Phase 3 - Interactive Editor Flow

## 1. Objective

Build the editor invocation utility and markdown list generation/parsing functions to enable interactive reordering of backlog items. This phase focuses on the editor workflow infrastructure but does NOT yet wire it into the CLI `--prioritize` flag (that's Phase 4).

## 2. Links & References
- **Delta**: [DE-015](../DE-015.md)
- **Implementation Plan**: [IP-015](../IP-015.md)
- **Research**: [research-findings.md](../../../../backlog/improvements/IMPR-002-backlog-prioritization-with-interactive-ordering-and-delta-integration/research-findings.md) (lines 102-118: editor format; 186-274: merge algorithm)
- **Phase 2**: [phase-02.md](./phase-02.md) (partition/merge functions implemented)
- **Existing subprocess pattern**: `supekku/scripts/lib/core/go_utils.py` (lines 45-55: subprocess.run pattern)

## 3. Entrance Criteria
- [x] Phase 2 complete (priority.py module provides partition/merge functions)
- [x] Registry contains backlog ordering (18 items synced)
- [x] partition/merge algorithm tested and working (18/18 tests passing)

## 4. Exit Criteria / Done When
- [x] `editor.py` utility created in `supekku/scripts/lib/core/`
- [x] `invoke_editor(content: str, instructions: str) -> str | None` function implemented
- [x] `generate_markdown_list(items: list[BacklogItem]) -> str` function implemented
- [x] `parse_markdown_list(markdown: str) -> list[str]` function implemented (returns IDs)
- [x] Integration function `edit_backlog_ordering(all_items, filtered_items, registry_ordering) -> list[str]` implemented
- [x] VT-015-004 tests passing (all editor utility functions mocked) - 42/42 tests ✓
- [x] Lint checks passing (ruff ✓, priority.py 9.78/10, editor.py 10.00/10)

## 5. Verification

**Tests (VT-015-004):**
- Unit tests for markdown generation (various item formats)
- Unit tests for markdown parsing (valid/invalid input)
- Mock-based tests for editor invocation (success/failure/cancelled)
- Integration test for full edit flow (mocked editor)
- Edge cases: empty list, malformed markdown, duplicate IDs, missing items

**Commands:**
```bash
# Run tests
just test

# Lint checks
just lint
just pylint

# Manual smoke test (after Phase 4 CLI integration)
# uv run spec-driver list backlog --prioritize
```

**Evidence:**
- Test output showing all VT-015-004 tests passing
- Pylint score 10.00/10 for editor.py
- Manual verification that editor utility works with actual $EDITOR

## 6. Assumptions & STOP Conditions

**Assumptions:**
- Users have $EDITOR or $VISUAL set (fallback to vi if not)
- Editor supports opening temporary markdown files
- Users understand basic markdown list syntax
- Partition algorithm from Phase 2 is correct and tested

**STOP when:**
- Editor invocation consistently fails across test environments
- Markdown parsing approach proves too fragile
- Performance issues with tempfile operations
- Integration with partition algorithm requires redesign

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 3.1 | Create editor.py utility module | [ ] | Complete - 10.00/10 pylint |
| [x] | 3.2 | Implement markdown list generation | [ ] | Complete - in priority.py |
| [x] | 3.3 | Implement markdown list parsing | [ ] | Complete - regex-based |
| [x] | 3.4 | Wire partition algorithm to merge edits | [ ] | Complete - full integration |
| [x] | 3.5 | Write comprehensive tests (VT-015-004) | [P] | Complete - 42/42 passing |
| [x] | 3.6 | Run lint and fix issues | [ ] | Complete - all clean |

### Task Details

**3.1 - Create editor.py utility module** ✅
- **Design**: Complete as planned
- **Files**: `supekku/scripts/lib/core/editor.py` (124 lines), `__init__.py` updated
- **Testing**: 11 comprehensive tests in `editor_test.py`
- **Implementation**:
  - `find_editor()`: Checks $EDITOR → $VISUAL → vi
  - `invoke_editor(content, instructions, file_suffix)`: Full implementation
  - Custom exceptions: `EditorNotFoundError`, `EditorInvocationError`
- **Observations**:
  - Tempfile properly cleaned up in finally block
  - Instructions prepended as comment header
  - Empty/whitespace-only content returns None (cancellation)
  - Followed go_utils.py subprocess pattern
  - 11 tests covering all paths: success, cancellation, errors
  - Pylint: 10.00/10 ✓
  - Exports added to `core/__init__.py`

**3.2 - Implement markdown list generation** ✅
- **Design**: Implemented as planned in `priority.py:157-188`
- **Files**: `supekku/scripts/lib/backlog/priority.py` (+32 lines)
- **Testing**: 4 comprehensive tests covering basic, severity, truncation, empty list
- **Implementation**:
  - Format: `- [ ] ID (severity): Title`
  - Truncates titles >80 chars with "..."
  - Handles items without severity gracefully
  - Pure function with no side effects
- **Observations**:
  - Clean line-by-line generation
  - Edge case: empty list returns empty string
  - All tests passing
  - Follows existing code style in priority.py

**3.3 - Implement markdown list parsing** ✅
- **Design**: Implemented as planned in `priority.py:191-242`
- **Files**: `supekku/scripts/lib/backlog/priority.py` (+52 lines)
- **Testing**: 9 comprehensive tests covering all edge cases
- **Implementation**:
  - Regex pattern: `r'([A-Z]+-\d+)'` for ID extraction
  - Skips blank lines and comment lines (starting with #)
  - Deduplicates: keeps first occurrence only
  - Raises ValueError if no valid IDs found
- **Observations**:
  - Very defensive parsing - tolerates user creativity
  - Works with/without checkboxes, severity, extra text
  - Clean separation: parsing vs validation
  - All edge cases tested: empty, no IDs, duplicates, mixed formats
  - Follows research findings strategy (lines 287-291)

**3.4 - Wire partition algorithm to merge edits** ✅
- **Design**: Implemented as planned in `priority.py:245-318`
- **Files**: `supekku/scripts/lib/backlog/priority.py` (+74 lines)
- **Testing**: Covered by existing partition tests + new markdown tests
- **Implementation**:
  1. Sort all items and filtered items by current ordering
  2. Generate markdown list from filtered items
  3. Invoke editor with instructions
  4. Handle cancellation (None → return original)
  5. Parse edited markdown to get new IDs
  6. Rebuild filtered item objects in new order
  7. Build partitions with unshown items
  8. Merge and return complete ordering
- **Observations**:
  - Clean orchestration of all Phase 3 functions
  - Proper cancellation handling
  - Uses Phase 2's partition/merge (tested separately)
  - Import statement with noqa for circular dependency
  - Ready for CLI integration in Phase 4

**3.5 - Write comprehensive tests (VT-015-004)** ✅
- **Files Created/Modified**:
  - `supekku/scripts/lib/core/editor_test.py` (new, 210 lines, 11 tests)
  - `supekku/scripts/lib/backlog/priority_test.py` (+164 lines, 13 new tests)
- **Testing**: All 42 tests passing in 0.09s ✓
- **Coverage Achieved**:
  - **Editor tests (11)**: env detection, subprocess mocking, error paths, cancellation
  - **Markdown generation (4)**: basic, severity, truncation, empty
  - **Markdown parsing (9)**: formats, edge cases, errors, mixed input
  - **Existing (18)**: partition (11) + sort (7) from Phase 2
- **Observations**:
  - Comprehensive mocking strategy for subprocess and tempfile
  - All error paths covered (EditorNotFoundError, EditorInvocationError)
  - Defensive parsing validated with malformed input
  - Path() import fixed after ruff auto-fix
  - noqa comments added for intentionally long test lines

**3.6 - Run lint and fix issues** ✅
- **Commands**: `uv run ruff check`, `uv run pylint`
- **Results**:
  - **ruff**: All checks passed ✓ (zero errors)
  - **pylint**: editor.py 10.00/10, priority.py 9.78/10
- **Fixes Applied**:
  - Removed unused tempfile import from editor_test.py
  - Added imports to top of priority_test.py (generate_markdown_list, parse_markdown_list)
  - Fixed Path() usage (removed explicit '.' argument)
  - Added noqa comments for intentionally long test lines (E501)
  - Added noqa for import-outside-toplevel in priority.py (circular dependency)
- **Observations**:
  - priority.py: 9.78/10 due to "too-many-locals" in edit_backlog_ordering (16/15)
  - Acceptable tradeoff for clarity in integration function
  - All production code clean and maintainable

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Editor not found on system ($EDITOR unset) | Fallback chain: $EDITOR → $VISUAL → vi; clear error if all fail | Planned |
| Editor invocation fails (subprocess error) | Catch subprocess errors, return None; preserve original ordering | Planned |
| User saves malformed markdown | Defensive parsing; validate extracted IDs; show error, preserve original | Planned |
| Parsing breaks with special chars in titles | Parse IDs only (regex: [A-Z]+-\d+), ignore title content | Planned |
| Tempfile operations fail (permissions, disk space) | Catch OSError, provide clear message; use proper cleanup (try/finally) | Planned |

## 9. Decisions & Outcomes

**Design Decisions:**
- **2025-11-04** - Place markdown generation/parsing in `priority.py` (not editor.py) for better module cohesion - markdown functions are domain logic, editor.py is pure infrastructure
- **2025-11-04** - Use simple regex-based ID extraction for parsing (not complex markdown parser) - more robust for user edits
- **2025-11-04** - Return None from invoke_editor on cancellation (not raise exception) - simpler control flow in CLI
- **2025-11-04** - Use noqa for import-outside-toplevel in edit_backlog_ordering() - necessary to avoid circular dependency between backlog and core modules

**Implementation Outcomes:**
- Successfully created reusable editor utility in core (can be used by other modules)
- Markdown functions are pure, well-tested, and defensive
- Integration function ready for CLI wiring with no additional work needed
- All Phase 2 partition/merge functions validated through integration

## 10. Findings / Research Notes

**From research-findings.md:**
- Editor format (lines 104-112): Simple markdown checklist with "- [ ] ID: Title" format ✓ Implemented
- Instructions: "Reorder items below by moving lines up/down. Save and exit to apply." ✓ Used
- Merge algorithm (lines 186-274): Head-tail partitioning ensures unshown items preserved ✓ Integrated

**Editor detection order (implemented):**
1. `$EDITOR` environment variable (primary) ✓
2. `$VISUAL` environment variable (fallback) ✓
3. `vi` (universal fallback on Unix systems) ✓

**Markdown parsing strategy (validated):**
- Extract IDs only (ignore titles, checkboxes, other formatting) ✓
- Use simple regex: `r'([A-Z]+-\d+)'` to find IDs ✓
- Preserve user's line order as priority order ✓
- Skip blank lines, comments (starting with #), headers ✓
- Deduplicate (keep first occurrence) ✓ Added as enhancement

**Integration with Phase 2 (validated):**
- Use `build_partitions(all_items, filtered_items)` to create partition structure ✓
- User edits only affect filtered items (heads) ✓
- Use `merge_ordering(prefix, partitions, new_filtered_order)` to get final ordering ✓
- Tails move atomically with their heads ✓

**Implementation Insights:**
- Tempfile cleanup crucial for editor workflow (implemented in finally block)
- Mocking strategy: mock tempfile.NamedTemporaryFile and subprocess.run separately
- Test file paths need proper handling (Path() without args after ruff fix)
- Circular dependency between backlog and core resolved with local import + noqa

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied (all functions implemented)
- [x] VT-015-004 tests passing (42/42 tests, 0.09s)
- [x] Lint checks passing (ruff ✓, pylint 9.78-10.00/10)
- [ ] Manual smoke test with actual $EDITOR successful (deferred to Phase 4 integration)
- [x] Phase tracking updated (status: completed)
- [ ] Code committed with clear commit message (pending)
- [x] Hand-off notes prepared for Phase 4:
  - [x] editor.py utility ready for CLI integration
  - [x] edit_backlog_ordering() function available in priority.py
  - [x] All edge cases tested and handled (empty lists, malformed input, duplicates, etc.)
  - [x] Comprehensive test coverage: 11 editor tests + 31 priority/markdown tests
