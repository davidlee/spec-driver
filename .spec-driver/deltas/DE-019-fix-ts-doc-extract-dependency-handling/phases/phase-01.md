---
id: IP-019.PHASE-01
slug: 019-fix-ts-doc-extract-dependency-handling-phase-01
name: IP-019 Phase 01 - npm_utils module (TDD)
created: '2025-11-08'
updated: '2025-11-08'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-019.PHASE-01
plan: IP-019
delta: DE-019
objective: >-
  Create supekku/scripts/lib/core/npm_utils.py module with comprehensive test coverage
  using TDD approach. Module provides package manager detection, availability checks,
  command building, and installation instruction generation for npm/pnpm/bun.
entrance_criteria:
  - DR-019 design revision reviewed and approved
  - IP-019 implementation plan complete
  - Development environment ready (uv, python, linters configured)
exit_criteria:
  - npm_utils.py module complete with all planned functions
  - npm_utils_test.py achieves 100% test coverage
  - All tests passing (pytest)
  - Lint passing (ruff + pylint)
  - Code reviewed against DR-019 specification
verification:
  tests:
    - VT-019-001: Unit tests for npm_utils (package detection, availability, command building)
  evidence:
    - pytest output showing all tests passing
    - coverage report showing 100% for npm_utils.py
    - ruff and pylint output showing zero warnings
tasks:
  - id: '1.1'
    description: Create npm_utils.py stub and test file
    status: completed
  - id: '1.2'
    description: TDD - Package manager availability checks
    status: completed
  - id: '1.3'
    description: TDD - Package manager detection from lockfiles
    status: completed
  - id: '1.4'
    description: TDD - PackageManagerInfo dataclass and get_package_manager_info()
    status: completed
  - id: '1.5'
    description: TDD - is_npm_package_available() with local/global detection
    status: completed
  - id: '1.6'
    description: TDD - get_install_instructions() message generation
    status: completed
  - id: '1.7'
    description: Run full test suite and lint checks
    status: completed
risks:
  - risk: Package manager command syntax may vary across versions
    mitigation: Document tested versions in tests, add comments with version info
    status: mitigated
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-019.PHASE-01
progress:
  - timestamp: '2025-11-08T00:00:00Z'
    task: '1.1'
    status: completed
    note: Created npm_utils.py stub with module docstring and imports. Created npm_utils_test.py with basic import test. Initial test passing.
  - timestamp: '2025-11-08T00:01:00Z'
    task: '1.2'
    status: completed
    note: TDD - Added tests for is_npm_available(), is_pnpm_available(), is_bun_available(). Implemented all three functions using which() pattern. 7 tests passing.
  - timestamp: '2025-11-08T00:02:00Z'
    task: '1.3'
    status: completed
    note: TDD - Added 9 tests for detect_package_manager() covering lockfile detection (pnpm-lock.yaml, bun.lockb, package-lock.json, yarn.lock), directory traversal, priority ordering, and file vs directory paths. Implemented function extracted from typescript.py:281-307. All tests passing.
  - timestamp: '2025-11-08T00:03:00Z'
    task: '1.4'
    status: completed
    note: TDD - Created PackageManagerInfo dataclass with build_npx_command callable. Added 5 tests for get_package_manager_info() covering npm/pnpm/bun detection, correct command generation (npx --yes, pnpm dlx --package=X X, bunx --yes), and fallback to npm when PM not available. 21 tests total passing.
  - timestamp: '2025-11-08T00:04:00Z'
    task: '1.5'
    status: completed
    note: TDD - Implemented is_npm_package_available() with 6 tests covering local node_modules/.bin detection (with executable check), global PATH fallback, and priority ordering. Function checks local first (os.access for executable), then falls back to which(). 27 tests passing.
  - timestamp: '2025-11-08T00:05:00Z'
    task: '1.6'
    status: completed
    note: TDD - Implemented get_install_instructions() with 5 tests covering npm/pnpm/bun command formatting, prefer_local flag behavior, and multiline output. Function generates DRY installation messages using PackageManagerInfo fields. 32 tests passing.
  - timestamp: '2025-11-08T00:06:00Z'
    task: '1.7'
    status: completed
    note: Final verification - All 32 tests passing. Ruff lint passing (fixed import order, line length, nested if). Pylint 10.00/10. Updated supekku/scripts/lib/core/__init__.py to export all npm_utils functions. just quickcheck passing (1495 total tests).
