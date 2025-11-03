---
id: IP-011.PHASE-01
slug: cli-enhanced-filtering-and-self-documentation-phase-01
name: IP-011 Phase 01 - Enhanced Filtering
created: '2025-11-03'
updated: '2025-11-03'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-011.PHASE-01
plan: IP-011
delta: DE-011
objective: >-
  Implement multi-value filtering and reverse relationship queries for all list commands,
  enabling agents to construct complex queries natively without post-processing with jq/grep.
entrance_criteria:
  - Development environment set up with uv and dependencies installed
  - DE-009 completed (consistent JSON and status filtering baseline)
  - Existing CLI test suite passing (just test)
  - Both linters passing (just lint, just pylint)
  - Familiarity with CLAUDE.md skinny CLI patterns and formatter separation
  - Understanding of existing filter patterns (list deltas, list adrs, etc.)
exit_criteria:
  - Multi-value filter parsing utility implemented and tested
  - All list commands support comma-separated multi-value filters
  - Reverse relationship query flags implemented on relevant commands
  - Registry methods support reverse queries with glob pattern matching
  - Backward compatibility: existing single-value filters unchanged
  - All unit tests passing with comprehensive new test coverage
  - Both linters passing with zero warnings
  - Performance: reverse queries complete in <2s for typical registries
  - Manual workflow testing confirms multi-value and reverse query functionality
verification:
  tests:
    - VT-CLI-MULTI-FILTER
    - VT-CLI-REVERSE-QUERY
    - VT-CLI-BACKWARD-COMPAT
  evidence:
    - VT-PROD010-FILTER-002
    - VT-PROD010-FILTER-003
tasks:
  - id: "1.1"
    description: Research existing filter patterns and registry query methods
    status: pending
  - id: "1.2"
    description: Create core/filters.py module with multi-value filter utilities
    status: pending
  - id: "1.3"
    description: Write tests for multi-value filter parsing (TDD)
    status: pending
  - id: "1.4"
    description: Implement multi-value filter support in all list commands
    status: pending
  - id: "1.5"
    description: Write tests for reverse relationship queries (TDD)
    status: pending
  - id: "1.6"
    description: Add reverse query methods to registries (deltas, requirements, specs)
    status: pending
  - id: "1.7"
    description: Implement reverse relationship flags in list commands
    status: pending
  - id: "1.8"
    description: Add glob pattern support for verification artifact matching
    status: pending
  - id: "1.9"
    description: Write tests for verification status/kind filters (TDD)
    status: pending
  - id: "1.10"
    description: Implement --vstatus and --vkind flags for list requirements
    status: pending
  - id: "1.11"
    description: Write backward compatibility tests
    status: pending
  - id: "1.12"
    description: Run full test suite and linters, fix any issues
    status: pending
  - id: "1.13"
    description: Performance testing for reverse queries
    status: pending
  - id: "1.14"
    description: Manual validation of multi-value and reverse query workflows
    status: pending
risks:
  - description: Multi-value filter parsing breaks existing regex filters
    likelihood: medium
    impact: high
    mitigation: Comprehensive backward compatibility tests; escape comma in regex if needed
  - description: Reverse relationship queries too slow on large registries
    likelihood: medium
    impact: medium
    mitigation: Index relationships in registry; implement early filtering; performance tests
  - description: Glob pattern parsing conflicts with shell expansion
    likelihood: medium
    impact: low
    mitigation: Quote patterns in examples; document shell escaping requirements
