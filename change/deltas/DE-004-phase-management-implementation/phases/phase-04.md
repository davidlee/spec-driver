---
id: IP-004.PHASE-04
slug: 004-phase-management-implementation-phase-04
name: IP-004 Phase 04
created: '2025-11-03'
updated: '2025-11-03'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-004.PHASE-04
plan: IP-004
delta: DE-004
name: Phase 04 - Plan Metadata Auto-Update
objective: >-
  Implement automatic plan frontmatter updates when creating phases,
  ensuring show delta --json reflects newly created phases immediately.
entrance_criteria:
  - Phase 01 complete
  - Understanding of plan.overview block structure
exit_criteria:
  - create_phase() updates plan.overview phases array
  - VT-PHASE-006 passing (plan metadata update tests)
  - Manual test - create phase updates JSON output
  - All tests + linters passing
verification:
  tests:
    - VT-PHASE-006
  evidence:
    - Test output showing plan metadata update tests passing
    - Manual test showing phase in JSON output after creation
    - Lint output (ruff + pylint) passing
tasks:
  - Research plan.overview block update pattern
  - Implement update_plan_metadata() helper function
  - Integrate into create_phase() function
  - Write VT-PHASE-006 tests
  - Manual verification with IP-002
risks:
  - YAML block manipulation may be fragile
  - Race conditions if multiple phases created simultaneously
```

# Phase 04 - Plan Metadata Auto-Update

## 1. Objective

Enhance the `create_phase()` function to automatically update the plan's `plan.overview@v1` block when a new phase is created, ensuring that:
- `show delta --json` immediately reflects the newly created phase
- Plan metadata stays synchronized with filesystem state
- No manual editing of plan frontmatter required after phase creation

## 2. Links & References
- **Delta**: DE-004
- **Plan**: IP-004
- **Specs / PRODs**: PROD-006.FR-004 (metadata auto-population)
- **Requirements**: PROD-006.FR-004
- **Support Docs**:
  - Existing pattern: `update_verification_coverage()` in blocks module for YAML block updates
  - Plan template: `supekku/templates/plan.md`
  - Schema: `spec-driver schema show plan.overview`

## 3. Entrance Criteria
- [x] Phase 01 complete (create_phase function exists and works)
- [x] Understanding of plan.overview block structure from IP-004 examples
- [x] Research existing YAML block update patterns in codebase

## 4. Exit Criteria / Done When
- [x] `create_phase()` function updates plan.overview phases array
- [x] New phase entry includes minimal metadata (id at minimum)
- [x] VT-PHASE-006 passing (plan metadata update tests - 2 tests added)
- [x] Manual test: create phase for IP-002, verify in `show delta --json`
- [x] All existing tests still passing (1163 tests passing)
- [x] `just lint` and `just pylint` passing (ruff clean, pylint 9.81/10)

## 5. Verification

**VT-PHASE-006: Plan Metadata Update Tests**
- Location: `supekku/scripts/lib/changes/creation_test.py` (enhance CreateChangeTest)
- Tests:
  - `test_create_phase_updates_plan_metadata()` → plan.overview phases array updated
  - `test_create_phase_metadata_minimal()` → at least phase ID added
  - `test_create_phase_metadata_preserves_existing()` → doesn't corrupt existing phases
  - `test_create_phase_metadata_invalid_yaml()` → handles malformed blocks gracefully
- Command: `uv run pytest supekku/scripts/lib/changes/creation_test.py::CreateChangeTest::test_create_phase_updates_plan_metadata -v`

**Full Test Suite**: `just test`
**Linters**: `just lint` + `just pylint`

**Manual Test**:
```bash
# Create test phase for IP-002
uv run spec-driver create phase "Test Phase" --plan IP-002

# Verify appears in JSON output
uv run spec-driver show delta DE-002 --json | grep -A 5 '"phases"' | grep "Test Phase"

# Clean up test phase
rm change/deltas/DE-002-*/phases/phase-0X.md
# Manually remove from IP-002.md plan.overview block
```

## 6. Assumptions & STOP Conditions

**Assumptions**:
- Plan files always have a `plan.overview@v1` YAML block
- The phases array exists in the plan.overview block (may be empty)
- Plan file encoding is UTF-8
- YAML block format follows `\`\`\`yaml supekku:plan.overview@v1` pattern
- Existing YAML block update utilities exist (e.g., in blocks/ module)

