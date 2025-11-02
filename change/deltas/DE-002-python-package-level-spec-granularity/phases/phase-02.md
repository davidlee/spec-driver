```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-002.PHASE-02
plan: IP-002
delta: DE-002
name: Phase 02 - Migration Execution
objective: >-
  Delete file-level specs, generate package-level specs, update relationships,
  sync registry. Execute the breaking change cleanly.
entrance_criteria:
  - Phase 01 complete
  - Tooling changes tested and validated
  - 16 leaf packages identified
exit_criteria:
  - All existing file-level specs deleted (if any)
  - 16 package-level specs created
  - Registry synced successfully
  - Validation passes with no errors
```

# Phase 02 - Migration Execution

## 1. Objective

Execute the migration from file-level to package-level tech spec granularity:
- Delete any existing file-level tech specs
- Generate 16 package-level specs (one per leaf package)
- Update PROD spec relationships if needed
- Sync registry and validate

This is a breaking change but acceptable for a solo-developer project.

## 2. Links & References

- **Delta**: DE-002
- **Plan**: IP-002
- **Phase 01**: `phases/phase-01.md` (completed)
- **Requirements**:
  - PROD-005.FR-003 - Sync Operation Package Support
  - PROD-005.FR-004 - File-to-Package Resolution
- **16 Leaf Packages**:
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

## 3. Entrance Criteria

- [x] Phase 01 complete (all tooling validated)
- [x] VT-001 and VT-002 passing
- [x] 16 leaf packages identified
- [x] Package detection utilities available

## 4. Exit Criteria / Done When

- [x] Existing file-level specs deleted (111 specs removed)
- [x] 16 package-level specs created in `specify/tech/` (SPEC-110 to SPEC-125)
- [x] All SPEC-* references in PROD specs updated to package-level IDs
- [x] All frontmatter metadata updated (relations, interactions in PROD-001, 003, 004)
- [x] All body references updated (markdown links, mentions)
- [x] PythonAdapter updated for package-level discovery
- [x] Registry sync completes: `uv run spec-driver sync` ✓
- [x] Validation passes: `uv run spec-driver validate` ✓
- [x] All tests still passing: `just test` - 1094 passing ✓

## 5. Verification

**Manual Verification**:
- Count specs before: `find specify/tech -name "SPEC-*.md" | wc -l`
- Count specs after: should be 16
- Verify one spec per leaf package

**Automated Verification**:
```bash
# Sync registry
uv run spec-driver sync

# Validate workspace
uv run spec-driver validate

# Run full test suite
just test
```

## 6. Assumptions & STOP Conditions

**Assumptions**:
- No existing file-level tech specs to delete (fresh state)
- Manual spec creation acceptable (16 specs, ~15 minutes)
- PROD specs don't reference non-existent tech specs
- Solo developer - no coordination needed

**STOP Conditions**:
- STOP if sync fails with errors (escalate design issue)
- STOP if validation reveals broken relationships
- STOP if test suite regresses

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Check for existing file-level specs | [ ] | ✓ Found 111, deleted all |
| [x] | 2.2 | Update PythonAdapter + sync | [ ] | ✓ 16 specs created via tooling |
| [x] | 2.3 | Update PROD spec relationships | [ ] | ✓ 3 PROD specs updated |
| [x] | 2.4 | Sync registry | [ ] | ✓ Completed successfully |
| [x] | 2.5 | Validate workspace | [ ] | ✓ Passing |
| [x] | 2.6 | Run test suite | [ ] | ✓ 1094 tests passing |

### Task Details

**2.1 Check for Existing File-Level Specs**
- **Design / Approach**: Check `specify/tech/` for any SPEC-*.md files
- **Files / Components**: `specify/tech/` directory
- **Testing**: Manual inspection
- **Observations**: Found 111 existing file-level specs (SPEC-001 to SPEC-111)
- **Action Taken**: Deleted all 111 specs with `rm -rf specify/tech/SPEC-*`

**2.2 Update PythonAdapter for Package Discovery**
- **Design / Approach**:
  - Import `find_all_leaf_packages` from Phase 01 utilities
  - Replace file-based discovery with package-based discovery
  - Update `describe()` to add `packages` field to frontmatter
  - Run `spec-driver sync` to generate specs via tooling (not manual)
