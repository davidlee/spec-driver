---
id: IP-010.PHASE-04
slug: 010-policy-and-standard-management-phase-04
name: IP-010 Phase 04
created: '2025-11-03'
updated: '2025-11-03'
status: in-progress
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-010.PHASE-04
plan: IP-010
delta: DE-010
objective: >-
  Implement bidirectional cross-references between policies ↔ standards ↔ ADRs
  with automatic backlink maintenance in registries.
entrance_criteria:
  - Phase 03 complete - CLI commands working
  - PolicyRecord and StandardRecord have reference fields (standards, policies)
  - DecisionRecord has policies field but needs standards field
  - Backlink infrastructure exists in all three models
  - Cross-reference patterns understood
exit_criteria:
  - DecisionRecord extended with standards field
  - Backlink maintenance implemented in all three registries
  - Formatters display cross-references and backlinks
  - CLI list commands support cross-reference filtering
  - Cross-reference integrity tests passing
  - All linters passing (ruff + pylint)
verification:
  tests:
    - VT-PROD-003-007 - Bidirectional policy ↔ standard references
    - VT-PROD-003-008 - Policy/standard references in ADRs with backlinks
  evidence:
    - Integration tests for cross-reference integrity
    - Manual testing of backlink generation
    - Lint checks passing
tasks:
  - id: "4.1"
    description: Add standards field to DecisionRecord model
  - id: "4.2"
    description: Update DecisionRegistry.sync() for policy/standard backlinks
  - id: "4.3"
    description: Update PolicyRegistry.sync() for decision backlinks
  - id: "4.4"
    description: Update StandardRegistry.sync() for decision/policy backlinks
  - id: "4.5"
    description: Add cross-reference display to decision_formatters
  - id: "4.6"
    description: Add backlink display to policy_formatters
  - id: "4.7"
    description: Add backlink display to standard_formatters
  - id: "4.8"
    description: Add --standard flag to list adrs command
  - id: "4.9"
    description: Write cross-reference integrity tests
  - id: "4.10"
    description: Lint and test all code
risks:
  - description: Existing ADR files lack standards field
    mitigation: Field defaults to empty list - backward compatible
  - description: Backlink generation logic complex
    mitigation: Follow existing backlink patterns from decisions package
  - description: Formatter display cluttered with too many cross-refs
    mitigation: Show count in table view, full list in details/JSON
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-010.PHASE-04
files:
  references:
    - "supekku/scripts/lib/decisions/registry.py"
    - "supekku/scripts/lib/policies/registry.py"
    - "supekku/scripts/lib/standards/registry.py"
    - "supekku/scripts/lib/formatters/decision_formatters.py"
    - "supekku/scripts/lib/formatters/policy_formatters.py"
    - "supekku/scripts/lib/formatters/standard_formatters.py"
  context:
    - "change/deltas/DE-010-policy-and-standard-management/phases/phase-03.md"
    - "change/deltas/DE-010-policy-and-standard-management/PHASE-03-HANDOVER.md"
    - "docs/ux-research-cli-2025-11-03.md"
entrance_criteria:
  - item: "Phase 03 complete - CLI commands working"
    completed: true
  - item: "PolicyRecord and StandardRecord have reference fields"
    completed: true
  - item: "DecisionRecord has policies field"
    completed: true
  - item: "Backlink infrastructure exists in all models"
    completed: true
  - item: "Cross-reference patterns understood"
    completed: true
exit_criteria:
  - item: "DecisionRecord extended with standards field"
    completed: false
  - item: "Backlink maintenance implemented in all three registries"
    completed: false
  - item: "Formatters display cross-references and backlinks"
    completed: false
  - item: "CLI list commands support cross-reference filtering"
    completed: false
  - item: "Cross-reference integrity tests passing"
    completed: false
  - item: "All linters passing (ruff + pylint)"
    completed: false
