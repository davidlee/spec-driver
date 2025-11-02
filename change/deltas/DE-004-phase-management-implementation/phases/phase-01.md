---
id: IP-004.PHASE-01
slug: phase-management-implementation-phase-01
name: IP-004 Phase 01
created: '2025-11-02'
updated: '2025-11-02'
status: in-progress
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-004.PHASE-01
plan: IP-004
delta: DE-004
name: Phase 01 - Create Phase Command
objective: >-
  Implement `create phase` command with auto-numbering, metadata population,
  and template rendering. Covers core phase creation logic.
entrance_criteria:
  - DE-004 delta approved
  - PROD-006 spec reviewed
exit_criteria:
  - create_phase() function implemented in creation.py
  - CLI command wired in cli/create.py
  - VT-PHASE-001, VT-PHASE-002, VT-PHASE-004 passing
  - Manual test - create phase for IP-002 works
verification:
  tests:
    - VT-PHASE-001
    - VT-PHASE-002
    - VT-PHASE-004
  evidence:
    - Test output showing all tests passing
    - Manual test creating phase for IP-002
    - Lint output (ruff + pylint) passing
tasks:
  - Implement create_phase() function
  - Add CLI command in create.py
  - Write comprehensive unit tests
  - Test with real implementation plan
risks:
  - Phase numbering logic may be complex
  - Template rendering may need escaping
