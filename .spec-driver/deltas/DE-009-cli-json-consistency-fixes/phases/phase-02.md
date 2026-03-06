---
id: IP-009.PHASE-02
slug: cli-json-consistency-fixes-phase-02
name: IP-009 Phase 02
created: '2025-01-04'
updated: '2025-01-04'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-009.PHASE-02
plan: IP-009
delta: DE-009
objective: >-
  Complete PROD-010.FR-002 by implementing proper JSON serialization for show commands that currently return incomplete output (show spec) or crash (show adr, show policy, show standard). Add to_dict() methods to model objects or create dedicated JSON formatters to match the working pattern used by show delta/requirement.
entrance_criteria:
  - Development environment set up with uv and dependencies installed
  - Phase 01 completed - list commands and some show commands working
  - Existing CLI test suite passing (just test)
  - Both linters passing (just lint, just pylint)
  - Understanding of current implementation gaps (spec/adr/policy/standard)
  - Familiarity with working patterns (show delta uses format_delta_details_json formatter)
exit_criteria:
  - All show commands support --json flag with full structured output
  - show spec --json returns complete spec data (not just {"id":"..."})
  - show adr --json returns complete decision data without crashing
  - show policy --json returns complete policy data (if policies exist)
  - show standard --json returns complete standard data (if standards exist)
  - Consistent JSON schema patterns across all show commands
  - All unit tests passing with new test coverage for fixed commands
  - Both linters passing with zero warnings
  - Manual testing confirms all show --json commands work properly
  - PROD-010.FR-002 coverage status updated to "verified"
verification:
  tests:
    - VT-CLI-SHOW-SPEC-JSON
    - VT-CLI-SHOW-ADR-JSON
    - VT-CLI-SHOW-POLICY-JSON
    - VT-CLI-SHOW-STANDARD-JSON
  evidence:
    - VT-PROD010-JSON-002
tasks:
  - id: "2.1"
    description: Research existing model structures and identify to_dict() implementation patterns
    status: pending
  - id: "2.2"
    description: Write tests for show spec --json returning full spec data (TDD)
    status: pending
  - id: "2.3"
    description: Implement to_dict() method on Spec model or create format_spec_details_json formatter
    status: pending
  - id: "2.4"
    description: Update show spec command to use proper JSON serialization
    status: pending
  - id: "2.5"
    description: Write tests for show adr --json returning full decision data (TDD)
    status: pending
  - id: "2.6"
    description: Implement to_dict() method on DecisionRecord model
    status: pending
  - id: "2.7"
    description: Update show adr command to use proper JSON serialization
    status: pending
  - id: "2.8"
    description: Write tests for show policy/standard --json (TDD)
    status: pending
  - id: "2.9"
    description: Implement to_dict() methods on PolicyRecord and StandardRecord models
    status: pending
  - id: "2.10"
    description: Update show policy/standard commands to use proper JSON serialization
    status: pending
  - id: "2.11"
    description: Run full test suite and linters, fix any issues
    status: pending
  - id: "2.12"
    description: Manual validation of all show --json commands
    status: pending
  - id: "2.13"
    description: Update PROD-010 coverage block to mark FR-002 as verified
    status: pending
