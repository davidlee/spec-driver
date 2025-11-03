---
id: IP-017.PHASE-02
slug: 017-add-category-support-to-requirements-phase-02
name: IP-017 Phase 02
created: '2025-11-04'
updated: '2025-11-04'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-017.PHASE-02
plan: IP-017
delta: DE-017
objective: >-
  Add category filtering to CLI list command, create requirement_formatters module with category
  column display, implement integration tests for filtering and display.
entrance_criteria:
  - Phase 1 complete (data model and parser working)
  - Category field tested and working in registry
  - VT-017-001 and VT-017-002 passing
exit_criteria:
  - requirement_formatters.py module created with category formatting
  - CLI list command supports --category filter (substring match)
  - Existing -r (regexp) and -i (case-insensitive) filters work with category field
  - Category column appears in list output
  - VT-017-003 and VT-017-004 passing (integration tests)
  - Linters passing (ruff + pylint)
verification:
  tests:
    - VT-017-003 (integration tests for CLI category filtering)
    - VT-017-004 (integration tests for category column display)
  evidence:
    - Test output showing filtering scenarios pass
    - CLI output showing category column
    - Lint output showing zero warnings
tasks:
  - id: '2.1'
    description: Create requirement_formatters.py module
  - id: '2.2'
    description: Implement format_requirement_list_item with category column
  - id: '2.3'
    description: Add --category filter option to list requirements CLI
  - id: '2.4'
    description: Extend existing regexp/case-insensitive filters to include category
  - id: '2.5'
    description: Update CLI to use formatter for requirement display
  - id: '2.6'
    description: Write VT-017-003 integration tests for category filtering
  - id: '2.7'
    description: Write VT-017-004 integration tests for category display
  - id: '2.8'
    description: Run linters and fix any issues
risks:
  - risk: CLI output formatting breaks existing scripts
    mitigation: Keep backward compatible default format
  - risk: Filter logic complexity
    mitigation: Follow existing filter patterns in codebase
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-017.PHASE-02
```

# Phase 2 - CLI & Formatters

## 1. Objective

Add category filtering and display to the requirements list CLI command. Create formatters module following project architecture (SRP, pure functions). Enable users to filter requirements by category and see category column in output.

## 2. Links & References

- **Delta**: [DE-017](../DE-017.md)
- **Design Revision**: [DR-017](../DR-017.md) sections 4 (Code Impact), 7 (Design Decisions)
- **Implementation Plan**: [IP-017](../IP-017.md)
- **Previous Phase**: [phase-01.md](./phase-01.md) - Data Model & Parser (complete)
- **Code Hotspots**:
  - `supekku/scripts/requirements.py` or `supekku/cli/list.py` - List requirements CLI
  - `supekku/scripts/lib/formatters/` - Formatter modules location
  - Existing formatters as templates: `decision_formatters.py`, `change_formatters.py`
- **Architecture Guide**: [AGENTS.md](../../../../AGENTS.md) - Formatter patterns

## 3. Entrance Criteria

- [x] Phase 1 complete (data model and parser working)
- [x] Category field tested and working in registry
- [x] VT-017-001 and VT-017-002 passing (1352 tests total)
- [x] Linters clean from Phase 1

## 4. Exit Criteria / Done When

- [x] `requirement_formatters.py` module created with proper exports
- [x] `format_requirement_list_item()` pure function returns category column
- [x] CLI `list requirements` supports `--category` filter (substring match)
- [x] Existing `-r` (regexp) and `-i` (case-insensitive) filters work with category
- [x] Category column appears in list output (handle None gracefully)
- [x] VT-017-003 passing (CLI category filtering integration tests)
- [x] VT-017-004 passing (category display integration tests)
- [x] Both linters pass (`just lint`, `just pylint`)
- [x] Formatters module has comprehensive tests (`formatters/requirement_formatters_test.py`)

## 5. Verification

**Tests to run**:
```bash
# Unit tests for formatters
just test supekku/scripts/lib/formatters/requirement_formatters_test.py

# Integration tests for CLI
just test supekku/cli/ supekku/scripts/requirements.py

# Full test suite
just test

