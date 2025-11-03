---
id: IP-017.PHASE-02
slug: 017-add-category-support-to-requirements-phase-02
name: IP-017 Phase 02
created: '2025-11-04'
updated: '2025-11-04'
status: draft
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

- [ ] `requirement_formatters.py` module created with proper exports
- [ ] `format_requirement_list_item()` pure function returns category column
- [ ] CLI `list requirements` supports `--category` filter (substring match)
- [ ] Existing `-r` (regexp) and `-i` (case-insensitive) filters work with category
- [ ] Category column appears in list output (handle None gracefully)
- [ ] VT-017-003 passing (CLI category filtering integration tests)
- [ ] VT-017-004 passing (category display integration tests)
- [ ] Both linters pass (`just lint`, `just pylint`)
- [ ] Formatters module has comprehensive tests (`formatters/requirement_formatters_test.py`)

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
| [ ] | 2.1 | Create requirement_formatters.py module | [ ] | Pure functions, no business logic |
| [ ] | 2.2 | Implement format_requirement_list_item | [ ] | Include category column |
| [ ] | 2.3 | Add --category filter to CLI | [ ] | Substring match on category field |
| [ ] | 2.4 | Extend regexp/case-insensitive filters | [ ] | Include category in search fields |
| [ ] | 2.5 | Update CLI to use formatter | [ ] | Replace inline formatting |
| [ ] | 2.6 | Write VT-017-003 filtering tests | [ ] | Integration tests for CLI filters |
| [ ] | 2.7 | Write VT-017-004 display tests | [ ] | Integration tests for category column |
| [ ] | 2.8 | Run linters and fix issues | [ ] | ruff + pylint |

### Task Details

**2.1 Create requirement_formatters.py module**
- **Design / Approach**: Follow pattern from `decision_formatters.py` and `change_formatters.py`
- **Files / Components**:
  - Create `supekku/scripts/lib/formatters/requirement_formatters.py`
  - Update `supekku/scripts/lib/formatters/__init__.py` with exports
- **Testing**: Import test in `requirement_formatters_test.py`
- **Observations & AI Notes**: TBD

**2.2 Implement format_requirement_list_item**
- **Design / Approach**: Pure function signature: `format_requirement_list_item(req: RequirementRecord, options: dict) -> str`
- **Files / Components**: `requirement_formatters.py`
- **Testing**: Unit tests for various category values (present, None, special chars)
- **Observations & AI Notes**: Return tab-separated: `{label}\t{status}\t{category}\t{title}`, display "-" for None category

**2.3 Add --category filter to CLI**
- **Design / Approach**: Add `--category` option, filter records where category substring matches
- **Files / Components**: Find list requirements command (likely `supekku/scripts/requirements.py` or `supekku/cli/list.py`)
- **Testing**: Integration tests in VT-017-003
- **Observations & AI Notes**: Use case-sensitive substring match by default, combine with -i for case-insensitive

**2.4 Extend regexp/case-insensitive filters**
- **Design / Approach**: Include category field in regexp and case-insensitive search scope
- **Files / Components**: CLI filter logic
- **Testing**: Integration tests verify filters work on category
- **Observations & AI Notes**: Handle None category gracefully (skip in filter or treat as empty string)

**2.5 Update CLI to use formatter**
- **Design / Approach**: Import and call `format_requirement_list_item()` instead of inline formatting
- **Files / Components**: List requirements CLI
- **Testing**: Existing CLI tests should still pass, new tests verify category column
- **Observations & AI Notes**: Follow skinny CLI pattern - delegate all formatting to formatter module

**2.6 Write VT-017-003 filtering tests**
- **Design / Approach**: Integration tests that create test specs with categories, run CLI commands, verify filtering
- **Files / Components**: New test file or add to existing CLI tests
- **Testing**: pytest
- **Observations & AI Notes**: Use tempdir-based test specs like in Phase 1 tests

**2.7 Write VT-017-004 display tests**
- **Design / Approach**: Integration tests verifying category column appears in output
- **Files / Components**: Same test file as VT-017-003
- **Testing**: pytest with output parsing
- **Observations & AI Notes**: Verify both categorized and uncategorized requirements display correctly

**2.8 Run linters and fix issues**
- **Design / Approach**: `just lint`, `just pylint`, fix warnings
- **Files / Components**: All modified files (formatters, CLI, tests)
- **Testing**: Linters pass with zero warnings
- **Observations & AI Notes**: TBD

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| CLI output format change breaks existing scripts | Keep backward compatible, add category as additional column | Not started |
| Filter logic complexity introduces bugs | Follow existing filter patterns, comprehensive integration tests | Not started |
| Formatter module structure unclear | Review existing formatters as templates, follow AGENTS.md patterns | Not started |
| Cannot locate list requirements CLI command | Use `grep -r "list.*requirement"` to find command entry point | Not started |

## 9. Decisions & Outcomes

- `2025-11-04` - Phase 2 scope: CLI filtering + formatters only (defer CLI command structure changes)

## 10. Findings / Research Notes

**CLI Command Location** (to be confirmed):
- Likely `supekku/scripts/requirements.py` or `supekku/cli/list.py`
- Use `uv run spec-driver list requirements --help` to verify current implementation
- Check `grep -r "def.*list.*requirement" supekku/` for command definition

**Formatter Pattern** (from existing code):
- Pure functions: `def format_X_list_item(artifact: Model) -> str`
- No business logic, only display formatting
- Export via `__init__.py` `__all__` list
- Comprehensive tests in `formatters/X_formatters_test.py`

**Filter Pattern** (to research):
- Check existing decision/change list commands for filter examples
- Likely uses list comprehension: `[r for r in records if matches(r, filters)]`
- Regexp filter typically uses `re.search(pattern, field, re.IGNORECASE if -i else 0)`

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied (all 9 items)
- [ ] VT-017-003 and VT-017-004 evidence captured
- [ ] Lint output captured (zero warnings)
- [ ] IP-017 updated with any plan changes
- [ ] Hand-off notes to Phase 3 (Verification & Polish)