risks:
  - description: Adding to_dict() methods might break existing code that expects different structure
    likelihood: low
    impact: medium
    mitigation: Comprehensive test coverage; check for existing usage of these models
  - description: JSON output schema differences between show commands confuse agents
    likelihood: medium
    impact: high
    mitigation: Follow consistent pattern - all show commands return similar top-level structure
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-009.PHASE-02
tasks_completed: 13
tasks_total: 13
```

# Phase 02 - Complete FR-002: Show Command JSON Serialization

## 1. Objective

Complete PROD-010.FR-002 by fixing the broken/incomplete `--json` flag implementations for show commands. Currently:
- ✅ `show delta --json` - works (uses dedicated formatter)
- ✅ `show requirement --json` - works
- ❌ `show spec --json` - returns minimal `{"id": "SPEC-XXX"}` instead of full data
- ❌ `show adr --json` - crashes with AttributeError (DecisionRecord lacks to_dict())
- ❌ `show policy --json` - likely incomplete/broken (same pattern as spec/adr)
- ❌ `show standard --json` - likely incomplete/broken (same pattern as spec/adr)

## 2. Links & References

- **Delta**: [DE-009](../DE-009.md) - CLI JSON consistency fixes
- **Implementation Plan**: [IP-009](../IP-009.md)
- **Previous Phase**: [Phase 01](./phase-01.md) - List commands and basic show support
- **Requirement**: PROD-010.FR-002 - All show commands MUST support `--json` flag for structured output
- **Code Files**:
  - `supekku/cli/show.py` - Show command implementations (lines 35-236)
  - `supekku/scripts/lib/specs/registry.py` - Spec model
  - `supekku/scripts/lib/decisions/registry.py` - DecisionRecord model
  - `supekku/scripts/lib/policies/registry.py` - PolicyRecord model
  - `supekku/scripts/lib/standards/registry.py` - StandardRecord model
  - `supekku/scripts/lib/formatters/` - JSON formatter patterns

## 3. Entrance Criteria

- [x] Development environment set up with uv and dependencies installed
- [x] Phase 01 completed - list commands and some show commands working
- [x] Existing CLI test suite passing (just test)
- [x] Both linters passing (just lint, just pylint)
- [x] Investigation complete - identified exact gaps in implementation
- [x] Working patterns identified (show delta uses `format_delta_details_json()`)

## 4. Exit Criteria / Done When

- [ ] All show commands support --json flag with full structured output
- [ ] `show spec --json` returns complete spec data (id, name, status, kind, path, packages, requirements, etc.)
- [ ] `show adr --json` returns complete decision data without crashing
- [ ] `show policy --json` returns complete policy data
- [ ] `show standard --json` returns complete standard data
- [ ] Consistent JSON schema patterns across all show commands
- [ ] All unit tests passing with new test coverage for fixed commands
- [ ] Both linters passing with zero warnings
- [ ] Manual testing confirms all show --json commands work properly
- [ ] PROD-010 coverage block updated to mark FR-002 as "verified"

## 5. Verification

**Tests to run**:
- Unit tests: `uv run pytest supekku/cli/test_cli.py::TestShowCommandJSON -v`
- Full test suite: `just test`
- Lint checks: `just lint && just pylint`

**Manual validation commands**:
```bash
# Test each show command with --json
uv run spec-driver show spec PROD-010 --json
uv run spec-driver show spec SPEC-110 --json
uv run spec-driver show adr ADR-001 --json
uv run spec-driver show delta DE-009 --json
uv run spec-driver show requirement PROD-010.FR-001 --json

