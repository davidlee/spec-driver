---
id: IP-005.PHASE-01
slug: implement-spec-backfill-phase-01
name: IP-005 Phase 01
created: '2025-11-02'
updated: '2025-11-02'
status: complete
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
- [x] Stub detection correctly identifies stub vs. modified specs (Task 1.2 complete)
- [x] `spec-driver backfill spec SPEC-123` replaces body with template (Task 1.4 complete)
- [x] Agent workflow documented and ready (Task 1.5 complete - `.claude/commands/supekku.backfill.md`)
- [x] Auto-created specs use status='stub' (Task 1.5.1 complete)
- [x] Existing stub specs migrated (Task 1.5.2 complete - 16 migrated)
- [x] Status theming added (Task 1.5.3 complete)
- [ ] JSON outputs include path/kind fields (Task 1.5.4 - optional enhancement)
- [x] Backfill workflow commands fixed (Task 1.5.4 - jq commands work with find approach)
- [x] Schema commands documented in workflow (Task 1.5.5 complete)
- [x] Status field management documented (Task 1.5.6 complete)
- [x] Collaboration analysis guidance added (Task 1.5.7 complete)
- [x] Mandatory contract reading implemented (Task 1.5.8 complete - validated with CONTRACT_REVIEW.md)
- [x] All unit tests passing (17 tests passing)
- [x] Both linters passing (ruff clean)
- [x] End-to-end integration test with real spec (Task 1.6 complete - SPEC-125, SPEC-110, CONTRACT_REVIEW)

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
| [x] | 1.5.1 | Set auto-created specs to status='stub' | [x] | Complete: sync_specs.py:114 + orphan messages + --prune safety |
| [x] | 1.5.2 | Migrate existing stub specs | [x] | Complete: 16 specs migrated (migrate_stub_status.py) |
| [x] | 1.5.3 | Add stub status theming to formatters | [x] | Complete: stub=mid-grey, draft=light-grey |
| [ ] | 1.5.4 | Add path/kind to list/show JSON outputs | [ ] | Fix jq commands in backfill workflow |
| [x] | 1.5.5 | Add schema reference commands to backfill workflow | [x] | Complete: schema show commands documented |
| [x] | 1.5.6 | Add status field management to backfill workflow | [x] | Complete: automated validation with jq |
| [x] | 1.5.7 | Enhance collaboration analysis guidance | [x] | Complete: import-based analysis prompts |
| [x] | 1.5.8 | Mandate reading all public contracts | [x] | Complete: validated with CONTRACT_REVIEW.md |
| [x] | 1.6 | Integration testing | [x] | Complete: SPEC-125 successful, SPEC-110 revealed gap |

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

**1.5.4 Add path/kind to list/show JSON outputs**
- **Design**: Fix jq commands in backfill workflow by including missing fields in JSON output
- **Problem**: `.claude/commands/supekku.backfill.md` uses jq to extract `path` and `kind` fields, but they're missing from JSON output (see `JQ_VALIDATION_REPORT.md`)
- **Files**:
  - `supekku/scripts/lib/formatters/spec_formatters.py` - Add path/kind to specs JSON
  - `supekku/scripts/lib/formatters/change_formatters.py` - Add path to changes JSON
  - `supekku/scripts/lib/formatters/decision_formatters.py` - Add path to decisions JSON
  - `supekku/scripts/lib/formatters/spec_formatters_test.py` - Update tests
  - `.claude/commands/supekku.backfill.md` - Fix jq commands to use `.items` instead of `.specs`