tasks:
  - id: "4.1"
    description: "Add standards field to DecisionRecord model"
    status: completed
    files:
      added: []
      modified:
        - "supekku/scripts/lib/decisions/registry.py"
      removed: []
      tests: []
  - id: "4.2"
    description: "Update DecisionRegistry.sync() for policy/standard backlinks"
    status: completed
    files:
      added: []
      modified:
        - "supekku/scripts/lib/decisions/registry.py"
      removed: []
      tests: []
  - id: "4.3"
    description: "Update PolicyRegistry.sync() for decision backlinks"
    status: completed
    files:
      added: []
      modified:
        - "supekku/scripts/lib/policies/registry.py"
      removed: []
      tests: []
  - id: "4.4"
    description: "Update StandardRegistry.sync() for decision/policy backlinks"
    status: completed
    files:
      added: []
      modified:
        - "supekku/scripts/lib/standards/registry.py"
      removed: []
      tests: []
  - id: "4.5"
    description: "Add cross-reference display to decision_formatters"
    status: pending
    files:
      added: []
      modified:
        - "supekku/scripts/lib/formatters/decision_formatters.py"
        - "supekku/scripts/lib/formatters/decision_formatters_test.py"
      removed: []
      tests:
        - "supekku/scripts/lib/formatters/decision_formatters_test.py"
  - id: "4.6"
    description: "Add backlink display to policy_formatters"
    status: pending
    files:
      added: []
      modified:
        - "supekku/scripts/lib/formatters/policy_formatters.py"
        - "supekku/scripts/lib/formatters/policy_formatters_test.py"
      removed: []
      tests:
        - "supekku/scripts/lib/formatters/policy_formatters_test.py"
  - id: "4.7"
    description: "Add backlink display to standard_formatters"
    status: pending
    files:
      added: []
      modified:
        - "supekku/scripts/lib/formatters/standard_formatters.py"
        - "supekku/scripts/lib/formatters/standard_formatters_test.py"
      removed: []
      tests:
        - "supekku/scripts/lib/formatters/standard_formatters_test.py"
  - id: "4.8"
    description: "Add --standard flag to list adrs command"
    status: pending
    files:
      added: []
      modified:
        - "supekku/cli/list.py"
        - "supekku/cli/test_cli.py"
      removed: []
      tests:
        - "supekku/cli/test_cli.py"
  - id: "4.9"
    description: "Write cross-reference integrity tests"
    status: pending
    files:
      added:
        - "supekku/scripts/lib/cross_references_test.py"
      modified: []
      removed: []
      tests:
        - "supekku/scripts/lib/cross_references_test.py"
  - id: "4.10"
    description: "Lint and test all code"
    status: pending
    files:
      added: []
      modified: []
      removed: []
      tests: []