**STOP Conditions**:
- STOP if no existing pattern for YAML block updates found (need design decision)
- STOP if plan.overview block parsing requires major refactoring
- STOP if tests reveal race conditions or data corruption issues

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 4.1 | Research existing YAML block update patterns | [ ] | Complete - found patterns in blocks/ |
| [x] | 4.2 | Design update approach (minimal vs full) | [ ] | Complete - chose minimal (id-only) |
| [x] | 4.3 | Implement update_plan_overview_phases() | [ ] | Complete - 60 lines in creation.py |
| [x] | 4.4 | Integrate into create_phase() | [ ] | Complete - with error handling |
| [x] | 4.5 | Write VT-PHASE-006 tests | [x] | Complete - 2 tests added |
| [x] | 4.6 | Run full test suite | [ ] | Complete - 1163 tests passing |
| [x] | 4.7 | Manual test with IP-002 | [ ] | Complete - verified JSON output |
| [x] | 4.8 | Run linters | [ ] | Complete - ruff clean, pylint 9.81/10 |

### Task Details

**4.1 Research Existing YAML Block Update Patterns**
- **Design / Approach**: Search blocks/ module for update utilities, understand read→parse→modify→write pattern
- **Files / Components**: `supekku/scripts/lib/blocks/*.py`
- **Testing**: N/A (research)
- **Observations**: Found `extract_plan_overview()` in plan.py, `formatted_yaml()` pattern in RevisionChangeBlock. YAML settings: `sort_keys=False, indent=2, default_flow_style=False`.

**4.2 Design Update Approach**
- **Design / Approach**: Option A (minimal): only `- id: {phase_id}`. Option B (full): complete metadata.
- **Testing**: N/A (design decision)
- **Observations**: Chose minimal (id-only) approach. Rationale: safer, less user conflict, sufficient for JSON output. Python 3.7+ dict ordering preserves field order.

**4.3-4.4 Implementation**
- **Design / Approach**: Create helper function, integrate into create_phase() with error handling
- **Files / Components**: `supekku/scripts/lib/changes/creation.py` (lines 459-526, 650-659)
- **Testing**: VT-PHASE-006
- **Observations**: Added `_update_plan_overview_phases()` helper (60 lines). Integration uses try/except with warnings. Added `warnings` import. Error handling prevents phase creation failure if metadata update fails.

**4.5 Write VT-PHASE-006**
- **Design / Approach**: Pytest with temp fixtures, verify phases array updated, test edge cases
- **Files / Components**: `supekku/scripts/lib/changes/creation_test.py` (lines 225-288)
- **Observations**: Initial test failure due to YAML format (`- id:` not `  - id:`). Fixed assertions. 2 tests added: update verification and preservation of existing phases.

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| YAML block manipulation fragile | Follow existing patterns, comprehensive tests | ✅ Mitigated - used proven patterns, tests passing |
| Race conditions | Document single-user assumption, consider file locking if needed | ✅ Accepted - single-user assumption documented |
| Corrupting existing phase metadata | Preserve existing entries, validate before write | ✅ Mitigated - test confirms preservation |

## 9. Decisions & Outcomes
- `2025-11-03` - Phase 04 created to implement plan metadata auto-update (moved from out-of-scope)
- `2025-11-03` - Chose minimal metadata approach (id-only) over full metadata for safety
- `2025-11-03` - Error handling strategy: warn but don't fail phase creation if metadata update fails

## 10. Findings / Research Notes

**2025-11-03 - Research Findings (Task 4.1)**:
- Found `extract_plan_overview()` and `render_plan_overview_block()` in `blocks/plan.py`
- RevisionChangeBlock has sophisticated `formatted_yaml()` and `replace_content()` methods
- PlanOverviewBlock is simpler (dataclass with raw_yaml + data only)
- YAML formatting pattern from RevisionChangeBlock: `sort_keys=False`, `indent=2`, `default_flow_style=False`
- Regex pattern for plan.overview block: `` r"```(?:yaml|yml)\s+supekku:plan.overview@v1\n(.*?)```" ``

**2025-11-03 - Design Decision (Task 4.2)**:
- Initially considered minimal (id-only) vs full metadata approach
- Chose minimal (id-only) for safety and to minimize user conflict
- Rationale: Plan files already have full metadata in manually-maintained sections; ID is sufficient for JSON output
- YAML dump handles field ordering correctly due to Python 3.7+ dict ordering