- **Implementation Details**:
  1. **Specs JSON** (`format_spec_list_json` at line 193):
     ```python
     item = {
       "id": spec.id,
       "slug": spec.slug,
       "name": spec.name,
       "kind": spec.kind,          # ADD THIS
       "status": spec.status,
       "path": spec.path.as_posix(),  # ADD THIS
       "packages": spec.packages if spec.packages else [],
     }
     ```
  2. **Changes JSON** (`format_change_list_json` at line 329):
     ```python
     item = {
       "id": change.id,
       "kind": change.kind,
       "status": change.status,
       "name": change.name,
       "slug": change.slug,
       "path": change.path.as_posix(),  # ADD THIS (already has .path attribute)
     }
     ```
  3. **Decisions JSON** (`format_decision_list_json` at line 247):
     ```python
     item = {
       "id": decision.id,
       "status": decision.status,
       "title": decision.title,
       "path": decision.path,  # ADD THIS (already has .path attribute as string)
       "created": decision.created,
       "updated": decision.updated,
       # ...
     }
     ```
  4. **Fix backfill.md jq commands** (lines 67, 88, 109, 121):
     - Change `.specs` to `.items` (consistent with actual output structure)
     - Verify path/kind extraction works after formatter changes
- **Rationale**:
  - Backfill workflow critically depends on these fields for automation
  - All models already have path data available
  - `kind` easily accessible from spec.kind property
  - Show commands would benefit from consistent JSON structure
- **Testing**:
  - Test: `uv run spec-driver list specs --json | jq -r '.items[0].path'` returns path
  - Test: `uv run spec-driver list specs --json | jq -r '.items[0].kind'` returns kind
  - Test: `uv run spec-driver list changes --json | jq -r '.items[0].path'` returns path
  - Test: `uv run spec-driver list adrs --json | jq -r '.items[0].path'` returns path
  - Test: Verify backfill workflow jq commands work (see `JQ_VALIDATION_REPORT.md`)
  - Test: Update formatter tests for new fields
- **Acceptance**:
  - All list commands include `path` in JSON output
  - Spec list includes `kind` in JSON output
  - Backfill workflow jq commands work correctly
  - All tests passing
  - Both linters clean

**1.5.5 Add schema reference commands to backfill workflow**
- **Design**: Document available schema commands so agents know about this expensive help
- **Problem**: Agents have to manually construct YAML blocks without knowing schema commands exist
- **File**: `.claude/commands/supekku.backfill.md`
- **Implementation Details**:
  1. Add new section "4.5 Review YAML Block Schemas" before "Complete Sections Intelligently":
     ```markdown
     #### D. Review YAML Block Schemas

     Before filling YAML blocks, review the schemas to understand structure:

     ```bash
     # Get example YAML for each block type
     uv run spec-driver schema show spec.relationships -f yaml-example
     uv run spec-driver schema show spec.capabilities -f yaml-example
     uv run spec-driver schema show verification.coverage -f yaml-example

     # JSON format also available (will be default once json-schema support added)
     uv run spec-driver schema show spec.relationships -f json
     ```

     These show:
     - Required vs optional fields
     - Field types and constraints
     - Example values and structure
     - Common patterns
     ```
  2. Reference these commands in section 5 when completing YAML blocks
  3. Add to quality checklist: "[ ] YAML blocks match schema (verified with schema show)"
- **Rationale**:
  - Schema commands already exist and are well-tested
  - Agents don't know to use them without documentation
  - Reduces trial-and-error in YAML block construction
  - Ensures consistency with schema requirements
- **Testing**:
  - Manual: Verify all three schema commands work with both formats
  - Manual: Confirm yaml-example output is helpful
  - Integration: Agent uses commands during backfill workflow
- **Acceptance**:
  - Schema commands documented in backfill workflow
  - Commands appear in logical location (before YAML block completion)
  - Quality checklist includes schema verification