```

# Phase 1 - npm_utils module (TDD)

## 1. Objective

Create a new shared utility module `supekku/scripts/lib/core/npm_utils.py` that centralizes all npm package manager logic for reuse across TypeScriptAdapter, installer, and future doctor command. Use Test-Driven Development approach to ensure comprehensive coverage and correctness.

**Key deliverables**:
- Package manager detection (npm, pnpm, bun) from lockfiles
- Availability checks for package managers
- Command building with correct auto-install syntax for each PM
- Local + global npm package detection
- DRY installation instruction generation

## 2. Links & References
- **Delta**: [DE-019](../DE-019.md)
- **Design Revision Sections**: DR-019 Section 10 (Implementation Details - npm_utils.py)
- **Specs / PRODs**: SPEC-124 (sync adapters)
- **Support Docs**:
  - Package manager docs: npx, pnpm dlx, bunx
  - Existing pattern: `supekku/scripts/lib/core/go_utils.py` (similar availability checks)

## 3. Entrance Criteria
- [x] DR-019 design revision reviewed and approved
- [x] IP-019 implementation plan complete
- [x] Development environment ready (uv, python, linters configured)
- [x] Familiar with existing `go_utils.py` pattern for availability checks

## 4. Exit Criteria / Done When
- [x] `supekku/scripts/lib/core/npm_utils.py` created with all functions from DR-019
- [x] `supekku/scripts/lib/core/npm_utils_test.py` achieves 100% test coverage
- [x] All unit tests passing (`uv run pytest supekku/scripts/lib/core/npm_utils_test.py`)
- [x] Ruff lint passing (`uv run ruff check supekku/scripts/lib/core/npm_utils.py`)
- [x] Pylint passing (`uv run pylint supekku/scripts/lib/core/npm_utils.py`)
- [x] Code reviewed against DR-019 specification
- [x] `__init__.py` updated to export npm_utils functions

## 5. Verification

### Tests to run
```bash
# Unit tests
uv run pytest supekku/scripts/lib/core/npm_utils_test.py -v

# Coverage check
uv run pytest supekku/scripts/lib/core/npm_utils_test.py --cov=supekku/scripts/lib/core/npm_utils --cov-report=term-missing