```

# Phase 04 - Cross-References and Backlinks

## 1. Objective

Implement bidirectional cross-references between policies, standards, and ADRs with automatic backlink maintenance. This enables:
- ADRs to reference policies and standards they implement or comply with
- Policies to reference standards they require
- Standards to reference policies they support
- Automatic backlinks showing which ADRs/policies/standards reference each artifact

## 2. Links & References

- **Delta**: [DE-010](../DE-010.md)
- **Implementation Plan**: [IP-010](../IP-010.md)
- **Specs / PRODs**:
  - [PROD-003](../../../../specify/product/PROD-003/PROD-003.md) - FR-007, FR-008
- **Support Docs**:
  - `supekku/scripts/lib/decisions/registry.py` - DecisionRecord model and registry
  - `supekku/scripts/lib/policies/registry.py` - PolicyRecord model and registry
  - `supekku/scripts/lib/standards/registry.py` - StandardRecord model and registry
  - Phase 03 handover - Reference fields already exist in PolicyRecord/StandardRecord
  - UX research report - Cross-reference filtering patterns

## 3. Entrance Criteria

- [x] Phase 03 complete - CLI commands working (84/84 tests passing)
- [x] PolicyRecord has `standards` field for referencing standards
- [x] StandardRecord has `policies` field for referencing policies
- [x] DecisionRecord has `policies` field for referencing policies
- [x] All three models have `backlinks` dict field for maintaining backlinks
- [x] Cross-reference patterns understood (studied existing models)

## 4. Exit Criteria / Done When

- [ ] DecisionRecord extended with `standards: list[str]` field
- [ ] DecisionRegistry.sync() builds backlinks from policies/standards
- [ ] PolicyRegistry.sync() builds backlinks from decisions
- [ ] StandardRegistry.sync() builds backlinks from decisions/policies
- [ ] decision_formatters displays policies and standards in details view
- [ ] policy_formatters displays backlinks (decisions referencing this policy)
- [ ] standard_formatters displays backlinks (decisions/policies referencing this standard)
- [ ] `list adrs --standard STD-XXX` filtering works
- [ ] Cross-reference integrity tests passing (VT-PROD-003-007, VT-PROD-003-008)
- [ ] All linters passing (ruff + pylint)

## 5. Verification

**Integration Tests**:
- VT-PROD-003-007: Test bidirectional policy ↔ standard references
  - Create policy referencing standard
  - Verify standard backlink generated
  - Create standard referencing policy
  - Verify policy backlink generated

- VT-PROD-003-008: Test ADR → policy/standard references with backlinks
  - Create ADR referencing policy and standard
  - Verify policy backlink includes ADR
  - Verify standard backlink includes ADR

**Manual Verification**:
```bash
# Test cross-reference display
uv run spec-driver show policy POL-001  # Should show backlinks
uv run spec-driver show standard STD-001  # Should show backlinks
uv run spec-driver show adr ADR-001  # Should show policies/standards

# Test filtering
uv run spec-driver list adrs --standard STD-001
uv run spec-driver list policies --standard STD-001
uv run spec-driver list standards --policy POL-001

