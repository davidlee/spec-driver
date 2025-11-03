---
id: IP-004.PHASE-06
slug: 004-phase-management-implementation-phase-06
name: IP-004 Phase 06 - Schema Completion & Verification
created: '2025-11-03'
updated: '2025-11-03'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-004.PHASE-06
plan: IP-004
delta: DE-004
objective: >-
  Simplify plan.overview schema to eliminate duplication (ID-only phases array),
  add JSON schema for phase.tracking@v1, execute verification artifacts, and
  prepare DE-004 for completion.
entrance_criteria:
  - Phases 01, 04, 05 complete (core functionality implemented)
  - All VT-PHASE tests passing (VT-001 through VT-007)
  - phase.overview schema already registered and working
exit_criteria:
  - phase.tracking@v1 has JSON schema with schema show support
  - VA-PHASE-001 executed (performance benchmark <2sec for 20 phases)
  - VA-PHASE-002 executed (UX review of delta display readability)
  - All acceptance criteria in DE-004 satisfied
  - Requirements registry updated with verification status
verification:
  tests:
    - VA-PHASE-001
    - VA-PHASE-002
  evidence:
    - JSON schema for phase.tracking viewable via schema show
    - Performance benchmark results
    - UX review findings
    - Updated requirements registry
tasks:
  - Research metadata-driven validation pattern for phase.tracking
  - Create JSON schema definition for phase.tracking@v1
  - Register schema in metadata system
  - Verify schema show phase.tracking works
  - Execute VA-PHASE-001 (performance benchmark)
  - Execute VA-PHASE-002 (UX review)
  - Update requirements registry with verification results
  - Update DE-004 with completion notes
risks:
  - Metadata-driven validation migration may be complex
  - Performance may not meet <2sec threshold (mitigation: optimize if needed)
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-004.PHASE-06

files:
  references:
    - supekku/scripts/lib/blocks/schema_registry.py
    - supekku/scripts/lib/blocks/metadata/schema.py
    - supekku/scripts/lib/blocks/plan.py
  context:
    - change/deltas/DE-004-*/phases/phase-05.md

entrance_criteria:
  - item: Phases 01, 04, 05 complete
    completed: true
  - item: All VT-PHASE tests passing
    completed: true
  - item: phase.overview schema registered
    completed: true

exit_criteria:
  - item: phase.tracking JSON schema created
    completed: false
  - item: schema show phase.tracking works
    completed: false
  - item: VA-PHASE-001 executed
    completed: false
  - item: VA-PHASE-002 executed
    completed: false
  - item: Requirements registry updated
    completed: false

