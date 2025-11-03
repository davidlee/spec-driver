---
id: IP-010.PHASE-01
slug: policy-and-standard-management-phase-01
name: IP-010 Phase 01
created: '2025-11-03'
updated: '2025-11-03'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-010.PHASE-01
plan: IP-010
delta: DE-010
objective: >-
  Create domain packages (policies/, standards/) with models, registry, and creation logic
  mirroring the proven decisions/ package architecture.
entrance_criteria:
  - Delta DE-010 approved and PROD-003 reviewed
  - Decisions package structure understood (SPEC-117 reference)
  - Template structure defined
exit_criteria:
  - PolicyRecord and StandardRecord models implemented
  - PolicyRegistry and StandardRegistry with YAML serialization
  - Creation functions with ID generation and frontmatter building
  - Unit tests passing for all domain logic
  - Lint checks passing (just lint, just pylint)
verification:
  tests:
    - VT-PROD-003-001 - E2E test for policy creation
    - VT-PROD-003-002 - Integration test for policy lifecycle
    - VT-PROD-003-003 - E2E test for standard creation
    - VT-PROD-003-004 - Unit test for default status behavior
  evidence:
    - Test run output showing all unit tests passing
    - Lint checks passing (ruff + pylint)
    - Registry YAML files generated correctly
tasks:
  - id: "1.1"
    description: Research decisions package architecture
  - id: "1.2"
    description: Create policies/ package structure
  - id: "1.3"
    description: Create standards/ package structure
  - id: "1.4"
    description: Implement PolicyRecord and StandardRecord models
  - id: "1.5"
    description: Implement PolicyRegistry with YAML serialization
  - id: "1.6"
    description: Implement StandardRegistry with YAML serialization
  - id: "1.7"
    description: Implement policy creation with ID generation
  - id: "1.8"
    description: Implement standard creation with ID generation
  - id: "1.9"
    description: Create policy and standard templates
  - id: "1.10"
    description: Write comprehensive unit tests
  - id: "1.11"
    description: Lint and validate all code
risks:
  - description: Decisions package may use internal APIs not suitable for reuse
    mitigation: Extract patterns, not code; implement independently if needed
  - description: Template structure may need iteration
    mitigation: Start with PROD-003 spec; refine based on actual usage
