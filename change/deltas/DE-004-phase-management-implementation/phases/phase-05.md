---
id: IP-004.PHASE-05
slug: 004-phase-management-implementation-phase-05
name: IP-004 Phase 05
created: '2025-11-03'
updated: '2025-11-03'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-004.PHASE-05
plan: IP-004
delta: DE-004
name: Phase 05 - Structured Progress Tracking
objective: >-
  Implement phase.tracking@v1 YAML block for structured completion tracking
  of entrance/exit criteria and tasks, replacing regex-based progress parsing.
entrance_criteria:
  - Phases 01, 02, 04 complete (core functionality working)
  - Understanding of existing phase.overview block structure
  - User approval for structured tracking design
exit_criteria:
  - phase.tracking@v1 schema defined and documented
  - Parser/validator for tracking block implemented
  - Formatter updated to use structured data instead of regex
  - Phase template includes new tracking block
  - VT-PHASE-007 passing (tracking block tests)
  - Backward compatibility maintained (tracking block optional)
verification:
  tests:
    - VT-PHASE-007
  evidence:
    - Test output showing tracking block parsing/validation
    - Manual test with phase-05.md tracking block
    - Backward compat test with existing phases (no tracking block)
tasks:
  - Define phase.tracking@v1 schema
  - Implement parser and validator
  - Update formatter to use tracking data
  - Update phase template
  - Write comprehensive tests
  - Add migration guide for existing phases
risks:
  - Breaking changes to existing phase files
  - Complex data structure may be harder to maintain manually
  - Need to support both tracking block and markdown checkboxes
