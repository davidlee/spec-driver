# Phase 02 Research Findings

**Date**: 2025-11-03
**Phase**: IP-007.PHASE-02
**Researcher**: Agent

## PROD Requirements Summary

### PROD-008: Requirements Lifecycle Coherence

**Core Contract:**
- **FR-001**: Specs frontmatter and coverage blocks are THE authoritative record of requirement lifecycle state
- **FR-002**: Every delta changing requirement behavior MUST document VT/VA/VH in implementation plan and **promote final state back to spec coverage block before completion**
- **FR-003**: Audits reconcile observed vs spec, raise drift warnings until corrected

**Key Insight**: The delta completion workflow is the enforcement point where spec coverage updates must happen. This is where we insert the coverage completeness check.

### PROD-009: Requirement Lifecycle Semantics

**Core Semantics:**
- **FR-001**: Specs declare baseline lifecycle statuses (planned, asserted, legacy_verified, deprecated)
- **FR-002**: Lifecycle engine overlays statuses from deltas and audits using timestamp precedence
- **FR-003**: Validation emits warnings when overlays disagree

**Valid Coverage Statuses**: planned, in-progress, verified, failed, blocked

**Status Precedence**: Most recent timestamp wins; if tied, audits > deltas

## Existing Completion Workflow Analysis

### File: `supekku/scripts/complete_delta.py`

**Current Flow** (lines 344-458):
1. Load workspace and delta registry
2. Validate delta exists and status is appropriate
3. Collect requirements from `delta.applies_to.requirements`
4. Handle already-completed case (idempotent)
5. Display preview
6. Prompt for spec sync
7. Display actions
8. Handle dry-run
9. **Confirm unless force mode** ← **INSERTION POINT**
10. Update requirements in revision sources (if flag set)
11. Sync requirements registry
12. Update delta frontmatter status to 'completed'
13. Sync delta registry

**Key Functions:**
- `complete_delta()` - main orchestration (line 344)
- `validate_delta_status()` - checks delta status (line 54)
- `collect_requirements_to_update()` - gets requirements from delta (line 77)
- `update_requirements_in_revision_sources()` - persists requirement updates (line 207)

**Existing Flags:**
- `--dry-run` - preview without changes
- `--force` - skip all prompts
- `--skip-sync` - skip spec sync prompt
- `--skip-update-requirements` - only mark delta complete, don't update requirements

### File: `supekku/cli/complete.py`

**Structure**: Thin wrapper around `complete_delta_impl()`
- Uses Typer for CLI argument parsing
- Maps flags to implementation function
- Simple error handling and exit codes

**Clean separation**: CLI handles parsing, script handles logic (follows AGENTS.md skinny CLI pattern)

## Verification Coverage Infrastructure

### File: `supekku/scripts/lib/blocks/verification.py`

**Available Tools:**
- `load_coverage_blocks(path: Path)` - extracts coverage blocks from markdown files
- `extract_coverage_blocks(text: str)` - parses coverage from text
- `VerificationCoverageBlock` - dataclass with `raw_yaml` and `data` fields
- `VerificationCoverageValidator` - validates block schema and entries

**Coverage Entry Structure:**
```python
{
  'artefact': 'VT-902',      # V[TAH]-###
  'kind': 'VT|VA|VH',        # Verification type
  'requirement': 'SPEC-100.FR-001',
  'status': 'planned|in-progress|verified|failed|blocked',
  'phase': 'IP-007.PHASE-01',  # Optional
  'notes': 'Description'       # Optional
}
```

**Constants:**
- `VALID_STATUSES = {"planned", "in-progress", "verified", "failed", "blocked"}`
- `VALID_KINDS = {"VT", "VA", "VH"}`

## Requirements Registry Integration (Phase 01)

**From Phase 01 completion notes:**
- Registry already processes coverage blocks via `_apply_coverage_blocks()`
- Coverage extracted from specs, IPs, deltas, audits
- `RequirementRecord.verified_by` populated with artefact IDs
- Lifecycle status computed from aggregated coverage
- Drift detection emits warnings to stderr

**Registry Access:**
```python
workspace = Workspace.from_cwd()
requirements_registry = workspace.requirements
# Registry has: records (dict), status info, verified_by lists
```

## Implementation Design

### Coverage Completeness Check Function

**Purpose**: Verify all delta requirements have `status: verified` coverage in parent specs

**Location**: `supekku/scripts/lib/changes/coverage_check.py` (new module, keeps CLI thin)

**Signature:**
```python
def check_coverage_completeness(
  delta_id: str,
  workspace: Workspace,
) -> tuple[bool, list[CoverageMissing]]:
  """Check if all delta requirements have verified coverage in specs.

  Returns:
    (is_complete, missing_coverage_details)
  """
```

**Algorithm:**
1. Load delta from workspace.delta_registry
2. Extract `applies_to.requirements` list
3. For each requirement:
   - Parse requirement ID to get parent spec (e.g., "PROD-008.FR-001" → "PROD-008")
   - Discover spec file path (use workspace or registry)
   - Load spec file and extract coverage blocks
   - Find coverage entry matching this requirement
   - Check if status == 'verified'
   - Collect failures: missing block, missing entry, non-verified status
4. Return (all_verified, missing_list)

**Data Structure for Missing Coverage:**
```python
@dataclass
class CoverageMissing:
  requirement_id: str
  spec_id: str
  spec_path: Path
  current_status: str | None  # None if missing entirely
  reason: str  # 'missing_block' | 'missing_entry' | 'not_verified'
```

### Integration Point