**2025-11-03 - Implementation Notes (Task 4.3-4.4)**:
- Created `_update_plan_overview_phases()` helper function (60 lines)
- Integration uses try/except to avoid failing phase creation if metadata update fails
- Warnings issued if update fails but phase created successfully
- Added `warnings` import to creation.py

**2025-11-03 - Testing Results (Task 4.5-4.7)**:
- VT-PHASE-006: 2 new tests added to creation_test.py
  - `test_create_phase_updates_plan_metadata` - verifies phase ID added to plan.overview
  - `test_create_phase_metadata_preserves_existing` - verifies existing phases not corrupted
- Initial test failure: YAML dump uses `- id:` not `  - id:` (no leading spaces for list items)
- All tests passing after fix: 1163 total tests
- Manual test successful: created phase-04 for IP-002, verified in JSON output, cleaned up

**2025-11-03 - Linter Results (Task 4.8)**:
- ruff: All checks passed
- pylint: 9.81/10 (minor complexity warnings in create_phase, acceptable)

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] VT-PHASE-006 passing (2 new tests)
- [x] All tests passing (1163 tests, +2 from before)
- [x] Linters passing (ruff clean, pylint 9.81/10)
- [x] Manual test successful (create phase, verify JSON output)
- [ ] Code committed with clear message
- [ ] IP-004 plan updated
- [ ] Verification evidence stored
- [x] Hand-off notes: See section 12 below

## 12. Handover Notes

**Phase Status**: ✅ COMPLETED (2025-11-03)

**What Was Delivered**:
1. **Plan Metadata Auto-Update Feature**:
   - `create phase` now automatically updates plan.overview phases array
   - New phases immediately visible in `show delta --json` output
   - No manual editing of plan frontmatter required

2. **Code Changes**:
   - `supekku/scripts/lib/changes/creation.py`:
     - Added `PLAN_MARKER`, `extract_plan_overview` imports (line 16-17)
     - Added `warnings` import (line 6)
     - Added `_update_plan_overview_phases()` helper function (lines 459-526)
     - Integrated helper into `create_phase()` with error handling (lines 650-659)
   - `supekku/scripts/lib/changes/creation_test.py`:
     - Added 2 VT-PHASE-006 tests (lines 225-288)

3. **Test Coverage**:
   - `test_create_phase_updates_plan_metadata` - verifies plan.overview updated
   - `test_create_phase_metadata_preserves_existing` - verifies no corruption
   - All 1163 tests passing

**How It Works**:
- When `create_phase()` runs, after creating the phase file, it calls `_update_plan_overview_phases()`
- Helper extracts plan.overview block, appends `{id: phase_id}` to phases array
- YAML re-serialized with `sort_keys=False, indent=2, default_flow_style=False`
- Block replaced using regex, file written back
- If update fails, warning issued but phase creation succeeds

**Known Limitations**:
- Single-user assumption (no file locking for concurrent writes)
- Minimal metadata only (id field) - full metadata still manually maintained
- Delta frontmatter NOT updated (phases list in delta.relationships block)

**Potential Issues / Watch-outs**:
- YAML formatting: uses `- id:` not `  - id:` (no leading spaces for list items)
- If plan.overview block missing/malformed, warning issued but phase still created
- pylint complexity warnings on `create_phase()` (acceptable at 9.81/10)

**Next Steps for DE-004**:
1. **Phase 02** - Enhanced Display & Validation:
   - Enhance `format_delta_details()` to show phase summaries
   - Add schema validation for phase.overview blocks
   - VT-PHASE-003, VT-PHASE-005

2. **Phase 03** - Verification & Polish:
   - Complete VA-PHASE-001 (performance benchmarks)
   - Complete VA-PHASE-002 (UX review)
   - Update documentation

3. **Commit & Complete**:
   - Commit Phase 04 changes
   - Update IP-004 plan metadata (ironically, manually for now)
   - Mark delta as complete

**Files Modified (Uncommitted)**:
- `supekku/scripts/lib/changes/creation.py` (+71 lines)
- `supekku/scripts/lib/changes/creation_test.py` (+68 lines)
- `change/deltas/DE-004-phase-management-implementation/phases/phase-04.md` (this file)

**Questions for Continuation**:
- Should Phases 02-03 be implemented before commit, or commit Phase 01+04 separately?
- Should delta.relationships phases array also be auto-updated? (Currently out of scope)
- Should full metadata be auto-populated in future enhancement?
