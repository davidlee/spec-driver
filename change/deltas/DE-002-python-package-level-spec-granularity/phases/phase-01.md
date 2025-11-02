```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-002.PHASE-01
plan: IP-002
delta: DE-002
name: Phase 01 - Tooling & Validation
objective: >-
  Implement package detection logic, validate deterministic ordering,
  audit registry for package-level support. Ensure foundation is sound
  before migration.
entrance_criteria:
  - PROD-005 spec approved and synced
  - DE-002 delta created
  - Research complete on existing codebase
exit_criteria:
  - Package detection logic implemented and tested
  - Deterministic ordering validated across platforms
  - Registry audit complete with adaptation plan
  - VT-001 and VT-002 passing
  - VA-002 design review complete
```

# Phase 01 - Tooling & Validation

## 1. Objective

Implement and validate the foundational utilities for package-level spec granularity:
- Package detection logic (leaf package identification)
- Validate deterministic file ordering already works
- Audit registry for package-level compatibility
- Document rollup extensibility approach

This phase ensures the technical foundation is solid before executing the migration.

## 2. Links & References

- **Delta**: DE-002
- **Plan**: IP-002
- **Specs / PRODs**: PROD-005 (all FR and NF requirements)
- **Requirements**:
  - PROD-005.FR-001 - Leaf Python Package Identification
  - PROD-005.FR-002 - Deterministic File Ordering
  - PROD-005.NF-002 - Design Extensibility
- **Support Docs**:
  - `EXECUTION_PLAN.md` - Research findings
  - IP-002.md - Full implementation plan

## 3. Entrance Criteria

- [x] PROD-005 spec approved and synced
- [x] DE-002 delta created
- [x] Research complete on existing codebase
- [x] 16 leaf packages identified in supekku/

## 4. Exit Criteria / Done When

- [x] `supekku/scripts/lib/specs/package_utils.py` implemented (201 lines, 10.00/10 pylint)
- [x] `supekku/scripts/lib/specs/package_utils_test.py` passing (VT-001) - 29 tests
- [x] Deterministic ordering validated via enhanced tests (VT-002) - 8 tests
- [x] VA-002 rollup extensibility design review documented
- [x] All tests passing: `just test` - 1094 tests
- [x] All linters passing: `just lint` + `just pylint` - 9.68/10
- [x] Registry audit documented (no changes needed)

## 5. Verification

**VT-001: Package Detection Unit Tests**
- Test leaf package identification (16 known leaf packages)
- Test non-leaf package detection (8 parent packages)
- Test validation errors for non-packages
- Test edge cases: single-file packages, deeply nested

**VT-002: Deterministic Ordering Validation**
- Location: `supekku/scripts/lib/docs/python/variants_test.py` (enhance)
- Run contract generation 10 times on `supekku/scripts/lib/formatters/`
- Verify byte-identical output (MD5 hash comparison)
- Test with packages of varying file counts

**VA-002: Rollup Extensibility Design Review**
- Document how rollup mechanism could be added
- Confirm configuration-driven approach viable
- Verify no breaking changes required

**Commands**:
```bash
# Run VT-001
uv run pytest supekku/scripts/lib/specs/package_utils_test.py -v

# Run VT-002
uv run pytest supekku/scripts/lib/docs/python/variants_test.py::test_deterministic_ordering -v

# Full test suite
just test

# Linters
just lint
just pylint
```

## 6. Assumptions & STOP Conditions

**Assumptions**:
- Existing `sorted(path.rglob("*.py"))` provides deterministic ordering (needs validation)
- Registry already package-aware via `find_by_package()` and `Spec.packages`
- 16 leaf packages is manageable count for manual migration in Phase 02
- macOS and Linux ordering behavior is identical