**Insert before line 426** in `complete_delta()`:
```python
# Confirm unless force mode
if not force and not prompt_yes_no("Proceed with completion?", default=False):
  return 1

# NEW: Coverage enforcement check
if not is_coverage_enforcement_enabled():
  # Log that enforcement is disabled
  pass
elif not force:
  is_complete, missing = check_coverage_completeness(delta_id, workspace)
  if not is_complete:
    display_coverage_error(delta_id, missing)
    return 1
```

**Rationale**:
- After preview and spec sync, before final confirmation
- Skip if `--force` flag (emergency override)
- Skip if environment variable disables enforcement
- Fail before making any changes to ensure clean exit

### Environment Variable

```python
def is_coverage_enforcement_enabled() -> bool:
  """Check if coverage enforcement is enabled."""
  value = os.getenv('SPEC_DRIVER_ENFORCE_COVERAGE', 'true').lower()
  return value in ('true', '1', 'yes', 'on')
```

### Error Display

**Function**: `display_coverage_error(delta_id, missing_list)`

**Format:**
```
ERROR: Cannot complete {delta_id} - coverage verification required

The following requirements need verified coverage in their specs:

  {requirement_id} (in {spec_path})
    Current status: {status or 'missing'}
    Action: Update coverage block status to 'verified'

Example coverage update:
```yaml supekku:verification.coverage@v1
entries:
  - artefact: VT-902
    kind: VT
    requirement: {requirement_id}
    status: verified  # ← Update this
    notes: Description of verification
```

See: .spec-driver/RUN.md for coverage workflow documentation

To bypass this check (emergency only):
  uv run spec-driver complete delta {delta_id} --force
```

## Testing Strategy

### No Existing Tests Found
- No `complete_delta_test.py` exists
- Need to create test file from scratch
- Use existing test patterns from `registry_test.py`, `updater_test.py`

### Test Fixtures Needed
- Sample delta with requirements
- Sample spec with coverage blocks (verified, planned, missing)
- Test workspace setup

### Test Cases
1. `test_completion_succeeds_with_verified_coverage` - all requirements verified
2. `test_completion_fails_with_planned_coverage` - some requirements planned
3. `test_completion_fails_with_missing_coverage` - coverage entry missing
4. `test_completion_succeeds_with_force_flag` - bypass check with --force
5. `test_completion_respects_env_var_disabled` - SPEC_DRIVER_ENFORCE_COVERAGE=false
6. `test_error_message_formatting` - verify error output is correct

## Documentation Updates

### RUN.md (needs creation or update)

Add section on delta completion workflow with coverage requirements

### AGENTS.md

Add to "Before Completing Delta" checklist:
- [ ] All VT/VA/VH verification artifacts executed
- [ ] Spec coverage blocks updated with verified status
- [ ] `uv run spec-driver complete delta DE-XXX` succeeds without --force

## Open Questions & Decisions

### Q1: How to discover parent spec path from requirement ID?

**Options:**
1. Parse requirement ID (e.g., "PROD-008.FR-001" → "PROD-008"), look up in workspace
2. Use requirements registry to find parent spec
3. Convention-based path construction

**Recommendation**: Use workspace/registry lookup - most reliable, handles spec moves

### Q2: Should we also check IP coverage status?

**Analysis**: PROD-008.FR-002 says "implementation plan documents VT/VA/VH" but the authoritative record is the spec. IP is transient work tracking, spec is permanent record.

**Decision**: Check only spec coverage status. IP coverage is for in-progress tracking.

### Q3: What if spec has no coverage block at all?

**Options:**
1. Hard error - block completion
2. Warning - allow completion
3. Graceful degradation - skip enforcement for that spec

**Recommendation**: Warning + skip enforcement. Legacy specs may not have coverage blocks yet. Log warning encouraging adoption.

### Q4: Should we validate all requirements or only those touched by delta?

**Analysis**: Delta `applies_to.requirements` lists touched requirements. Other requirements in spec are unaffected.

**Decision**: Only validate requirements listed in delta's `applies_to.requirements`.

## Implementation Risks

### Risk: False positives for legacy specs
**Mitigation**: Gracefully skip enforcement when spec lacks coverage blocks, log adoption nudge

### Risk: Spec path discovery fails
**Mitigation**: Use workspace API which should handle spec discovery; add error handling

### Risk: Coverage parsing errors
**Mitigation**: Use existing validated parser (`load_coverage_blocks`), catch exceptions

### Risk: Performance impact
**Mitigation**: Only load specs for touched requirements (not all specs); should be <1s

## Next Steps

1. Create `supekku/scripts/lib/changes/coverage_check.py` with core logic
2. Integrate into `complete_delta()` workflow
3. Add `--force` flag handling (already exists, just extend)
4. Add environment variable check
5. Implement error display function
6. Create test file with comprehensive test cases
7. Update documentation (RUN.md, AGENTS.md)
8. Manual validation sessions (VA-320, VH-201)
9. Lint and test

## File Locations Summary

**Existing Files to Modify:**
- `supekku/scripts/complete_delta.py` - add coverage check integration (~20 lines)
- `supekku/cli/complete.py` - already has --force flag, no changes needed

**New Files to Create:**
- `supekku/scripts/lib/changes/coverage_check.py` - coverage completeness logic
- `supekku/scripts/lib/changes/coverage_check_test.py` - test suite
- `.spec-driver/RUN.md` - workflow documentation (or update if exists)

**Files to Update:**
- `AGENTS.md` - add coverage checklist
- `supekku/scripts/lib/changes/__init__.py` - export new functions if needed
