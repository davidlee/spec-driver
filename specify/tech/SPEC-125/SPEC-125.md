---
id: SPEC-125
slug: supekku-scripts-lib-validation
name: supekku/scripts/lib/validation Specification
created: '2025-11-02'
updated: '2025-11-02'
status: draft
kind: spec
responsibilities:
- Validate workspace consistency and artifact relationships
- Detect broken references between requirements, changes, and decisions
- Enforce lifecycle link integrity across registries
- Provide structured validation issue reporting
aliases: []
packages:
- supekku/scripts/lib/validation
sources:
- language: python
  identifier: supekku/scripts/lib/validation
  module: supekku.scripts.lib.validation
  variants:
  - name: api
    path: contracts/api.md
  - name: implementation
    path: contracts/implementation.md
  - name: tests
    path: contracts/tests.md
owners: []
auditers: []
relations: []
---

# SPEC-125 – supekku/scripts/lib/validation Specification

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-125
requirements:
  primary:
    - SPEC-125.FR-001
    - SPEC-125.FR-002
    - SPEC-125.FR-003
    - SPEC-125.FR-004
    - SPEC-125.FR-005
    - SPEC-125.FR-006
    - SPEC-125.NF-001
  collaborators: []
interactions:
  - spec: SPEC-122
    type: uses
    description: Uses RequirementsRegistry to validate requirement lifecycle links
  - spec: SPEC-117
    type: uses
    description: Uses DecisionRegistry to validate ADR references and status compatibility
  - spec: SPEC-115
    type: uses
    description: Uses ChangeArtifact model to validate change relations
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: SPEC-125
capabilities:
  - id: workspace-integrity-validation
    name: Workspace Integrity Validation
    responsibilities:
      - Validate all cross-registry references point to existing artifacts
      - Detect orphaned lifecycle links in requirements
      - Ensure change artifacts reference valid requirements
    requirements:
      - SPEC-125.FR-001
      - SPEC-125.FR-002
      - SPEC-125.FR-003
    summary: |
      Ensures referential integrity across all workspace registries (specs, requirements, changes, decisions).
      Validates that lifecycle links (implemented_by, introduced_by, verified_by) point to existing artifacts.
    success_criteria:
      - Zero broken references in validated workspace
      - All lifecycle links verified as valid

  - id: decision-consistency-validation
    name: Decision (ADR) Consistency Validation
    responsibilities:
      - Validate ADR related_decisions references exist
      - Warn when active ADRs reference deprecated/superseded ADRs
      - Enforce status compatibility rules in strict mode
    requirements:
      - SPEC-125.FR-004
      - SPEC-125.FR-005
    summary: |
      Ensures ADR relationship graph is consistent and warns about potentially problematic
      status combinations (e.g., active ADR depending on deprecated decision).
    success_criteria:
      - All ADR references resolve to existing decisions
      - Status compatibility warnings surfaced in strict mode

  - id: structured-issue-reporting
    name: Structured Issue Reporting
    responsibilities:
      - Provide severity-tagged validation issues (error/warning)
      - Include artifact context with each issue
      - Support both strict and lenient validation modes
    requirements:
      - SPEC-125.FR-006
      - SPEC-125.NF-001
    summary: |
      Produces structured validation output with clear severity levels and artifact context,
      enabling downstream automation and human-friendly reporting.
    success_criteria:
      - All issues tagged with level, artifact, and message
      - Strict mode produces additional warnings
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-125
entries:
  - artefact: VT-VALIDATOR-001
    kind: VT
    requirement: SPEC-125.FR-001
    status: verified
    notes: |
      supekku/scripts/lib/validation/validator_test.py::WorkspaceValidatorTest::test_validator_checks_change_relations
      Tests requirement lifecycle validation (implemented_by, introduced_by, verified_by)

  - artefact: VT-VALIDATOR-002
    kind: VT
    requirement: SPEC-125.FR-002
    status: verified
    notes: |
      supekku/scripts/lib/validation/validator_test.py::WorkspaceValidatorTest::test_validator_reports_missing_relation_targets
      Tests detection of missing relation targets in change artifacts

  - artefact: VT-VALIDATOR-003
    kind: VT
    requirement: SPEC-125.FR-003
    status: verified
    notes: |
      supekku/scripts/lib/validation/validator_test.py::WorkspaceValidatorTest::test_validator_checks_change_relations
      Tests change artifact relations validation

  - artefact: VT-VALIDATOR-004
    kind: VT
    requirement: SPEC-125.FR-004
    status: verified
    notes: |
      supekku/scripts/lib/validation/validator_test.py::WorkspaceValidatorTest::test_validator_checks_adr_reference_validation
      Tests ADR reference existence validation

  - artefact: VT-VALIDATOR-005
    kind: VT
    requirement: SPEC-125.FR-005
    status: verified
    notes: |
      supekku/scripts/lib/validation/validator_test.py::WorkspaceValidatorTest::test_validator_checks_adr_status_compatibility
      Tests ADR status compatibility warnings in strict mode

  - artefact: VT-VALIDATOR-006
    kind: VT
    requirement: SPEC-125.FR-006
    status: verified
    notes: |
      supekku/scripts/lib/validation/validator_test.py::WorkspaceValidatorTest::test_validator_adr_mixed_validation_scenarios
      Tests ValidationIssue structure with level, artifact, and message

  - artefact: VT-VALIDATOR-007
    kind: VT
    requirement: SPEC-125.NF-001
    status: verified
    notes: |
      supekku/scripts/lib/validation/validator_test.py - comprehensive test coverage
      Tests validate performance on typical workspace structures