```

# Phase 01 - Enhanced Filtering

## 1. Objective

Implement advanced filtering capabilities to eliminate agent post-processing workflows:

1. **Multi-value filters**: Support comma-separated values in all filters (e.g., `-s draft,in-progress`)
2. **Reverse relationship queries**: Enable native reverse traversal (`--implements`, `--verified-by`, `--informed-by`)
3. **Glob pattern support**: Match verification artifacts with patterns (`--verified-by "VT-CLI-*"`)
4. **Verification filters**: Filter requirements by verification status/kind (`--vstatus`, `--vkind`)
5. **Backward compatibility**: Ensure existing single-value filters continue to work unchanged

**Success Signal**: Agents use native CLI filters instead of piping through jq/grep, reducing token consumption and latency.

## 2. Links & References

- **Delta**: [DE-011](../DE-011.md)
- **Product Spec**: [PROD-010](../../../specify/product/PROD-010/PROD-010.md) - CLI Agent UX (FR-004, FR-005)
- **Tech Spec**: [SPEC-110](../../../specify/tech/SPEC-110/SPEC-110.md) - supekku/cli
- **Requirements**:
  - PROD-010.FR-004: Multi-value filter support
  - PROD-010.FR-005: Reverse relationship queries
- **Support Docs**:
  - UX Research Report: `docs/ux-research-cli-2025-11-03.md` (Section 13: Medium-Term improvements)
  - CLAUDE.md: Skinny CLI patterns, formatter separation
  - DE-009: Foundation delta (consistent JSON baseline)

## 3. Entrance Criteria

- [x] Development environment set up with uv and dependencies installed
- [x] DE-009 completed (consistent JSON and status filtering baseline)
- [ ] Existing CLI test suite passing (`just test`)
- [ ] Both linters passing (`just lint`, `just pylint`)
- [ ] Familiarity with CLAUDE.md skinny CLI patterns and formatter separation
- [ ] Understanding of existing filter patterns (review `list deltas`, `list adrs` implementations)
- [ ] Registry structure understood (ChangeRegistry, SpecRegistry, RequirementRegistry)
- [ ] Existing relationship metadata patterns reviewed (delta `implements`, requirement `verified_by`)

## 4. Exit Criteria / Done When

- [ ] `core/filters.py` module created with `parse_multi_value_filter()` utility
- [ ] All list commands accept comma-separated multi-value filters
- [ ] Multi-value filters work for status, kind, and other categorical fields
- [ ] `list deltas --implements <REQ-ID>` returns correct filtered results
- [ ] `list requirements --verified-by <ARTIFACT>` returns correct filtered results
- [ ] `list specs --informed-by <ADR>` returns correct filtered results
- [ ] Glob patterns supported for verification artifacts (`--verified-by "VT-*"`)
- [ ] `list requirements --vstatus <STATUS>` filters by verification status
- [ ] `list requirements --vkind <KIND>` filters by verification artifact kind
- [ ] Verification filters support multi-value syntax (`--vstatus verified,failed`)
- [ ] Backward compatibility tests pass (single-value filters unchanged)
- [ ] All new tests passing (>40 new test cases expected)
- [ ] Both linters passing (`just lint`, `just pylint`)
- [ ] Performance benchmark: reverse queries complete in <2s for typical registries
- [ ] Manual workflow validation confirms functionality

## 5. Verification

**Unit Tests**:
```bash
# Multi-value filter tests
uv run pytest supekku/cli/test_cli.py::TestMultiValueFilters -v
uv run pytest supekku/scripts/lib/core/filters_test.py -v

# Reverse relationship query tests
uv run pytest supekku/cli/test_cli.py::TestReverseRelationships -v
uv run pytest supekku/scripts/lib/changes/registry_test.py::test_find_by_implements -v
uv run pytest supekku/scripts/lib/requirements/registry_test.py::test_find_by_verified_by -v

# Backward compatibility tests
uv run pytest supekku/cli/test_cli.py::TestFilterBackwardCompatibility -v

# Performance tests
uv run pytest supekku/cli/test_cli.py::TestReverseQueryPerformance -v
```

**Integration Tests**:
```bash
# Full suite
just test

# Linters
just lint
just pylint
```

**Manual Validation**:
```bash
# Test multi-value filters
spec-driver list deltas -s draft,in-progress --json
spec-driver list specs -k prod,tech --json
spec-driver list requirements -k FR,NF --json

# Test reverse relationship queries
spec-driver list deltas --implements PROD-010.FR-004 --json
spec-driver list deltas --implements SPEC-110.FR-001 --json
spec-driver list requirements --verified-by VT-PROD010-FILTER-002 --json

# Test glob patterns
spec-driver list requirements --verified-by "VT-CLI-*" --json
spec-driver list requirements --verified-by "VT-PROD010-*" --json

# Test verification status filters
spec-driver list requirements --vstatus verified --json
spec-driver list requirements --vstatus planned,in-progress --json
spec-driver list requirements --vstatus failed,blocked --json

