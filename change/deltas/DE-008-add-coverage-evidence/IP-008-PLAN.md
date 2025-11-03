# Implementation Plan for DE-008

## Analysis

### Core Changes Required

1. **RequirementRecord Schema** (`supekku/scripts/lib/requirements/registry.py:50-112`)
   - Add `coverage_evidence: list[str]` field to dataclass
   - Update `to_dict()` to serialize coverage_evidence
   - Update `from_dict()` to deserialize coverage_evidence
   - Update `merge()` to handle coverage_evidence merging

2. **Coverage Sync Logic** (`supekku/scripts/lib/requirements/registry.py:520-619`)
   - Modify `_apply_coverage_evidence()` to populate `coverage_evidence` instead of `verified_by`
   - Keep artifact filtering (VT/VA/VH vs AUD distinction)

3. **Validation Rules** (`supekku/scripts/lib/validation/validator.py`)
   - Remove false-positive check at line 61-66 (VT/VA/VH in verified_by)
   - Add warning: coverage_evidence exists but status not in [baseline, active, verified]
   - Add warning: no audit in verified_by after grace period (default 30 days from introduced date)

4. **Display/Formatting** (`supekku/scripts/lib/formatters/requirement_formatters.py`)
   - Update formatters to show both verified_by and coverage_evidence
   - JSON output must include both fields

5. **Tests**
   - `supekku/scripts/lib/requirements/registry_test.py`: Add coverage_evidence serialization tests
   - `supekku/scripts/lib/requirements/registry_test.py`: Add coverage sync tests
   - `supekku/scripts/lib/validation/validator_test.py`: Add validation warning tests
   - `supekku/scripts/lib/formatters/requirement_formatters_test.py`: Add display tests

6. **Documentation**
   - `supekku/about/glossary.md`: Update RequirementRecord entry
   - Relevant SPEC docs to be updated during closeout

## Phasing Strategy

### Phase 01: Schema & Sync Foundation
**Objective**: Add coverage_evidence field and update sync logic without breaking existing functionality.

**Scope**:
- RequirementRecord dataclass changes
- Serialization/deserialization
- Coverage sync logic update
- Unit tests for schema and sync

**Rationale**: Establish data foundation before validation/display changes.

### Phase 02: Validation & Display
**Objective**: Implement validation warnings and update all display logic.

**Scope**:
- Validation warning logic
- Formatter updates
- CLI/JSON output changes
- Integration tests
- Documentation updates

**Rationale**: Build on phase 01 foundation; validation and display naturally group together.

## Entry Criteria

- [x] DE-008 delta approved
- [x] SPEC-122 and SPEC-125 reviewed for guidance
- [x] Test strategy identified
- [x] No blocking dependencies

## Exit Criteria (Overall)

- [ ] All tests passing (zero regressions)
- [ ] Ruff lint clean
- [ ] Pylint >= 0.73
- [ ] Coverage sync populates coverage_evidence correctly
- [ ] WorkspaceValidator emits no false positives for VT/VA/VH
- [ ] Validation warnings trigger appropriately
- [ ] CLI output distinguishes coverage from audit verification
- [ ] Documentation updated

## Risks

1. **Existing registry data**: Manual cleanup required for mixed verified_by entries
   - Mitigation: Document cleanup procedure; sync repopulates correctly going forward

2. **Delta completion workflow**: Could break if tightly coupled to verified_by
   - Mitigation: Review `check_coverage_completeness()` - already uses coverage blocks, not registry

3. **Grace period undefined**: PROD-009 may not specify exact duration
   - Mitigation: Use 30-day default, make configurable via constant

## Test Strategy

- **Unit tests**: RequirementRecord serialization, sync logic, validation rules
- **Integration tests**: Full sync workflow with coverage blocks
- **Regression tests**: Ensure existing functionality unchanged
- **Manual verification**: CLI output correctness
