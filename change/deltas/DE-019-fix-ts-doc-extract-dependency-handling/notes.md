# Notes for DE-019

## Progress Summary (2025-11-08)

### ✅ Phase 1 COMPLETE - npm_utils module
**Agent**: Claude (Session ending 2025-11-08)
**Commit**: 48e9b7e - wip(DE-019): npm_utils module foundation

**Deliverables**:
- Created `supekku/scripts/lib/core/npm_utils.py` (189 lines)
- Created `supekku/scripts/lib/core/npm_utils_test.py` (32 tests, 100% passing)
- Updated `supekku/scripts/lib/core/__init__.py` with exports
- Updated `DE-019.md` frontmatter with ISSUE-021 context_input
- Updated `IP-019.md` verification coverage (VT-019-001: verified)

**Quality Gates**:
- ✅ pytest: 32/32 tests passing
- ✅ ruff: All checks passed
- ✅ pylint: 10.00/10
- ✅ just quickcheck: 1495 tests passing

**Key Implementation Details**:
- TDD approach throughout (tests written first for all functions)
- Package manager detection from lockfiles (pnpm-lock.yaml > bun.lockb > package-lock.json/yarn.lock)
- Local + global npm package detection with executable check (os.access)
- DRY installation instruction generation using PackageManagerInfo
- Auto-includes `--yes` flags in npx/pnpm dlx/bunx commands (prevents hangs)

### ✅ Phase 2 COMPLETE - TypeScriptAdapter refactor
**Agent**: Claude (Session ending 2025-11-10)
**Status**: Code implementation and automated testing complete

**Deliverables**:
- Refactored `_get_npx_command()` to use npm_utils with caching
- Removed 3 duplicate PM detection methods (~33 lines)
- Added `_ensure_ts_doc_extract_available()` with instance caching
- Updated `generate()` with pre-flight validation and graceful skip
- Updated/rewrote 27 TypeScriptAdapter tests (all passing)
- Net change: +47 lines code, -33 lines deleted = +14 lines (better architecture)

**Quality Gates**:
- ✅ pytest: 59/59 passing (32 npm_utils + 27 TypeScriptAdapter)
- ✅ ruff: All checks passed
- ✅ pylint: 9.71/10 (typescript.py), 10.00/10 (test)
- ✅ sync suite: 104/104 tests passing

**Key Implementation Details**:
- Instance-level caching: `_pm_info` and `_ts_doc_extract_available`
- Pre-flight validation in `generate()` prevents silent hangs (ISSUE-021)
- Graceful degradation: returns empty list with warning (not error)
- Warning includes PM-specific install instructions via `get_install_instructions()`
- Uses Rich Console for styled warning output to stderr

### 🔜 Phase 3 READY - Installer & final verification
**Status**: Phase 2 complete, ready for Phase 3
**File**: `change/deltas/DE-019-fix-ts-doc-extract-dependency-handling/phases/phase-03.md` (to be created)

**Next Agent Tasks**:
1. Create Phase 3 sheet: `uv run spec-driver create phase --plan IP-019`
2. Add installer warnings for missing ts-doc-extract in TypeScript projects
3. Create integration test for sync with missing dependency
4. Manual verification: sync with/without ts-doc-extract across package managers
5. Update IP-019 verification coverage (mark VT-019-002, VT-019-004 as verified)

**Critical Design Decisions** (from DR-019):
- DEC-019-002: Validate in `generate()` not `_extract_ast()` (fail-fast)
- DEC-019-003: Cache per adapter instance (avoid repeated subprocess calls)
- DEC-019-004: Skip gracefully with actionable warning (don't fail entire sync)

**Files to Modify**:
- `supekku/scripts/lib/sync/adapters/typescript.py` - main refactor
- `supekku/scripts/lib/sync/adapters/typescript_test.py` - update mocks

**Target Code Locations**:
- Lines 54-62: Delete `is_pnpm_available()`, `is_bun_available()`
- Lines 281-307: Delete `_detect_package_manager()`
- Lines 309-327: Refactor `_get_npx_command()` to use npm_utils
- Lines 352-415: Update `_extract_ast()` to use cached pm_info
- Lines 476-609: Update `generate()` with pre-flight validation

## Agent Handover Checklist
- [x] Phase 1 complete (all tasks 1.1-1.7)
- [x] Phase 1 sheet updated with progress tracking
- [x] Phase 1 wrap-up checklist complete
- [x] Delta frontmatter updated (ISSUE-021 linked)
- [x] IP-019 verification coverage updated (VT-019-001: verified)
- [x] Phase 2 sheet created and fully populated
- [x] Handover notes written in phase-01.md
- [x] This notes.md file updated with progress summary

## Quick Reference Commands
```bash
# Run npm_utils tests
uv run pytest supekku/scripts/lib/core/npm_utils_test.py -v

# Run TypeScriptAdapter tests (baseline for Phase 2)
uv run pytest supekku/scripts/lib/sync/adapters/typescript_test.py -v

# Quick verification
just quickcheck

# Full verification
just

# View delta
uv run spec-driver show delta DE-019

# View phase sheet
cat change/deltas/DE-019-fix-ts-doc-extract-dependency-handling/phases/phase-02.md
```

## npm_utils API Quick Reference
```python
from supekku.scripts.lib.core import (
  get_package_manager_info,  # → PackageManagerInfo
  is_npm_package_available,  # → bool
  get_install_instructions,  # → str
  detect_package_manager,    # → "npm" | "pnpm" | "bun"
)

# Get PM info for a path (auto-detects, includes --yes flags)
pm_info = get_package_manager_info(Path("/project"))
cmd = pm_info.build_npx_command("ts-doc-extract")  # ["npx", "--yes", "ts-doc-extract"]

# Check if package available (local node_modules/.bin or global PATH)
available = is_npm_package_available("ts-doc-extract", Path("/project"))

# Get install instructions (PM-specific, DRY)
instructions = get_install_instructions("ts-doc-extract", pm_info)
```
