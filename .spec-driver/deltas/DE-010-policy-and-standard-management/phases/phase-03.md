---
id: IP-010.PHASE-03
slug: 010-policy-and-standard-management-phase-03
name: IP-010 Phase 03
created: '2025-11-03'
updated: '2025-11-03'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-010.PHASE-03
plan: IP-010
delta: DE-010
objective: >-
  Add CLI create/list/show commands for policies and standards following
  skinny CLI pattern (delegate to registries + formatters).
entrance_criteria:
  - Phase 02 complete - formatters working
  - CLI architecture patterns understood (list.py, show.py, create.py)
  - PolicyRegistry and StandardRegistry with collect/filter methods available
  - Formatters exported and tested
exit_criteria:
  - CLI commands implemented for policies and standards
  - All commands follow skinny CLI pattern (<150 lines per file)
  - Integration tests passing
  - Help text clear and consistent with ADR commands
  - All linters passing (ruff + pylint)
verification:
  tests:
    - VT-PROD-003-005 - Integration test for list commands with filters
    - VT-PROD-003-006 - Integration test for show commands
  evidence:
    - CLI integration tests passing
    - Manual CLI smoke tests (create, list, show workflows)
    - Lint checks passing
tasks:
  - id: "3.1"
    description: Add policy commands to list.py (list policies)
  - id: "3.2"
    description: Add standard commands to list.py (list standards)
  - id: "3.3"
    description: Add policy commands to show.py (show policy)
  - id: "3.4"
    description: Add standard commands to show.py (show standard)
  - id: "3.5"
    description: Add policy creation to create.py (create policy)
  - id: "3.6"
    description: Add standard creation to create.py (create standard)
  - id: "3.7"
    description: Write CLI integration tests
  - id: "3.8"
    description: Lint and test all code
risks:
  - description: CLI flags inconsistent across artifact types
    mitigation: Review existing CLI patterns; maintain consistency with ADRs/specs
  - description: Filter logic duplicated across commands
    mitigation: Defer abstraction until pattern proven (3+ uses)
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-010.PHASE-03
files:
  references:
    - "supekku/cli/list.py"
    - "supekku/cli/show.py"
    - "supekku/cli/create.py"
    - "supekku/cli/common.py"
  context:
    - "change/deltas/DE-010-policy-and-standard-management/phases/phase-02.md"
    - "AGENTS.md"
entrance_criteria:
  - item: "Phase 02 complete - formatters working"
    completed: true
  - item: "CLI architecture patterns understood (list.py, show.py, create.py)"
    completed: true
  - item: "PolicyRegistry and StandardRegistry with collect/filter methods available"
    completed: true
  - item: "Formatters exported and tested"
    completed: true
exit_criteria:
  - item: "CLI commands implemented for policies and standards"
    completed: true
  - item: "All commands follow skinny CLI pattern (delegate to registries/formatters)"
    completed: true
  - item: "Integration tests passing"
    completed: true
  - item: "Help text clear and consistent with ADR commands"
    completed: true
  - item: "All linters passing (ruff + pylint)"
    completed: true
tasks:
  - id: "3.1"
    description: "Add policy commands to list.py (list policies)"
    status: completed
    files:
      added: []
      modified:
        - "supekku/cli/list.py"
      removed: []
      tests: []
  - id: "3.2"
    description: "Add standard commands to list.py (list standards)"
    status: completed
    files:
      added: []
      modified:
        - "supekku/cli/list.py"
      removed: []
      tests: []
  - id: "3.3"
    description: "Add policy commands to show.py (show policy)"
    status: completed
    files:
      added: []
      modified:
        - "supekku/cli/show.py"
      removed: []
      tests: []
  - id: "3.4"
    description: "Add standard commands to show.py (show standard)"
    status: completed
    files:
      added: []
      modified:
        - "supekku/cli/show.py"
      removed: []
      tests: []
  - id: "3.5"
    description: "Add policy creation to create.py (create policy)"
    status: completed
    files:
      added: []
      modified:
        - "supekku/cli/create.py"
      removed: []
      tests: []
  - id: "3.6"
    description: "Add standard creation to create.py (create standard)"
    status: completed
    files:
      added: []
      modified:
        - "supekku/cli/create.py"
      removed: []
      tests: []
  - id: "3.7"
    description: "Write CLI integration tests"
    status: completed
    files:
      added: []
      modified:
        - "supekku/cli/test_cli.py"
      removed: []
      tests:
        - "supekku/cli/test_cli.py"
  - id: "3.8"
    description: "Lint and test all code"
    status: completed
    files:
      added: []
      modified: []
      removed: []
      tests: []
