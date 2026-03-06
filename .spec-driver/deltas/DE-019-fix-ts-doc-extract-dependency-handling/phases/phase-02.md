---
id: IP-019.PHASE-02
slug: 019-fix-ts-doc-extract-dependency-handling-phase-02
name: IP-019 Phase 02 - TypeScriptAdapter refactor
created: '2025-11-08'
updated: '2025-11-08'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-019.PHASE-02
plan: IP-019
delta: DE-019
objective: >-
  Refactor TypeScriptAdapter to use npm_utils module, add pre-flight dependency
  validation, and ensure graceful degradation when ts-doc-extract is missing.
entrance_criteria:
  - Phase 1 complete (npm_utils module available and tested)
  - All Phase 1 tests passing (32 tests)
  - npm_utils functions exported from supekku/scripts/lib/core/__init__.py
exit_criteria:
  - TypeScriptAdapter refactored to use npm_utils.get_package_manager_info()
  - Removed duplicate code: is_pnpm_available(), is_bun_available(), _detect_package_manager()
  - Added _ensure_ts_doc_extract_available() method with caching
  - Updated _get_npx_command() to use PackageManagerInfo.build_npx_command with --yes flags
  - Updated generate() to call _ensure_ts_doc_extract_available() at start
  - TypeScript files skipped gracefully with actionable warning when ts-doc-extract missing
  - All TypeScriptAdapter tests updated and passing
  - Manual sync test succeeds with and without ts-doc-extract
verification:
  tests:
    - VT-019-002: Unit tests for TypeScriptAdapter graceful degradation
    - VT-019-004: Existing TypeScriptAdapter tests updated to mock npm_utils
  evidence:
    - pytest output showing all TypeScriptAdapter tests passing
    - Manual test: sync without ts-doc-extract shows warning and skips TypeScript files
    - Manual test: sync with ts-doc-extract generates contracts successfully
tasks:
  - id: '2.1'
    description: Refactor _get_npx_command() to use npm_utils.get_package_manager_info()
    status: pending
  - id: '2.2'
    description: Remove duplicate methods (is_pnpm_available, is_bun_available, _detect_package_manager)
    status: pending
  - id: '2.3'
    description: Add _ensure_ts_doc_extract_available() method with instance-level caching
    status: pending
  - id: '2.4'
    description: Update generate() to validate ts-doc-extract availability upfront
    status: pending
  - id: '2.5'
    description: Update TypeScriptAdapter tests to mock npm_utils, add degradation tests
    status: pending
  - id: '2.6'
    description: Run full verification (tests + manual sync)
    status: pending
risks:
  - risk: Existing TypeScriptAdapter tests may break during refactor
    mitigation: Run tests after each incremental change, fix immediately
    status: open
  - risk: npm_utils caching may not align with TypeScriptAdapter lifecycle
    mitigation: Use instance variable _ts_doc_extract_available for per-adapter caching
    status: mitigated
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-019.PHASE-02
progress:
  - timestamp: '2025-11-10'
    task: '2.1'
    status: completed
    notes: >
      Refactored _get_npx_command() to use get_package_manager_info() with
      instance-level caching (_pm_info). Now delegates to PackageManagerInfo.build_npx_command()
      which includes --yes flags automatically.
  - timestamp: '2025-11-10'
    task: '2.2'
    status: completed
    notes: >
      Removed duplicate PM detection methods: is_pnpm_available(), is_bun_available(),
      _detect_package_manager(). Deleted ~33 lines of code.
  - timestamp: '2025-11-10'
    task: '2.3'
    status: completed
    notes: >
      Added _ensure_ts_doc_extract_available() method with instance-level caching
      (_ts_doc_extract_available). Calls is_npm_package_available() and caches result.
  - timestamp: '2025-11-10'
    task: '2.4'
    status: completed
    notes: >
      Updated generate() to call _ensure_ts_doc_extract_available() upfront.
      On failure, shows warning with PM-specific install instructions via Rich console
      and returns empty list (graceful skip per DEC-019-004).
  - timestamp: '2025-11-10'
    task: '2.5'
    status: completed
    notes: >
      Updated all TypeScriptAdapter tests - deleted obsolete tests for removed methods,
      rewrote _get_npx_command tests to mock get_package_manager_info(),
      added 3 new tests for _ensure and graceful degradation. All 27 tests passing.
  - timestamp: '2025-11-10'
    task: '2.6'
    status: completed
    notes: >
      Full verification complete: ruff (pass), pylint (9.71/10 typescript.py, 10.00/10 test),
      59/59 tests passing (32 npm_utils + 27 TypeScriptAdapter), all sync tests passing (104/104).