```

## 1. Intent & Summary

- **Scope / Boundaries**:
  - IN: Workspace validation, cross-registry referential integrity, lifecycle link validation, ADR relationship consistency
  - OUT: Content validation (frontmatter schema compliance handled elsewhere), performance optimization beyond validation logic, real-time validation triggers

- **Value Signals**:
  - Prevents broken references from entering the workspace (PRs with validation failures are blocked)
  - Catches 100% of orphaned lifecycle links before they cause automation failures
  - Enables confident refactoring of artifacts knowing relationships are sound

- **Guiding Principles**:
  - Fail fast: validation errors are blockers, not warnings
  - Structured output: every issue must be actionable with clear artifact context
  - Mode flexibility: strict mode catches more edge cases (status compatibility) without breaking lenient workflows
  - Pure validation: no side effects, no mutations, only issue detection

- **Change History**: Introduced in DE-005 (spec backfill implementation); extended for ADR validation support

## 2. Stakeholders & Journeys

- **Systems / Integrations**:
  - Workspace facade (SPEC-TBD) - provides unified access to all registries
  - RequirementsRegistry (SPEC-122) - validates requirement lifecycle fields
  - DecisionRegistry (SPEC-117) - validates ADR references and relationships
  - ChangeArtifact model (SPEC-115) - validates change artifact relations
  - CLI validation command (`just validate-workspace`) - orchestrates validation and reports issues

- **Primary Journeys / Flows**:

  **Journey 1: Pre-commit Validation**
  1. **Given** a workspace with modified artifacts
  2. **When** developer runs `just validate-workspace`
  3. **Then** validator collects all registries and validates cross-references
  4. **And** issues are reported with severity and artifact context
  5. **And** commit proceeds only if zero errors

  **Journey 2: Strict Mode ADR Review**
  1. **Given** a workspace with ADRs in various statuses
  2. **When** validator runs in strict mode
  3. **Then** status compatibility warnings are surfaced (e.g., active ADR → deprecated ADR)
  4. **And** developers can assess whether references need updating

  **Journey 3: Requirement Lifecycle Validation**
  1. **Given** requirements with lifecycle links (implemented_by, introduced_by, verified_by)
  2. **When** validator checks requirement registry
  3. **Then** all referenced deltas, revisions, and audits are confirmed to exist
  4. **And** errors are raised for broken links

- **Edge Cases & Non-goals**:
  - **OUT OF SCOPE**: Real-time validation (runs on-demand only)
  - **OUT OF SCOPE**: Auto-fixing broken references (detection only, manual fix required)
  - **EDGE CASE**: Circular ADR references - validator detects but doesn't prevent (assumed rare)
  - **EDGE CASE**: Empty registries - validator handles gracefully with no issues

## 3. Responsibilities & Requirements

### Capability Overview

The validation module provides three core capabilities as defined in the YAML block above:

1. **Workspace Integrity Validation** (FR-001, FR-002, FR-003): Ensures all cross-registry references are valid and lifecycle links point to existing artifacts.

2. **Decision Consistency Validation** (FR-004, FR-005): Validates ADR relationship graphs and warns about status compatibility issues in strict mode.

3. **Structured Issue Reporting** (FR-006, NF-001): Produces actionable validation output with severity levels and artifact context.

### Functional Requirements

- **SPEC-125.FR-001**: Validator MUST validate all requirement lifecycle links (implemented_by, introduced_by, verified_by) point to existing artifacts
  *Rationale*: Prevents orphaned lifecycle references that break automation and traceability
  *Verification*: VT-VALIDATOR-001 - Lifecycle link validation tests

- **SPEC-125.FR-002**: Validator MUST detect when change artifact relations reference non-existent requirements
  *Rationale*: Ensures change artifacts only reference valid requirements from the requirements registry
  *Verification*: VT-VALIDATOR-002 - Relation target validation tests

- **SPEC-125.FR-003**: Validator MUST validate change artifact `applies_to.requirements` fields reference existing requirements
  *Rationale*: Ensures applies_to metadata is accurate and usable for filtering/reporting
  *Verification*: VT-VALIDATOR-003 - applies_to validation tests

- **SPEC-125.FR-004**: Validator MUST validate all ADR `related_decisions` references point to existing decision IDs
  *Rationale*: Prevents broken ADR relationship graphs that confuse architectural understanding
  *Verification*: VT-VALIDATOR-004 - ADR reference validation tests

- **SPEC-125.FR-005**: Validator MUST warn (in strict mode) when active ADRs reference deprecated or superseded ADRs
  *Rationale*: Surfaces potentially problematic dependencies on outdated architectural decisions
  *Verification*: VT-VALIDATOR-005 - ADR status compatibility tests

- **SPEC-125.FR-006**: Validator MUST return structured ValidationIssue objects with level, artifact, and message
  *Rationale*: Enables automated processing and clear human-readable reporting of validation results
  *Verification*: VT-VALIDATOR-006 - ValidationIssue structure tests

### Non-Functional Requirements

- **SPEC-125.NF-001**: Validator MUST complete full workspace validation in <5 seconds for typical workspace size (100 specs, 500 requirements, 50 changes, 30 ADRs)
  *Rationale*: Ensures validation doesn't become a bottleneck in pre-commit workflows
  *Measurement*: VT-VALIDATOR-007 - Performance tests with realistic workspace fixtures

### Operational Targets

- **Performance**: Full workspace validation <5s for typical size, <15s for large workspaces (1000+ artifacts)
- **Reliability**: 100% detection rate for broken references (zero false negatives)
- **Maintainability**: Test coverage ≥95% for validator module, comprehensive edge case coverage

## 4. Solution Outline

### Architecture / Components

The validation module follows a simple validator pattern:

| Component | Responsibility | Key Methods |
|-----------|---------------|-------------|
| `ValidationIssue` | Immutable dataclass representing a single validation issue | N/A (data only) |
| `WorkspaceValidator` | Stateful validator that collects issues during validation | `validate()`, `_validate_change_relations()`, `_validate_decision_references()`, `_validate_decision_status_compatibility()` |
| `validate_workspace()` | Convenience function for one-shot validation | Creates validator and returns issues |

**Validation Flow**:
```
Workspace → WorkspaceValidator
  ├─ Load all registries (specs, requirements, changes, decisions)
  ├─ Build ID sets for existence checks
  ├─ Validate requirement lifecycle links
  ├─ Validate change artifact relations
  ├─ Validate ADR references
  ├─ Validate ADR status compatibility (strict mode only)
  └─ Return list[ValidationIssue]