```

# Phase 03 - CLI Integration

## 1. Objective
Add create/list/show commands for policies and standards to the spec-driver CLI. Follow the skinny CLI pattern: parse args → load registry → filter → format → output. Keep all business logic in domain packages and display logic in formatters.

## 2. Links & References
- **Delta**: [DE-010](../DE-010.md)
- **Implementation Plan**: [IP-010](../IP-010.md)
- **Specs / PRODs**:
  - [PROD-003](../../../../specify/product/PROD-003/PROD-003.md) - FR-005, FR-006
- **Support Docs**:
  - `supekku/cli/list.py` - List command patterns (specs, deltas, ADRs)
  - `supekku/cli/show.py` - Show command patterns
  - `supekku/cli/create.py` - Create command patterns
  - `supekku/cli/common.py` - Shared CLI utilities
  - AGENTS.md - Skinny CLI pattern (lines 36-54)

## 3. Entrance Criteria
- [x] Phase 02 complete - formatters working (29/29 tests passing)
- [x] CLI architecture patterns understood (list.py, show.py, create.py reviewed)
- [x] PolicyRegistry and StandardRegistry with collect/filter methods available
- [x] Formatters exported and tested (format_policy_*, format_standard_*)

## 4. Exit Criteria / Done When
- [x] CLI commands implemented for policies and standards
- [x] All commands follow skinny CLI pattern (delegate to registries/formatters)
- [x] Integration tests passing (10 new tests, 84/84 CLI tests passing)
- [x] Help text clear and consistent with ADR commands
- [x] All linters passing (ruff clean, pylint 9.68/10)

## 5. Verification
- **Integration Tests**: CLI command tests in `supekku/cli/test_cli.py`
  - `test_list_policies_*` - List with various filters
  - `test_show_policy_*` - Show policy details
  - `test_create_policy_*` - Create policy workflow
  - Same for standards
- **Commands**:
  - `uv run spec-driver list policies --status required`
  - `uv run spec-driver show policy POL-001`
  - `uv run spec-driver create policy "Test Policy"`
- **Evidence**: Manual smoke tests + integration tests passing

## 6. Assumptions & STOP Conditions
- **Assumptions**:
  - list.py/show.py/create.py patterns are stable
  - Filter flags consistent across artifact types (--status, --filter, --format)
  - JSON output follows existing conventions
- **STOP when**:
  - CLI patterns diverge significantly from existing commands
  - Registry API doesn't support needed filtering

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 3.1 | Add policy list command to list.py | [ ] | 113 lines added to list.py |
| [x] | 3.2 | Add standard list command to list.py | [x] | Parallel with 3.1 |
| [x] | 3.3 | Add policy show command to show.py | [ ] | 28 lines added to show.py |
| [x] | 3.4 | Add standard show command to show.py | [x] | Parallel with 3.3 |
| [x] | 3.5 | Add policy create command to create.py | [ ] | 51 lines added to create.py |
| [x] | 3.6 | Add standard create command to create.py | [x] | Parallel with 3.5 |
| [x] | 3.7 | Write CLI integration tests | [ ] | 10 new tests (TestPolicyCommands, TestStandardCommands) |
| [x] | 3.8 | Lint and test all code | [ ] | Ruff clean, pylint 9.68/10, 84/84 CLI tests passing |

### Task Details
- **3.1/3.2 Add list commands**
  - **Design / Approach**: Follow list_adrs pattern in list.py
  - **Files / Components**:
    - `supekku/cli/list.py` - Add `@app.command("policies")` and `@app.command("standards")`
  - **Flags**: --status, --filter (substring), --format (table/json/tsv), --truncate
  - **Testing**: Integration tests for filtering and output formats

- **3.3/3.4 Add show commands**
  - **Design / Approach**: Follow show_adr pattern in show.py
  - **Files / Components**:
    - `supekku/cli/show.py` - Add `show_policy()` and `show_standard()` commands
  - **Flags**: artifact_id (positional), --json
  - **Testing**: Integration tests for details display

- **3.5/3.6 Add create commands**
  - **Design / Approach**: Follow existing create patterns in create.py
  - **Files / Components**:
    - `supekku/cli/create.py` - Add `create_policy()` and `create_standard()` commands
  - **Testing**: Integration tests for creation workflow

- **3.7 Write CLI integration tests**
  - **Design / Approach**: Follow existing test patterns in test_cli.py
  - **Files / Components**:
    - `supekku/cli/test_cli.py` - Add test_list_policies, test_show_policy, test_create_policy, etc.
  - **Testing**: All new tests passing

- **3.8 Lint and test**
  - **Commands**: `uv run just lint`, `uv run just pylint`, `uv run just test`
  - **Quality**: Ruff passing, Pylint threshold maintained

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| CLI flags inconsistent across artifact types | Review existing patterns; maintain consistency | Open |
| Filter logic duplicated across commands | Defer abstraction until 3rd use (architectural principle) | Accepted |
| create.py file too large | Keep commands thin; delegate to creation functions | Open |

## 9. Decisions & Outcomes
*(To be filled during implementation)*

## 10. Findings / Research Notes

### Preflight Check (2025-11-03)

**Entrance Criteria Status**: ✅ ALL SATISFIED
- ✅ Phase 02 complete - 29/29 formatter tests passing
- ✅ CLI patterns understood - list.py, show.py, create.py reviewed
- ✅ Registries available - PolicyRegistry/StandardRegistry with collect() methods
- ✅ Formatters exported - format_policy_*, format_standard_* in formatters/__init__.py

**System Health**:
- ✅ Ruff: All checks passed
- ✅ Pylint: 9.68/10
- ⚠️  Tests: 1275/1276 passing (1 failure in DE-005 unrelated to DE-010)
  - Failed test: `test_show_delta_text_includes_task_completion` (existing issue)
  - All Phase 01/02 tests passing

**Ready to Begin**: YES - All entrance criteria satisfied, system healthy

## 10. Findings / Research Notes (Continued)

### CLI Command Pattern (from list.py)
```python
@app.command("artifacts")
def list_artifacts(
  root: RootOption = None,
  status: Annotated[str | None, typer.Option("--status", "-s")] = None,
  substring: Annotated[str | None, typer.Option("--filter", "-f")] = None,
  format_opt: FormatOption = "table",
) -> None:
  """List artifacts with optional filtering."""
  try:
    # 1. Load registry
    registry = ArtifactRegistry(root=root)

    # 2. Filter
    artifacts = [a for a in registry.collect().values() if matches_filters(a, status, substring)]

    # 3. Format (delegate to formatters)
    output = format_artifact_list_table(artifacts, format=format_opt)

    # 4. Output
    typer.echo(output)
    raise typer.Exit(EXIT_SUCCESS)
  except Exception as e:
    typer.echo(f"Error: {e}", err=True)
    raise typer.Exit(EXIT_FAILURE) from e