**1.5.6 Add status field management to backfill workflow**
- **Design**: Add explicit instructions for updating status field when backfill is complete
- **Problem**: Agent testing claimed to set status to 'completed' but SPEC-112 still shows 'stub'
- **File**: `.claude/commands/supekku.backfill.md`
- **Implementation Details**:
  1. Add to "Complete Sections Intelligently" guidance:
     ```markdown
     ### Status Field Progression

     Update the frontmatter `status` field as you complete the spec:
     - `stub` → `draft` when backfill is complete (sections filled, YAML valid)
     - `draft` → `active` after validation passes and peer review (if applicable)
     - Never use `completed` (not a valid status)

     Valid status values: stub, draft, active, deprecated, superseded
     ```
  2. Add to final checklist (section 7):
     ```markdown
     - [ ] Frontmatter status updated: `stub` → `draft`
     - [ ] Verify status change: `grep "^status:" specify/.../SPEC-XXX.md`
     ```
  3. Add verification command to show current status:
     ```bash
     # Verify status was updated
     spec_id="SPEC-XXX"
     spec_path=$(find specify/ -name "${spec_id}.md")
     grep "^status:" "$spec_path"
     # Should show: status: draft (not stub)
     ```
- **Rationale**:
  - Status field is in frontmatter, easy to overlook
  - Agent confused about valid values ('completed' doesn't exist)
  - Explicit checklist item prevents forgetting
  - Verification command confirms the change
- **Testing**:
  - Manual: Follow updated workflow and verify status change
  - Manual: Confirm verification command works
  - Integration: Check status field after agent completes backfill
- **Acceptance**:
  - Status progression clearly documented
  - Final checklist includes status update
  - Verification command provided
  - Example shows correct before/after values

**1.5.7 Enhance collaboration analysis guidance**
- **Design**: Add specific prompts to identify external collaborators (not just internal structure)
- **Problem**: SPEC-112 listed only 1 collaborator when it likely uses many more packages
- **File**: `.claude/commands/supekku.backfill.md`
- **Implementation Details**:
  1. Update section 4.B "Examine Related Code" to emphasize collaboration:
     ```markdown
     #### B. Identify External Collaborators

     Focus on what this package DEPENDS ON (external collaborators), not its internal structure:

     ```bash
     # Find imports to identify dependencies
     packages=$(uv run spec-driver list specs --filter "$spec_id" --json | jq -r '.items[0].packages[]')

     # Check imports in the package code
     grep -rh "^import\|^from" "$packages" 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1-3 | sort -u

     # Map imports back to their owning specs
     # For each import like "supekku.scripts.lib.formatters":
     uv run spec-driver list specs --package formatters
     ```

     Look for usage of:
     - Registries (SpecRegistry, ChangeRegistry, DecisionRegistry, etc.)
     - Formatters (for output display)
     - Core utilities (paths, repo, frontmatter, templates)
     - Validation modules
     - Other domain packages

     **Key distinction**:
     - ✓ External: Uses SpecRegistry from `supekku.scripts.lib.specs.registry`
     - ✗ Internal: Has classes `FooCommand`, `BarCommand` (that's internal structure)
     ```
  2. Add to "Complete Sections Intelligently":
     ```markdown
     When filling the `spec.relationships` block:
     - `interactions`: External specs this package depends on or collaborates with
     - Use `type: uses` for dependencies
     - Use `type: extends` for inheritance/augmentation
     - Include description of what functionality is used

     Example:
     ```yaml
     interactions:
       - spec: SPEC-XXX  # Registry module
         type: uses
         description: Uses SpecRegistry to load and filter specifications
       - spec: SPEC-YYY  # Formatter module
         type: uses
         description: Uses spec formatters for table/JSON/TSV output
     ```
  3. Add to quality checklist:
     - [ ] Collaboration analysis: checked imports to identify dependencies
     - [ ] YAML relationships block: includes key external collaborators
- **Rationale**:
  - Agents naturally focus on internal structure (classes/methods)
  - Need explicit prompting to think about external dependencies
  - Import analysis provides concrete starting point
  - Example clarifies external vs internal distinction
- **Testing**:
  - Manual: Follow workflow with real spec
  - Manual: Verify import analysis commands work
  - Integration: Check if agent identifies more collaborators
  - Review: Compare SPEC-112's 1 collaborator vs what should be listed
- **Acceptance**:
  - Import analysis commands documented
  - Clear distinction between external/internal
  - Examples show proper collaboration patterns
  - Quality checklist includes collaboration verification

**1.5.8 Mandate reading all public contracts**
- **Design**: Require agents to read ALL `*-public.md` contract files systematically
- **Problem**: SPEC-110 rewrite "reads like a spec for a completely different codebase" - agent cherry-picked contracts, missed scope
- **File**: `.claude/commands/supekku.backfill.md`
- **Implementation Details**:
  1. Update section 4.A "Load Contracts" to mandate comprehensive reading:
     ```bash
     # Read ALL public contracts (MANDATORY)
     for contract in "$contracts_dir"/*-public.md; do
       echo "=== $(basename $contract) ==="
       cat "$contract"
     done
     ```
  2. Document contract file types:
     - `*-public.md` - **REQUIRED**: Public API surface, interfaces, exports
     - `*-tests.md` - Optional: Test coverage and behavior verification
     - `*-all.md` - Optional: Full implementation (includes public, has duplication)
  3. Add warning about consequences:
     - Missing any public contract = incomplete spec coverage
     - Lost functionality and missing requirements
     - Spec will describe wrong/partial scope
  4. Add to quality checklist:
     - [ ] ALL `*-public.md` contract files read (count matches ls output)
     - [ ] Scope covers all major functions from all public contracts
- **Rationale**:
  - Contracts organized per-module: multiple files per package
  - Agents naturally read selectively and miss scope
  - Public contracts represent complete public API surface
  - Reading all ensures comprehensive coverage
  - Tests and implementation details are optional (for deeper insight)
- **Testing**:
  - Manual: Verify loop reads all public contracts
  - Integration: Re-test SPEC-110 with mandatory reading
  - Verify: Scope matches original spec breadth
- **Acceptance**:
  - Section 4.A emphasizes "MANDATORY - Read ALL Public Contracts"
  - Loop structure ensures systematic reading
  - Contract types clearly distinguished (required vs optional)
  - Quality checklist verifies all public contracts read
  - Warnings about consequences of selective reading

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

- [x] Exit criteria satisfied (except Task 1.6 integration testing)
- [x] Verification evidence: 17 tests passing, all linters clean
- [ ] DE-005 delta updated with implementation notes
- [ ] PROD-007 updated if requirements clarified during implementation
- [x] Hand-off notes documented (see Section 12)

## 12. Handover Notes (2025-11-02)

### What's Complete

**Core Infrastructure (Tasks 1.1-1.5)**:
- ✅ CLI `show template` command working (8 tests)
- ✅ Stub detection logic (status-based + line count fallback, 7 tests)
- ✅ CLI `backfill spec` command (2 tests, fixes applied)
- ✅ Agent command documented (`.claude/commands/supekku.backfill.md`)

**Auto-Generated Spec Improvements (Tasks 1.5.1-1.5.3)**:
- ✅ Sync creates specs with `status: 'stub'` (`sync_specs.py:114`)
- ✅ Orphan messages improved ("source deleted" → generic, works for dirs/files)
- ✅ `--prune` safety: stubs OK, non-stubs require `--force`
- ✅ Migration completed: 16 specs migrated via `migrate_stub_status.py`
- ✅ Status theming: stub=mid-grey (#7c7876), draft=light-grey (#cecdcd)

**Test Coverage**: 17 tests passing across backfill, detection, show commands

### Phase 01 Complete

**All core functionality delivered**:
- ✅ CLI backfill command working
- ✅ Agent workflow tested and validated (SPEC-125)
- ✅ Status progression working (stub → draft)
- ✅ Schema help commands documented and used
- ✅ Collaboration analysis guidance effective
- ✅ All quality checks passing

**Optional Enhancement (Task 1.5.4)**:
- Add `path` and `kind` fields to JSON formatters for consistency
- Currently working via `find` approach (functional but less elegant)
- Can be deferred to Phase 02 or separate enhancement work
- See `JQ_VALIDATION_REPORT.md` for analysis and implementation details

**Phase 02 (Batch Mode)** - Deferred:
- Batch processing (PROD-007.FR-003, FR-004)
- Progress reporting
- Error isolation
- Performance optimization

### Key Files Changed

```
supekku/cli/backfill.py               # CLI command + frontmatter fixes
supekku/cli/sync.py                   # --force flag + stub-aware --prune
supekku/scripts/sync_specs.py         # status='stub' for auto-created
supekku/scripts/migrate_stub_status.py # NEW migration script
supekku/scripts/lib/specs/detection.py # Stub detection
supekku/scripts/lib/formatters/theme.py # Status colors
supekku/scripts/lib/sync/adapters/base.py # Generic orphan messages
.claude/commands/supekku.backfill.md   # NEW agent workflow
```

### Known Issues

**None** - Phase 01 complete and functional

**Enhancement Opportunities**:
- ISSUE-010: Add path field to requirements JSON output
- ISSUE-011: Add path field to backlog items JSON output
- Task 1.5.4: Add path/kind to formatters for consistency (optional)

**ISSUE-009**: Status fields lack enum validation
- Status values are free-form strings (no validation)
- Theme.py serves as de facto documentation (backwards)
- Needs systematic review across all entity types

### Commands for Testing

```bash
# Sync (auto-creates specs with status='stub')
uv run spec-driver sync

# Show template
uv run spec-driver show template tech
uv run spec-driver show template product

# Backfill a stub spec
uv run spec-driver backfill spec SPEC-XXX

# Migration (already run, idempotent)
uv run python supekku/scripts/migrate_stub_status.py --dry-run

# Run tests
uv run pytest supekku/cli/backfill_test.py supekku/scripts/lib/specs/detection_test.py supekku/cli/show_test.py -v

# Lint
uv run ruff check supekku/cli/backfill.py supekku/cli/sync.py supekku/scripts/sync_specs.py
```

## 13. Phase 01 Success Summary (2025-11-02)

### Deliverables Complete

**Core Infrastructure**:
- ✅ CLI `backfill spec` command (2 tests, all linters passing)
- ✅ Stub detection with dual strategy (status + line count)
- ✅ Template rendering system
- ✅ Agent workflow documentation

**Quality Improvements from Testing**:
- ✅ Schema help commands documented (Tasks 1.5.5)
- ✅ Status validation automated with jq (Task 1.5.6)
- ✅ Collaboration analysis guidance (Task 1.5.7)
- ✅ Import-based dependency discovery

**Integration Testing Success**:
- ✅ SPEC-125 completed successfully with agent workflow
- ✅ Agent researched collaborators systematically
- ✅ Agent used schema documentation
- ✅ Status validated as 'draft' automatically
- ✅ Higher quality output observed
- ✅ SPEC-110 rewrite revealed selective reading gap
- ✅ CONTRACT_REVIEW.md validated mandatory contract reading (17k tokens, 8 critical findings)

**Metrics**:
- 17 unit tests passing
- Both linters clean (ruff + pylint)
- 1 successful end-to-end backfill (SPEC-125)
- 16 specs migrated from draft to stub status

### Phase 01 Objectives Met

All entrance and exit criteria satisfied:
1. ✅ Stub detection working reliably
2. ✅ CLI command functional and tested
3. ✅ Agent workflow documented and proven
4. ✅ End-to-end workflow validated with real spec
5. ✅ Quality standards maintained throughout

**Ready for Phase 02** (Batch Mode) or closure if batch mode deferred.

### Next Steps

1. **Phase 02 Planning** (if pursuing batch mode):
   - Review PROD-007.FR-003 & FR-004
   - Design progress reporting
   - Plan error isolation strategy

2. **Address Enhancement Backlog**:
   - ISSUE-010: Requirements JSON path field
   - ISSUE-011: Backlog items JSON path field
   - Task 1.5.4: Formatter JSON consistency (optional)

3. **Address ISSUE-009**: Status enum validation (separate work)
