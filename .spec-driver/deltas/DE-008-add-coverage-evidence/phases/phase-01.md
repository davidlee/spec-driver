---
id: IP-008.PHASE-01
slug: add-coverage-evidence-phase-01
name: IP-008 Phase 01 - Schema & sync foundation
created: '2025-11-03'
updated: '2025-11-03'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-008.PHASE-01
plan: IP-008
delta: DE-008
objective: >-
  Add coverage_evidence field to RequirementRecord and update sync logic
  to populate it instead of verified_by for VT/VA/VH artifacts.
entrance_criteria:
  - SPEC-122 guidance reviewed
  - Test fixtures identified
exit_criteria:
  - RequirementRecord serialization includes coverage_evidence
  - Coverage sync populates coverage_evidence, not verified_by
  - Unit tests passing for schema and sync
  - Zero regressions
verification:
  tests:
    - VT-910
    - VT-911
  evidence:
    - Test run output showing coverage_evidence serialization
    - Test run output showing sync logic
tasks:
  - id: '1.1'
    description: Add coverage_evidence field to RequirementRecord dataclass
  - id: '1.2'
    description: Update RequirementRecord serialization methods
  - id: '1.3'
    description: Update coverage sync logic to populate coverage_evidence
  - id: '1.4'
    description: Write unit tests for schema changes
  - id: '1.5'
    description: Write unit tests for sync logic
  - id: '1.6'
    description: Run full test suite and verify zero regressions
  - id: '1.7'
    description: Lint and fix any issues
risks:
  - description: Breaking existing code that accesses RequirementRecord
    mitigation: Comprehensive test coverage before changes
```

# Phase 01 - Schema & Sync Foundation

## 1. Objective

Establish the data foundation for separating coverage evidence from audit verification by:
- Adding `coverage_evidence: list[str]` field to RequirementRecord
- Updating serialization/deserialization to handle the new field
- Modifying coverage sync logic to populate coverage_evidence instead of verified_by for VT/VA/VH artifacts
- Ensuring all changes are fully tested with zero regressions

## 2. Links & References
- **Delta**: [DE-008](../DE-008.md)
- **Implementation Plan**: [IP-008](../IP-008.md)
- **Design Revision Sections**: Not required (straightforward schema addition)
- **Specs / PRODs**: SPEC-122 (requirements registry)
- **Support Docs**:
  - `supekku/scripts/lib/requirements/registry.py:50-112` – RequirementRecord
  - `supekku/scripts/lib/requirements/registry.py:520-619` – Coverage sync
  - ISSUE-012 – Problem statement

## 3. Entrance Criteria
- [x] SPEC-122 reviewed for requirements registry patterns
- [x] Test fixtures identified in `registry_test.py`
- [x] Implementation plan approved
- [x] No blocking dependencies

## 4. Exit Criteria / Done When
- [x] RequirementRecord dataclass has coverage_evidence field with default empty list
- [x] `to_dict()` serializes coverage_evidence to YAML
- [x] `from_dict()` deserializes coverage_evidence from YAML
- [x] `merge()` handles coverage_evidence correctly (union of lists)
- [x] `_apply_coverage_evidence()` populates coverage_evidence, not verified_by, for VT/VA/VH
- [x] Unit tests pass for all schema operations
- [x] Unit tests pass for sync logic
- [x] Full test suite runs with zero regressions (1166 passing)
- [x] Ruff lint passes
- [x] Pylint passes (9.60/10 and 9.70/10 >> 0.73)

## 5. Verification
- **Tests to run**:
  - `uv run pytest supekku/scripts/lib/requirements/registry_test.py -v` – Unit tests
  - `uv run pytest` – Full regression suite
  - `just lint` – Ruff linter
  - `just pylint` – Pylint check
- **Evidence to capture**:
  - VT-910: Test output showing RequirementRecord with coverage_evidence serializes correctly
  - VT-911: Test output showing sync populates coverage_evidence from coverage blocks

## 6. Assumptions & STOP Conditions
- **Assumptions**:
  - Existing test fixtures can be extended for coverage_evidence
  - Coverage block parsing logic (`load_coverage_blocks`) works correctly
  - No other code directly accesses RequirementRecord internals beyond to_dict/from_dict
- **STOP when**:
  - Test failures indicate deeper architectural issues
  - Coverage sync logic reveals unexpected coupling to verified_by field
  - Breaking changes to RequirementRecord API surface

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]` in progress, `[x]` done, `[blocked]` blocked)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Add coverage_evidence field to RequirementRecord | [ ] | Completed - line 64 |
| [x] | 1.2 | Update to_dict() for coverage_evidence | [ ] | Completed - line 96 |
| [x] | 1.3 | Update from_dict() for coverage_evidence | [ ] | Completed - line 114 |
| [x] | 1.4 | Update merge() for coverage_evidence | [ ] | Completed - lines 80-82 |
| [x] | 1.5 | Modify _apply_coverage_evidence sync logic | [ ] | Completed - line 623 |
| [x] | 1.6 | Write unit tests for schema operations | [ ] | VT-910 - 3 new tests |
| [x] | 1.7 | Write unit tests for sync logic | [ ] | VT-911 - Updated existing |
| [x] | 1.8 | Run full test suite | [ ] | 1166 tests passing |
| [x] | 1.9 | Lint (ruff + pylint) | [ ] | Ruff clean, pylint 9.60+|