```

# Phase 2 - TypeScriptAdapter Refactor

## 1. Objective

Refactor `supekku/scripts/lib/sync/adapters/typescript.py` to eliminate duplicate package manager detection logic by delegating to the new `npm_utils` module. Add pre-flight validation for `ts-doc-extract` availability and ensure graceful degradation with actionable user warnings when the dependency is missing.

**Key deliverables**:
- Remove ~50 lines of duplicate code (PM detection methods)
- Add `_ensure_ts_doc_extract_available()` with caching
- Use `PackageManagerInfo.build_npx_command()` with `--yes` flags
- Skip TypeScript files gracefully with warning when ts-doc-extract unavailable
- All tests passing with npm_utils mocked appropriately

## 2. Links & References
- **Delta**: [DE-019](../DE-019.md)
- **Design Revision Sections**: DR-019 Section 4 (Code Impact Summary), Section 7 (Design Decisions)
- **Specs / PRODs**: SPEC-124 (sync adapters)
- **Support Docs**:
  - Phase 1 npm_utils module: `supekku/scripts/lib/core/npm_utils.py`
  - Current TypeScriptAdapter: `supekku/scripts/lib/sync/adapters/typescript.py:281-415`
  - DR-019 decisions: DEC-019-002 (validate in generate()), DEC-019-003 (cache availability)

## 3. Entrance Criteria
- [x] Phase 1 complete (npm_utils module available)
- [x] All Phase 1 tests passing (32 tests)
- [x] npm_utils functions exported from core/__init__.py
- [ ] Existing TypeScriptAdapter tests passing as baseline

## 4. Exit Criteria / Done When
- [x] `_get_npx_command()` refactored to use `npm_utils.get_package_manager_info()`
- [x] Removed: `is_pnpm_available()`, `is_bun_available()`, `_detect_package_manager()`
- [x] Added: `_ensure_ts_doc_extract_available()` with instance caching
- [x] `_extract_ast()` uses cached pm_info with `--yes` flags
- [x] `generate()` calls `_ensure_ts_doc_extract_available()` at start, skips gracefully if False
- [x] Warning message includes package manager-specific install instructions
- [x] All TypeScriptAdapter tests passing (27/27)
- [ ] Manual sync without ts-doc-extract shows warning and skips TypeScript (deferred to Phase 3)
- [ ] Manual sync with ts-doc-extract generates contracts successfully (deferred to Phase 3)

## 5. Verification

### Tests to run
```bash
# Unit tests for TypeScriptAdapter
uv run pytest supekku/scripts/lib/sync/adapters/typescript_test.py -v

# All sync tests
uv run pytest supekku/scripts/lib/sync/ -v

# Manual tests
# 1. Without ts-doc-extract
npm uninstall -g ts-doc-extract
uv run spec-driver sync  # Should warn and skip TS files

# 2. With ts-doc-extract
npm install -g ts-doc-extract
uv run spec-driver sync  # Should generate contracts

