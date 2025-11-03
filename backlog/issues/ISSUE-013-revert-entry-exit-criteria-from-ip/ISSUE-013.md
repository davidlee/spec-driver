---
id: ISSUE-013
name: Restore entry/exit criteria to IP and phase.overview schemas
created: '2025-11-03'
updated: '2025-11-03'
status: resolved
kind: issue
categories:
  - process_gap
  - schema_design
severity: p2
impact: process
linked_deltas:
  - DE-004
  - DE-012
related_requirements: []
---

# ISSUE-013 – Restore entry/exit criteria to IP and phase.overview schemas

## Problem Statement

During DE-004 Phase 06 (schema simplification), entry and exit criteria were removed from the `plan.overview` phases array to eliminate duplication with `phase.overview` blocks. The phases array was simplified to ID-only format: `{id: "IP-XXX.PHASE-NN"}`.

**However, this was a mistake for two critical reasons:**

1. **IP Planning Contract**: Entry/exit criteria in the IP are part of the upfront planning contract, created before phase sheets exist. They define the gates that must be satisfied for phases to begin and complete, serving as a quality contract between the planner and implementer.

2. **Phase Sheet Sync**: While phase sheets also have entry/exit criteria in their markdown sections and `phase.tracking` blocks, these can drift from the original plan. The IP should remain the source of truth for the planned gates, with tooling to detect and warn about drift.

**Current State**: Entry/exit criteria exist only in:
- Phase sheet markdown (sections 3 & 4)
- `phase.tracking@v1` blocks (optional, structured format)
- IP markdown table (Section 4 - manual duplication, no validation)

**Desired State**: Entry/exit criteria also in:
- `plan.overview@v1` phases array (upfront planning contract)
- `phase.overview@v1` blocks (copied from IP during `create phase`)
- Tooling warns when phase criteria drift from IP baseline

## Context

**Commit**: 6f69db8 "feat(DE-004): Phase 06 - schema simplification & phase.tracking metadata"

**What was removed from plan.overview phases**:
```yaml
phases:
  - id: IP-004.PHASE-01
    name: "Phase 01 - Create Phase Command"  # REMOVED
    objective: "Implement create phase..."   # REMOVED
    entrance_criteria:                        # REMOVED
      - "DE-004 delta approved"
      - "PROD-006 spec reviewed"
    exit_criteria:                           # REMOVED
      - "create_phase() function implemented"
      - "CLI command wired"
      - "VT-PHASE-001, 002, 004 passing"
```

**Current simplified format**:
```yaml
phases:
  - id: IP-004.PHASE-01
```

**Why this matters**:
- IPs are created during planning, before implementation begins
- Entry/exit criteria are quality gates that must be defined upfront
- Phase sheets are created just-in-time during execution
- The IP criteria serve as the baseline contract
- Drift detection helps catch scope creep or missed requirements

## Proposed Solution

### 1. Restore to IP Schema (plan.overview@v1)

Add back to `PLAN_OVERVIEW_METADATA.fields.phases.items.properties`:
```python
"name": FieldMetadata(
  type="string",
  required=False,  # Optional for backward compat
  description="Phase name/title",
),
"objective": FieldMetadata(
  type="string",
  required=False,
  description="Phase objective statement",
),
"entrance_criteria": FieldMetadata(
  type="array",
  required=False,
  description="Criteria that must be met before starting phase",
  items=FieldMetadata(type="string", description="Criterion"),
),
"exit_criteria": FieldMetadata(
  type="array",
  required=False,
  description="Criteria that must be met to complete phase",
  items=FieldMetadata(type="string", description="Criterion"),
),
```

### 2. Restore to Phase Schema (phase.overview@v1)

Phase metadata already has these fields - ensure they're populated during `create phase`.

### 3. Tooling Support

**During `create phase --plan IP-XXX`**:
1. Read entry/exit criteria from IP's `plan.overview` phases array
2. Copy them into the new phase's `phase.overview` block
3. Copy them into the `phase.tracking` block if using structured tracking

**Drift Detection (future enhancement)**:
- `spec-driver validate workspace` compares phase criteria to IP baseline
- Warns if criteria have drifted (additions, deletions, modifications)
- Suggests either updating the phase or updating the IP if scope changed