### Task Details

- **1.1 Add coverage_evidence field**
  - **Design / Approach**: Add `coverage_evidence: list[str] = field(default_factory=list)` to RequirementRecord dataclass after verified_by
  - **Files / Components**: `supekku/scripts/lib/requirements/registry.py:50-65`
  - **Testing**: Verify dataclass initialization
  - **Observations & AI Notes**: TBD during implementation
  - **Commits / References**: TBD

- **1.2-1.4 Update serialization methods**
  - **Design / Approach**:
    - `to_dict()`: Add `"coverage_evidence": self.coverage_evidence` to returned dict
    - `from_dict()`: Add `coverage_evidence=list(data.get("coverage_evidence", []))`
    - `merge()`: Add `coverage_evidence=sorted(set(self.coverage_evidence) | set(other.coverage_evidence))`
  - **Files / Components**: `supekku/scripts/lib/requirements/registry.py:82-112`
  - **Testing**: Unit tests for round-trip serialization
  - **Observations & AI Notes**: TBD
  - **Commits / References**: TBD

- **1.5 Modify coverage sync logic**
  - **Design / Approach**:
    - In `_apply_coverage_evidence()` at line 608-619
    - Change `record.verified_by = sorted(set(record.verified_by) | artefacts)`
    - To `record.coverage_evidence = sorted(set(record.coverage_evidence) | artefacts)`
    - Keep verified_by logic separate for audit sync
  - **Files / Components**: `supekku/scripts/lib/requirements/registry.py:608-619`
  - **Testing**: Mock coverage blocks and verify sync populates coverage_evidence
  - **Observations & AI Notes**: TBD
  - **Commits / References**: TBD

- **1.6-1.7 Write unit tests**
  - **Design / Approach**:
    - Test RequirementRecord with coverage_evidence serializes/deserializes
    - Test merge() combines coverage_evidence from two records
    - Test sync from coverage blocks populates coverage_evidence
    - Test that verified_by is NOT populated by VT/VA/VH sync
  - **Files / Components**: `supekku/scripts/lib/requirements/registry_test.py`
  - **Testing**: New test cases following existing patterns
  - **Observations & AI Notes**: TBD
  - **Commits / References**: TBD

- **1.8-1.9 Testing and linting**
  - **Design / Approach**: Run full test suite, then both linters
  - **Files / Components**: All modified files
  - **Testing**: `just test`, `just lint`, `just pylint`
  - **Observations & AI Notes**: TBD
  - **Commits / References**: TBD

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Breaking existing serialization | Comprehensive unit tests before changes | [ ] |
| Merge logic incorrect | Test merge scenarios explicitly | [ ] |
| Sync logic has hidden dependencies | Review all callers of _apply_coverage_evidence | [ ] |

## 9. Decisions & Outcomes
- `2025-11-03` - Use simple list structure for coverage_evidence matching verified_by pattern (not richer metadata)
- `2025-11-03` - Apply union strategy in merge() to combine coverage evidence from multiple sources
- `2025-11-03` - Updated existing test `test_sync_processes_coverage_blocks` to check coverage_evidence instead of verified_by
- `2025-11-03` - All changes completed in single pass with zero regressions

## 10. Findings / Research Notes
- RequirementRecord currently at line 50-112 in registry.py
- Coverage sync at line 520-619 uses `_apply_coverage_evidence()` method
- Existing tests in `registry_test.py` use fixtures we can extend
- Coverage blocks parsed by `load_coverage_blocks()` from `supekku/scripts/lib/blocks/verification.py`
- **Implementation went smoothly** - no unexpected coupling or architectural issues
- Line length fix required on merge() for ruff compliance
- Import organization required for pylint compliance

## 11. Wrap-up Checklist
- [x] All exit criteria satisfied
- [x] VT-910 and VT-911 evidence captured (3 new tests + 1 updated test)
- [x] IP-008 updated with phase completion status (pending)
- [x] Hand-off notes to Phase 02: coverage_evidence field ready for validation/display work

### Test Evidence (VT-910, VT-911)
```
14 tests passing in requirements/registry_test.py:
- test_coverage_evidence_field_serialization (VT-910)
- test_coverage_evidence_merge (VT-910)
- test_coverage_sync_populates_coverage_evidence (VT-911)
- test_sync_processes_coverage_blocks (updated for VT-911)

Full suite: 1166 tests passing
Ruff: All checks passed
Pylint: registry.py 9.60/10, registry_test.py 9.70/10
```

### Phase 02 Hand-off
The `coverage_evidence` field is now fully functional and tested:
- Schema: RequirementRecord dataclass includes coverage_evidence
- Serialization: YAML round-trip working correctly
- Sync: Coverage blocks populate coverage_evidence (not verified_by)
- Testing: Comprehensive unit tests in place with zero regressions

**Ready for**: Validation warnings implementation and formatter/display updates.