```

# Phase 01 - Foundation & Domain Models

## 1. Objective
Build the foundational domain packages for policies and standards with models, registries, and creation logic. Mirror the proven architecture from `supekku/scripts/lib/decisions/` while following architectural principles (SRP, pure functions, no premature abstraction).

## 2. Links & References
- **Delta**: [DE-010](../DE-010.md)
- **Implementation Plan**: [IP-010](../IP-010.md)
- **Specs / PRODs**:
  - [PROD-003](../../../../specify/product/PROD-003/PROD-003.md) - Requirements FR-001 through FR-004
  - SPEC-117 - Registry pattern reference (decisions package)
- **Support Docs**:
  - `supekku/scripts/lib/decisions/` - Reference implementation
  - AGENTS.md - Architecture principles

## 3. Entrance Criteria
- [x] Delta DE-010 approved and PROD-003 reviewed
- [ ] Decisions package structure understood (research complete)
- [ ] Template structure defined (Statement, Rationale, Scope, Verification)

## 4. Exit Criteria / Done When
- [ ] PolicyRecord and StandardRecord models implemented with full frontmatter support
- [ ] PolicyRegistry and StandardRegistry with YAML serialization working
- [ ] Creation functions generate valid files with ID generation and frontmatter
- [ ] Unit tests passing for all domain logic (models, registry, creation)
- [ ] Lint checks passing (just lint, just pylint)
- [ ] Can create POL-001 and STD-001 via creation functions
- [ ] Registry YAML serialization verified

## 5. Verification
- **Unit Tests**:
  - `supekku/scripts/lib/policies/registry_test.py` - PolicyRegistry CRUD, filtering, serialization
  - `supekku/scripts/lib/policies/creation_test.py` - ID generation, frontmatter, template rendering
  - `supekku/scripts/lib/standards/registry_test.py` - StandardRegistry CRUD, filtering, serialization
  - `supekku/scripts/lib/standards/creation_test.py` - ID generation, frontmatter, template rendering
- **Commands**: `uv run pytest -v supekku/scripts/lib/policies/ supekku/scripts/lib/standards/`
- **Lint**: `just lint` (ruff), `just pylint` on new files
- **Evidence**: Test output showing all tests passing, lint output clean

## 6. Assumptions & STOP Conditions
- **Assumptions**:
  - Decisions package patterns are stable and suitable for reuse
  - YAML serialization approach from decisions package works for policies/standards
  - Frontmatter schema can be extended without breaking existing code
- **STOP when**:
  - Decisions package uses undocumented internal APIs that can't be safely reused
  - Template structure conflicts with existing artifact conventions
  - Registry performance issues discovered (requires architectural discussion)

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 1.1 | Research decisions package architecture | [ ] | Study models, registry, creation patterns |
| [ ] | 1.2 | Create policies/ package structure | [ ] | __init__.py, models.py, registry.py, creation.py |
| [ ] | 1.3 | Create standards/ package structure | [x] | Can do in parallel with 1.2 |
| [ ] | 1.4 | Implement PolicyRecord and StandardRecord models | [ ] | Dataclasses mirroring DecisionRecord |
| [ ] | 1.5 | Implement PolicyRegistry with YAML serialization | [ ] | Load, filter, sync to YAML |
| [ ] | 1.6 | Implement StandardRegistry with YAML serialization | [x] | Can do in parallel with 1.5 |
| [ ] | 1.7 | Implement policy creation with ID generation | [ ] | Generate POL-XXX IDs, build frontmatter |
| [ ] | 1.8 | Implement standard creation with ID generation | [x] | Can do in parallel with 1.7 |
| [ ] | 1.9 | Create policy and standard templates | [ ] | Markdown templates with sections |
| [ ] | 1.10 | Write comprehensive unit tests | [ ] | Cover models, registry, creation |
| [ ] | 1.11 | Lint and validate all code | [ ] | just lint + just pylint |

### Task Details

- **1.1 Research decisions package architecture**
  - **Design / Approach**: Study `supekku/scripts/lib/decisions/` to understand:
    - DecisionRecord model structure and frontmatter fields
    - DecisionRegistry YAML serialization and filtering
    - Decision creation: ID generation, frontmatter building, template rendering
    - Test patterns and fixtures
  - **Files / Components**:
    - `supekku/scripts/lib/decisions/registry.py`
    - `supekku/scripts/lib/decisions/creation.py`
    - `supekku/scripts/lib/decisions/models.py` (if exists)
    - Test files in decisions package
  - **Testing**: N/A - research only
  - **Observations & AI Notes**: (To be filled during execution)

- **1.2 Create policies/ package structure**
  - **Design / Approach**:
    - Create `supekku/scripts/lib/policies/` directory
    - Add `__init__.py` with exports
    - Create `models.py`, `registry.py`, `creation.py` stubs
  - **Files / Components**:
    - `supekku/scripts/lib/policies/__init__.py`
    - `supekku/scripts/lib/policies/models.py`
    - `supekku/scripts/lib/policies/registry.py`
    - `supekku/scripts/lib/policies/creation.py`
  - **Testing**: Import tests to verify package structure

- **1.3 Create standards/ package structure**
  - **Design / Approach**: Mirror policies/ structure for standards
  - **Files / Components**: Same as 1.2 but in `standards/`
  - **Testing**: Import tests

- **1.4 Implement PolicyRecord and StandardRecord models**
  - **Design / Approach**:
    - PolicyRecord dataclass with fields: id, title, status, created, updated, reviewed, owners, supersedes, superseded_by, standards, specs, requirements, deltas, related_policies, related_standards, tags, summary, path, backlinks
    - StandardRecord with same fields but status includes "default"
    - Follow DecisionRecord patterns
  - **Files / Components**: `models.py` in each package
  - **Testing**: Unit tests for model instantiation, serialization

- **1.5 Implement PolicyRegistry with YAML serialization**
  - **Design / Approach**:
    - PolicyRegistry class to load policies from `specify/policies/`
    - Parse frontmatter and build PolicyRecord instances
    - Serialize to `specify/.registry/policies.yaml`
    - Support filtering by status, tags, references
  - **Files / Components**: `supekku/scripts/lib/policies/registry.py`
  - **Testing**: Registry CRUD tests, YAML serialization tests

- **1.6 Implement StandardRegistry with YAML serialization**
  - **Design / Approach**: Mirror PolicyRegistry for standards
  - **Files / Components**: `supekku/scripts/lib/standards/registry.py`
  - **Testing**: Registry tests

- **1.7 Implement policy creation with ID generation**
  - **Design / Approach**:
    - Function to generate next POL-XXX ID
    - Build frontmatter with all required fields
    - Render template with Statement/Rationale/Scope/Verification sections
    - Write to `specify/policies/POL-XXX-slug.md`
  - **Files / Components**: `supekku/scripts/lib/policies/creation.py`
  - **Testing**: Creation tests, ID generation tests, template rendering tests

- **1.8 Implement standard creation with ID generation**
  - **Design / Approach**: Mirror policy creation for STD-XXX
  - **Files / Components**: `supekku/scripts/lib/standards/creation.py`
  - **Testing**: Creation tests

- **1.9 Create policy and standard templates**
  - **Design / Approach**:
    - Create `.spec-driver/templates/policy-template.md`
    - Create `.spec-driver/templates/standard-template.md`
    - Include frontmatter template + sections (Statement, Rationale, Scope, Verification)
  - **Files / Components**: Template markdown files
  - **Testing**: Template validation tests

- **1.10 Write comprehensive unit tests**
  - **Design / Approach**:
    - Test all models, registries, creation functions
    - Follow decisions package test patterns
    - Cover edge cases (missing fields, invalid status, etc.)
  - **Files / Components**:
    - `supekku/scripts/lib/policies/registry_test.py`
    - `supekku/scripts/lib/policies/creation_test.py`
    - `supekku/scripts/lib/standards/registry_test.py`
    - `supekku/scripts/lib/standards/creation_test.py`
  - **Testing**: Run all tests with pytest

- **1.11 Lint and validate all code**
  - **Design / Approach**: Run linters on all new code
  - **Files / Components**: All new Python files
  - **Testing**: `just lint`, `just pylint`

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Decisions package uses internal APIs | Extract patterns, implement independently | Monitored |
| Template structure needs iteration | Start with spec, refine as needed | Accepted |
| Duplication with decisions code | Defer abstraction until 3rd use (architectural principle) | Planned |

## 9. Decisions & Outcomes
- (To be filled during execution)

## 10. Findings / Research Notes
- (To be filled during research task 1.1)

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored (test output, lint results)
- [ ] IP-010 updated with lessons learned
- [ ] Phase 02 ready to begin (formatters can proceed)