```

# Phase 05 - Structured Progress Tracking

## 1. Objective

Replace regex-based task/criteria completion parsing with structured YAML data, enabling:
- Accurate automated progress calculation
- Queryable completion status
- Validation of tracking data
- Better tooling support (auto-update, reporting)

## 2. Links & References
- **Delta**: DE-004
- **Plan**: IP-004
- **Related Phases**: Phase 01 (phase creation), Phase 02 (display)
- **Specs / PRODs**: Extension of PROD-006 functionality
- **Support Docs**:
  - Existing pattern: `phase.overview@v1` block structure
  - Schema patterns: `supekku/scripts/lib/blocks/plan.py`
  - Current regex parsing: `supekku/scripts/lib/changes/artifacts.py` (task count extraction)

## 3. Entrance Criteria
- [x] Phases 01, 02, 04 complete (phase creation, display, plan metadata working)
- [x] User approved structured tracking design
- [x] Understanding of phase.overview and block parser patterns
- [ ] Decision on whether to make tracking block required or optional

## 4. Exit Criteria / Done When
- [ ] `phase.tracking@v1` schema defined with validation rules
- [ ] Parser extracts tracking block from phase files
- [ ] Validator ensures tracking data consistency
- [ ] Formatter uses tracking block (with fallback to regex for backward compat)
- [ ] Phase template includes tracking block with examples
- [ ] VT-PHASE-007 tests passing (parsing, validation, formatting)
- [ ] Migration guide written for converting existing phases
- [ ] All existing tests still passing
- [ ] Linters passing

## 5. Verification

**VT-PHASE-007: Tracking Block Tests**
- Location: `supekku/scripts/lib/blocks/plan_test.py` (or new `tracking_test.py`)
- Tests:
  - `test_parse_tracking_block()` → extract tracking block from phase markdown
  - `test_validate_tracking_block_valid()` → valid tracking data passes
  - `test_validate_tracking_block_missing_required()` → error on missing phase ID
  - `test_validate_tracking_block_invalid_status()` → error on bad task status
  - `test_tracking_completion_calculation()` → calculate % complete correctly
  - `test_formatter_with_tracking_block()` → use tracking data for display
  - `test_formatter_backward_compat()` → fallback to regex when no tracking block
- Command: `uv run pytest supekku/scripts/lib/blocks/tracking_test.py -v`

**Manual Tests**:
- Create phase-05 with tracking block, verify `show delta` uses it
- Test existing phases (without tracking) still display correctly
- Update tracking block manually, verify formatter reflects changes

## 6. Assumptions & STOP Conditions

**Assumptions**:
- Tracking block is **optional** (backward compatibility)
- When tracking block exists, it takes precedence over regex parsing
- Task status values: `pending`, `in_progress`, `completed`, `blocked`
- Criteria completion is boolean (true/false)
- One tracking block per phase file

**STOP Conditions**:
- STOP if making tracking block required breaks too many existing phases
- STOP if backward compatibility becomes too complex
- STOP if user wants different schema structure

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 5.1 | Define phase.tracking@v1 schema | [ ] | Design first |
| [ ] | 5.2 | Implement tracking block parser | [ ] | After 5.1 |
| [ ] | 5.3 | Implement tracking block validator | [x] | Parallel with 5.2 |
| [ ] | 5.4 | Update formatter to use tracking data | [ ] | After 5.2 |
| [ ] | 5.5 | Write VT-PHASE-007 tests | [x] | Can start with 5.2 |
| [ ] | 5.6 | Update phase template | [ ] | After 5.1 |
| [ ] | 5.7 | Add this phase-05 tracking block | [ ] | Self-dogfood |
| [ ] | 5.8 | Run full test suite | [ ] | Final gate |

### Task Details

**5.1 Define phase.tracking@v1 Schema**
- **Design / Approach**:
  - Schema marker: `supekku:phase.tracking@v1`
  - Required fields: `schema`, `version`, `phase` (ID)
  - Optional arrays: `entrance_criteria`, `exit_criteria`, `tasks`
  - Criteria format: `{item: str, completed: bool}`
  - Task format: `{id: str, description: str, status: str}`
  - Status enum: `pending | in_progress | completed | blocked`
- **Files / Components**:
  - `supekku/scripts/lib/blocks/plan.py` - add constants and schema
  - Document in `.spec-driver/schemas/` (if exists)
- **Testing**: Schema validation tests
- **Observations & AI Notes**: [To be filled]

**5.2 Implement Tracking Block Parser**
- **Design / Approach**:
  - Add `extract_phase_tracking()` function similar to `extract_phase_overview()`
  - Regex pattern: `` r"```(?:yaml|yml)\s+supekku:phase.tracking@v1\n(.*?)```" ``
  - Return `PhaseTrackingBlock` dataclass with `raw_yaml` and `data`
  - Handle missing block gracefully (return None for backward compat)
- **Files / Components**:
  - `supekku/scripts/lib/blocks/plan.py` - add parser
  - Export in `__all__`
- **Testing**: VT-PHASE-007
- **Observations & AI Notes**: [To be filled]

**5.3 Implement Tracking Block Validator**
- **Design / Approach**:
  - Add `PhaseTrackingValidator` class following `PhaseOverviewValidator` pattern
  - Validate schema/version match
  - Validate phase ID required and matches file
  - Validate criteria structure (item + completed fields)
  - Validate task structure (id + description + status fields)
  - Validate status enum values
- **Files / Components**:
  - `supekku/scripts/lib/blocks/plan.py` - add validator
- **Testing**: VT-PHASE-007
- **Observations & AI Notes**: [To be filled]

**5.4 Update Formatter to Use Tracking Data**
- **Design / Approach**:
  - Modify `_enrich_phase_data()` to check for tracking block first
  - If tracking block exists, calculate completion from structured data
  - If no tracking block, fallback to current regex parsing
  - Extract task counts: `len([t for t in tasks if t['status'] == 'completed'])`
  - Extract criteria completion: `len([c for c in criteria if c['completed']])`
- **Files / Components**:
  - `supekku/scripts/lib/formatters/change_formatters.py` - update enrichment
  - `supekku/scripts/lib/changes/artifacts.py` - may need helper function
- **Testing**: VT-PHASE-007 + existing formatter tests
- **Observations & AI Notes**: [To be filled]

**5.5 Write VT-PHASE-007 Tests**
- **Design / Approach**: Comprehensive test suite covering all scenarios
- **Files / Components**: `supekku/scripts/lib/blocks/tracking_test.py` (new)
- **Testing**: Self-testing
- **Observations & AI Notes**: [To be filled]

**5.6 Update Phase Template**
- **Design / Approach**:
  - Add tracking block after phase.overview block
  - Include example data with inline comments
  - Make it clear tracking block is optional
- **Files / Components**: `supekku/templates/phase.md`
- **Testing**: Manual - create new phase, verify template correct
- **Observations & AI Notes**: [To be filled]

**5.7 Add Tracking Block to This Phase**
- **Design / Approach**: Dogfood the feature by adding tracking to phase-05.md
- **Testing**: Verify `show delta DE-004` shows accurate progress for phase-05
- **Observations & AI Notes**: [To be filled]

**5.8 Run Full Test Suite**
- **Testing**: `just test` and `just lint`
- **Observations & AI Notes**: [To be filled]

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Breaking existing phases without tracking block | Make tracking block optional, maintain regex fallback | Design |
| Manual editing of YAML is error-prone | Provide clear examples, add validation | Design |
| Complexity of dual-mode formatter | Clear separation of tracking vs regex paths | Pending |
| Schema evolution in future | Version field allows future changes | Design |

## 9. Decisions & Outcomes
- `2025-11-03` - Phase 05 created to implement structured tracking (user requested)
- `2025-11-03` - Tracking block will be optional for backward compatibility
- `2025-11-03` - Task status values: pending, in_progress, completed, blocked

## 10. Findings / Research Notes

**Schema Design Considerations**:
- Keep it simple - don't over-engineer
- Match phase.overview structure where possible
- Boolean completion for criteria (simpler than tri-state)
- String status for tasks (more granular than boolean)

**Example Tracking Block**:
```yaml
```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-004.PHASE-05
entrance_criteria:
  - item: "Phases 01, 02, 04 complete"
    completed: true
  - item: "User approval for design"
    completed: true
exit_criteria:
  - item: "Schema defined and documented"
    completed: false
  - item: "Parser/validator implemented"
    completed: false
tasks:
  - id: "5.1"
    description: "Define phase.tracking@v1 schema"
    status: pending
  - id: "5.2"
    description: "Implement tracking block parser"
    status: pending
```
```

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] VT-PHASE-007 passing
- [ ] All tests passing (backward compat verified)
- [ ] Linters passing
- [ ] Code committed with clear message
- [ ] Template updated and verified
- [ ] Migration guide written (optional enhancement)
- [ ] Hand-off notes: Phase 03 (VA artifacts) can proceed independently