```

# Phase 01 - Create Phase Command

## 1. Objective

Implement the core `spec-driver create phase` command that enables automated phase creation with:
- Auto-incrementing phase numbering (PHASE-01, PHASE-02, ...)
- Automatic metadata population (phase ID, plan ID, delta ID)
- Template rendering with variable substitution
- Error handling for invalid inputs

## 2. Links & References
- **Delta**: DE-004
- **Plan**: IP-004
- **Specs / PRODs**: PROD-006 (all requirements, focus on FR-001, FR-002, FR-004)
- **Requirements**:
  - PROD-006.FR-001 - Create phase files from template
  - PROD-006.FR-002 - Auto-determine next phase number
  - PROD-006.FR-004 - Auto-populate metadata
- **Support Docs**:
  - Existing pattern: `create_delta()` in `supekku/scripts/lib/changes/creation.py`
  - Template: `supekku/templates/phase.md`
  - Schema: `spec-driver schema show phase.overview`

## 3. Entrance Criteria
- [x] DE-004 delta created and reviewed
- [x] PROD-006 spec complete and synced
- [x] IP-004 plan detailed with 3 phases
- [x] Research complete on existing creation patterns

## 4. Exit Criteria / Done When
- [ ] `create_phase()` function exists in `supekku/scripts/lib/changes/creation.py`
- [ ] CLI command `phase` added to `supekku/cli/create.py`
- [ ] VT-PHASE-001 passing (phase creation unit tests)
- [ ] VT-PHASE-002 passing (auto-numbering tests)
- [ ] VT-PHASE-004 passing (metadata population tests)
- [ ] Manual test: `spec-driver create phase "Test Phase" --plan IP-002` works
- [ ] All existing tests still passing
- [ ] `just lint` and `just pylint` passing

## 5. Verification

**VT-PHASE-001: Phase Creation Unit Tests**
- Location: `supekku/scripts/lib/changes/creation_test.py` (new file or enhance existing)
- Tests:
  - `test_create_phase_first_in_sequence()` → creates phase-01.md
  - `test_create_phase_with_metadata()` → frontmatter valid
  - `test_create_phase_invalid_plan()` → raises error
  - `test_create_phase_empty_name()` → raises error
- Command: `uv run pytest supekku/scripts/lib/changes/creation_test.py::test_create_phase* -v`

**VT-PHASE-002: Auto-Numbering Tests**
- Same location as VT-PHASE-001
- Tests:
  - `test_phase_numbering_starts_at_01()`
  - `test_phase_numbering_increments()`
  - `test_phase_numbering_with_gaps()` → warns but succeeds
- Command: Same pytest command, different test names

**VT-PHASE-004: Metadata Population Tests**
- Same location
- Tests:
  - `test_phase_id_format()` → matches `IP-XXX.PHASE-NN`
  - `test_plan_id_from_flag()`
  - `test_delta_id_from_plan()`
  - `test_name_from_argument()`
- Command: Same pytest command

**Full Test Suite**: `just test`
**Linters**: `just lint` + `just pylint`

## 6. Assumptions & STOP Conditions

**Assumptions**:
- Template at `supekku/templates/phase.md` is correct structure
- Plan documents always have `delta:` field in frontmatter
- Phase directory is always `{delta_dir}/phases/`
- Phase numbering always starts at 01, zero-padded two digits
- Existing `create_delta()` pattern is good reference

**STOP Conditions**:
- STOP if template rendering requires major refactoring
- STOP if plan lookup logic is significantly complex (escalate design review)
- STOP if test framework doesn't support filesystem fixtures easily

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [WIP] | 1.1 | Research existing create_delta pattern | [ ] | Reading creation.py |
| [ ] | 1.2 | Implement create_phase() function | [ ] | Depends on 1.1 |
| [ ] | 1.3 | Add phase CLI command | [x] | Can start with 1.2 |
| [ ] | 1.4 | Write VT-PHASE-001 tests | [x] | Can start with 1.2 |
| [ ] | 1.5 | Write VT-PHASE-002 tests | [x] | Can start with 1.2 |
| [ ] | 1.6 | Write VT-PHASE-004 tests | [x] | Can start with 1.2 |
| [ ] | 1.7 | Run full test suite | [ ] | Final gate |
| [ ] | 1.8 | Manual test with IP-002 | [ ] | Final verification |

### Task Details

**1.1 Research Existing Patterns**
- **Design / Approach**: Read `create_delta()` to understand:
  - How it finds delta directory
  - How it renders templates
  - How it populates metadata
  - Error handling patterns
- **Files / Components**: `supekku/scripts/lib/changes/creation.py`
- **Testing**: N/A (research only)
- **Observations & AI Notes**: [To be filled]

**1.2 Implement create_phase() Function**
- **Design / Approach**:
  - Function signature: `create_phase(name: str, plan_id: str, root: Path | None = None) -> PhaseCreationResult`
  - Steps:
    1. Find plan document by plan_id
    2. Read plan frontmatter to get delta_id
    3. Find delta directory
    4. Scan `phases/` directory for existing phases
    5. Determine next phase number (parse filenames, find max, increment)
    6. Generate phase ID: `{plan_id}.PHASE-{number:02d}`
    7. Render template with variables
    8. Write phase file to `{delta_dir}/phases/phase-{number:02d}.md`
    9. Return result with phase_id and file_path
- **Files / Components**:
  - `supekku/scripts/lib/changes/creation.py` - new function
  - Export in `supekku/scripts/lib/changes/__init__.py`
- **Testing**: Covered by tasks 1.4-1.6
- **Observations & AI Notes**: [To be filled]

**1.3 Add Phase CLI Command**
- **Design / Approach**: Follow existing `create_delta` pattern in `create.py`
  ```python
  @app.command("phase")
  def create_phase_cmd(
    name: Annotated[str, typer.Argument(help="Phase name")],
    plan: Annotated[str, typer.Option("--plan", help="Plan ID (e.g., IP-002)")],
    root: RootOption = None,
  ) -> None:
    """Create a new phase for an implementation plan."""
    try:
      result = create_phase(name, plan, root)
      typer.echo(f"Phase created: {result.phase_id}")
      typer.echo(str(result.phase_path))
      raise typer.Exit(EXIT_SUCCESS)
    except PhaseCreationError as e:
      typer.echo(f"Error creating phase: {e}", err=True)
      raise typer.Exit(EXIT_FAILURE) from e
  ```
- **Files / Components**: `supekku/cli/create.py`
- **Testing**: Manual test in task 1.8
- **Observations & AI Notes**: [To be filled]

**1.4-1.6 Write Test Suites**
- **Design / Approach**: Use pytest with temporary directory fixtures
  - Create temp directory structure
  - Create mock plan + delta documents
  - Call create_phase()
  - Assert file created with correct content
  - Test edge cases (errors, gaps, etc.)
- **Files / Components**: `supekku/scripts/lib/changes/creation_test.py`
- **Testing**: Self-contained verification
- **Observations & AI Notes**: [To be filled]

**1.7 Run Full Test Suite**
- **Testing**: `just test` (runs all tests including new ones)
- **Observations & AI Notes**: [To be filled]

**1.8 Manual Test with IP-002**
- **Design / Approach**:
  ```bash
  spec-driver create phase "Phase 04 - Manual Test" --plan IP-002
  # Verify phase-04.md created with correct metadata
  cat change/deltas/DE-002-.../phases/phase-04.md
  # Clean up test phase afterward
  rm change/deltas/DE-002-.../phases/phase-04.md
  ```
- **Observations & AI Notes**: [To be filled]

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Phase number parsing complex | Use simple regex, test edge cases | Pending |
| Template rendering escaping needed | Test with special chars in name | Pending |
| Plan lookup failure modes | Clear error messages, test invalid IDs | Pending |

## 9. Decisions & Outcomes
- `2025-11-02` - Phase numbering: zero-padded two digits (PHASE-01, not PHASE-1)
- `2025-11-02` - Gaps in numbering: warn but allow (flexibility over strictness)
- `2025-11-02` - Function location: `creation.py` (alongside create_delta)

## 10. Findings / Research Notes
[To be filled as research progresses]

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] All tests passing (VT-PHASE-001, VT-PHASE-002, VT-PHASE-004)
- [ ] Linters passing (ruff + pylint)
- [ ] Manual test successful
- [ ] Code committed with clear message
- [ ] IP-004 plan updated with progress
- [ ] Hand-off notes: Phase 02 can begin (formatter + validation)