# Verify JSON is valid and complete
uv run spec-driver show spec PROD-010 --json | jq '.'
uv run spec-driver show adr ADR-001 --json | jq '.'
```

**Evidence to capture**:
- Before/after JSON output samples
- Test coverage report showing new tests
- Linter output showing zero warnings

## 6. Assumptions & STOP Conditions

**Assumptions**:
- Pattern from `show delta` (using dedicated formatter) is the preferred approach
- Alternative: Adding `to_dict()` methods to model classes is acceptable
- Spec/DecisionRecord/PolicyRecord/StandardRecord models are safe to modify
- No breaking changes to existing JSON output from working commands

**STOP when**:
- Discover that models are used elsewhere and to_dict() would break things
- JSON schema changes would break existing agent code
- Uncertainty about correct data structure to return

## 7. Tasks & Progress

*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 2.1 | Research model structures and patterns | [ ] | Understand Spec/DecisionRecord structure |
| [ ] | 2.2 | Write tests for show spec --json (TDD) | [ ] | Test should expect full spec data |
| [ ] | 2.3 | Implement Spec JSON serialization | [ ] | Add to_dict() or formatter |
| [ ] | 2.4 | Update show spec to use JSON serialization | [ ] | Modify supekku/cli/show.py:35-60 |
| [ ] | 2.5 | Write tests for show adr --json (TDD) | [ ] | Test should expect full decision data |
| [ ] | 2.6 | Implement DecisionRecord to_dict() | [ ] | Fix AttributeError |
| [ ] | 2.7 | Update show adr to use JSON serialization | [ ] | Modify supekku/cli/show.py:151-178 |
| [ ] | 2.8 | Write tests for show policy/standard --json | [ ] | TDD for both commands |
| [ ] | 2.9 | Implement PolicyRecord/StandardRecord to_dict() | [ ] | Same pattern as DecisionRecord |
| [ ] | 2.10 | Update show policy/standard commands | [ ] | Modify supekku/cli/show.py:180-236 |
| [ ] | 2.11 | Run full test suite and linters | [ ] | Ensure all tests pass |
| [ ] | 2.12 | Manual validation of all show commands | [ ] | Test each command manually |
| [ ] | 2.13 | Update PROD-010 coverage block | [ ] | Mark FR-002 as verified |

### Task Details

- **2.1 Research model structures and patterns**
  - **Design / Approach**:
    - Read Spec, DecisionRecord, PolicyRecord, StandardRecord class definitions
    - Check if they inherit from dataclasses or have existing serialization
    - Look at how ChangeArtifact (delta) implements JSON serialization
    - Decide: to_dict() methods vs dedicated formatters
  - **Files / Components**:
    - `supekku/scripts/lib/specs/registry.py`
    - `supekku/scripts/lib/decisions/registry.py`
    - `supekku/scripts/lib/changes/artifacts.py` (ChangeArtifact example)
    - `supekku/scripts/lib/formatters/change_formatters.py` (formatter example)
  - **Testing**: N/A (research task)
  - **Observations & AI Notes**: (to be filled during execution)
  - **Commits / References**: (to be filled during execution)

- **2.2 Write tests for show spec --json (TDD)**
  - **Design / Approach**:
    - Create test in `supekku/cli/test_cli.py::TestShowCommandJSON`
    - Test should verify JSON contains: id, name, status, kind, path, packages
    - Verify JSON is valid parseable structure
    - Test both PROD and SPEC kinds
  - **Files / Components**: `supekku/cli/test_cli.py`
  - **Testing**: Tests should FAIL initially (TDD)
  - **Observations & AI Notes**: (to be filled)
  - **Commits / References**: (to be filled)

- **2.3 Implement Spec JSON serialization**
  - **Design / Approach**:
    - Option A: Add `to_dict()` method to Spec class
    - Option B: Create `format_spec_details_json()` formatter function
    - Follow pattern that delta uses (likely formatter approach)
  - **Files / Components**:
    - Spec model or `supekku/scripts/lib/formatters/spec_formatters.py`
  - **Testing**: Tests from 2.2 should now PASS
  - **Observations & AI Notes**: (to be filled)
  - **Commits / References**: (to be filled)

- **2.4 Update show spec to use JSON serialization**
  - **Design / Approach**:
    - Modify `supekku/cli/show.py:50-52` to use proper serialization
    - Remove fallback to `{"id": spec.id}`
    - Call formatter or to_dict() method
  - **Files / Components**: `supekku/cli/show.py` lines 35-60
  - **Testing**: Run tests to confirm
  - **Observations & AI Notes**: (to be filled)
  - **Commits / References**: (to be filled)

- **2.5 Write tests for show adr --json (TDD)**
  - **Design / Approach**:
    - Create test verifying show adr returns full DecisionRecord data
    - Test should verify JSON contains: id, title, status, created, updated, decided, reviewed
    - Test should NOT crash
  - **Files / Components**: `supekku/cli/test_cli.py`
  - **Testing**: Should FAIL initially (currently crashes)
  - **Observations & AI Notes**: (to be filled)
  - **Commits / References**: (to be filled)

- **2.6 Implement DecisionRecord to_dict()**
  - **Design / Approach**:
    - Add `to_dict()` method to DecisionRecord class
    - Handle date serialization properly (convert datetime to string)
    - Include all relevant fields: id, title, status, created, updated, decided, reviewed, tags
  - **Files / Components**: `supekku/scripts/lib/decisions/registry.py`
  - **Testing**: Tests from 2.5 should PASS
  - **Observations & AI Notes**: (to be filled)
  - **Commits / References**: (to be filled)

- **2.7 Update show adr to use JSON serialization**
  - **Design / Approach**:
    - The hasattr check at line 168 should now work properly
    - Verify no crashes and full output
  - **Files / Components**: `supekku/cli/show.py` lines 151-178
  - **Testing**: Manual test + automated test
  - **Observations & AI Notes**: (to be filled)
  - **Commits / References**: (to be filled)

- **2.8-2.10: Policy/Standard commands**
  - Same pattern as ADR implementation
  - May skip if no policies/standards exist in repo yet

- **2.11 Run full test suite and linters**
  - **Commands**:
    - `just test` - all tests must pass
    - `just lint` - must pass with zero warnings
    - `just pylint` - score must not decrease
  - **Testing**: Regression testing
  - **Observations & AI Notes**: (to be filled)
  - **Commits / References**: (to be filled)

- **2.12 Manual validation**
  - **Commands**: See Verification section above
  - **Testing**: Manual smoke test of all show commands
  - **Observations & AI Notes**: (to be filled)
  - **Commits / References**: (to be filled)

- **2.13 Update coverage block**
  - **Files**: `specify/product/PROD-010/PROD-010.md` lines 175-181
  - **Change**: Update VT-PROD010-JSON-002 status from "in-progress" to "verified"
  - **Testing**: N/A
  - **Observations & AI Notes**: (to be filled)
  - **Commits / References**: (to be filled)

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Adding to_dict() breaks existing code | Comprehensive test coverage; grep for existing usage of these models | Not started |
| JSON schema inconsistency confuses agents | Follow consistent pattern across all show commands; document schema | Not started |
| Date serialization issues (datetime objects) | Use isoformat() or str() for dates; test with various date fields | Not started |
| Performance impact from serialization | Measure performance; keep serialization simple | Low priority |

## 9. Decisions & Outcomes

- `2025-01-04` - Created phase sheet to complete FR-002 based on investigation findings
- `2025-01-04` - Decision: Add `to_dict(root)` method to Spec model rather than creating dedicated formatter. Matches pattern used by DecisionRecord/PolicyRecord/StandardRecord.
- `2025-01-04` - Fixed all show commands (spec/adr/policy/standard) by properly calling `to_dict(repo_root)` instead of using problematic hasattr() fallback
- `2025-01-04` - Phase completed successfully - all tests passing, linters clean

## 10. Findings / Research Notes

**From Investigation (2025-01-04)**:

Current state of show commands:
```bash
# ✅ Working correctly
show delta --json      # Uses format_delta_details_json() formatter
show requirement --json  # Proper structured output