# Test verification kind filters
spec-driver list requirements --vkind VT --json
spec-driver list requirements --vkind VA,VH --json
spec-driver list requirements --vkind VT,VA,VH --json

# Test combining verification filters
spec-driver list requirements --vstatus verified --vkind VT,VA --json
spec-driver list requirements --spec SPEC-110 --vstatus failed --json
spec-driver list requirements --verified-by "VT-*" --vstatus verified --json

# Test backward compatibility
spec-driver list deltas -s draft --json  # Single value should still work
spec-driver list specs -k prod --json     # Single value should still work

# Performance testing
time spec-driver list deltas --implements SPEC-110.FR-001 --json  # Should be <2s
time spec-driver list requirements --verified-by "VT-*" --json     # Should be <2s
time spec-driver list requirements --vstatus verified --vkind VT --json  # Should be <2s
```

**Evidence to Capture**:
- Test output showing all new tests passing
- Performance benchmark results (query execution times)
- Before/after examples showing multi-value vs post-processing workflows
- Manual validation notes confirming functionality

## 6. Assumptions & STOP Conditions

**Assumptions**:
- Comma (`,`) is appropriate separator (no conflicts with existing usage)
- Registry metadata includes relationship fields (`implements`, `verified_by`, `informed_by`)
- Glob pattern matching uses Python `fnmatch` or similar (standard glob syntax)
- Performance target of <2s is achievable without complex indexing

**STOP Conditions**:
- If comma separator conflicts with existing regex filters, STOP for alternative design
- If reverse query performance exceeds 5s on typical registries, STOP for indexing strategy
- If backward compatibility tests fail, STOP for root cause analysis
- If glob pattern parsing requires shell-specific escaping, STOP for documentation strategy

## 7. Tasks & Progress

*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Research existing patterns | [ ] | Completed - see Section 10 |
| [x] | 1.2 | Create core/filters.py module | [ ] | Completed - pylint 10/10 |
| [ ] | 1.3 | Write multi-value filter tests | [x] | Can parallelize with 1.5 |
| [ ] | 1.4 | Implement multi-value filters | [ ] | After 1.3 |
| [ ] | 1.5 | Write reverse query tests | [x] | Can parallelize with 1.3 |
| [ ] | 1.6 | Add reverse query methods to registries | [ ] | After 1.5 |
| [ ] | 1.7 | Implement reverse query flags | [ ] | After 1.6 |
| [ ] | 1.8 | Add glob pattern support | [ ] | After 1.7 |
| [ ] | 1.9 | Write vstatus/vkind filter tests | [x] | Can parallelize with 1.3, 1.5 |
| [ ] | 1.10 | Implement vstatus/vkind flags | [ ] | After 1.9 |
| [ ] | 1.11 | Write backward compat tests | [x] | Can start early |
| [ ] | 1.12 | Full test suite + linters | [ ] | After 1.4, 1.7, 1.8, 1.10 |
| [ ] | 1.13 | Performance testing | [ ] | After 1.7 |
| [ ] | 1.14 | Manual validation | [ ] | Final step |

### Task Details

#### **1.1 Research existing patterns** ✅
- **Design / Approach**:
  - Review current filter implementations in `list deltas`, `list adrs`, `list requirements`
  - Examine registry query methods in `ChangeRegistry`, `SpecRegistry`, `RequirementRegistry`
  - Identify relationship metadata fields: `delta.implements`, `requirement.verified_by`, `spec.informed_by`
  - Document current filter parsing patterns (single-value handling)
  - Identify glob pattern library options (fnmatch vs glob)
- **Files / Components**:
  - `supekku/cli/list.py` - existing filter implementations
  - `supekku/scripts/lib/changes/registry.py` - ChangeRegistry query methods
  - `supekku/scripts/lib/specs/registry.py` - SpecRegistry query methods
  - `supekku/scripts/lib/requirements/registry.py` - RequirementRegistry query methods
  - `.spec-driver/registry/*.yaml` - registry YAML structures
- **Testing**: No tests for research phase
- **Observations & AI Notes**:
  - All findings documented in Section 10
  - Key decision: `--verified-by` should search BOTH `verified_by` and `coverage_evidence` fields
  - DecisionRegistry.filter() provides excellent pattern for reverse queries
  - Python fnmatch confirmed as glob library choice
- **Commits / References**: Phase sheet updated with research findings

#### **1.2 Create core/filters.py module** ✅
- **Design / Approach**:
  - Create new module `supekku/scripts/lib/core/filters.py`
  - Implement `parse_multi_value_filter(value: str) -> list[str]` utility
  - Handle comma-separated values: "draft,in-progress" → ["draft", "in-progress"]
  - Handle single values (backward compat): "draft" → ["draft"]
  - Handle empty/None values: None → []
  - Pure function (no side effects)
- **Files / Components**:
  - `supekku/scripts/lib/core/filters.py` (new file) - 42 lines
  - `supekku/scripts/lib/core/__init__.py` - export utility
- **Testing**: Unit tests in task 1.3
- **Observations & AI Notes**:
  - Pure function with comprehensive docstring and examples
  - Strips whitespace from each value for flexibility
  - Returns empty list for None/empty input (simplifies caller logic)
  - Linters: ruff clean, pylint 10.00/10
- **Commits / References**: Next commit

#### **1.3 Write multi-value filter tests (TDD)**
- **Design / Approach**:
  - Write tests BEFORE implementation (TDD)
  - Test `parse_multi_value_filter()` utility:
    - Single value: "draft" → ["draft"]
    - Multiple values: "draft,in-progress" → ["draft", "in-progress"]
    - Whitespace handling: "draft, in-progress" → ["draft", "in-progress"]
    - Empty string: "" → []
    - None: None → []
  - Test multi-value filters in list commands:
    - `list deltas -s draft,in-progress` returns union
    - `list specs -k prod,tech` returns union
    - `list requirements -k FR,NF` returns union
  - Test backward compatibility:
    - Single-value filters still work unchanged
- **Files / Components**:
  - `supekku/scripts/lib/core/filters_test.py` (new file)
  - `supekku/cli/test_cli.py` - add TestMultiValueFilters class
- **Testing**: Tests will initially FAIL (TDD red phase)
- **Observations & AI Notes**: *Record edge cases discovered*
- **Commits / References**: *Commit hash after tests written*

#### **1.4 Implement multi-value filters**
- **Design / Approach**:
  - Implement `parse_multi_value_filter()` in `core/filters.py`
  - Update all list commands to use utility for status, kind filters
  - Modify filter logic: `status in parse_multi_value_filter(status_arg)`
  - Maintain backward compatibility: single values work as before
  - Commands to update: list_deltas, list_adrs, list_specs, list_requirements, list_revisions, list_changes
- **Files / Components**:
  - `supekku/scripts/lib/core/filters.py` - implement utility
  - `supekku/cli/list.py` - update all list commands
- **Testing**: Run tests from 1.3; all should now PASS (TDD green phase)
- **Observations & AI Notes**: *Record implementation challenges*
- **Commits / References**: *Commit hash after implementation*

#### **1.5 Write reverse query tests (TDD)**
- **Design / Approach**:
  - Write tests BEFORE implementation
  - Test registry reverse query methods:
    - `ChangeRegistry.find_by_implements(req_id)` returns matching deltas
    - `RequirementRegistry.find_by_verified_by(artifact)` returns matching requirements
    - `SpecRegistry.find_by_informed_by(adr_id)` returns matching specs
  - Test CLI reverse query flags:
    - `list deltas --implements PROD-010.FR-004 --json`
    - `list requirements --verified-by VT-CLI-001 --json`
    - `list specs --informed-by ADR-001 --json`
  - Test glob pattern matching:
    - `list requirements --verified-by "VT-*"` matches all VT artifacts
    - `list requirements --verified-by "VT-CLI-*"` matches VT-CLI-* only
- **Files / Components**:
  - `supekku/scripts/lib/changes/registry_test.py` - add test_find_by_implements
  - `supekku/scripts/lib/requirements/registry_test.py` - add test_find_by_verified_by
  - `supekku/scripts/lib/specs/registry_test.py` - add test_find_by_informed_by
  - `supekku/cli/test_cli.py` - add TestReverseRelationships class
- **Testing**: Tests will initially FAIL (TDD red phase)
- **Observations & AI Notes**: *Record expected behavior, edge cases*
- **Commits / References**: *Commit hash after tests written*

#### **1.6 Add reverse query methods to registries**
- **Design / Approach**:
  - Implement `ChangeRegistry.find_by_implements(req_id)` method
  - Implement `RequirementRegistry.find_by_verified_by(artifact_pattern)` with glob support
  - Implement `SpecRegistry.find_by_informed_by(adr_id)` method
  - Use Python `fnmatch` for glob pattern matching
  - Filter in-memory (no indexing for now; optimize later if needed)
- **Files / Components**:
  - `supekku/scripts/lib/changes/registry.py` - add find_by_implements
  - `supekku/scripts/lib/requirements/registry.py` - add find_by_verified_by
  - `supekku/scripts/lib/specs/registry.py` - add find_by_informed_by
- **Testing**: Run tests from 1.5; registry tests should now PASS
- **Observations & AI Notes**: *Record implementation approach*
- **Commits / References**: *Commit hash after implementation*

#### **1.7 Implement reverse query flags in list commands**
- **Design / Approach**:
  - Add `--implements` flag to `list deltas` command
  - Add `--verified-by` flag to `list requirements` command
  - Add `--informed-by` flag to `list specs` command
  - Wire flags to registry reverse query methods
  - Combine with existing filters (AND logic)
- **Files / Components**:
  - `supekku/cli/list.py` - add flags to list_deltas, list_requirements, list_specs
  - `supekku/cli/common.py` - potentially add shared option types
- **Testing**: Run tests from 1.5; CLI tests should now PASS
- **Observations & AI Notes**: *Record CLI integration challenges*
- **Commits / References**: *Commit hash after implementation*

#### **1.8 Add glob pattern support**
- **Design / Approach**:
  - Ensure `find_by_verified_by()` uses `fnmatch` for pattern matching
  - Test glob patterns: `VT-*`, `VA-*`, `VT-CLI-*`, etc.
  - Document quoting requirements for shell (use `"pattern"` in examples)
- **Files / Components**:
  - `supekku/scripts/lib/requirements/registry.py` - glob support in find_by_verified_by
- **Testing**: Glob pattern tests should pass
- **Observations & AI Notes**: *Record pattern matching edge cases*
- **Commits / References**: *Commit hash after glob support*

#### **1.9 Write tests for verification status/kind filters (TDD)**
- **Design / Approach**:
  - Write tests BEFORE implementation (TDD)
  - Test `--vstatus` flag on `list requirements`:
    - Single value: `--vstatus verified` returns requirements with verified test artifacts
    - Multi-value: `--vstatus planned,in-progress` returns union
    - Filter by verification entry status, not requirement status
  - Test `--vkind` flag on `list requirements`:
    - Single value: `--vkind VT` returns requirements with unit tests
    - Multi-value: `--vkind VT,VA` returns requirements with tests OR agent validation
    - Filter by verification artifact kind
  - Test combining filters: `--vstatus verified --vkind VT,VA`
  - Test interaction with existing filters: `--spec SPEC-110 --vstatus failed`
- **Files / Components**:
  - `supekku/cli/test_cli.py` - add TestVerificationStatusFilters class
  - Test data should include requirements with multiple verification entries with different statuses/kinds
- **Testing**: Tests will initially FAIL (TDD red phase)
- **Observations & AI Notes**: *Record expected behavior for verification filters*
- **Commits / References**: *Commit hash after tests written*

#### **1.10 Implement --vstatus and --vkind flags for list requirements**
- **Design / Approach**:
  - Add `--vstatus` / `--verification-status` flag to `list requirements` command
  - Add `--vkind` / `--verification-kind` flag to `list requirements` command
  - Both flags use multi-value filter parsing from `core/filters.py`
  - Implement `RequirementRegistry.find_by_verification_status()` method
  - Implement `RequirementRegistry.find_by_verification_kind()` method
  - Filter logic: requirement matches if ANY of its verification entries match the filter
  - Combine with existing filters (AND logic across different filter types)
  - Valid values:
    - vstatus: planned, in-progress, verified, failed, blocked
    - vkind: VT, VA, VH
- **Files / Components**:
  - `supekku/cli/list.py` - add flags to list_requirements command
  - `supekku/scripts/lib/requirements/registry.py` - add filter methods
  - `supekku/scripts/lib/blocks/verification.py` - reference VALID_STATUSES and VALID_KINDS constants
- **Testing**: Run tests from 1.9; should now PASS (TDD green phase)
- **Observations & AI Notes**: *Record implementation approach, edge cases*
- **Commits / References**: *Commit hash after implementation*

#### **1.11 Write backward compatibility tests**
- **Design / Approach**:
  - Test single-value filters still work: `-s draft` (not `draft,`)
  - Test regex filters unchanged (if supported)
  - Test empty filter values handled correctly
  - Ensure no breaking changes to existing CLI usage
- **Files / Components**:
  - `supekku/cli/test_cli.py` - add TestFilterBackwardCompatibility class
- **Testing**: All backward compat tests must PASS
- **Observations & AI Notes**: *Record any breaking changes discovered*
- **Commits / References**: *Commit hash after tests*

#### **1.10 Full test suite + linters**
- **Design / Approach**:
  - Run full test suite: `just test`
  - Run both linters: `just lint`, `just pylint`
  - Fix any failing tests or lint issues
  - Ensure zero warnings from both linters
  - Validate test coverage for new code (aim for >90%)
- **Files / Components**: All modified files
- **Testing**: Full suite validation
- **Observations & AI Notes**: *Record issues found, fixes applied*
- **Commits / References**: *Commit hash for fixes*

#### **1.11 Performance testing**
- **Design / Approach**:
  - Benchmark reverse query performance on typical registries
  - Measure time for `list deltas --implements SPEC-110.FR-001`
  - Measure time for `list requirements --verified-by "VT-*"`
  - Target: <2s for typical registries (~20-30 deltas, ~80 requirements)
  - If exceeds threshold, consider indexing or early filtering optimization
- **Files / Components**:
  - `supekku/cli/test_cli.py` - add TestReverseQueryPerformance class (optional)
- **Testing**: Manual timing with `time` command; optional automated tests
- **Observations & AI Notes**: *Record performance results, bottlenecks*
- **Commits / References**: N/A (performance validation)

#### **1.12 Full test suite + linters**
- **Design / Approach**:
  - Run full test suite: `just test`
  - Run both linters: `just lint`, `just pylint`
  - Fix any failing tests or lint issues
  - Ensure zero warnings from both linters
  - Validate test coverage for new code (aim for >90%)
- **Files / Components**: All modified files
- **Testing**: Full suite validation
- **Observations & AI Notes**: *Record issues found, fixes applied*
- **Commits / References**: *Commit hash for fixes*

#### **1.13 Performance testing**
- **Design / Approach**:
  - Benchmark reverse query performance on typical registries
  - Measure time for `list deltas --implements SPEC-110.FR-001`
  - Measure time for `list requirements --verified-by "VT-*"`
  - Measure time for `list requirements --vstatus verified --vkind VT`
  - Target: <2s for typical registries (~20-30 deltas, ~80 requirements)
  - If exceeds threshold, consider indexing or early filtering optimization
- **Files / Components**:
  - `supekku/cli/test_cli.py` - add TestReverseQueryPerformance class (optional)
- **Testing**: Manual timing with `time` command; optional automated tests
- **Observations & AI Notes**: *Record performance results, bottlenecks*
- **Commits / References**: N/A (performance validation)

#### **1.14 Manual validation**
- **Design / Approach**:
  - Test multi-value filters manually with various combinations
  - Test reverse relationship queries with real artifact IDs
  - Test glob patterns with various verification artifact patterns
  - Test verification status and kind filters
  - Test combining multiple filter types
  - Validate backward compatibility with existing single-value filters
  - Cross-reference with PROD-010.FR-004 and FR-005 requirements
  - Document findings and any gaps discovered
- **Files / Components**: N/A (manual testing)
- **Testing**: Manual workflow validation
- **Observations & AI Notes**: *Record validation results, gaps found*
- **Commits / References**: N/A

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Multi-value parsing breaks regex filters | Comprehensive backward compatibility tests; escape comma if needed | Planned |
| Reverse queries too slow (>2s) | In-memory filtering first; add indexing only if needed | Planned |
| Glob patterns conflict with shell expansion | Quote patterns in examples; document shell escaping | Planned |
| Relationship metadata missing in registries | Verify metadata structure in research phase; add if missing | Planned |

## 9. Decisions & Outcomes

- `2025-11-03` - Phase scope: Focus on filtering only; defer self-documentation to Phase 2
- `2025-11-03` - Separator choice: Use comma (`,`) for consistency with common CLI tools
- `2025-11-03` - Glob library: Use Python `fnmatch` for standard glob syntax
- `2025-11-03` - Performance target: <2s for typical registries; optimize only if needed

## 10. Findings / Research Notes

*(Use for code spelunking results, pattern discoveries, reference links)*

**Existing Filter Patterns**:
- **Single-value status filters**: All list commands use simple string comparison
  - `list_deltas`: `normalize_status(artifact.status) != normalize_status(status)` - line 331
  - `list_requirements`: `r.status.lower() == status.lower()` - line 985
  - `list_adrs`: Uses `DecisionRegistry.iter(status=status)` - line 651
- **String matching**: No comma-separated parsing exists yet
- **Regexp filters**: Implemented consistently across commands with `matches_regexp()` helper
- **Filter combination**: AND logic (all filters must match)

**Registry Query Methods**:
- **ChangeRegistry** (registry.py:30-92):
  - `collect()` - returns dict of artifacts
  - No filtering methods - filtering done in CLI layer
- **RequirementsRegistry** (registry.py:128-1057):
  - `search()` - substring matching on title/label (lines 1014-1043)
  - No reverse relationship query methods exist yet
  - `records` dict: key=uid (e.g., "PROD-001.FR-001")
- **DecisionRegistry** (registry.py:112-393):
  - `filter()` - relationship filtering (lines 298-328)
  - Filters by: tag, spec, delta, requirement, policy
  - Pattern: `if spec and spec not in decision.specs: matches = False`
  - This is a good reference pattern for reverse queries!

**Relationship Metadata Structure**:
- **Delta registry** (deltas.yaml):
  - `applies_to.requirements` - list of requirement IDs (e.g., PROD-005.FR-001)
  - `applies_to.specs` - list of spec IDs
  - Pattern: delta "implements" requirements
- **Requirements registry** (requirements.yaml):
  - `implemented_by` - list of delta IDs (empty in examples seen)
  - `verified_by` - list of verification artifact IDs (e.g., AUD-001)
  - `coverage_evidence` - list of test artifact IDs (e.g., VT-001)
  - Note: Both `verified_by` and `coverage_evidence` could match verification artifacts!

**Glob Pattern Support**:
- Python standard library `fnmatch` is appropriate choice
- Already used in codebase (found in sync adapters)
- Pattern: `fnmatch.fnmatch(artifact_id, pattern)`

**Key Insights**:
1. No multi-value parsing exists - need to create utility
2. DecisionRegistry.filter() provides good pattern for reverse queries
3. Requirements have TWO fields for verification: `verified_by` and `coverage_evidence`
4. Need to decide: should `--verified-by` search both fields or just one?
5. Verification coverage blocks are separate from registry - stored in spec/plan content

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied (all 12 items in Section 4)
- [ ] Verification evidence stored (test outputs, performance benchmarks)
- [ ] DE-011 updated with Phase 1 implementation notes
- [ ] IP-011 verification coverage updated with test results
- [ ] Hand-off notes prepared for Phase 2 (self-documentation)
- [ ] Performance benchmarks documented
- [ ] Backward compatibility confirmed

## 12. Hand-off Notes

**For Phase 2** (Self-Documentation):
- Multi-value filter patterns established; can reference for consistency
- Registry query methods available for introspection in enum commands
- Test patterns established for CLI flag additions
- Performance baseline: reverse queries complete in <2s

**Known Limitations**:
- No indexing yet; performance adequate for current registry sizes but may need optimization for larger registries
- Glob pattern support limited to `fnmatch` syntax (not full regex)
