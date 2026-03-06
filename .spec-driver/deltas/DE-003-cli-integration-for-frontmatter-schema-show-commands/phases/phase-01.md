---
id: IP-003.PHASE-01
slug: cli-integration-for-frontmatter-schema-show-commands-phase-01
name: IP-003 Phase 01 - CLI Implementation
created: '2025-11-02'
updated: '2025-11-02'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-003.PHASE-01
plan: IP-003
delta: DE-003
objective: >-
  Extend existing schema CLI commands to support all 16 frontmatter kinds with
  JSON Schema and YAML example output formats.
entrance_criteria:
  - Frontmatter metadata registry accessible
  - Existing schema.py patterns understood
exit_criteria:
  - All frontmatter kinds accessible via CLI
  - Comprehensive tests passing
  - Lint checks passing
verification:
  tests:
    - supekku/cli/schema_test.py
  evidence:
    - 23 schema tests passing (8 new)
    - 78 total CLI tests passing
    - Ruff: 0 errors
    - Pylint: 9.67/10
tasks:
  - Review existing CLI structure
  - Verify frontmatter registry
  - Extend list command for frontmatter
  - Extend show command for frontmatter
  - Add helper functions
  - Write comprehensive tests
  - Lint and manual testing
risks: []
```

# Phase 01 - CLI Implementation

## 1. Objective
Extend the existing `supekku/cli/schema.py` to support frontmatter schema queries via CLI, enabling agents and developers to access JSON Schema and YAML examples for all 16 frontmatter kinds.

## 2. Links & References
- **Delta**: DE-003 - CLI Integration for Frontmatter Schema Show Commands
- **Requirement**: PROD-004.FR-004 - CLI MUST support `schema show frontmatter.{kind}` commands
- **Specs / PRODs**: PROD-004 (Frontmatter Metadata Validation)
- **Support Docs**:
  - Frontmatter metadata registry: `supekku/scripts/lib/core/frontmatter_metadata/`
  - JSON Schema generation: `supekku/scripts/lib/blocks/metadata/`

## 3. Entrance Criteria
- [x] Frontmatter metadata registry verified accessible (16 entries)
- [x] JSON Schema generation function tested and working
- [x] Existing CLI patterns reviewed and understood

## 4. Exit Criteria / Done When
- [x] CLI supports `schema list frontmatter`
- [x] CLI supports `schema show frontmatter.{kind} --format=json-schema`
- [x] CLI supports `schema show frontmatter.{kind} --format=yaml-example`
- [x] All 16 frontmatter kinds tested
- [x] Comprehensive tests passing (no regressions)
- [x] Lint checks passing (ruff + pylint)

## 5. Verification

**Tests Run:**
```bash
uv run pytest supekku/cli/schema_test.py -v
# Result: 23 tests passing (8 new frontmatter tests)

uv run pytest supekku/cli/ -v
# Result: 78 tests passing (no regressions)

uv run ruff check supekku/cli/schema.py supekku/cli/schema_test.py
# Result: All checks passed

uv run pylint --indent-string "  " supekku/cli/schema.py supekku/cli/schema_test.py
# Result: 9.67/10
```

**Manual Testing:**
- `spec-driver schema list frontmatter` - Verified 16 kinds listed
- `spec-driver schema show frontmatter.prod --format=json-schema` - Verified JSON Schema output
- `spec-driver schema show frontmatter.delta --format=yaml-example` - Verified YAML example output
- Tested all 16 frontmatter kinds with both formats

## 6. Assumptions & STOP Conditions
- **Assumptions**: Frontmatter metadata registry is stable and complete
- **No STOP conditions encountered**

## 7. Tasks & Progress

| Status | ID | Description | Notes |
| --- | --- | --- | --- |
| [x] | 1.1 | Review existing CLI structure | Examined schema.py patterns |
| [x] | 1.2 | Verify frontmatter registry accessible | 16 entries confirmed |
| [x] | 1.3 | Extend list command for frontmatter | Added optional schema_type parameter |
| [x] | 1.4 | Extend show command for frontmatter | Added frontmatter.{kind} detection |
| [x] | 1.5 | Add helper functions | _show_frontmatter_schema, _render_frontmatter_json_schema, _render_frontmatter_yaml_example |
| [x] | 1.6 | Write comprehensive tests | 8 new test methods added |
| [x] | 1.7 | Lint and fix issues | Ruff and pylint passing |
| [x] | 1.8 | Manual testing | All 16 kinds tested |

### Task Details

- **1.3-1.5: Implementation**
  - **Design / Approach**: Extended existing schema.py following established patterns
  - **Files / Components**: supekku/cli/schema.py (3 new functions, 2 modified commands)
  - **Testing**: Comprehensive unit tests covering all paths
  - **Key Decision**: Reused existing Rich rendering patterns for consistency

- **1.6: Test Coverage**
  - **Files**: supekku/cli/schema_test.py
  - **Coverage**: All 16 frontmatter kinds, both output formats, error cases
  - **Result**: 100% of new functionality covered

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Breaking existing CLI | Extended (not replaced) existing commands | ✅ No regressions |
| JSON Schema incompatibility | Used existing metadata_to_json_schema function | ✅ Verified compliant |

## 9. Decisions & Outcomes
- `2025-11-02` - Use `frontmatter.{kind}` format (not `frontmatter {kind}`) for consistency with block type patterns
- `2025-11-02` - Only support json-schema and yaml-example formats for frontmatter (not markdown/json)
- `2025-11-02` - Make schema_type optional parameter to list command (not separate command)

## 10. Findings / Research Notes
- Existing schema.py already had patterns for block schemas
- Frontmatter metadata registry well-structured and complete
- metadata_to_json_schema() function handles all conversion automatically
- Rich library provides consistent formatting across CLI

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored (test results above)
- [x] Spec/Delta/Plan updated with implementation details
- [x] No additional phases needed

**Phase Status**: ✅ **COMPLETE**