# ❌ Broken - returns minimal JSON
show spec --json       # Returns only {"id": "PROD-010"}
# Code: show.py:51 falls back to {"id": spec.id}

# ❌ Broken - crashes
show adr --json        # AttributeError: DecisionRecord has no to_dict()
# Code: show.py:168 tries decision.to_dict() but method doesn't exist

# ❓ Unknown - likely same pattern as spec/adr
show policy --json     # Probably incomplete/broken
show standard --json   # Probably incomplete/broken
```

**Code Pattern Analysis**:

Working pattern (show delta):
```python
if json_output:
    typer.echo(format_delta_details_json(artifact, root=root))
```

Broken pattern (show spec/adr/policy/standard):
```python
if json_output:
    output = obj.to_dict() if hasattr(obj, "to_dict") else {"id": obj.id}
    typer.echo(json.dumps(output, indent=2))
```

The hasattr() check is defensive but fails because:
- Spec lacks to_dict() → fallback to minimal {"id": ...}
- DecisionRecord lacks to_dict() → crashes when hasattr returns False incorrectly

**Recommended Approach**:
Option A: Add to_dict() methods to model classes (simpler, more portable)
Option B: Create dedicated formatters (more separation of concerns, follows delta pattern)

Lean toward Option A unless models are complex or used in many places.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] PROD-010 coverage block updated to mark FR-002 as "verified"
- [x] IP-009 plan updated and marked as completed
- [x] DE-009 delta status marked as "completed"
- [x] Tests passing (`just test` - 92/92 passing)
- [x] Linters clean (`just lint` passed, `just pylint` 9.67/10)
- [ ] No uncommitted changes (pending commit)