### 4. Migration Strategy

**Backward Compatibility**: Keep fields optional so existing ID-only plans continue working.

**Migration Path**:
- New IPs created with full metadata (name, objective, criteria)
- Existing IPs can be enhanced incrementally when revised
- `create phase` works with both formats (full metadata preferred, ID-only fallback)

## Requirements

### FR-013.001: IP Schema Restoration
**Statement**: The `plan.overview@v1` schema SHALL support `name`, `objective`, `entrance_criteria`, and `exit_criteria` fields in the phases array.

**Acceptance Criteria**:
- Schema metadata updated in `plan_metadata.py`
- Fields are optional for backward compatibility
- JSON Schema generation includes new fields
- Documentation updated

**Verification**: VT-SCHEMA-013-001 (unit tests for schema validation)

### FR-013.002: Phase Creation with Criteria Copy
**Statement**: The `create phase` command SHALL copy entry/exit criteria from the IP's plan.overview block into the new phase's phase.overview and phase.tracking blocks.

**Acceptance Criteria**:
- Criteria copied from IP phases array to phase.overview
- Criteria copied to phase.tracking entrance_criteria/exit_criteria arrays
- If IP has no criteria, phase is created without them (graceful fallback)
- Manual test: create phase from IP with criteria populates correctly

**Verification**: VT-CREATE-013-002 (unit tests for create_phase with criteria)

### FR-013.003: Drift Detection Warning
**Statement**: The workspace validator SHOULD warn when phase entry/exit criteria differ from the IP baseline.

**Priority**: P2 (can be deferred to separate delta)

**Acceptance Criteria**:
- `validate workspace` compares phase.overview/tracking criteria to IP
- Warnings logged for additions, deletions, or modifications
- Warning includes phase ID and specific drifts
- Does not block validation (warning only)

**Verification**: VT-VALIDATE-013-003 (validator tests for drift detection)

### NF-013.001: Backward Compatibility
**Statement**: The schema changes MUST NOT break existing IP files using ID-only phase format.

**Acceptance Criteria**:
- All existing IPs continue to parse correctly
- `show delta` works with both formats
- `create phase` works with both formats (prefers full, falls back to ID-only)
- All 1200+ existing tests still pass

**Verification**: VT-COMPAT-013-001 (regression test suite)

## Affected Files

**Schema Definitions**:
- `supekku/scripts/lib/blocks/plan_metadata.py` - PLAN_OVERVIEW_METADATA
- `supekku/scripts/lib/blocks/phase_metadata.py` - PHASE_OVERVIEW_METADATA (already has fields)

**Creation Logic**:
- `supekku/scripts/lib/changes/creation.py` - create_phase() function
- `supekku/cli/create.py` - phase creation command

**Validation** (future):
- `supekku/scripts/lib/validation/validator.py` - drift detection

**Templates**:
- `supekku/templates/plan.md` - update Phase Overview table guidance
- `supekku/templates/phase.md` - already has criteria sections

**Tests**:
- `supekku/scripts/lib/blocks/plan_metadata_test.py` - schema tests
- `supekku/scripts/lib/changes/creation_test.py` - create_phase tests
- `supekku/scripts/lib/validation/validator_test.py` - drift detection tests (future)

## Success Criteria

- [ ] Schema changes merged and documented
- [ ] `create phase` copies criteria from IP
- [ ] Backward compatibility verified (all existing tests pass)
- [ ] Manual test: create IP with full phase metadata, then create phase, verify criteria copied
- [ ] Manual test: create IP with ID-only phases, create phase, verify graceful fallback
- [ ] Documentation updated (frontmatter-schema.md, IP template guidance)

## Notes

**Why not remove from phase.overview too?**
Phase sheets need their own copy because:
1. They're created just-in-time, long after IP planning
2. They may legitimately evolve during implementation
3. Having both allows drift detection (IP = baseline, phase = reality)

**Why this is P2 not P3?**
This affects the core implementation workflow contract. Without upfront criteria in the IP:
- Planning is incomplete (no quality gates defined)
- Phase sheets start without clear baseline
- Drift is undetectable
- Implementation handoffs are ambiguous
