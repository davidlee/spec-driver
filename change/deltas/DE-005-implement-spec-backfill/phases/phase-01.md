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
  Implement core spec backfill functionality: template retrieval, stub detection,
  single-spec completion, and agent command. Batch mode deferred to future phase.
entrance_criteria:
  - PROD-007 complete and validated
  - Contracts generation working (via sync)
exit_criteria:
  - Template retrieval CLI command working
  - Stub detection logic implemented and tested
  - Single spec backfill workflow end-to-end functional
  - Agent command created and documented
verification:
  tests:
    - VT-004
    - VT-005
    - VT-001
  evidence:
    - End-to-end workflow demonstration
    - Test suite passing
tasks:
  - Add show template command
  - Implement stub detection
  - Create completion logic
  - Build CLI backfill command
  - Write agent command
  - Integration testing
risks:
  - Stub detection false positives
  - Template rendering issues
```

# Phase 01 - Core Backfill Implementation

## 1. Objective

Implement single-spec backfill workflow with template retrieval and stub detection. Users can backfill one spec at a time through agent workflow. Batch mode deferred to Phase 02.

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
- [ ] SpecRegistry supports reading/writing specs
- [ ] Template rendering infrastructure exists

## 4. Exit Criteria / Done When
- [ ] `spec-driver show template <kind>` returns valid template markdown
- [ ] Stub detection correctly identifies stub vs. modified specs
- [ ] `/supekku.backfill SPEC-123` completes single spec end-to-end
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
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 1.1 | Add `show template` command to CLI | [x] | Can do first |
| [ ] | 1.2 | Implement stub detection logic | [ ] | Needs 1.1 |
| [ ] | 1.3 | Create completion module | [x] | Can do in parallel |
| [ ] | 1.4 | Build CLI `backfill spec` command | [ ] | Needs 1.2, 1.3 |
| [ ] | 1.5 | Write agent command `.claude/commands/supekku.backfill.md` | [ ] | Needs 1.4 |
| [ ] | 1.6 | Integration testing & dogfooding | [ ] | Final validation |

### Task Details

**1.1 Add `show template` command**
- **Design**: Add subcommand to `supekku/cli/show.py`: `@app.command("template")`
- **Files**: `supekku/cli/show.py`, `supekku/cli/show_test.py`
- **Approach**: Load Jinja2 template from `supekku/templates/spec.md` (or `product-spec.md`), render without variables (or with placeholders), return markdown
- **Testing**: Unit test for both kinds; verify output matches template structure

**1.2 Implement stub detection**
- **Design**: `is_stub_spec(spec_path) -> bool` in `supekku/scripts/lib/specs/detection.py`
- **Approach**: Read spec, extract content after frontmatter, render template for same kind, compare strings (exact match = stub)
- **Files**: `supekku/scripts/lib/specs/detection.py`, `detection_test.py`
- **Testing**: Test with stub spec (True), modified spec (False), partially-modified spec (False)

**1.3 Create completion module**
- **Design**: `complete_spec(spec_id, interactive=True) -> CompletionResult` in `supekku/scripts/lib/specs/completion.py`
- **Approach**: Read spec + contracts → identify gaps → fill sections using contracts → validate
- **Files**: `supekku/scripts/lib/specs/completion.py`, `completion_test.py`
- **Testing**: Mock contracts, verify section filling, YAML block generation

**1.4 Build CLI backfill command**
- **Design**: New module `supekku/cli/backfill.py` with `@app.command("spec")`
- **Approach**: Check stub with detection logic → if modified require `--force` → call completion module → sync/validate
- **Files**: `supekku/cli/backfill.py`, `backfill_test.py`
- **Testing**: Test stub auto-replace, modified requires --force, validation integration

**1.5 Write agent command**
- **Design**: Create `.claude/commands/supekku.backfill.md` following `supekku.specify.md` pattern
- **Content**: Workflow steps, user prompts, CLI invocations, validation checks
- **Testing**: Manual test with real agent session

**1.6 Integration testing**
- **Approach**: End-to-end test: create stub spec → run `/supekku.backfill` → verify completion
- **Dogfooding**: Use workflow to backfill a real stub spec in the project
- **Evidence**: Document successful backfill with before/after comparison

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Stub detection false positives | Exact string matching; comprehensive test suite | Not started |
| Template rendering varies by environment | Pin Jinja2 version; test on multiple systems | Not started |
| Performance issues with large specs | Optimize string comparison; benchmark | Not started |

## 9. Decisions & Outcomes

- `2025-11-02` - CLI command named `backfill` (vs `complete` or `fill`) - clearer intent
- `2025-11-02` - Stub detection uses exact string match (vs fuzzy/semantic) - simpler, safer

## 10. Findings / Research Notes

- Template location: `supekku/templates/spec.md` (tech), need to check for product template
- SpecRegistry already supports read/write (no changes needed)
- Contracts location pattern: `specify/{kind}/{spec-id}/contracts/*.md`

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored (test results, dogfooding screenshots)
- [ ] DE-005 delta updated with implementation notes
- [ ] PROD-007 updated if requirements clarified during implementation
- [ ] Hand-off notes for Phase 02 (batch mode implementation)