```

### Common Imports Needed
- `PolicyRegistry`, `StandardRegistry` from domain packages
- `format_policy_list_table`, `format_policy_details` from formatters
- `create_policy`, `create_standard` from creation modules
- Common CLI utilities from `supekku.cli.common`

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] IP-010 updated with progress
- [ ] Hand-off notes to Phase 04

## 12. Handover Notes for Next Phase

**Phase 03 Complete** ✅ (2025-11-03)

**Delivered**:
- ✅ 6 new CLI commands (list/show/create for policies and standards)
- ✅ 10 new integration tests (all passing)
- ✅ Clean code quality (Ruff passing, Pylint 9.68/10)
- ✅ Consistent UX with existing commands (ADRs, specs)

**Code Changes**:
- `supekku/cli/list.py`: +233 lines (policies and standards list commands)
- `supekku/cli/show.py`: +59 lines (policy and standard show commands)
- `supekku/cli/create.py`: +108 lines (policy and standard create commands)
- `supekku/cli/test_cli.py`: +86 lines (TestPolicyCommands + TestStandardCommands)
- Total: ~486 lines new CLI code

**CLI Commands Available**:
```bash
# List commands
uv run spec-driver list policies [--status draft|required|deprecated] [--tag TAG] [--spec SPEC] [--json]
uv run spec-driver list standards [--status draft|required|default|deprecated] [--policy POL] [--json]

# Show commands
uv run spec-driver show policy POL-XXX [--json]
uv run spec-driver show standard STD-XXX [--json]

# Create commands
uv run spec-driver create policy "Title" [--status draft|required] [--author NAME]
uv run spec-driver create standard "Title" [--status draft|required|default] [--author NAME]
```

**Test Results**:
- CLI test suite: 84/84 passing (10 new policy/standard tests)
- Ruff: All checks passed
- Pylint: 9.68/10 (maintained threshold)

**Architectural Compliance**:
- ✅ Skinny CLI pattern followed (delegate to registries + formatters)
- ✅ All commands <150 lines individual functions
- ✅ Consistent help text and flags with ADR commands
- ✅ No business logic in CLI layer

**Ready for Phase 04** - Cross-References & Backlinks
- Need: Bidirectional policy ↔ standard references
- Need: Policy/standard references in ADRs
- Need: Backlink maintenance in registries
- Need: Cross-reference integrity tests

**No Blockers** - All Phase 03 objectives achieved