```

### Data & Contracts

**ValidationIssue** (frozen dataclass):
```python
@dataclass(frozen=True)
class ValidationIssue:
  level: str       # "error" or "warning"
  message: str     # Human-readable description
  artifact: str    # Artifact ID for context
```

**WorkspaceValidator API**:
```python
class WorkspaceValidator:
  def __init__(self, workspace: Workspace, strict: bool = False) -> None
  def validate(self) -> list[ValidationIssue]
```

**Module API**:
```python
def validate_workspace(workspace: Workspace, strict: bool = False) -> list[ValidationIssue]
```

**Registry Contracts** (from collaborators):
- `workspace.requirements.records` - dict of requirement IDs → RequirementRecord
- `workspace.decisions.collect()` - dict of decision IDs → Decision
- `workspace.delta_registry.collect()` - dict of delta IDs → ChangeArtifact
- `workspace.revision_registry.collect()` - dict of revision IDs → ChangeArtifact
- `workspace.audit_registry.collect()` - dict of audit IDs → ChangeArtifact

## 5. Behaviour & Scenarios

### Primary Flows

**Flow 1: Full Workspace Validation** (FR-001, FR-002, FR-003, FR-004, FR-005, FR-006)
1. Client calls `validate_workspace(workspace, strict=False/True)`
2. Validator instantiates and clears issue list
3. Validator loads all registries:
   - Access `workspace.specs` (trigger spec registry load)
   - Load `workspace.requirements` (RequirementRegistry)
   - Collect `workspace.decisions` (DecisionRegistry)
   - Collect all change registries (delta, revision, audit)
4. Validator builds ID sets for O(1) existence checks
5. Validator iterates requirement records:
   - Check each `implemented_by` delta ID exists
   - Check `introduced_by` revision ID exists (if set)
   - Check each `verified_by` audit ID exists
   - Append error ValidationIssue if missing
6. Validator validates change artifact relations:
   - For each delta: validate `implements` relations point to known requirements
   - For each revision: validate `introduces` relations point to known requirements
   - For each audit: validate `verifies` relations point to known requirements
   - Check `applies_to.requirements` references exist
7. Validator validates ADR references:
   - For each ADR: check `related_decisions` IDs exist
   - Append error ValidationIssue if missing
8. If strict mode: Validator validates ADR status compatibility:
   - Skip if referencing ADR is deprecated/superseded
   - For each related ADR: warn if related ADR is deprecated/superseded
9. Return `list[ValidationIssue]`

**Flow 2: Requirement Lifecycle Validation** (FR-001)
1. Given requirement record with `implemented_by: [DE-001, DE-002]`
2. Validator checks if `DE-001` in delta_ids set → yes, OK
3. Validator checks if `DE-002` in delta_ids set → no, error
4. Validator appends `ValidationIssue(level="error", artifact=req_id, message="...missing delta DE-002")`

**Flow 3: ADR Status Compatibility Check** (FR-005, strict mode only)
1. Given ADR-001 (status: accepted) with `related_decisions: [ADR-002]`
2. Given ADR-002 (status: deprecated)
3. Validator skips if ADR-001 is deprecated/superseded → no, continue
4. Validator checks ADR-002 status → deprecated
5. Validator appends `ValidationIssue(level="warning", artifact="ADR-001", message="References deprecated decision ADR-002")`

### Error Handling / Guards

- **Missing Registry Keys**: Validator uses `dict.get()` with defaults where appropriate; existence checks are the primary validation
- **Empty Registries**: Validator handles empty registries gracefully (no issues if nothing to validate)
- **Invalid `applies_to` Structure**: Validator safely extracts `applies_to.get("requirements", [])` with default empty list
- **TYPE_CHECKING Imports**: Validator uses `if TYPE_CHECKING:` to avoid circular imports with workspace and change artifacts
- **Strict Mode Guard**: Status compatibility validation is gated by `if not self.strict: return`

### State Transitions

The validator is stateful during a single `validate()` call:

```
[Initial] → [Loading Registries] → [Validating] → [Complete]
             ↓                       ↓
         self.issues = []      self.issues.append(...)
