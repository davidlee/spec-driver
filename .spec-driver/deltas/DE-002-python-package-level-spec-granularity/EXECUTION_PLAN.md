# DE-002 Execution Plan

**Date**: 2025-11-02
**Status**: In Progress - Phase 01
**Implementer**: Claude (Agent)

## Research Summary

### Current State Analysis

**Package Count**:
- Total packages: 24 (all directories with `__init__.py`)
- **Leaf packages: 16** (packages with no child packages)

**Leaf Packages Identified**:
```
supekku/cli
supekku/scripts/backlog
supekku/scripts/cli
supekku/scripts/lib/backlog
supekku/scripts/lib/blocks/metadata
supekku/scripts/lib/changes/blocks
supekku/scripts/lib/core/frontmatter_metadata
supekku/scripts/lib/decisions
supekku/scripts/lib/deletion
supekku/scripts/lib/docs/python
supekku/scripts/lib/formatters
supekku/scripts/lib/relations
supekku/scripts/lib/requirements
supekku/scripts/lib/specs
supekku/scripts/lib/sync/adapters
supekku/scripts/lib/validation
```

**Key Findings**:

1. **Registry (`supekku/scripts/lib/specs/registry.py`)**:
   - Already has `find_by_package()` method (line 49-51)
   - Spec model has `packages` property (via frontmatter)
   - **Conclusion**: Registry already package-aware, minimal changes needed

2. **PythonAdapter (`supekku/scripts/lib/sync/adapters/python.py`)**:
   - Currently file-centric (skips `__init__.py` at line 372)
   - Uses `discover_targets()` with file-level iteration
   - **Needs**: Adaptation to discover packages instead of files

3. **Deterministic Ordering**:
   - Confirmed in `supekku/scripts/lib/docs/python/variants.py:40-50`
   - Uses `sorted(path.rglob("*.py"))` for file ordering
   - Already handles directories via `rglob()`
   - **Conclusion**: FR-002 already satisfied

4. **Spec Model (`supekku/scripts/lib/specs/models.py`)**:
   - Has `packages` property (line 25-30)
   - **Conclusion**: Model ready for package-level specs

## Phase 01 Implementation Plan

### Task 1: Package Detection Utilities

**File**: `supekku/scripts/lib/specs/package_utils.py` (new)

**Functions**:
```python
def is_leaf_package(path: Path) -> bool:
    """Check if path is a leaf package (has __init__.py, no child packages)."""

def find_package_for_file(file_path: Path) -> Path | None:
    """Traverse up from file to find containing package."""

def validate_package_path(path: Path) -> None:
    """Validate path is a Python package, raise errors otherwise."""

def find_all_leaf_packages(root: Path) -> list[Path]:
    """Find all leaf packages under root directory."""
```

**Tests**: `supekku/scripts/lib/specs/package_utils_test.py` (new)

### Task 2: VT-001 - Package Detection Tests

**Test Cases**:
- Leaf package identification (16 known leaf packages)
- Non-leaf package rejection (8 parent packages)
- Non-package path rejection (no `__init__.py`)
- Single-file package handling
- Edge cases: deeply nested, test-only packages

**Location**: `supekku/scripts/lib/specs/package_utils_test.py`

### Task 3: VT-002 - Deterministic Ordering Validation

**Enhancement to**: `supekku/scripts/lib/docs/python/variants_test.py`

**Test Cases**:
- Run contract generation 10 times on `supekku/scripts/lib/formatters/`
- Verify byte-identical output
- Test with different file counts (1 file, 5 files, 10+ files)

**Acceptance**: All runs produce identical MD5 hash

### Task 4: Registry Audit

**Findings**:
- `SpecRegistry.find_by_package()` already exists ✓
- `Spec.packages` property already exists ✓
- **Action**: Document in VA-002 that no breaking changes needed

### Task 5: VA-002 - Rollup Extensibility Design Review

**Document**: `change/deltas/DE-002-python-package-level-spec-granularity/VA-002-rollup-extensibility.md`

**Contents**:
- How rollup mechanism could be added via frontmatter (`rollup: true`)
- No breaking changes to existing package specs
- Configuration-driven approach viable

## Phase 01 Exit Criteria

- [ ] `package_utils.py` implemented
- [ ] `package_utils_test.py` passing (VT-001)
- [ ] Deterministic ordering validated (VT-002)
- [ ] VA-002 design review complete
- [ ] All tests passing: `just test`
- [ ] All linters passing: `just lint` + `just pylint`

## Phase 02 Preview

**Actual count**: 16 leaf packages (not ~25-30 as estimated)

**Migration**:
1. Delete existing file-level specs (if any exist)
2. Generate 16 package-level specs (one per leaf package)
3. Update registry sync
4. Validate

## Phase 03 Preview

**Verification**:
- VT-003: Sync integration (test with 5 package specs)
- VT-004: File-to-package resolution
- VA-001: Git diff stability analysis

## Implementation Notes

**Time Estimates (revised)**:
- Phase 01: 2-3 hours ✓
- Phase 02: 1 hour (fewer specs than expected)
- Phase 03: 1 hour
- **Total**: 4-5 hours

**Key Insight**: The existing codebase is already well-prepared for package-level specs. The `Spec.packages` property and `Registry.find_by_package()` method indicate this pattern was anticipated.