**STOP Conditions**:
- STOP if deterministic ordering fails on current platform
- STOP if registry requires major refactoring (escalate design review)
- STOP if leaf package count differs significantly from 16 (re-estimate effort)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Implement package detection utilities | [ ] | ✓ 201 lines, 10.00/10 pylint |
| [x] | 1.2 | Write VT-001 package detection tests | [x] | ✓ 29 tests passing |
| [x] | 1.3 | Enhance VT-002 deterministic ordering tests | [x] | ✓ 8 tests passing |
| [x] | 1.4 | Document VA-002 rollup extensibility | [x] | ✓ Design complete |
| [x] | 1.5 | Audit registry implementation | [x] | ✓ No changes needed |
| [x] | 1.6 | Run full test suite and lint | [ ] | ✓ 1094 tests, 9.68/10 |


### Task Details

**1.1 Package Detection Utilities**
- **Design / Approach**: Pure functions following `core/` utilities pattern
  - `is_leaf_package(path)` - Check `__init__.py` + no child packages
  - `find_package_for_file(file_path)` - Traverse up to find package
  - `validate_package_path(path)` - Raise errors for invalid paths
  - `find_all_leaf_packages(root)` - Discover all leaf packages
- **Files / Components**:
  - New: `supekku/scripts/lib/specs/package_utils.py`
  - Export in: `supekku/scripts/lib/specs/__init__.py`
- **Testing**: Covered by task 1.2

**1.2 VT-001 Package Detection Tests**
- **Design / Approach**: Comprehensive unit tests using real supekku/ structure
- **Files / Components**: New `supekku/scripts/lib/specs/package_utils_test.py`
- **Testing**: Self-contained verification

**1.3 VT-002 Deterministic Ordering Tests**
- **Design / Approach**: Enhance existing test file
- **Files / Components**: Enhance `supekku/scripts/lib/docs/python/variants_test.py`
- **Testing**: Run with `pytest -v`

**1.4 VA-002 Rollup Extensibility Design Review**
- **Design / Approach**: Document rollup mechanism approach
- **Files / Components**: New `change/deltas/DE-002-.../VA-002-rollup-extensibility.md`
- **Testing**: N/A (design document)

**1.5 Registry Audit**
- **Design / Approach**: Read-only code review
- **Files / Components**: Review `registry.py` and `models.py`
- **Observations**: Already compatible - no changes needed

**1.6 Run Full Test Suite and Lint**
- **Testing**: `just test`, `just lint`, `just pylint`

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Deterministic ordering fails on platform | VT-002 validates early | Pending |
| Registry requires major refactoring | Audit complete (none needed) | ✓ Mitigated |
| Leaf package count estimate wrong | Already counted: 16 packages | ✓ Mitigated |

## 9. Decisions & Outcomes

- `2025-11-02` - Research complete: 16 leaf packages identified, registry already compatible
- `2025-11-02` - Package utilities location: `specs/package_utils.py` (domain-specific, not core)
- `2025-11-02` - Testing strategy: Test against real supekku/ structure for integration confidence
- `2025-11-02` - **Phase 01 Complete**: All exit criteria satisfied, ready for Phase 02

## 10. Findings / Research Notes

**Registry Compatibility** (`registry.py:49-51`): `find_by_package()` exists ✓
**Spec Model** (`models.py:25-30`): `packages` property exists ✓
**Deterministic Ordering** (`variants.py:40-50`): `sorted(rglob())` works ✓

**16 Leaf Packages**:
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

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied (all 7 items complete)
- [x] VT-001 passing (29 tests, 100% pass rate)
- [x] VT-002 passing (8 tests, deterministic ordering confirmed)
- [x] VA-002 documented (rollup extensibility design complete)
- [x] All tests passing (`just test` - 1094 tests)
- [x] All linters passing (ruff: ✓, pylint: 9.68/10, improved)
- [x] Hand-off to Phase 02: **Ready for migration with 16 package-level specs**

**Phase 01 Status**: ✅ **COMPLETE**
**Duration**: ~2.5 hours
**Quality**: All gates passed, pylint score improved
**Deliverables**: 4 files created (package_utils.py, 2 test files, VA-002.md), 37 new tests