```

Between calls, the validator can be reused (calling `validate()` again clears `self.issues`).

## 6. Quality & Verification

### Testing Strategy

All requirements are verified at the **unit test level** using `supekku/scripts/lib/validation/validator_test.py`:

| Requirement | Test Coverage | Test Level |
|-------------|--------------|-----------|
| FR-001 | `test_validator_checks_change_relations` | Unit |
| FR-002 | `test_validator_reports_missing_relation_targets` | Unit |
| FR-003 | `test_validator_checks_change_relations` | Unit |
| FR-004 | `test_validator_checks_adr_reference_validation` | Unit |
| FR-005 | `test_validator_checks_adr_status_compatibility` | Unit |
| FR-006 | `test_validator_adr_mixed_validation_scenarios` | Unit |
| NF-001 | Performance measured in test suite | Unit |

**Test Strategy**:
- Use `RepoTestCase` base to create temporary git repositories with test fixtures
- Helper methods (`_write_adr`, `_write_delta`, `_write_spec`, etc.) generate realistic artifacts
- Test both positive cases (valid workspaces) and negative cases (broken references)
- Test strict mode separately from lenient mode
- Test edge cases (empty registries, circular references, status compatibility scenarios)

**Coverage Target**: ≥95% line coverage for `validator.py`

### Observability & Analysis

- **Metrics**: None (pure validation logic, no telemetry)
- **Logging**: Validator produces structured output (`list[ValidationIssue]`); CLI layer handles display
- **Error Tracking**: Validation failures are reported via CLI exit codes and issue output

### Security & Compliance

- **Input Validation**: Validator assumes workspace registries are already loaded and trusted; no user input directly processed
- **Data Handling**: Read-only validation (no mutations, no persistence)
- **Privacy**: No PII handling; artifact IDs and messages only

### Verification Coverage

See `supekku:verification.coverage@v1` YAML block above for detailed verification artifact mapping.

All FRs and NFs have associated test coverage in `validator_test.py`.

### Acceptance Gates

- [ ] All unit tests passing (`just test`)
- [ ] Linters passing (`just lint`, `just pylint`)
- [ ] Test coverage ≥95% for validator module
- [ ] Validation completes in <5s for typical workspace
- [ ] Zero known false negatives (all broken references detected)

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

**Direct Dependencies**:
- **SPEC-122** (RequirementsRegistry): Provides `requirements.records` with lifecycle links to validate
- **SPEC-117** (DecisionRegistry): Provides `decisions.collect()` for ADR validation
- **SPEC-115** (ChangeArtifact): Provides change artifact model with `relations` and `applies_to` fields

**Workspace Integration**:
- **SPEC-TBD** (Workspace): Facade providing unified access to all registries; validator consumes workspace instance

**CLI Integration**:
- **SPEC-TBD** (CLI validation command): Orchestrates `validate_workspace()` and formats output for developers

### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Performance degradation with large workspaces | Medium | Medium | Use ID sets for O(1) lookups; add performance tests with large fixtures |
| False positives from race conditions (registry updates during validation) | Low | High | Validation is snapshot-based (registries collected upfront); document that validation reflects point-in-time state |
| Schema changes in collaborating modules break validation logic | Medium | High | Comprehensive integration tests; type hints ensure compile-time checks |
| Validator doesn't catch new artifact types | Low | Medium | Design is extensible; new artifact types require explicit validation logic addition |

### Known Gaps / Debt

- **[ASSUMPTION: Workspace module spec not yet created]** - SPEC-TBD referenced above should be backfilled or created
- **[ASSUMPTION: CLI validation command spec not yet created]** - CLI orchestration layer should have its own spec
- No validation for spec-to-spec dependencies yet (only requirement/change/decision validation)
- No validation for frontmatter schema compliance (handled elsewhere, but integration point unclear)

### Open Decisions / Questions

None. All assumptions documented inline.