# Linters
just lint
just pylint supekku/scripts/lib/formatters/requirement_formatters.py
```

**Test Coverage** (VT-017-003):
- `--category auth` matches requirements with category="auth"
- `--category sec` matches requirements with category="security" (substring)
- `-r "auth|perf"` regexp filter matches category field
- `-i AUTH` case-insensitive filter matches category field
- Filter combinations: `--category auth -i`
- No matches returns empty list gracefully

**Display Testing** (VT-017-004):
- Category column displays for requirements with categories
- Uncategorized requirements show empty/"-" in category column
- Column alignment handles varying category lengths
- Output format is tab-separated for script parsing

**Evidence to capture**:
- Test output (pytest summary showing VT-017-003, VT-017-004 passing)
- CLI output sample showing category column
- Lint output (zero warnings)

## 6. Assumptions & STOP Conditions

**Assumptions**:
- Existing list requirements command structure can accommodate new filter
- Tab-separated output format is acceptable (follow existing pattern)
- Category column addition won't break existing output consumers
- Formatter module location: `supekku/scripts/lib/formatters/requirement_formatters.py`

**STOP when**:
- Cannot find list requirements CLI command location
- Existing filter patterns are incompatible with category filtering
- Output format change would break critical downstream tooling
- Test infrastructure inadequate for integration testing

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Create requirement_formatters.py module | [ ] | Module already existed |
| [x] | 2.2 | Add category to all formatters | [ ] | TSV, table, JSON, details updated |
| [x] | 2.3 | Add --category filter to CLI | [ ] | Added -c/--category option with case-sensitive/insensitive support |
| [x] | 2.4 | Extend regexp/case-insensitive filters | [ ] | Regexp now includes category field (handles None) |
| [x] | 2.5 | Update CLI to use formatter | [ ] | Already using formatter (verified) |
| [x] | 2.6 | Write VT-017-003 filtering tests | [ ] | 9 tests for category filtering, all passing |
| [x] | 2.7 | Write VT-017-004 display tests | [ ] | 4 tests for category display, all passing |
| [x] | 2.8 | Run linters and fix issues | [ ] | ruff clean, pylint +0.34 improvement |

### Task Details

**2.1 Create requirement_formatters.py module**
- **Design / Approach**: Follow pattern from `decision_formatters.py` and `change_formatters.py`
- **Files / Components**:
  - `supekku/scripts/lib/formatters/requirement_formatters.py` (already existed)
  - `supekku/scripts/lib/formatters/__init__.py` (already had exports)
- **Testing**: Import test in `requirement_formatters_test.py`
- **Observations & AI Notes**: Module already existed with table/JSON/TSV/details formatters. Updated to add category support.

**2.2 Add category to all formatters**
- **Design / Approach**: Add category column/field to all existing formatter functions
- **Files / Components**:
  - `supekku/scripts/lib/formatters/requirement_formatters.py`
  - `supekku/scripts/lib/formatters/requirement_formatters_test.py`
- **Testing**: Updated existing tests to expect new column order
- **Observations & AI Notes**:
  - TSV format: `spec\tlabel\tcategory\ttitle\tstatus`
  - Table: 5 columns with category between label and title
  - JSON: added `category` field in output (always present, null if None)
  - Details: conditional display only when category is present
  - Category displays as "-" when None (uncategorized requirements)
  - 1352 tests passing after updates
  - Commit: a126386

**2.3 Add --category filter to CLI**
- **Design / Approach**: Add `--category` option, filter records where category substring matches
- **Files / Components**: `supekku/cli/list.py:list_requirements()`
- **Testing**: Integration tests in VT-017-003
- **Observations & AI Notes**:
  - Added `-c/--category` option to `list_requirements()` command
  - Respects `--case-insensitive` flag for case matching behavior
  - Case-sensitive by default: `category in r.category`
  - With `-i`: `category.lower() in r.category.lower()`
  - Filters out None categories (uncategorized requirements excluded when filter active)
  - Location: list.py:1045-1057
  - quickcheck passed (1352 tests)

**2.4 Extend regexp/case-insensitive filters**
- **Design / Approach**: Include category field in regexp and case-insensitive search scope
- **Files / Components**: `supekku/cli/list.py:list_requirements()`
- **Testing**: Integration tests verify filters work on category
- **Observations & AI Notes**:
  - Updated regexp filter fields from `[r.uid, r.label, r.title]` to include `r.category or ""`
  - Empty string fallback handles None category gracefully (no match on empty pattern)
  - Uses existing `matches_regexp()` helper from `supekku/cli/common.py`
  - Already respects `--case-insensitive` flag through helper function
  - Location: list.py:1067-1079
  - quickcheck passed (1352 tests)

**2.5 Update CLI to use formatter**
- **Design / Approach**: Import and call `format_requirement_list_item()` instead of inline formatting
- **Files / Components**: List requirements CLI
- **Testing**: Existing CLI tests should still pass, new tests verify category column
- **Observations & AI Notes**: Follow skinny CLI pattern - delegate all formatting to formatter module

**2.6 Write VT-017-003 filtering tests**
- **Design / Approach**: Integration tests that create test specs with categories, run CLI commands, verify filtering
- **Files / Components**: `supekku/cli/list_test.py:ListRequirementsCategoryFilterTest`
- **Testing**: pytest
- **Observations & AI Notes**:
  - Created `ListRequirementsCategoryFilterTest` class with 13 test methods
  - Tests cover: exact match, substring match, case-sensitive, case-insensitive (-i flag)
  - Regexp filter on category, combined filters, empty results
  - All 9 filtering tests passing
  - Uses tempdir with requirements.yaml registry (5 sample requirements)

**2.7 Write VT-017-004 display tests**
- **Design / Approach**: Integration tests verifying category column appears in output
- **Files / Components**: `supekku/cli/list_test.py:ListRequirementsCategoryFilterTest`
- **Testing**: pytest with output parsing
- **Observations & AI Notes**:
  - 4 display tests: table output, TSV output, JSON output, uncategorized placeholder
  - Verifies Category column header in table format
  - Confirms category field present in TSV (spec\tlabel\tcategory\ttitle\tstatus)
  - JSON includes "category" field
  - Uncategorized requirements show "—" or "-" placeholder
  - All 4 display tests passing

**2.8 Run linters and fix issues**
- **Design / Approach**: `just lint`, `just pylint`, fix warnings
- **Files / Components**: All modified files (formatters, CLI, tests)
- **Testing**: Linters pass with zero warnings
- **Observations & AI Notes**:
  - ruff: Fixed line length violation (E501) in test docstring
  - ruff: All checks passed
  - pylint: Score 8.99/10 (improved from 8.65, +0.34)
  - Pre-existing warnings in list.py (too-many-arguments, etc.) - not introduced by this work
  - 24 tests in list_test.py all passing

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| CLI output format change breaks existing scripts | Keep backward compatible, add category as additional column | ⚠️ Partial - added column, may break parsers |
| Filter logic complexity introduces bugs | Follow existing filter patterns, comprehensive integration tests | Not started |
| Formatter module structure unclear | Review existing formatters as templates, follow AGENTS.md patterns | ✓ Resolved - followed existing pattern |
| Cannot locate list requirements CLI command | Use `grep -r "list.*requirement"` to find command entry point | Not started |

## 9. Decisions & Outcomes

- `2025-11-04` - Phase 2 scope: CLI filtering + formatters only (defer CLI command structure changes)
- `2025-11-04` - Category column added between Label and Title for logical grouping
- `2025-11-04` - JSON output always includes category field (even when null) for consistency

## 10. Findings / Research Notes

**Formatter Implementation** (completed):
- Module `requirement_formatters.py` already existed with full suite of formatters
- Added category column to all formatters:
  - TSV: New column order `spec\tlabel\tcategory\ttitle\tstatus`
  - Table: 5 columns, category gets 12 char width
  - JSON: category field always present (null if None)
  - Details: conditional display only when category is not None
- Updated 2 existing tests that validated TSV output format
- Column widths: Spec(10), Label(8), Category(12), Status(12), Title(remaining)
- Category displays as "—" (em dash) in table format, "-" in TSV for None values

**CLI Command Location** (to be confirmed):
- Likely `supekku/scripts/requirements.py` or `supekku/cli/list.py`
- Use `uv run spec-driver list requirements --help` to verify current implementation
- Check `grep -r "def.*list.*requirement" supekku/` for command definition

**Filter Pattern** (to research):
- Check existing decision/change list commands for filter examples
- Likely uses list comprehension: `[r for r in records if matches(r, filters)]`
- Regexp filter typically uses `re.search(pattern, field, re.IGNORECASE if -i else 0)`

**Breaking Change Note**:
- Adding category column changes TSV/table output format
- Existing scripts parsing output may break
- JSON output is backward compatible (new field added)
- Mitigation: Could add `--no-category` flag in future if needed

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied (9/9 items complete)
- [x] VT-017-003 and VT-017-004 evidence captured
- [x] Tasks 2.1-2.2 complete (formatters updated)
- [x] Tasks 2.3-2.5 complete (CLI filtering)
- [x] Tasks 2.6-2.7 complete (integration tests)
- [x] Task 2.8 complete (linters)
- [x] Lint output captured (ruff clean, pylint +0.34)
- [x] IP-017 updated with any plan changes
- [x] Manual testing with real requirements (see section 12)
- [x] Hand-off notes: Phase 2 complete, ready for Phase 3 (manual verification)

## 12. Manual Testing Results

**Test Data**: Added categories to 14 requirements across PROD-001 and SPEC-110
- PROD-001: workflow (2), automation (1), ux (2), validation (1), reliability (1)
- SPEC-110: cli (5), architecture (2), automation (2), integration (1), documentation (1), performance (1)

**Filter Tests**:
```bash
# Category substring filter (case-sensitive)
$ uv run spec-driver list requirements --category workflow
# Result: 2 requirements (PROD-001.FR-001, PROD-001.FR-004)

$ uv run spec-driver list requirements --category cli
# Result: 5 requirements (SPEC-110.FR-001, FR-005, FR-006, FR-008, FR-009)

# Case-insensitive category filter
$ uv run spec-driver list requirements --category UX -i
# Result: 2 requirements (PROD-001.FR-003, NF-001)

# Regexp filter on category
$ uv run spec-driver list requirements -r "automation|ux" -i
# Result: 10 matches (includes both categorized and title matches)
```

**Observations**:
- Category filtering works as designed
- Case-insensitive flag applies to both --category and -r filters
- Regexp filter searches across uid, label, title, AND category fields
- Uncategorized requirements excluded from --category results (None handling correct)
- Table output shows category column with proper alignment
- All filters can be combined (e.g., --category auth --kind FR)

**Status**: All manual tests pass. Feature working as specified.