# Test JSON output
uv run spec-driver show policy POL-001 --json  # backlinks in JSON
```

**Lint Checks**:
```bash
uv run just lint
uv run just pylint
uv run just test
```

## 6. Assumptions & STOP Conditions

**Assumptions**:
- Existing ADR files will not have `standards` field → defaults to empty list (backward compatible)
- Backlink generation follows same pattern as existing decision registry
- Cross-references stored in frontmatter, backlinks in registry YAML
- Backlinks regenerated on each registry sync (not persisted in markdown)

**STOP Conditions**:
- Backlink generation causes performance issues with large artifact counts
- Cross-reference cycles detected (policy → standard → policy)
- Existing ADRs fail to parse after schema change

## 7. Tasks & Progress

*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 4.1 | Add standards field to DecisionRecord | [ ] | ✅ Complete - field added to model, to_dict, parsing |
| [x] | 4.2 | Update DecisionRegistry.sync() for backlinks | [ ] | ✅ Complete - placeholder for future backlinks |
| [x] | 4.3 | Update PolicyRegistry.sync() for backlinks | [x] | ✅ Complete - builds backlinks from decisions |
| [x] | 4.4 | Update StandardRegistry.sync() for backlinks | [x] | ✅ Complete - builds backlinks from decisions + policies |
| [ ] | 4.5 | Add cross-refs to decision_formatters | [ ] | Pending - show policies/standards in details |
| [ ] | 4.6 | Add backlinks to policy_formatters | [x] | Pending - show decision backlinks |
| [ ] | 4.7 | Add backlinks to standard_formatters | [x] | Pending - show decision/policy backlinks |
| [ ] | 4.8 | Add --standard flag to list adrs | [ ] | Pending - follow --policy pattern |
| [ ] | 4.9 | Write cross-reference integrity tests | [ ] | Pending - comprehensive testing |
| [ ] | 4.10 | Lint and test all code | [ ] | Pending - final verification |

### Task Details

#### 4.1 Add standards field to DecisionRecord
- **Design / Approach**: Add `standards: list[str] = field(default_factory=list)` to DecisionRecord dataclass
- **Files / Components**:
  - `supekku/scripts/lib/decisions/registry.py` - DecisionRecord class (line 20-106)
  - Update `to_dict()` method to include standards field
- **Testing**: Existing tests should pass with new field defaulting to empty list
- **Observations**: Backward compatible change - existing ADRs will parse fine

#### 4.2 Update DecisionRegistry.sync() for backlinks
- **Design / Approach**: Build backlinks from policies and standards that reference this decision
- **Files / Components**:
  - `supekku/scripts/lib/decisions/registry.py` - DecisionRegistry.sync() method
  - Follow existing backlink pattern from decisions package
- **Testing**: Unit tests for backlink generation
- **Observations**: Need to iterate through policies/standards registries

#### 4.3 Update PolicyRegistry.sync() for decision backlinks
- **Design / Approach**: Build backlinks from decisions that reference this policy
- **Files / Components**:
  - `supekku/scripts/lib/policies/registry.py` - PolicyRegistry.sync() method
- **Testing**: Unit tests for backlink generation
- **Observations**: Parallel with 4.2 - same pattern, different direction

#### 4.4 Update StandardRegistry.sync() for backlinks
- **Design / Approach**: Build backlinks from decisions and policies that reference this standard
- **Files / Components**:
  - `supekku/scripts/lib/standards/registry.py` - StandardRegistry.sync() method
- **Testing**: Unit tests for backlink generation
- **Observations**: Standards have backlinks from both decisions AND policies

#### 4.5 Add cross-reference display to decision_formatters
- **Design / Approach**:
  - Table view: Show count of policies/standards
  - Details view: Show full list of policies and standards
  - JSON view: Include in output
- **Files / Components**:
  - `supekku/scripts/lib/formatters/decision_formatters.py`
  - `supekku/scripts/lib/formatters/decision_formatters_test.py`
- **Testing**: Test with ADR that has policies and standards references

#### 4.6 Add backlink display to policy_formatters
- **Design / Approach**:
  - Details view: Show "Referenced by" section with decisions
  - JSON view: Include backlinks
- **Files / Components**:
  - `supekku/scripts/lib/formatters/policy_formatters.py`
  - `supekku/scripts/lib/formatters/policy_formatters_test.py`
- **Testing**: Test with policy that has decision backlinks

#### 4.7 Add backlink display to standard_formatters
- **Design / Approach**:
  - Details view: Show "Referenced by" with decisions and policies
  - JSON view: Include backlinks
- **Files / Components**:
  - `supekku/scripts/lib/formatters/standard_formatters.py`
  - `supekku/scripts/lib/formatters/standard_formatters_test.py`
- **Testing**: Test with standard that has decision+policy backlinks

#### 4.8 Add --standard flag to list adrs
- **Design / Approach**: Follow existing `--policy` flag pattern
- **Files / Components**:
  - `supekku/cli/list.py` - list_adrs() function
  - `supekku/cli/test_cli.py` - CLI integration tests
- **Testing**: Integration test for filtering ADRs by standard

#### 4.9 Write cross-reference integrity tests
- **Design / Approach**:
  - Test policy → standard → backlinks
  - Test ADR → policy → backlinks
  - Test ADR → standard → backlinks
  - Test bidirectional integrity
- **Files / Components**:
  - New file: `supekku/scripts/lib/cross_references_test.py` OR
  - Add to existing registry tests
- **Testing**: Comprehensive integration tests covering all cross-ref paths

#### 4.10 Lint and test all code
- **Commands**:
  - `uv run just lint`
  - `uv run just pylint`
  - `uv run just test`
- **Quality**: Ruff passing, Pylint threshold maintained

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Existing ADR files lack standards field | Field defaults to empty list - backward compatible | Accepted |
| Backlink generation complex | Follow proven patterns from decisions package | Open |
| Formatter display cluttered | Show counts in table, full lists in details/JSON | Open |
| Performance with large artifact counts | Defer optimization until proven necessary | Accepted |
| Cross-reference cycles | Document as acceptable - not enforced | Open |

## 9. Decisions & Outcomes

**2025-11-03** - Defer help text examples to DE-011
- Rationale: UX research identifies need for examples, but Phase 04 scope is cross-references
- Keep Phase 04 focused on core functionality
- Separate UX improvement delta already in flight

**2025-11-03** - Backlinks not persisted in markdown
- Rationale: Backlinks are derived data, regenerated on sync
- Reduces risk of stale/inconsistent backlinks
- Registry YAML is source of truth for backlinks

## 10. Findings / Research Notes

### Implementation Progress (2025-11-03)

**Tasks 4.1-4.4 Complete** (40 mins)

✅ **Task 4.1**: Added `standards: list[str]` field to DecisionRecord
- Updated dataclass, `to_dict()`, and `_parse_adr_file()`
- Backward compatible - defaults to empty list
- Lint passing

✅ **Task 4.2**: Updated DecisionRegistry with backlink infrastructure
- Added `_build_backlinks()` method called from `write()`
- Clears existing backlinks per ADR-002 (derived data)
- Placeholder for future extensibility (specs/requirements referencing decisions)

✅ **Task 4.3**: PolicyRegistry builds backlinks from decisions
- Iterates through decisions, finds policies referenced
- Builds `backlinks["decisions"]` list for each policy
- Uses lazy import (`noqa: PLC0415`) to avoid circular dependencies
- Lint passing

✅ **Task 4.4**: StandardRegistry builds backlinks from decisions AND policies
- Two backlink sources: decisions.standards and policies.standards
- Populates `backlinks["decisions"]` and `backlinks["policies"]`
- Handles both artifact types correctly
- Lint passing

**Key Observations**:
- Lazy imports with `# noqa: PLC0415` work cleanly for circular dependency avoidance
- ADR-002 pattern (compute backlinks at runtime, don't persist in frontmatter) followed correctly
- Backlinks cleared on each sync - fresh computation from forward references
- All three registries now support cross-reference backlink generation

**Remaining Work** (estimated 1.5-2 hours):
- Formatter updates (4.5-4.7) - display cross-refs and backlinks
- CLI flag addition (4.8) - `--standard` for list adrs
- Integration tests (4.9) - verify backlink integrity
- Final lint/test (4.10)

### Pre-flight Analysis (2025-11-03)

**DecisionRecord Current State** (supekku/scripts/lib/decisions/registry.py:20-106):
- ✅ Has `policies: list[str]` field (line 34)
- ❌ Missing `standards: list[str]` field
- ✅ Has `backlinks: dict[str, list[str]]` field (line 47)
- ✅ `to_dict()` method serializes all fields to YAML

**PolicyRecord Current State** (supekku/scripts/lib/policies/registry.py:21-95):
- ✅ Has `standards: list[str]` field (line 34)
- ✅ Has `backlinks: dict[str, list[str]]` field (line 43)
- ✅ Ready for cross-references

**StandardRecord Current State** (supekku/scripts/lib/standards/registry.py):
- ✅ Has `policies: list[str]` field
- ✅ Has `backlinks: dict[str, list[str]]` field
- ✅ Ready for cross-references

**UX Research Insights** (docs/ux-research-cli-2025-11-03.md):
- Relationship filters should follow pattern: `--policy POL-XXX`, `--standard STD-XXX`
- Cross-reference display should be consistent across artifact types
- JSON output should include full backlinks for agent consumption

### Backlink Pattern Analysis

Existing backlink pattern (from decisions registry):
```python
# Build backlinks from references in frontmatter
for artifact in all_artifacts:
  for ref_id in artifact.specs:
    specs[ref_id].backlinks.setdefault('decisions', []).append(artifact.id)
```

Apply same pattern for:
- Decisions → Policies (build policy backlinks)
- Decisions → Standards (build standard backlinks)
- Policies → Standards (build standard backlinks)

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored (test output, manual test results)
- [ ] IP-010 updated with progress
- [ ] Hand-off notes for Phase 05 (if continuing) or delta completion