- **Spec Template**:
  ```yaml
  ---
  id: SPEC-XXX
  slug: <package-slug>
  name: <package.path> Specification
  created: '2025-11-02'
  updated: '2025-11-02'
  status: draft
  kind: spec
  packages:
    - <package/path>
  ---
  
  # SPEC-XXX – <package.path>
  
  Package-level specification for <package.path>.
  
  ## Purpose
  
  [TODO: Describe package purpose and responsibilities]
  
  ## Architecture
  
  [TODO: Package-level design notes]
  ```
- **Files Modified**:
  - `supekku/scripts/lib/sync/adapters/python.py`:
    - Line 8: Added `find_all_leaf_packages` import
    - Lines 81-108: Replaced file discovery with package discovery
    - Lines 128-150: Added package-aware frontmatter generation
  - `supekku/scripts/lib/sync/adapters/python_test.py`:
    - Lines 243-269: Updated test for package discovery (fixed failing test)
- **Files Created**: 16 package-level specs:
  - SPEC-110: supekku/cli
  - SPEC-111: supekku/scripts/backlog
  - SPEC-112: supekku/scripts/cli
  - SPEC-113: supekku/scripts/lib/backlog
  - SPEC-114: supekku/scripts/lib/blocks/metadata
  - SPEC-115: supekku/scripts/lib/changes/blocks
  - SPEC-116: supekku/scripts/lib/core/frontmatter_metadata
  - SPEC-117: supekku/scripts/lib/decisions
  - SPEC-118: supekku/scripts/lib/deletion
  - SPEC-119: supekku/scripts/lib/docs/python
  - SPEC-120: supekku/scripts/lib/formatters
  - SPEC-121: supekku/scripts/lib/relations
  - SPEC-122: supekku/scripts/lib/requirements
  - SPEC-123: supekku/scripts/lib/specs
  - SPEC-124: supekku/scripts/lib/sync/adapters
  - SPEC-125: supekku/scripts/lib/validation
- **Testing**: All specs validated via `spec-driver validate`

**2.3 Update PROD Spec Relationships**
- **Design / Approach**:
  - Search for any SPEC-* references in PROD spec frontmatter and body
  - Map old file-level SPEC IDs to new package-level IDs
  - Update frontmatter `relations:` and `interactions:` blocks
  - Update body references in "Related Specs" sections
- **Mapping Applied**:
  - SPEC-003, SPEC-004, SPEC-006, SPEC-007, SPEC-008, SPEC-041, SPEC-085 → SPEC-110 (supekku/cli)
  - SPEC-042, SPEC-043, SPEC-055 → SPEC-117 (supekku/scripts/lib/decisions)
  - SPEC-036 → SPEC-116 (supekku/scripts/lib/core/frontmatter_metadata)
  - Formatters refs → SPEC-120 (supekku/scripts/lib/formatters)
- **Files Modified**:
  - `specify/product/PROD-001/PROD-001.md`:
    - Lines 31-33: Updated `interactions:` from 3 specs to 1 (SPEC-110)
    - Lines 596-600: Updated body "Related Specs" section
  - `specify/product/PROD-003/PROD-003.md`:
    - Lines 11-16: Updated `relations:` (SPEC-003, SPEC-004, SPEC-043 → SPEC-110, SPEC-117)
    - Lines 46-50: Updated `interactions:` block
    - Lines 626-628: Updated body references
  - `specify/product/PROD-004/PROD-004.md`:
    - Lines 11-15: Updated `relations:` (SPEC-036 → SPEC-116)
    - Line 50: Updated `interactions:` block
    - Line 731: Updated body reference
- **Testing**: `spec-driver validate` confirms no broken references

**2.4 Sync Registry**
- **Design / Approach**: Run `uv run spec-driver sync`
- **Result**: Completed successfully
  - Reported 107 orphaned units (old file-level specs marked as deleted)
  - Created 16 new package-level specs (SPEC-110 to SPEC-125)
  - Rebuilt symlink indices successfully

**2.5 Validate Workspace**
- **Design / Approach**: Run `uv run spec-driver validate`
- **Result**: ✓ Workspace validation passed
  - All SPEC references resolved correctly
  - No broken relationships detected