tasks:
  - id: "6.1"
    description: Simplify plan.overview schema to ID-only phases array
    status: pending
    files:
      references:
        - change/deltas/DE-004-*/phases/phase-06-implementation-plan.md
      modified:
        - supekku/scripts/lib/blocks/metadata/*_schema.py

  - id: "6.2"
    description: Update create_phase to write only ID to plan.overview
    status: pending
    files:
      modified:
        - supekku/scripts/lib/changes/creation.py
      tests:
        - supekku/scripts/lib/changes/creation_test.py

  - id: "6.3"
    description: Update parser for backward compatibility
    status: pending
    files:
      modified:
        - supekku/scripts/lib/blocks/plan.py
        - supekku/scripts/lib/blocks/plan_metadata.py

  - id: "6.4"
    description: Update plan template with simplified phases array
    status: pending
    files:
      modified:
        - .spec-driver/templates/implementation-plan-template.md

  - id: "6.5"
    description: Update and run all tests (VT-PHASE-006, formatters, etc)
    status: pending
    files:
      tests:
        - supekku/scripts/lib/changes/creation_test.py
        - supekku/scripts/lib/formatters/change_formatters_test.py

  - id: "6.6"
    description: Migrate IP-004.md to simplified format
    status: pending
    files:
      modified:
        - change/deltas/DE-004-phase-management-implementation/IP-004.md

  - id: "6.7"
    description: Add JSON schema for phase.tracking@v1
    status: pending
    files:
      added:
        - supekku/scripts/lib/blocks/metadata/*phase_tracking*.py

  - id: "6.8"
    description: Execute VA-PHASE-001 and VA-PHASE-002
    status: pending

  - id: "6.9"
    description: Update requirements registry and DE-004 completion
    status: pending
    files:
      modified:
        - .spec-driver/registry/requirements.yaml
        - change/deltas/DE-004-phase-management-implementation/DE-004.md
```

# Phase 06 - Schema Completion & Verification

## 1. Objective

Complete the phase management implementation by:
1. **Simplify plan.overview schema** - Remove duplication by storing only phase IDs (not full metadata)
2. **Add JSON schema for phase.tracking@v1** (currently only has registration)
3. **Execute verification artifacts** VA-PHASE-001 and VA-PHASE-002
4. **Update requirements registry** with verification status
5. **Prepare DE-004 for completion**

This is the final phase - all core functionality is implemented and tested.

**Key Architectural Change**: Making phase.overview the single source of truth for phase metadata, eliminating duplication in plan.overview.

## 2. Links & References

- **Delta**: DE-004 - Phase Management Implementation
- **Plan**: IP-004
- **Specs**: PROD-006 (Phase Management)
- **Related Phase**: Phase 05 implemented phase.tracking but didn't add JSON schema

**Key Files:**
- Schema registry: `supekku/scripts/lib/blocks/schema_registry.py`
- Metadata schemas: `supekku/scripts/lib/blocks/metadata/`
- Tracking implementation: `supekku/scripts/lib/blocks/plan.py`

## 3. Entrance Criteria

- [x] Phases 01, 04, 05 complete (core functionality implemented)
- [x] All VT-PHASE tests passing (19 tracking tests + 7 creation + 12 formatter = 38 tests)
- [x] phase.overview schema already registered and working
- [x] `schema show phase.overview` works correctly

## 4. Exit Criteria / Done When

- [ ] phase.tracking@v1 has JSON schema definition
- [ ] `schema show phase.tracking` works (no longer says "not migrated yet")
- [ ] VA-PHASE-001 executed: phase creation <2sec for 20 phases
- [ ] VA-PHASE-002 executed: delta display readable with 1/3/5/10 phases
- [ ] All acceptance criteria in DE-004.md satisfied
- [ ] Requirements registry updated with verification status
- [ ] DE-004 marked ready for completion

## 5. Verification

**VA-PHASE-001: Performance Benchmark**
```bash
# Create test plan with 0 phases
# Time creation of 20 sequential phases
# Verify each creation <2 seconds
# Document results
```

**VA-PHASE-002: UX Review**
```bash
# View deltas with different phase counts:
uv run spec-driver show delta DE-004  # 5 phases
uv run spec-driver show delta DE-002  # 3 phases (if exists)
# Assess: readability, truncation, information density
# Document findings
```

**Schema Validation:**
```bash
uv run spec-driver schema show phase.tracking
# Should display JSON schema, not "not migrated yet" message
```

## 6. Assumptions & STOP Conditions

**Assumptions:**
- Metadata-driven validation pattern follows existing schemas (phase.overview, plan.overview, etc.)
- Performance will meet threshold (early tests show <1sec per phase)
- Delta display already readable (formatter working in practice)

**STOP Conditions:**
- If metadata-driven validation requires major refactoring → escalate to user
- If performance significantly below threshold → need optimization phase
- If schema migration breaks existing functionality → rollback required

## 7. Tasks & Progress

*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 6.1 | Simplify plan.overview schema (ID-only) | [ ] | See phase-06-implementation-plan.md |
| [ ] | 6.2 | Update create_phase (write ID only) | [ ] | Backward compat required |
| [ ] | 6.3 | Update parser for backward compat | [ ] | Handle old + new formats |
| [ ] | 6.4 | Update plan template | [ ] | Simplified phases array |
| [ ] | 6.5 | Update and run all tests | [ ] | VT-PHASE-006, formatters |
| [ ] | 6.6 | Migrate IP-004.md | [ ] | Test with real data |
| [ ] | 6.7 | Add phase.tracking JSON schema | [P] | Can parallelize with 6.1-6.6 |
| [ ] | 6.8 | Execute VAs (performance + UX) | [P] | Can parallelize |
| [ ] | 6.9 | Update registry + DE-004 completion | [ ] | Final step |

### Task Details

#### 6.1 Research Metadata-Driven Validation
- **Design / Approach**:
  - Examine `supekku/scripts/lib/blocks/metadata/schema.py`
  - Study how `phase.overview` was migrated to JSON schema
  - Understand schema registration in `schema_registry.py`
  - Check if there's a pattern for file path schemas

- **Files / Components**:
  - `supekku/scripts/lib/blocks/metadata/schema.py` - base schema utilities
  - `supekku/scripts/lib/blocks/schema_registry.py` - registration
  - Existing schemas in `metadata/` directory as examples

- **Testing**: Manual review of existing schemas
- **Observations & AI Notes**: *(To be filled)*

#### 6.2 Create JSON Schema for phase.tracking@v1
- **Design / Approach**:
  - Define JSON schema matching PhaseTrackingBlock structure
  - Include file path tracking (references, context, task files)
  - Support optional fields for backward compatibility
  - Add comprehensive examples

- **Files / Components**:
  - Create: `supekku/scripts/lib/blocks/metadata/phase_tracking_schema.py`
  - Or extend existing schema file if pattern suggests it

- **Testing**: Validate against existing phase-05.md tracking block
- **Observations & AI Notes**: *(To be filled)*

#### 6.3 Register Schema in Metadata System
- **Design / Approach**:
  - Add phase.tracking registration to schema_registry
  - Ensure backward compatibility (existing code still works)
  - Update any import statements needed

- **Files / Components**:
  - Modify: `supekku/scripts/lib/blocks/schema_registry.py`

- **Testing**: Run `schema list` and `schema show phase.tracking`
- **Observations & AI Notes**: *(To be filled)*

#### 6.5 Execute VA-PHASE-001 (Performance Benchmark)
- **Design / Approach**:
  - Create temporary test plan
  - Time 20 sequential phase creations
  - Calculate average, max, min times
  - Document results

- **Acceptance**: All creations <2 seconds
- **Observations & AI Notes**: *(To be filled)*

#### 6.6 Execute VA-PHASE-002 (UX Review)
- **Design / Approach**:
  - Review delta display with varying phase counts
  - Assess readability, truncation effectiveness
  - Verify task completion stats are helpful
  - Document any UX improvements for future

- **Acceptance**: Display readable and informative
- **Observations & AI Notes**: *(To be filled)*

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Metadata migration requires complex refactoring | Study existing patterns first; ask user if complex | - |
| JSON schema doesn't support file path structures | Use array of strings, add validation in code if needed | - |
| Performance benchmark fails threshold | Profile and optimize; acceptable if close (e.g., 2.5sec) | - |
| Breaking changes to existing tracking blocks | Ensure backward compatibility; test with phase-05.md | - |

## 9. Decisions & Outcomes

- `2025-11-03` - Phase 06 scope: Schema completion + verification artifacts (not a full verification phase)
- *(Update as work progresses)*

## 10. Findings / Research Notes

**Current Status (2025-11-03):**
- `phase.overview` has full JSON schema support ✅
- `phase.tracking` is registered but says "JSON Schema not yet available" ❌
- Display already reads from phase files (confirmed via JSON output) ✅
- **Duplication identified**: plan.overview duplicates phase metadata unnecessarily

**Key Finding**:
`show delta --json` proves phase.overview is already canonical source. The plan.overview
phases array can be simplified to just IDs without breaking anything.

**Implementation Plan**: See `phase-06-implementation-plan.md` for comprehensive breakdown
of all components requiring changes (schema, creation, parser, template, tests).

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored (VA-PHASE-001, VA-PHASE-002 results)
- [ ] DE-004 updated with completion notes
- [ ] Requirements registry updated
- [ ] Hand-off notes: None needed (final phase)
- [ ] Ready for delta completion via `spec-driver complete delta DE-004`
