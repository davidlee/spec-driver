# Notes for DE-005

## Task 1.1 Complete (2025-11-02) ✓

Implemented `show template` command:
- Added to `supekku/cli/show.py:140-186`
- 8 tests passing (`supekku/cli/show_test.py`)
- Both linters 10/10
- Supports tech/product kinds, --json flag

## Task 1.2 Revised Approach (2025-11-02)

**IMPORTANT CHANGE**: Switched from template-matching to status-based detection

**Why**: User insight - all auto-generated specs are exactly 28 lines

**New approach**:
- Primary: Check `status == "stub"` in frontmatter
- Fallback: Line count ≤30 (pragmatic, handles human error)
- Much simpler, faster, no false positives

**Documentation**: See `STATUS-BASED-STUB-DETECTION.md` for full analysis

**Files updated**:
- `phases/phase-01.md` - Task 1.2 rewritten with new approach
- `STATUS-BASED-STUB-DETECTION.md` - Full rationale and implementation plan

## Design Revision (2025-11-02)

**Major simplification**: See `REVISED-DESIGN.md`

**Key Changes**:
- **Removed Task 1.3** (completion module) - agents handle intelligent completion
- **Simplified Task 1.4** (CLI) - just replaces body with template
- **Revised Task 1.5** (agent command) - orchestrates completion workflow

**Rationale**: CLI does mechanics, agent does intelligence. Simpler, more flexible, less brittle.

## Implementation Plan Updated

- IP-005: Sections 4-8 updated to reflect simplified design
- phase-01.md: All task details revised
- Task 1.1: Already complete ✓
- Task 1.2: Ready to implement (status + line count detection)
- Task 1.4: Simplified to body replacement only
- Task 1.5: Revised to agent-driven completion
- Task 1.6: Simplified integration testing

## Task 1.2 Complete (2025-11-02) ✓

Implemented stub detection:
- Added `supekku/scripts/lib/specs/detection.py`
- 7 tests passing (`supekku/scripts/lib/specs/detection_test.py`)
- Both linters 10/10
- Status-based primary check + line count fallback (≤30)
- Avoids strict frontmatter validation (parse manually with YAML)

## Task 1.4 Complete (2025-11-02) ✓

Implemented CLI backfill command:
- Added `supekku/cli/backfill.py` with simplified body replacement logic
- Registered in `supekku/cli/main.py`
- 2 tests passing (error handling + help text)
- Both linters 10/10
- Command working: `uv run spec-driver backfill spec SPEC-XXX`
- Preserves frontmatter, replaces body with template
- Fills spec_id, name, kind from frontmatter

## Next Steps

1. ✅ Task 1.2 (stub detection) - COMPLETE
2. ✅ Task 1.4 (CLI backfill command) - COMPLETE
3. Write Task 1.5 (agent command - revised)
4. Run Task 1.6 (integration testing)

---

## Handover Summary (2025-11-02)

### What's Complete

**Task 1.1 - Template Retrieval** ✅
- File: `supekku/cli/show.py` (lines 140-186)
- Tests: `supekku/cli/show_test.py` (8 tests passing)
- Quality: Both linters 10/10
- Command: `uv run spec-driver show template <kind>`

**Task 1.2 - Stub Detection** ✅
- Files:
  - `supekku/scripts/lib/specs/detection.py` (50 lines)
  - `supekku/scripts/lib/specs/detection_test.py` (7 tests passing)
- Quality: Both linters 10/10
- Logic: Status-based primary check + line count fallback (≤30)
- Key decision: Manual YAML parsing to avoid strict validation

**Task 1.4 - CLI Backfill Command** ✅
- Files:
  - `supekku/cli/backfill.py` (113 lines)
  - `supekku/cli/backfill_test.py` (2 tests passing)
  - `supekku/cli/main.py` (registered command)
- Quality: Both linters 10/10
- Command: `uv run spec-driver backfill spec SPEC-XXX [--force]`
- Behavior: Replaces body with template, preserves frontmatter, fills basic vars

### What's Remaining

**Task 1.5 - Agent Command** (Not Started)
- Create `.claude/commands/supekku.backfill.md`
- See `phases/phase-01.md` lines 329-397 for detailed spec
- Agent orchestrates: CLI reset → gather context → fill sections → validate
- Goal: ≤3 questions per spec, <10 min completion time

**Task 1.6 - Integration Testing** (Not Started)
- Manual end-to-end testing with real stub specs
- Verify full workflow: backfill → agent completion → validation
- See `phases/phase-01.md` lines 399-450 for test scenarios

### Architecture Summary

**Simplified Design** (see `REVISED-DESIGN.md`):
- **CLI** (Tasks 1.1, 1.2, 1.4): Mechanics - body replacement, stub detection
- **Agent** (Task 1.5): Intelligence - section completion, inference from contracts
- **Removed**: Task 1.3 (programmatic completion) - overengineered

### Key Files to Reference

- `REVISED-DESIGN.md` - Full design rationale
- `STATUS-BASED-STUB-DETECTION.md` - Stub detection approach
- `phases/phase-01.md` - Detailed task breakdown (lines 329-450 for remaining tasks)
- `IP-005.md` - Updated implementation plan

### Quality Gates Achieved

- ✅ All tests passing (17 total: 8+7+2)
- ✅ All linters 10/10 (ruff + pylint)
- ✅ CLI commands working and registered
- ✅ Design documented and rationale captured

### To Resume

1. Implement Task 1.5: Create agent command file following spec in phase-01.md
2. Execute Task 1.6: Manual integration testing per test scenarios
3. Update phase sheet and notes as tasks complete
4. Final validation: `just test && just lint && just pylint`