**2.6 Run Test Suite**
- **Design / Approach**: Run `just test`
- **Result**: ✓ All 1094 tests passing
  - Fixed 1 test that expected file-level discovery
  - All other tests unaffected by migration

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| PROD specs reference non-existent tech specs | Search and update before sync | ✓ Resolved - 3 PROD specs updated |
| Spec ID numbering conflicts | Use sequential IDs from SPEC-110 | ✓ Resolved - No conflicts |
| Manual spec creation errors | Used tooling (sync) instead | ✓ Avoided - Automated |
| Sync fails with new package-level specs | Phase 01 validated registry compatibility | ✓ Mitigated - Sync successful |
| Test regressions | Updated failing test for package discovery | ✓ Resolved - 1 test fixed |

## 9. Decisions & Outcomes

- `2025-11-02` - **Migration approach changed**: Used tooling (PythonAdapter + sync) instead of manual creation
- `2025-11-02` - **Spec ID range**: SPEC-110 to SPEC-125 (16 specs, continuing from existing range)
- `2025-11-02` - **PROD spec consolidation**: Reduced from 7 unique old SPEC refs to 4 package-level refs
- `2025-11-02` - **Key insight**: Adapter update was the right approach - proves tooling works end-to-end
- `2025-11-02` - **Phase 02 Complete**: All exit criteria met, ready for Phase 03

## 10. Findings / Research Notes

**Pre-Migration State**:
- 111 existing file-level specs (SPEC-001 to SPEC-111)
- All were auto-generated placeholders from previous sync runs
- 16 leaf packages confirmed in Phase 01

**Post-Migration State**:
- 16 package-level specs (SPEC-110 to SPEC-125)
- Each spec has `packages: [path]` frontmatter field
- All specs auto-generated via `spec-driver sync`
- Registry successfully indexes package-level specs

**Code Changes Summary**:
1. **python.py** (3 sections modified):
   - Import section: Added `find_all_leaf_packages`
   - `discover_targets()`: Package discovery instead of file discovery
   - `describe()`: Added `packages` field to frontmatter

2. **python_test.py** (1 test fixed):
   - `test_discover_targets_auto_discovery`: Updated for package-level discovery

3. **3 PROD specs** (frontmatter + body):
   - PROD-001: 3 SPEC refs → 1 SPEC ref (SPEC-110)
   - PROD-003: 3 SPEC refs → 2 SPEC refs (SPEC-110, SPEC-117)
   - PROD-004: 1 SPEC ref → 1 SPEC ref (SPEC-116)

**Orphaned Specs**:
- Sync reported 107 orphaned units (old file-level sources)
- These can be pruned with `--prune` flag if needed
- Not a blocker - just informational warnings

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied (all 9 items complete)
- [x] 16 package-level specs created (SPEC-110 to SPEC-125)
- [x] PythonAdapter updated for package discovery
- [x] 3 PROD specs updated (frontmatter + body)
- [x] Sync completed successfully
- [x] Validation passing
- [x] All 1094 tests passing
- [x] Code changes: 2 files modified (python.py, python_test.py), 3 PROD specs updated
- [x] Hand-off to Phase 03: **Ready for final verification and documentation**

**Phase 02 Status**: ✅ **COMPLETE**
**Duration**: ~1.5 hours
**Quality**: All gates passed, 1094 tests passing, validation clean
**Key Achievement**: Proved package-level pattern works end-to-end via tooling

## 12. SPEC References to Update

**Actual Metadata References Found**:

### PROD-001 (Spec Creation Workflow)
```yaml
interactions:
  - with: SPEC-003  # CLI create commands
  - with: SPEC-041  # Templates
  - with: SPEC-085  # Schema show
```

### PROD-003 (Policy & Standard Artifacts)
```yaml
relations:
  - type: extends
    target: SPEC-003  # CLI create commands
  - type: extends
    target: SPEC-004  # CLI list commands
  - type: collaborates
    target: SPEC-043  # Registry pattern
interactions:
  - with: SPEC-003
  - with: SPEC-004
  - with: SPEC-043
```

### PROD-004 (Frontmatter Metadata Validation)
```yaml
relations:
  - type: implements
    target: SPEC-036  # Replaces imperative validation
interactions:
  - with: SPEC-036
```

**Action Required**:
These SPEC IDs need to be mapped to the new package-level specs once created. The mapping will be:
- Old file-level SPEC-XXX → New package-level SPEC-YYY (based on which package contains the file)

**Note**: Most other SPEC references in PROD specs are illustrative examples in the body text and don't need updating.
