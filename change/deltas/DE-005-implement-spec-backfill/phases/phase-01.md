---
id: IP-005.PHASE-01
slug: implement-spec-backfill-phase-01
name: IP-005 Phase 01
created: '2025-11-02'
updated: '2025-11-02'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-005.PHASE-01
plan: IP-005
delta: DE-005
objective: >-
  Implement simplified spec backfill: stub detection, CLI body replacement with template,
  and agent workflow. Agent handles intelligent completion. Batch mode deferred.
entrance_criteria:
  - PROD-007 complete and validated
  - Contracts generation working (via sync)
  - Task 1.1 (show template) complete
exit_criteria:
  - Stub detection logic implemented and tested
  - CLI backfill command replaces body with template
  - Agent command workflow functional
  - End-to-end backfill demonstrated
verification:
  tests:
    - VT-004
    - VT-005
    - VT-001
  evidence:
    - End-to-end workflow demonstration
    - Test suite passing
tasks:
  - Implement stub detection (1.2)
  - Build CLI backfill command (1.4 - simplified)
  - Write agent command (1.5 - revised)
  - Integration testing (1.6)
risks:
  - Stub detection false positives
  - Accidental overwrite of manual content
```

# Phase 01 - Core Backfill Implementation

## 1. Objective

Implement simplified single-spec backfill: CLI replaces stub body with template (mechanics), agent completes sections intelligently (intelligence). Batch mode deferred to Phase 02.

**Design Change (2025-11-02)**: See `REVISED-DESIGN.md` - removed Task 1.3 (completion module), simplified Task 1.4 (CLI just replaces body), revised Task 1.5 (agent does completion).

## 2. Links & References
- **Delta**: [DE-005](../DE-005.md)
- **Specs / PRODs**: PROD-007.FR-001, FR-002, FR-005, FR-006
- **Support Docs**:
  - PROD-001 (spec creation patterns)
  - `.claude/commands/supekku.specify.md` (similar agent command)
  - `supekku/templates/spec.md` (Jinja2 template)

## 3. Entrance Criteria
- [x] PROD-007 complete and validated
- [x] Contracts generation working (via sync)
- [x] SpecRegistry supports reading/writing specs (confirmed in `supekku/scripts/lib/specs/registry.py`)
- [x] Template rendering infrastructure exists (confirmed: `supekku/templates/spec.md` with Jinja2)

## 4. Exit Criteria / Done When
- [x] `spec-driver show template <kind>` returns valid template markdown (Task 1.1 complete)
- [ ] Stub detection correctly identifies stub vs. modified specs (Task 1.2)
- [ ] `spec-driver backfill spec SPEC-123` replaces body with template (Task 1.4)
- [ ] `/supekku.backfill SPEC-123` agent workflow completes single spec end-to-end (Task 1.5)
- [ ] All unit tests passing (`just test`)
- [ ] Both linters passing (`just lint` + `just pylint`)

## 5. Verification
- **Unit tests**: `supekku/scripts/lib/specs/completion_test.py`, `supekku/cli/backfill_test.py`
- **Integration test**: End-to-end workflow with real stub spec
- **Commands**:
  ```bash
  just test  # All tests
  just lint  # Ruff + pylint
  uv run spec-driver show template tech  # Manual verification
  ```
- **Evidence**: Successful backfill of PROD-007 itself (dogfooding)

## 6. Assumptions & STOP Conditions
- **Assumptions**:
  - Template structure stable (no breaking changes during implementation)
  - Contracts available for test specs
  - Agent has file read/write permissions
- **STOP when**:
  - Stub detection shows >5% false positive rate in testing
  - Template rendering fails for existing specs
  - Manual content overwrite occurs in testing

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[REMOVED]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Add `show template` command to CLI | [x] | Complete: 8 tests passing, both linters 10/10 |
| [x] | 1.2 | Implement stub detection logic | [x] | Complete: 7 tests passing, both linters 10/10 |
| [REMOVED] | 1.3 | Create completion module | N/A | Removed - agent does completion, not code |
| [x] | 1.4 | Build CLI `backfill spec` command (SIMPLIFIED) | [x] | Complete: 2 tests passing, both linters 10/10 |
| [x] | 1.5 | Write agent command (REVISED) | [x] | Complete: `.claude/commands/supekku.backfill.md` created |
| [x] | 1.5.1 | Set auto-created specs to status='stub' | [x] | Complete: sync_specs.py:114 + orphan messages fixed |
| [ ] | 1.5.2 | Migrate existing stub specs | [ ] | Update draft specs ≤30 lines to status='stub' |
| [ ] | 1.5.3 | Add stub status theming to formatters | [ ] | Mid-grey color for stub status in list output |
| [ ] | 1.6 | Integration testing | [ ] | Final validation |

### Task Details

**1.1 Add `show template` command**
- **Design**: Add subcommand to `supekku/cli/show.py`: `@app.command("template")`
- **Files**:
  - `supekku/cli/show.py` - Add command function
  - `supekku/cli/show_test.py` - Add test cases
- **Implementation Details**:
  1. Function signature: `show_template(kind: Annotated[str, typer.Argument(help="Spec kind: tech or product")])`
  2. Load template from `supekku/templates/spec.md` using Jinja2 Environment
  3. Render template with only `kind` variable set, other variables as placeholder strings
  4. Return rendered markdown to stdout
  5. Add `--json` flag for machine-readable output (returns `{"kind": str, "template": str}`)
  6. Error handling: InvalidKind, TemplateNotFound
- **Dependencies**:
  - Jinja2 (already in project)
  - Template path resolution via repo root
- **Testing**:
  - Unit test: `test_show_template_tech()` - verify tech template returned
  - Unit test: `test_show_template_product()` - verify product template with conditionals
  - Unit test: `test_show_template_invalid_kind()` - expect error
  - Unit test: `test_show_template_json_output()` - verify JSON structure
- **Acceptance**:
  - `uv run spec-driver show template tech` outputs valid markdown
  - `uv run spec-driver show template product` outputs valid markdown
  - Both outputs match expected template structure

**1.2 Implement stub detection**
- **Design**: Status-based detection with line-count fallback (REVISED 2025-11-02)
- **Files**:
  - `supekku/scripts/lib/specs/detection.py` - New module
  - `supekku/scripts/lib/specs/detection_test.py` - Tests
- **Implementation Details**:
  1. `is_stub_spec(spec_path: Path) -> bool`:
     - Primary: Check `status == "stub"` in frontmatter
     - Fallback: Line count ≤30 (accounts for human error/typos)
     - Return True if either condition met
  2. Rationale (see `STATUS-BASED-STUB-DETECTION.md`):
     - Empirical: All auto-generated tech specs = 28 lines
     - Real edits add significant content (356+ lines observed)
     - Much simpler than template-matching approach
     - Fast: O(1) file read vs Jinja2 rendering
- **Implementation**:
  ```python
  def is_stub_spec(spec_path: Path) -> bool:
      """Detect if spec is a stub based on status and line count."""
      frontmatter, _ = load_validated_markdown_file(spec_path)

      # Primary: explicit stub status
      if frontmatter.get("status") == "stub":
          return True

      # Fallback: line count for legacy/human-error tolerance
      total_lines = spec_path.read_text().count('\n') + 1
      return total_lines <= 30
  ```
- **Testing**:
  - Test: `test_is_stub_spec_status_stub()` - status="stub" → True
  - Test: `test_is_stub_spec_line_count()` - 28 lines → True
  - Test: `test_is_stub_spec_modified()` - 200 lines → False
  - Test: `test_is_stub_spec_draft_long()` - status="draft", 100 lines → False
  - Test: `test_is_stub_spec_missing_file()` - FileNotFoundError
- **Acceptance**:
  - Works with existing specs (no migration needed)
  - Zero false positives on real specs (tested on specify/product/)
  - Fast execution (<1ms per check)
  - Simple, maintainable code

**1.3 Create completion module** [REMOVED]
- **Reason**: Overengineered - agents can complete specs better than programmatic logic
- **Replacement**: Agent command (Task 1.5) handles intelligent completion
- **Design Change**: CLI does mechanics (Task 1.4), agent does intelligence (Task 1.5)

**~~Original Design (archived for reference)~~**:
- **Design**: Core business logic module for spec completion
- **Files**:
  - `supekku/scripts/lib/specs/completion.py` - New module
  - `supekku/scripts/lib/specs/completion_test.py` - Tests
- **Data Models**:
  ```python
  @dataclass
  class CompletionResult:
      success: bool
      spec_id: str
      spec_path: Path
      sections_filled: list[str]  # e.g., ["section_3", "section_4"]
      errors: list[str]
      warnings: list[str]
      questions_asked: int

  @dataclass
  class ContractInfo:
      path: Path
      kind: str  # "function", "class", "method"
      name: str
      signature: str | None
      docstring: str | None
  ```
- **Implementation Details**:
  1. `complete_spec(spec_id: str, *, interactive: bool = True, root: Path | None = None) -> CompletionResult`:
     - Load spec from SpecRegistry
     - Verify it's a stub (optional check, can force)
     - Load contracts from `specify/{kind}/{spec_id}/contracts/`
     - Analyze contracts to extract: functions, classes, docstrings
     - Build completion context (what info is available)
     - Fill sections incrementally (preserving existing content)
     - Write back to spec file
     - Return result with summary
  2. `load_contracts(spec_id: str, kind: str, root: Path) -> list[ContractInfo]`:
     - Find contracts directory: `{root}/specify/{kind}/{spec_id}/contracts/`
     - Parse each `.md` file using markdown parser
     - Extract code blocks and structure
     - Return list of ContractInfo objects
  3. `parse_contract_file(path: Path) -> list[ContractInfo]`:
     - Parse markdown with code fences
     - Extract function/class signatures
     - Extract docstrings
     - Return structured info
  4. `fill_section_1(spec: Spec, contracts: list[ContractInfo]) -> str`:
     - Intent & Summary section
     - Infer scope from contract names
     - Build value signals from docstrings
     - Return filled section markdown
  5. `fill_section_3_requirements(spec: Spec, contracts: list[ContractInfo]) -> str`:
     - Functional Requirements
     - Generate FR-NNN from contract functions
     - Link to verification (planned)
     - Return requirements markdown
  6. Helper: `generate_yaml_blocks(spec_id: str, requirements: list[str]) -> dict[str, str]`:
     - Generate `spec.relationships` block
     - Generate `spec.capabilities` block
     - Generate `verification.coverage` block
     - Return dict of block_name -> yaml_string
- **Interactive Mode**:
  - Ask user for: scope boundaries, key behaviors, edge cases
  - Max 3 questions per spec
  - Use defaults if non-interactive
- **Testing Strategy**:
  - Unit tests with mocked contracts
  - Test each section filling function independently
  - Test YAML block generation
  - Test interactive vs non-interactive
  - Integration test with real contract files
- **Testing**:
  - Test: `test_complete_spec_success()` - full workflow with mocks
  - Test: `test_load_contracts()` - parse real contract files
  - Test: `test_parse_contract_file()` - extract functions/classes
  - Test: `test_fill_section_1()` - intent & summary generation
  - Test: `test_fill_section_3_requirements()` - FR generation from contracts
  - Test: `test_generate_yaml_blocks()` - valid YAML output
  - Test: `test_complete_spec_preserves_frontmatter()` - no FM changes
  - Test: `test_complete_spec_interactive_mode()` - question prompts
  - Test: `test_complete_spec_missing_contracts()` - graceful degradation
- **Acceptance**:
  - Can complete stub spec with contracts present
  - Preserves all frontmatter fields
  - Generates valid, parseable YAML blocks
  - Fills at least 4 major sections
  - Interactive mode asks ≤3 questions

**1.4 Build CLI backfill command** (SIMPLIFIED)
- **Design**: Replace stub spec body with fresh template (preserving frontmatter)
- **Philosophy**: CLI does mechanics only - agent handles intelligence (see Task 1.5)
- **Files**:
  - `supekku/cli/backfill.py` - New CLI module
  - `supekku/cli/backfill_test.py` - Tests
  - Update main CLI to register command
- **Command Structure**:
  ```python
  app = typer.Typer(help="Backfill incomplete specifications", no_args_is_help=True)

  @app.command("spec")
  def backfill_spec(
      spec_id: Annotated[str, typer.Argument(help="Spec ID to backfill")],
      force: Annotated[bool, typer.Option("--force", help="Force backfill even if modified")] = False,
      root: RootOption = None,
  ) -> None:
  ```
- **Implementation Details**:
  1. Load spec from SpecRegistry
  2. Check if spec exists → error if not
  3. Check if stub using `is_stub_spec()` (unless `--force`)
  4. If not stub and not force → error with helpful message
  5. Load template from `supekku/templates/spec.md`
  6. Render template with basic vars from frontmatter:
     - `spec_id` = spec.frontmatter["id"]
     - `name` = spec.frontmatter["name"]
     - `kind` = spec.frontmatter["kind"]
     - Leave YAML blocks as template boilerplate (agent fills these)
  7. Write spec: preserve frontmatter, replace body with rendered template
  8. Print success message with path
  9. Exit with SUCCESS/FAILURE
- **Output Format**:
  ```
  ✓ Backfilled SPEC-042: specify/tech/SPEC-042/SPEC-042.md
  ```
- **Error Messages**:
  - Spec not found: "Error: Specification not found: {spec_id}"
  - Not a stub: "Error: {spec_id} has been modified. Use --force to backfill anyway."
  - Template error: "Error: Failed to render template: {error_details}"
- **Testing**:
  - Test: `test_backfill_spec_stub_success()` - happy path with stub
  - Test: `test_backfill_spec_not_found()` - spec doesn't exist
  - Test: `test_backfill_spec_not_stub_no_force()` - requires --force
  - Test: `test_backfill_spec_force_override()` - --force works
  - Test: `test_backfill_spec_preserves_frontmatter()` - frontmatter unchanged
  - Test: `test_backfill_spec_fills_basic_vars()` - spec_id/name/kind filled
  - Test: `test_backfill_spec_template_error()` - handles template errors
- **Integration with Main CLI**:
  - Register in main CLI app
  - Verify command shows in `uv run spec-driver --help`
- **Acceptance**:
  - Command appears in help output
  - Replaces stub body with template
  - Preserves all frontmatter unchanged
  - Fills spec_id, name, kind from frontmatter
  - Modified spec requires --force
  - Error messages clear and actionable

**1.5 Write agent command** (REVISED)
- **Design**: Agent workflow orchestrating intelligent spec completion
- **Philosophy**: CLI resets spec to template (Task 1.4), agent fills sections intelligently
- **File**: `.claude/commands/supekku.backfill.md`
- **Structure**:
  1. **Front Matter**:
     ```yaml
     ---
     description: Backfill stub specifications with intelligent completion
     ---
     ```
  2. **Overview**:
     - Purpose: Complete auto-generated stub specs
     - When: After `spec-driver sync` generates stubs
     - How: CLI resets to template, agent completes sections using contracts/inference
  3. **Workflow Steps**:
     - Step 1: User specifies spec to backfill (SPEC-XXX)
     - Step 2: Run CLI to reset spec to template (`backfill spec SPEC-XXX`)
     - Step 3: Read the backfilled spec to understand structure
     - Step 4: Gather context (contracts, related specs, code if needed)
     - Step 5: Complete sections intelligently (ask ≤3 questions)
     - Step 6: Validate (`sync` + `validate`)
     - Step 7: Document evidence
  4. **Sections to Complete**:
     - Section 1: Intent & Summary
     - Section 3: Requirements (FR/NF)
     - Section 4: Architecture & Design
     - Section 6: Testing Strategy
     - YAML blocks: relationships, capabilities, verification
  5. **Intelligent Completion Guidelines**:
     - Prefer inferring from contracts over asking questions
     - Make reasonable assumptions (document them clearly)
     - Only ask user when decision significantly impacts design
     - Mark assumptions: "Assuming X based on Y"
     - Use contracts as primary source of truth
  6. **Quality Standards**:
     - [ ] All YAML blocks valid and parseable
     - [ ] Requirements testable and linked to capabilities
     - [ ] Architecture section has substance (not just placeholders)
     - [ ] Testing strategy concrete (not generic)
     - [ ] Assumptions documented where made
  7. **Final Checklist**:
     - [ ] CLI backfill executed successfully
     - [ ] Sections completed with substance
     - [ ] `uv run spec-driver sync` passed
     - [ ] `uv run spec-driver validate` passed
     - [ ] Evidence/decisions documented
- **Key Commands**:
  ```bash
  # Reset spec to template
  uv run spec-driver backfill spec SPEC-123

  # Force if needed
  uv run spec-driver backfill spec SPEC-123 --force

  # Validate completion
  uv run spec-driver sync
  uv run spec-driver validate
  ```
- **Testing**:
  - Manual test: Agent completes real stub spec end-to-end
  - Verify: ≤3 questions asked
  - Verify: Completed spec passes validation
  - Verify: Quality standards met
- **Acceptance**:
  - Command file complete and documented
  - Agent can successfully complete stub specs
  - Workflow efficient (≤10 min per spec)
  - Quality maintained (validation passes)

**1.5.1 Set auto-created specs to status='stub'**
- **Design**: Update sync code to mark auto-generated specs as stubs
- **Files**:
  - `supekku/scripts/sync_specs.py` - Change status field
  - `supekku/scripts/lib/specs/creation.py` - Verify manual creation unchanged
- **Implementation Details**:
  1. In `sync_specs.py:_create_spec_directory_and_file()` (line ~114):
     - Change: `"status": "draft"` → `"status": "stub"`
  2. Verify `creation.py:create_spec()` (line ~361):
     - Confirm: Keeps `"status": "draft"` for user-created specs
  3. Rationale:
     - Makes stub detection explicit and reliable
     - Aligns with backfill workflow expectations
     - Backward compatible via line count fallback in `is_stub_spec()`
- **Testing**:
  - Test: Run sync and verify new specs have `status: "stub"`
  - Test: Create manual spec and verify `status: "draft"`
  - Test: Existing detection tests still pass
- **Acceptance**:
  - Auto-generated specs land with `status: "stub"`
  - Manual specs still use `status: "draft"`
  - No test failures
  - Both linters pass

**1.5.2 Migrate existing stub specs**
- **Design**: One-time update of existing draft specs that are actually stubs
- **Approach**: Script to find and update specs matching stub criteria
- **Implementation Details**:
  1. Find all specs with `status: "draft"` AND ≤30 lines
  2. Update frontmatter to `status: "stub"`
  3. Preserve all other frontmatter fields
  4. Options considered:
     - A) Standalone migration script (chosen - explicit, auditable)
     - B) Sync flag `--migrate-stubs` (coupling concern)
     - C) Automatic during sync (risky, no user control)
- **Script Structure**:
  ```python
  # supekku/scripts/migrate_stub_status.py
  def migrate_stub_status():
    """Update draft specs ≤30 lines to status='stub'."""
    registry = SpecRegistry()
    migrated = []
    for spec in registry.all_specs():
      if spec.status == "draft" and is_stub_spec(spec.path):
        # Update frontmatter status to "stub"
        # Write back to file
        migrated.append(spec.id)
    return migrated
  ```
- **Testing**:
  - Test on a copy of existing specs
  - Verify only stubs are migrated
  - Verify frontmatter preservation
  - Check no corruption
- **Acceptance**:
  - All ≤30 line draft specs updated to stub
  - Longer draft specs unchanged
  - Migration script output documented
  - Can be run idempotently

**1.5.3 Add stub status theming to formatters**
- **Design**: Visual distinction for stub status in CLI list output
- **Files**:
  - `supekku/scripts/lib/formatters/spec_formatters.py` - Add color logic
  - Test file for formatter (if exists)
- **Implementation Details**:
  1. Research existing status colors in formatter
  2. Add stub status styling: mid-grey (ANSI color code or rich styling)
  3. Maintain consistency with other status colors
  4. Example:
     ```python
     STATUS_COLORS = {
       "stub": "bright_black",  # mid-grey
       "draft": "yellow",
       "accepted": "green",
       # ... etc
     }
     ```
- **Testing**:
  - Test: Visual output with stub specs
  - Test: Color codes correct
  - Test: Works in different terminals
  - Test: Formatter tests pass
- **Acceptance**:
  - Stub status shows in mid-grey
  - Other status colors unchanged
  - Output readable and consistent
  - Tests and linters pass

**1.6 Integration testing & dogfooding**
- **Purpose**: Validate entire workflow with real data
- **Approach**:
  1. **Setup Test Fixtures**:
     - Create or identify real stub spec for testing
     - Ensure contracts exist for test spec
     - Document initial state
  2. **End-to-End Test**:
     - Run: `uv run spec-driver show template tech`
     - Run: `uv run spec-driver backfill spec SPEC-XXX`
     - Verify: Spec file updated
     - Verify: Frontmatter preserved
     - Verify: Sections filled
     - Verify: YAML blocks valid
     - Run: `uv run spec-driver sync`
     - Run: `uv run spec-driver validate`
  3. **Dogfooding**:
     - Select real stub spec in project (or create one)
     - Run full backfill workflow
     - Document before/after comparison
     - Capture evidence (screenshots, diffs)
  4. **Integration Test Code**:
     - Add to test suite: `test_backfill_integration.py`
     - Test full workflow programmatically
     - Mock user input for interactive mode
     - Verify all components work together
- **Test Scenarios**:
  - Scenario 1: Stub spec with contracts → successful backfill
  - Scenario 2: Modified spec without --force → error
  - Scenario 3: Missing contracts → partial completion with warnings
  - Scenario 4: Interactive mode → questions asked and answered
  - Scenario 5: JSON output → parseable and complete
- **Evidence to Collect**:
  - Before/after diff of backfilled spec
  - CLI output showing progress
  - Validation results
  - Test suite results
  - Manual testing checklist
- **Acceptance**:
  - End-to-end test passes in CI
  - Real spec successfully backfilled (documented)
  - All quality gates passed:
    - `just test` → all passing
    - `just lint` → zero warnings
    - `just pylint` → threshold maintained
  - Evidence documented in phase wrap-up

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Stub detection false positives | Exact string matching; comprehensive test suite | Not started |
| Template rendering varies by environment | Pin Jinja2 version; test on multiple systems | Not started |
| Performance issues with large specs | Optimize string comparison; benchmark | Not started |

## 9. Decisions & Outcomes

- `2025-11-02` - CLI command named `backfill` (vs `complete` or `fill`) - clearer intent
- `2025-11-02` - Stub detection uses status + line count (vs template matching) - simpler, safer, faster
- `2025-11-02` - Agent command created: `.claude/commands/supekku.backfill.md` - comprehensive workflow guide
- `2025-11-02` - Fixed backfill.py exit code issue (removed explicit EXIT_SUCCESS raise, let normal return = 0)
- `2025-11-02` - Fixed backfill.py frontmatter handling (use `.data` property, convert mappingproxy to dict)

## 10. Findings / Research Notes

**Confirmed Infrastructure**:
- Template: `supekku/templates/spec.md` (unified for both product and tech via `{% if kind == 'prod' %}`)
  - Variables: `spec_id`, `name`, `kind`, plus YAML block variables
  - No separate product template needed
- SpecRegistry: `supekku/scripts/lib/specs/registry.py`
  - Full read/write support via `load_validated_markdown_file()`
  - Returns `Spec` model with `id`, `path`, `frontmatter`, `body`
- Contracts location: `specify/{kind}/{spec-id}/contracts/*.md`
- CLI pattern: Typer with thin orchestration, `RootOption`, standard error handling
- Agent command pattern: Structured workflow with quality gates (see `supekku.specify.md`)

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored (test results, dogfooding screenshots)
- [ ] DE-005 delta updated with implementation notes
- [ ] PROD-007 updated if requirements clarified during implementation
- [ ] Hand-off notes for Phase 02 (batch mode implementation)