# Lint
uv run ruff check supekku/scripts/lib/sync/adapters/typescript.py
uv run pylint --indent-string "  " supekku/scripts/lib/sync/adapters/typescript.py
```

### Evidence to capture
- pytest output showing all tests passing
- Manual sync output showing graceful skip warning
- Manual sync output showing successful contract generation

## 6. Assumptions & STOP Conditions

**Assumptions**:
- Existing TypeScriptAdapter tests have good coverage of core functionality
- npm_utils module is correct and tested (Phase 1 verification passed)
- TypeScriptAdapter is only used for contract generation (optional feature)

**STOP when**:
- TypeScriptAdapter tests cannot be fixed without changing npm_utils API
- Performance regression detected (pm_info lookup slower than current code)
- Discover that ts-doc-extract is required dependency (not optional)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 2.1 | Refactor _get_npx_command | [ ] | Use get_package_manager_info(), cache pm_info as instance var |
| [ ] | 2.2 | Remove duplicate PM methods | [ ] | Delete is_pnpm_available, is_bun_available, _detect_package_manager |
| [ ] | 2.3 | Add _ensure_ts_doc_extract_available | [ ] | Check local + global, cache result, return bool |
| [ ] | 2.4 | Update generate() with validation | [ ] | Call _ensure at start, skip with warning if False |
| [ ] | 2.5 | Update tests | [ ] | Mock npm_utils, add degradation tests |
| [ ] | 2.6 | Full verification | [ ] | Run all tests + manual sync tests |

### Task Details

#### 2.1 - Refactor _get_npx_command()
- **Design / Approach**:
  - Add instance variable `_pm_info: PackageManagerInfo | None = None`
  - In `_get_npx_command()`, check if `_pm_info` is None, if so call `get_package_manager_info(package_root)`
  - Cache result in `_pm_info` for reuse across files
  - Return `_pm_info.build_npx_command("ts-doc-extract")` instead of manually building command
- **Files / Components**:
  - `typescript.py`: Update `_get_npx_command()` method (lines 309-327)
  - Add import: `from supekku.scripts.lib.core import get_package_manager_info, PackageManagerInfo`
- **Testing**: Existing tests should still pass with npm_utils mocked
- **Observations & AI Notes**: This change centralizes PM detection and adds --yes flags automatically

#### 2.2 - Remove duplicate PM detection methods
- **Design / Approach**:
  - Delete `is_pnpm_available()` (lines 54-57)
  - Delete `is_bun_available()` (lines 59-62)
  - Delete `_detect_package_manager()` (lines 281-307)
  - Remove any imports no longer needed
- **Files / Components**:
  - `typescript.py`: Delete 3 methods (~33 lines)
- **Testing**: Tests should pass after updating mocks in task 2.5
- **Observations & AI Notes**: This is pure deletion, no logic changes

#### 2.3 - Add _ensure_ts_doc_extract_available()
- **Design / Approach**:
  - Add instance variable `_ts_doc_extract_available: bool | None = None`
  - Implement method that:
    - Returns cached value if not None
    - Calls `is_npm_package_available("ts-doc-extract", package_root)`
    - Caches and returns result
  - Package root determined from first file in generate() or None for global-only check
- **Files / Components**:
  - `typescript.py`: Add new method, add instance variables in `__init__` or class body
  - Import: `from supekku.scripts.lib.core import is_npm_package_available`
- **Testing**: Add unit test for caching behavior, test with/without ts-doc-extract available
- **Observations & AI Notes**: Per DEC-019-003, cache per adapter instance to avoid repeated subprocess calls

#### 2.4 - Update generate() with validation
- **Design / Approach**:
  - At start of `generate()`, call `_ensure_ts_doc_extract_available()`
  - If False:
    - Get `pm_info` from first file's package_root (or default npm)
    - Generate warning using `get_install_instructions("ts-doc-extract", pm_info)`
    - Print warning with Rich console
    - Return early (empty list or skip TypeScript files)
  - If True, proceed with normal generation
- **Files / Components**:
  - `typescript.py`: Update `generate()` method (lines 476-609)
  - Import: `from supekku.scripts.lib.core import get_install_instructions`
- **Testing**: Add integration test for graceful skip, verify warning message format
- **Observations & AI Notes**: Per DEC-019-002 and DEC-019-004, validate once at entry point, skip gracefully

#### 2.5 - Update tests
- **Design / Approach**:
  - Find all TypeScriptAdapter tests
  - Mock npm_utils functions: `get_package_manager_info`, `is_npm_package_available`
  - Add new tests:
    - Test graceful skip when ts-doc-extract unavailable
    - Test warning message includes install instructions
    - Test caching of availability check
  - Update existing tests to mock new dependencies
- **Files / Components**:
  - `typescript_test.py`: Update existing tests, add new test cases
- **Testing**: All tests must pass
- **Observations & AI Notes**: May need to mock at class level or per-test depending on test structure

#### 2.6 - Full verification
- **Design / Approach**:
  - Run full test suite
  - Run manual sync tests (with/without ts-doc-extract)
  - Run lint checks
  - Verify no performance regression
- **Files / Components**: All modified files
- **Testing**: Complete test matrix
- **Observations & AI Notes**: Final quality gate before phase completion

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Breaking existing tests during refactor | Run tests after each task, fix immediately | Open |
| Caching not aligned with adapter lifecycle | Use instance variables, clear cache per adapter instantiation | Mitigated |
| Warning message not actionable for users | Use get_install_instructions() for PM-specific guidance | Mitigated |

## 9. Decisions & Outcomes
- `2025-11-08` - Use instance-level caching for pm_info and availability check (aligns with DEC-019-003)
- `2025-11-08` - Validate in generate() not _extract_ast() (aligns with DEC-019-002)

## 10. Findings / Research Notes

**Current TypeScriptAdapter Code Analysis**:
- Lines 54-62: `is_pnpm_available()`, `is_bun_available()` - exact duplicates of npm_utils functions
- Lines 281-307: `_detect_package_manager()` - exact duplicate of npm_utils.detect_package_manager()
- Lines 309-327: `_get_npx_command()` - manually builds command, missing --yes flags (ISSUE-021 root cause)
- Lines 352-415: `_extract_ast()` - runs npx command, no pre-validation (hangs on install prompt)
- Lines 476-609: `generate()` - no pre-flight check, processes all files even if ts-doc-extract missing

**Refactor Impact**:
- Remove ~33 lines of duplicate code
- Add ~30 lines for validation + caching logic
- Net change: similar LOC but much better architecture (DRY, fail-fast, graceful degradation)

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied (code changes complete, automated testing complete)
- [x] Verification evidence: 59/59 tests passing (32 npm_utils + 27 TypeScriptAdapter), 104/104 sync tests
- [ ] Manual sync testing (deferred to Phase 3 integration)
- [ ] IP-019 updated with phase completion
- [x] Hand-off notes: TypeScriptAdapter refactored and ready for Phase 3

## 12. Phase 2 Completion Summary

**Status**: Code implementation complete, automated testing complete
**Date**: 2025-11-10

### Deliverables
1. **Code Changes**:
   - Added `__init__()` with instance variables `_pm_info` and `_ts_doc_extract_available`
   - Refactored `_get_npx_command()` to use npm_utils (15 lines → 7 lines with caching)
   - Deleted 3 duplicate methods (~33 lines)
   - Added `_ensure_ts_doc_extract_available()` method (20 lines)
   - Updated `generate()` with pre-flight validation and graceful degradation (25 lines added)
   - Net change: +47 lines, -33 lines = +14 lines (improved architecture, added caching and validation)

2. **Test Updates**:
   - Deleted 6 obsolete tests (is_pnpm_available, is_bun_available, _detect_package_manager)
   - Rewrote 4 _get_npx_command tests to use proper PackageManagerInfo mocks
   - Added 3 new tests (_ensure caching, not found, graceful degradation)
   - Net: 27 tests (down from 30, but better coverage of actual functionality)

3. **Quality Metrics**:
   - Ruff: All checks passed
   - Pylint: 9.71/10 (typescript.py), 10.00/10 (test) - complexity warnings pre-existing
   - Tests: 59/59 passing (32 npm_utils + 27 TypeScriptAdapter)
   - Sync suite: 104/104 passing

### Key Improvements
- ✅ Eliminated code duplication (DRY principle)
- ✅ Added `--yes` flags to prevent install prompts (ISSUE-021 root cause fixed)
- ✅ Added pre-flight validation (fail-fast per DEC-019-002)
- ✅ Graceful degradation with actionable warnings (DEC-019-004)
- ✅ Instance-level caching for performance (DEC-019-003)

### Next Steps (Phase 3)
- Installer updates to detect missing ts-doc-extract
- Integration test for sync with missing dependency
- Manual verification of warning messages and graceful skip
- Full end-to-end verification
