# Phase 06 Handoff - Ready for Implementation

## Executive Summary

Phase 06 has been **fully planned** and is ready for implementation. The scope has been expanded to include an important architectural improvement: **eliminating duplication between plan.overview and phase.overview**.

## Key Discovery

Analysis revealed that `show delta --json` already reads phase metadata from phase files, NOT from plan.overview. This means:
- **phase.overview** (in phase sheets) is already the canonical source
- **plan.overview** duplicates this metadata unnecessarily
- We can simplify plan.overview to store only phase IDs

## Revised Scope

### Primary Work: Simplify plan.overview Schema
1. Update JSON schema for `plan.overview@v1`
2. Change `phases` array from full metadata to ID-only: `{id: "IP-XXX.PHASE-NN"}`
3. Update `create_phase()` to write only IDs
4. Maintain backward compatibility (old format still works)
5. Update template and migrate IP-004.md

### Secondary Work: phase.tracking JSON Schema
6. Add JSON schema for `phase.tracking@v1` (currently registered but no schema)
7. Enable `schema show phase.tracking` command

### Verification Work
8. Execute VA-PHASE-001 (performance benchmark: <2sec for 20 phases)
9. Execute VA-PHASE-002 (UX review: delta display readability)
10. Update requirements registry with results

## Implementation Guide

**Comprehensive plan**: `phase-06-implementation-plan.md`

This document details:
- All files requiring changes
- Component-by-component implementation steps
- Testing strategy
- Backward compatibility approach
- Risk mitigation
- Definition of done

## Files Updated

1. **phase-06.md** - Full phase sheet with:
   - Updated objective and scope
   - 9 tasks with file tracking via `phase.tracking@v1`
   - References to implementation plan

2. **phase-06-implementation-plan.md** (NEW) - Comprehensive implementation guide

3. **IP-004.md** - Plan metadata updated with Phase 06 revised scope

## Target Schema (Simplified)

### Before (Current - Duplicated)
```yaml
phases:
  - id: IP-004.PHASE-01
    name: Phase 01 - Create Phase Command
    objective: Implement create phase command...
    entrance_criteria: [...]
    exit_criteria: [...]
```

### After (Simplified - ID Only)
```yaml
phases:
  - id: IP-004.PHASE-01
  - id: IP-004.PHASE-02
  - id: IP-004.PHASE-03
```

All metadata lives in phase.overview blocks in phase sheets.

## Components Requiring Changes

### Must Change
- [ ] `supekku/scripts/lib/blocks/plan_metadata.py` - PLAN_OVERVIEW_METADATA (line 40+)
- [ ] `supekku/scripts/lib/changes/creation.py` - create_phase function
- [ ] `.spec-driver/templates/implementation-plan-template.md` - phases array
- [ ] `supekku/scripts/lib/changes/creation_test.py` - VT-PHASE-006 updates

### Likely Change
- [ ] `supekku/scripts/lib/blocks/plan.py` (parser - backward compat)
- [ ] `supekku/scripts/lib/blocks/plan_metadata.py`

### Verify No Change Needed
- [ ] Formatters (already read from phase files - confirmed)

### Update After Implementation
- [ ] IP-004.md (migrate to simplified format)
- [ ] Example YAML in schema show output

## Testing Checklist

### Before Implementation
- [x] Confirmed display reads from phase files (via JSON output)
- [x] Identified all components needing changes

### During Implementation
- [ ] Unit tests: parser accepts ID-only format
- [ ] Unit tests: parser accepts old format (backward compat)
- [ ] Unit tests: create_phase writes only ID
- [ ] Integration: `show delta DE-004` output unchanged

### After Implementation
- [ ] Migrate IP-004.md to new format
- [ ] Verify `show delta DE-004` still works
- [ ] Create new phase, verify only ID added to plan
- [ ] Full test suite passing
- [ ] Linters clean

## Implementation Order

1. Update JSON schema (defines target state)
2. Update parser for backward compatibility
3. Update create_phase (write new format)
4. Update tests
5. Update template
6. Manual testing with DE-004
7. Migrate IP-004.md
8. Add phase.tracking JSON schema
9. Execute VAs
10. Update registry and complete delta

## Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| Breaking existing plans | Backward compat in parser | Planned |
| Display breaks | Already confirmed working | N/A |
| Tests assume old structure | Systematic fixture updates | Planned |
| Complex schema migration | Follow existing patterns | Planned |

## Success Criteria

- [ ] `schema show plan.overview` shows simplified example
- [ ] `create phase "Test" --plan IP-004` writes only ID
- [ ] Old format plans still parse and display correctly
- [ ] IP-004.md migrated and working
- [ ] All 40+ phase tests passing
- [ ] `show delta DE-004` output identical to before
- [ ] phase.tracking has JSON schema
- [ ] VAs executed and documented

## Notes for Implementer

**Good news**: Display already works correctly. Main work is:
1. Schema definition changes
2. Creation logic simplification
3. Parser flexibility (backward compat)

**The formatter doesn't need changes** - it already reads from phase files.

**Migration is safe** - backward compatibility ensures old plans keep working while new phases use simplified format.

## Key File Locations (Found)

✅ **Schema Definition**: `supekku/scripts/lib/blocks/plan_metadata.py`
- Symbol: `PLAN_OVERVIEW_METADATA` (line ~40)
- Phases field: lines ~85-130
- Example: lines ~150-175

✅ **Parser**: `supekku/scripts/lib/blocks/plan.py`
- Look for phase extraction logic

✅ **Creation Logic**: `supekku/scripts/lib/changes/creation.py`
- Function: `create_phase()` - search for plan metadata update

✅ **Template**: `.spec-driver/templates/implementation-plan-template.md`

See `phase-06-implementation-plan.md` for comprehensive details.

---

**Status**: ✅ FULLY PLANNED, READY FOR IMPLEMENTATION

Phase 06 scope defined, implementation plan written, ready to execute.