# Lint
uv run ruff check supekku/scripts/lib/core/npm_utils.py
uv run pylint --indent-string "  " supekku/scripts/lib/core/npm_utils.py
```

### Evidence to capture
- pytest output showing all tests passing
- Coverage report showing 100% coverage
- Lint output showing zero warnings

## 6. Assumptions & STOP Conditions

**Assumptions**:
- Package manager command syntax documented in DR-019 is current and correct
- `shutil.which()` is reliable for availability detection
- Package managers use standard lockfile names (pnpm-lock.yaml, bun.lockb, etc.)

**STOP when**:
- Package manager syntax found to be incorrect (requires DR-019 update)
- Dependency conflicts discovered (requires architecture discussion)
- Test coverage cannot reach 100% due to untestable code paths (requires refactor)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Create npm_utils.py stub and test file | [ ] | Complete - module structure created |
| [x] | 1.2 | TDD - Package manager availability checks | [ ] | Complete - 3 functions, 6 tests passing |
| [x] | 1.3 | TDD - Package manager detection | [ ] | Complete - 1 function, 9 tests passing |
| [x] | 1.4 | TDD - PackageManagerInfo and builder | [ ] | Complete - dataclass + builder, 5 tests passing |
| [x] | 1.5 | TDD - npm package availability check | [ ] | Complete - 6 tests, local/global detection with executable check |
| [x] | 1.6 | TDD - Install instructions generator | [ ] | Complete - 5 tests, DRY message generation for all package managers |
| [x] | 1.7 | Run full test suite and lint | [ ] | Complete - 32 tests passing, ruff+pylint clean, __init__.py updated |

### Task Details

#### 1.1 - Create npm_utils.py stub and test file
- **Design / Approach**:
  - Create `supekku/scripts/lib/core/npm_utils.py` with module docstring
  - Create `supekku/scripts/lib/core/npm_utils_test.py` with basic structure
  - Add imports: `Path`, `dataclass`, `Literal`, `Callable`, `subprocess`, `shutil.which`
  - Define `PackageManager` type alias: `Literal["npm", "pnpm", "bun"]`
- **Files / Components**:
  - `supekku/scripts/lib/core/npm_utils.py` (new)
  - `supekku/scripts/lib/core/npm_utils_test.py` (new)
- **Testing**: No tests yet, just structure
- **Observations & AI Notes**: Follow existing pattern from `go_utils.py`
- **Commits / References**: Initial commit with module stubs

#### 1.2 - TDD - Package manager availability checks
- **Design / Approach**:
  - Write tests first for `is_npm_available()`, `is_pnpm_available()`, `is_bun_available()`
  - Test cases:
    - PM available (mock `which()` returning `/usr/bin/npm`)
    - PM not available (mock `which()` returning None)
  - Implement functions using `shutil.which()` pattern from `go_utils.py`
- **Files / Components**:
  - `npm_utils.py`: Add 3 functions
  - `npm_utils_test.py`: Add test class with 6 test methods (2 per function)
- **Testing**:
  ```python
  @patch("supekku.scripts.lib.core.npm_utils.which")
  def test_is_npm_available_true(mock_which):
      mock_which.return_value = "/usr/bin/npm"
      assert is_npm_available() is True
  ```
- **Observations & AI Notes**: Pattern is identical to `is_go_available()`
- **Commits / References**: TDD cycle - tests → implementation → green

#### 1.3 - TDD - Package manager detection from lockfiles
- **Design / Approach**:
  - Write tests first for `detect_package_manager(path: Path) -> PackageManager`
  - Test cases:
    - pnpm-lock.yaml found → return "pnpm"
    - bun.lockb found → return "bun"
    - package-lock.json found → return "npm"
    - yarn.lock found → return "npm"
    - No lockfile found → return "npm" (default)
    - Nested directories (walk up to find lockfile)
  - Implement using Path.parent walking logic from current TypeScriptAdapter
- **Files / Components**:
  - `npm_utils.py`: Add `detect_package_manager()` function
  - `npm_utils_test.py`: Add test class with 6+ test methods
- **Testing**: Use `tmp_path` fixture to create test directory structures with lockfiles
- **Observations & AI Notes**: Extract logic from `typescript.py:281-307`
- **Commits / References**: TDD cycle - tests → implementation → green

#### 1.4 - TDD - PackageManagerInfo dataclass and get_package_manager_info()
- **Design / Approach**:
  - Write tests first for `PackageManagerInfo` dataclass
  - Test `get_package_manager_info(path: Path) -> PackageManagerInfo`
  - Test cases:
    - npm project → returns npm PackageManagerInfo with correct commands
    - pnpm project (with pnpm available) → returns pnpm PackageManagerInfo
    - bun project (with bun available) → returns bun PackageManagerInfo
    - pnpm project but pnpm not available → falls back to npm
  - Verify `build_npx_command()` callable generates correct syntax:
    - npm: `["npx", "--yes", "pkg"]`
    - pnpm: `["pnpm", "dlx", "--package=pkg", "pkg"]`
    - bun: `["bunx", "--yes", "pkg"]`
- **Files / Components**:
  - `npm_utils.py`: Add `PackageManagerInfo` dataclass, `get_package_manager_info()` function
  - `npm_utils_test.py`: Add test class with 4+ test methods
- **Testing**: Mock `detect_package_manager()`, `is_pnpm_available()`, `is_bun_available()`
- **Observations & AI Notes**: This is core function that other modules will use
- **Commits / References**: TDD cycle - tests → implementation → green

#### 1.5 - TDD - is_npm_package_available() with local/global detection
- **Design / Approach**:
  - Write tests first for `is_npm_package_available(package_name: str, package_root: Path | None = None) -> bool`
  - Test cases:
    - Local installation exists (`package_root/node_modules/.bin/pkg` exists and executable)
    - Global installation exists (local not found, but `which(pkg)` returns path)
    - Not installed anywhere (local and global checks fail)
    - No package_root provided (only check global)
  - Implement using Path.exists() check for local, `which()` for global
- **Files / Components**:
  - `npm_utils.py`: Add `is_npm_package_available()` function
  - `npm_utils_test.py`: Add test class with 4+ test methods
- **Testing**: Use `tmp_path` fixture, mock `which()`, create fake node_modules/.bin/
- **Observations & AI Notes**: Check local first (project-specific), then global
- **Commits / References**: TDD cycle - tests → implementation → green

#### 1.6 - TDD - get_install_instructions() message generation
- **Design / Approach**:
  - Write tests first for `get_install_instructions(package_name: str, pm_info: PackageManagerInfo, prefer_local: bool = False) -> str`
  - Test cases:
    - npm package manager → correct npm install commands
    - pnpm package manager → correct pnpm add commands
    - bun package manager → correct bun add commands
    - prefer_local=True → local command shown first
    - prefer_local=False → global command shown first
  - Generate formatted multi-line string with install options
- **Files / Components**:
  - `npm_utils.py`: Add `get_install_instructions()` function
  - `npm_utils_test.py`: Add test class with 5+ test methods
- **Testing**: Verify exact string output format, ensure no hardcoded package managers
- **Observations & AI Notes**: DRY source for all installation instructions
- **Commits / References**: TDD cycle - tests → implementation → green

#### 1.7 - Run full test suite and lint checks
- **Design / Approach**:
  - Run pytest with coverage
  - Run ruff check
  - Run pylint
  - Update `supekku/scripts/lib/core/__init__.py` to export npm_utils functions
  - Fix any lint warnings
- **Files / Components**:
  - `supekku/scripts/lib/core/__init__.py` (update exports)
- **Testing**: All previous tests must pass
- **Observations & AI Notes**: Final quality gate before phase completion
- **Commits / References**: Commit any lint fixes, export updates

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Package manager command syntax incorrect or version-specific | Document tested versions in test comments, verify with manual testing | Open |
| Local package detection unreliable on some systems | Add fallback logic, comprehensive testing with tmp_path fixtures | Open |
| Performance overhead from subprocess calls | Design already includes caching at adapter level | Mitigated |

## 9. Decisions & Outcomes

- `2025-11-08` - Use TDD approach for npm_utils (ensures correctness and coverage from start)
- `2025-11-08` - Follow `go_utils.py` pattern for consistency with existing codebase

## 10. Findings / Research Notes

- Verified package manager syntax from user research:
  - `npx --yes <package>` - npm
  - `pnpm dlx --package=<package> <package>` - pnpm requires package twice
  - `bunx --yes <package>` - bun
- Existing pattern in `go_utils.py:13-23` for `is_go_available()` using `which()`
- TypeScriptAdapter current detection logic at `typescript.py:281-307` can be extracted as-is

**Implementation Complete (All Tasks 1.1-1.7)**:
- Module structure created with proper docstrings and type hints
- 32 tests passing covering all npm_utils functionality
- Confirmed correct command syntax for all three package managers (npm/pnpm/bun)
- Fallback to npm when detected PM not available works correctly
- Local package detection checks executable permission via os.access()
- Global package detection uses which() fallback
- DRY installation instructions generated with PackageManagerInfo
- All exports added to supekku/scripts/lib/core/__init__.py
- Ruff lint: All checks passed
- Pylint: 10.00/10 score
- just quickcheck: 1495 tests passing

**Phase 1 Status**: COMPLETE - Ready for Phase 2 (TypeScriptAdapter refactor)

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied (all items in Section 4 checked)
- [x] Verification evidence stored (pytest + coverage + lint output)
- [x] IP-019 updated with phase completion
- [x] Hand-off notes: npm_utils module ready for use by TypeScriptAdapter (Phase 2)

### Hand-off to Phase 2

**Status**: Phase 1 COMPLETE - Ready for Phase 2 implementation

**What was delivered**:
- `supekku/scripts/lib/core/npm_utils.py` - 189 lines, fully implemented and tested
- `supekku/scripts/lib/core/npm_utils_test.py` - 32 tests, 100% passing
- Exported functions added to `supekku/scripts/lib/core/__init__.py`
- All quality gates passed: ruff (clean), pylint (10/10), just quickcheck (1495 tests)

**Key functions available for Phase 2**:
- `get_package_manager_info(path)` → PackageManagerInfo with build_npx_command callable
- `is_npm_package_available(pkg, root)` → bool (checks local + global)
- `get_install_instructions(pkg, pm_info, prefer_local)` → str (DRY messages)
- `detect_package_manager(path)`, `is_npm_available()`, `is_pnpm_available()`, `is_bun_available()`

**Important implementation notes**:
- PackageManagerInfo.build_npx_command includes `--yes` flags automatically (prevents hangs)
- is_npm_package_available checks local node_modules/.bin first (with executable check), then global PATH
- All functions use subprocess-based detection (which, os.access) - cache results to avoid overhead

**Next agent should**:
1. Read `change/deltas/DE-019-fix-ts-doc-extract-dependency-handling/phases/phase-02.md`
2. Verify baseline: run `uv run pytest supekku/scripts/lib/sync/adapters/typescript_test.py -v`
3. Start with Task 2.1 (refactor _get_npx_command)
4. Work incrementally through tasks 2.1-2.6, running tests after each change

**Files to modify in Phase 2**:
- `supekku/scripts/lib/sync/adapters/typescript.py` - main refactor target
- `supekku/scripts/lib/sync/adapters/typescript_test.py` - update mocks, add degradation tests

**Critical**: Follow DR-019 design decisions (validate in generate(), cache per instance, skip gracefully)
