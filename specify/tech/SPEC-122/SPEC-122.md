---
id: SPEC-122
slug: supekku-scripts-lib-requirements
name: supekku/scripts/lib/requirements Specification
created: '2025-11-02'
updated: '2025-11-02'
status: draft
kind: spec
responsibilities:
- Manage requirement records with comprehensive lifecycle tracking
- Synchronize requirements from specs and change artifacts into central registry
- Support requirement movement and reassignment between specs
- Track requirement implementation and verification status
- Provide flexible querying and filtering of requirements
- Maintain bidirectional links between requirements and change artifacts
aliases: []
packages:
- supekku/scripts/lib/requirements
sources:
- language: python
  identifier: supekku/scripts/lib/requirements
  module: supekku.scripts.lib.requirements
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

# SPEC-122 – supekku/scripts/lib/requirements

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-122
requirements:
  primary:
    - SPEC-122.FR-001
    - SPEC-122.FR-002
    - SPEC-122.FR-003
    - SPEC-122.FR-004
    - SPEC-122.FR-005
    - SPEC-122.FR-006
    - SPEC-122.FR-007
    - SPEC-122.FR-008
    - SPEC-122.FR-009
    - SPEC-122.NF-001
    - SPEC-122.NF-002
    - SPEC-122.NF-003
  collaborators: []
interactions:
  - spec: SPEC-123
    type: uses
    description: Uses SpecRegistry to iterate specs during sync operations
  - spec: SPEC-115
    type: uses
    description: Extracts relationships from delta/revision/audit artifacts for lifecycle tracking
  - spec: SPEC-TBD
    type: uses
    description: Uses core.repo for repository root detection
  - spec: SPEC-TBD
    type: uses
    description: Uses core.spec_utils for markdown file loading
  - spec: SPEC-TBD
    type: uses
    description: Uses blocks.relationships for extracting spec relationships blocks
  - spec: SPEC-TBD
    type: uses
    description: Uses blocks.revision for processing revision blocks
  - spec: SPEC-TBD
    type: uses
    description: Uses relations.manager for listing requirement relations
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: SPEC-122
capabilities:
  - id: requirement-record-model
    name: Requirement Record Model
    responsibilities:
      - Define immutable requirement identifier (uid) combining spec ID and label
      - Track requirement metadata (title, kind, status, path)
      - Maintain specs list showing all specs that reference the requirement
      - Track lifecycle events (introduced, implemented_by, verified_by)
      - Support serialization to/from dictionary and YAML
      - Provide merge semantics preserving lifecycle data during sync
    requirements:
      - SPEC-122.FR-001
      - SPEC-122.FR-002
    summary: |
      RequirementRecord is the core domain model representing a single requirement
      throughout its lifecycle. It combines intrinsic attributes (uid, title, kind)
      with lifecycle tracking (status, introduced, implemented_by, verified_by).
    success_criteria:
      - UID format is SPEC-ID.LABEL (e.g., SPEC-110.FR-001)
      - Status values limited to: pending, in-progress, live, retired
      - Merge operation preserves lifecycle fields from existing record
      - Round-trip serialization maintains all fields

  - id: central-registry
    name: Central Requirements Registry
    responsibilities:
      - Load and save requirements.yaml registry file
      - Store requirements keyed by uid
      - Provide atomic save operation for registry persistence
      - Support incremental updates (create/update tracking)
      - Maintain registry integrity across multiple sync operations
    requirements:
      - SPEC-122.FR-003
      - SPEC-122.NF-001
    summary: |
      RequirementsRegistry manages the central registry at .spec-driver/registry/requirements.yaml,
      providing CRUD operations and synchronization coordination.
    success_criteria:
      - Registry file uses YAML format with sorted keys
      - Load operation handles missing/empty registry gracefully
      - Save operation atomic (write to temp, rename)
      - Multiple sync operations result in consistent state

  - id: spec-synchronization
    name: Spec Synchronization
    responsibilities:
      - Extract requirements from spec markdown files using pattern matching
      - Parse structured relationship blocks for requirement lists
      - Update registry with discovered requirements (create/merge)
      - Track which specs reference each requirement
      - Support both SpecRegistry integration and direct file iteration
      - Return sync statistics (created, updated counts)
    requirements:
      - SPEC-122.FR-004
      - SPEC-122.FR-005
      - SPEC-122.NF-002
    summary: |
      Synchronizes requirements from specification documents into the central registry.
      Supports both inline requirement declarations (FR-001: text) and structured
      YAML blocks (spec.relationships) for explicit requirement listings.
    success_criteria:
      - Requirement pattern: `- FR-001: Title` or `- NF-001: Title`
      - Pattern matching case-insensitive, supports bold/italic markers
      - Relationship blocks parsed for primary/collaborator requirement lists
      - Each requirement linked to all specs that reference it
      - Sync idempotent (re-running produces same result)

  - id: change-artifact-tracking
    name: Change Artifact Tracking
    responsibilities:
      - Process delta frontmatter applies_to.requirements lists
      - Extract delta relationship blocks for implemented requirements
      - Track revision-introduced requirements from structured blocks
      - Link audit verification to requirements
      - Update requirement lifecycle fields (introduced, implemented_by, verified_by)
      - Support both frontmatter relations and inline relation markers
    requirements:
      - SPEC-122.FR-006
      - SPEC-122.FR-007
    summary: |
      Connects requirements to change artifacts (deltas, revisions, audits) by processing
      frontmatter, structured blocks, and relation markers. Maintains bidirectional links
      for requirement lifecycle tracking.
    success_criteria:
      - Delta implements relations add to requirement.implemented_by list
      - Revision introduces/moves relations set requirement.introduced field
      - Audit verifies relations add to requirement.verified_by list
      - Multiple artifacts can reference same requirement
      - Lists maintain sorted order for stable diffs

  - id: revision-block-processing
    name: Revision Block Processing
    responsibilities:
      - Parse structured revision blocks for requirement changes
      - Handle requirement moves (origin → destination spec)
      - Create placeholder records for requirements introduced in revisions
      - Apply lifecycle metadata from revision blocks
      - Update requirement specs lists based on move/add actions
      - Synchronize requirement paths when spec changes
    requirements:
      - SPEC-122.FR-007
    summary: |
      Processes structured revision blocks that declare requirement movements,
      introductions, and lifecycle updates. Supports complex requirement refactoring
      across specs with full provenance tracking.
    success_criteria:
      - Move action: requirement moves from origin spec to destination spec
      - Add action: requirement added to destination spec
      - Lifecycle fields (status, introduced_by, implemented_by, verified_by) applied
      - Origin records found by requirement ID
      - Placeholder records created with revision lifecycle metadata

  - id: requirement-movement
    name: Requirement Movement
    responsibilities:
      - Move requirement from one spec to another with uid update
      - Validate target spec exists (when SpecRegistry provided)
      - Update requirement path to match new spec location
      - Update specs list (remove old primary, add new primary)
      - Track movement origin via introduced_by field
      - Prevent duplicate requirement IDs in target spec
    requirements:
      - SPEC-122.FR-008
    summary: |
      Supports requirement refactoring by moving requirements between specs.
      Updates all related metadata and maintains lifecycle tracking.
    success_criteria:
      - New UID format: TARGET-SPEC.LABEL
      - Old UID removed from registry, new UID added
      - Requirement path updated to new spec location
      - Primary spec changed to target spec
      - Movement tracked via introduced_by field
      - Error if target requirement ID already exists

  - id: requirement-search
    name: Requirement Search & Query
    responsibilities:
      - Search by text query (uid, label, title)
      - Filter by requirement status
      - Filter by spec ID
      - Filter by implementing delta
      - Filter by introducing revision
      - Filter by verifying audit
      - Return sorted results by UID
    requirements:
      - SPEC-122.FR-009
      - SPEC-122.NF-003
    summary: |
      Provides flexible requirement querying with multiple filter dimensions.
      Supports automation and reporting workflows with consistent result ordering.
    success_criteria:
      - All filters combinable (AND semantics)
      - Text query searches uid, label, title (case-insensitive)
      - Results always sorted by UID for stable output
      - Empty filters return all requirements
      - Filters respect lifecycle links (implemented_by, verified_by, introduced)

  - id: status-management
    name: Status Management
    responsibilities:
      - Define valid requirement statuses (pending, in-progress, live, retired)
      - Validate status transitions
      - Update requirement status with validation
      - Prevent invalid status values
    requirements:
      - SPEC-122.FR-002
    summary: |
      Manages requirement lifecycle status with validation. Ensures only valid
      status values are used throughout the system.
    success_criteria:
      - Status constants exported from lifecycle module
      - set_status validates against VALID_STATUSES set
      - Error raised for invalid status values
      - Error includes list of valid statuses in message
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-122
entries:
  - artefact: VT-REQ-RECORD-001
    kind: VT
    requirement: SPEC-122.FR-001
    status: verified
    notes: |
      supekku/scripts/lib/requirements/registry_test.py::RequirementsRegistryTest
      Tests RequirementRecord model creation, serialization, merge semantics

  - artefact: VT-REQ-SYNC-001
    kind: VT
    requirement: SPEC-122.FR-004
    status: verified
    notes: |
      supekku/scripts/lib/requirements/registry_test.py::test_sync_creates_entries
      Tests sync_from_specs creates registry entries from spec requirements

  - artefact: VT-REQ-CHANGE-001
    kind: VT
    requirement: SPEC-122.FR-006
    status: verified
    notes: |
      supekku/scripts/lib/requirements/registry_test.py::test_sync_collects_change_relations
      Tests delta/revision/audit relation tracking updates lifecycle fields

  - artefact: VT-REQ-SEARCH-001
    kind: VT
    requirement: SPEC-122.FR-009
    status: verified
    notes: |
      supekku/scripts/lib/requirements/registry_test.py::test_sync_collects_change_relations
      Tests search by implemented_by and introduced_by filters

  - artefact: VT-REQ-LIFECYCLE-001
    kind: VT
    requirement: SPEC-122.FR-002
    status: verified
    notes: |
      supekku/scripts/lib/requirements/lifecycle.py
      Defines status constants and VALID_STATUSES set for validation
```

## 1. Intent & Summary

The `supekku/scripts/lib/requirements` package manages the central requirements registry and lifecycle tracking for the spec-driver framework. It extracts requirements from specification documents, tracks their implementation through change artifacts (deltas, revisions, audits), and provides comprehensive querying capabilities.

**Core Purpose**: Maintain single source of truth for all requirements across the workspace, with complete lifecycle tracking from introduction through implementation to verification.

**Design Philosophy**: Registry-centric synchronization model where requirements are parsed from specs and change artifacts, merged into a central YAML registry, and exposed via flexible search API. Pure data model (RequirementRecord) + stateful registry (RequirementsRegistry) pattern.

## 2. Stakeholders & Journeys

### Primary Users

**CLI Commands** (via SPEC-110)
- Load requirements for listing, filtering, status updates
- Trigger sync operations to rebuild registry
- Query requirements by spec, status, change artifact

**Change Management** (via SPEC-115)
- Link deltas to requirements they implement
- Track requirement introductions via revisions
- Record verification through audits

**Workspace Validation** (via SPEC-125)
- Validate requirement lifecycle completeness
- Check for orphaned requirements
- Verify bidirectional artifact links

### User Journeys

**Requirement Discovery**
1. Spec author writes requirements in spec markdown (FR-001: text)
2. User runs `spec-driver sync requirements`
3. Registry extracts requirements, assigns UIDs (SPEC-ID.LABEL)
4. Requirements queryable via `spec-driver list requirements`

**Lifecycle Tracking**
1. Delta created with `applies_to.requirements: [SPEC-110.FR-001]`
2. Sync operation links delta to requirement via `implemented_by`
3. Delta completion updates requirement status to `live`
4. Audit verification adds audit ID to requirement's `verified_by` list

**Requirement Refactoring**
1. User splits spec, needs to move requirements
2. Create revision with structured move block
3. Sync processes revision, updates requirement UIDs and specs lists
4. Old UID removed, new UID created, lifecycle preserved

## 3. Responsibilities & Requirements

### Capability Overview

The package provides three layers:
1. **Domain Model** (RequirementRecord) - immutable requirement representation
2. **Registry** (RequirementsRegistry) - CRUD operations and persistence
3. **Synchronization** - multi-source requirement extraction and lifecycle tracking

### Functional Requirements

- **FR-001**: Define RequirementRecord dataclass with uid, label, title, specs, primary_spec, kind, status, introduced, implemented_by, verified_by, path fields
- **FR-002**: Support requirement status values: pending, in-progress, live, retired
- **FR-003**: Load and save requirements registry at `.spec-driver/registry/requirements.yaml`
- **FR-004**: Extract requirements from spec markdown using pattern `- FR-NNN: Title` (case-insensitive, bold/italic tolerant)
- **FR-005**: Parse structured spec.relationships blocks for explicit requirement lists (primary, collaborators)
- **FR-006**: Process delta frontmatter applies_to.requirements and relationship blocks to link deltas to requirements
- **FR-007**: Process revision blocks for requirement moves, introductions, and lifecycle updates
- **FR-008**: Support move_requirement operation updating uid, specs, primary_spec, path, and introduced fields
- **FR-009**: Provide search API with filters: query, status, spec, implemented_by, introduced_by, verified_by

### Non-Functional Requirements

- **NF-001**: Registry file uses UTF-8 encoding and sorted YAML keys for diff stability
- **NF-002**: Sync operations idempotent (re-running produces identical registry)
- **NF-003**: Search results sorted by UID for stable output

### Operational Targets

- Registry sync completes in <5s for typical workspace (50 specs, 500 requirements)
- Memory usage <100MB for large workspaces (200 specs, 2000 requirements)
- Registry file size <1MB for typical workspace

## 4. Solution Outline

### Architecture / Components

```
requirements/
├── __init__.py           # Package exports
├── lifecycle.py          # Status constants and definitions
├── registry.py           # RequirementRecord, RequirementsRegistry, SyncStats
└── registry_test.py      # Comprehensive test suite
```

**Key Classes**:
- `RequirementRecord`: Immutable requirement representation with lifecycle tracking
- `RequirementsRegistry`: Central registry with CRUD, sync, search operations
- `SyncStats`: Statistics tracking for sync operations (created, updated counts)

**Dependencies**:
- `supekku.scripts.lib.specs` - SpecRegistry for spec iteration
- `supekku.scripts.lib.blocks` - Extracting structured YAML blocks
- `supekku.scripts.lib.relations` - Listing requirement relations
- `supekku.scripts.lib.core` - Repo root, markdown utilities

### Data & Contracts

**RequirementRecord Fields**:
```python
uid: str                    # SPEC-ID.LABEL (e.g., SPEC-110.FR-001)
label: str                  # FR-001, NF-001
title: str                  # Requirement description
specs: list[str]            # All specs referencing this requirement
primary_spec: str           # Primary owning spec
kind: str                   # "functional" or "non-functional"
status: RequirementStatus   # pending | in-progress | live | retired
introduced: str | None      # Revision ID that introduced requirement
implemented_by: list[str]   # Delta IDs implementing requirement
verified_by: list[str]      # Audit IDs verifying requirement
path: str                   # Relative path to primary spec file
```

**Registry YAML Format**:
```yaml
requirements:
  SPEC-110.FR-001:
    label: FR-001
    title: Provide unified command-line interface
    specs: [SPEC-110]
    primary_spec: SPEC-110
    kind: functional
    status: live
    introduced: RE-005
    implemented_by: [DE-012]
    verified_by: [AUD-003]
    path: specify/tech/SPEC-110/SPEC-110.md
```

**Sync API**:
```python
sync_from_specs(
  spec_dirs: Iterable[Path] | None = None,
  spec_registry: SpecRegistry | None = None,
  delta_dirs: Iterable[Path] | None = None,
  revision_dirs: Iterable[Path] | None = None,
  audit_dirs: Iterable[Path] | None = None,
) -> SyncStats
```

**Search API**:
```python
search(
  query: str | None = None,
  status: RequirementStatus | None = None,
  spec: str | None = None,
  implemented_by: str | None = None,
  introduced_by: str | None = None,
  verified_by: str | None = None,
) -> list[RequirementRecord]
```

## 5. Behaviour & Scenarios

### Primary Flows

**Sync from Specs**:
1. Iterate spec files or SpecRegistry.all_specs()
2. For each spec:
   - Extract inline requirements via regex pattern
   - Parse spec.relationships block for requirement lists
   - Create/merge RequirementRecord for each requirement
   - Track stats (created/updated)
3. Process change artifacts if provided:
   - Deltas: extract implements relations → update implemented_by
   - Revisions: extract introduces/moves relations → update introduced
   - Audits: extract verifies relations → update verified_by
4. Clean specs lists for unseen requirements
5. Save registry and return stats

**Requirement Movement**:
1. Validate source requirement exists
2. Validate target spec exists (if SpecRegistry provided)
3. Pop old record from registry
4. Update uid to TARGET-SPEC.LABEL
5. Update primary_spec and specs list
6. Update path to target spec location
7. Set introduced field if provided
8. Store updated record under new uid

**Revision Block Processing**:
1. Load revision blocks from file
2. For each requirement in block:
   - Find existing record by origin or create placeholder
   - Update uid if moving
   - Update destination spec and additional_specs
   - Apply lifecycle fields (status, introduced_by, implemented_by, verified_by)
   - Update path to match destination spec
3. Track stats and continue

### Error Handling / Guards

**Graceful Degradation**:
- Missing registry file → empty registry (not error)
- Invalid YAML in spec → skip spec, continue sync
- Missing spec in move operation → error with clear message
- Duplicate requirement ID in target spec → error with clear message

**Validation**:
- Status values validated against VALID_STATUSES
- UIDs validated to match SPEC-ID.LABEL pattern
- Paths validated to be relative to repo root

**Error Messages**:
- Include requirement UID in all errors
- Include list of valid statuses for status errors
- Include spec ID for missing spec errors

## 6. Quality & Verification

### Testing Strategy

**Unit Tests** (registry_test.py):
- RequirementRecord creation, serialization, merge
- Registry load/save operations
- Sync from specs (pattern matching, relationship blocks)
- Change artifact processing (deltas, revisions, audits)
- Requirement movement
- Search operations (all filter combinations)
- Status validation

**Integration Tests**:
- Full workspace sync (specs + changes)
- Revision block processing with placeholder creation
- Requirement movement with SpecRegistry

**Property Tests**:
- Sync idempotency (sync twice → same result)
- Round-trip serialization (record → dict → record)
- Merge commutativity (A.merge(B) preserves lifecycle)

### Observability & Analysis

**Logging**:
- Info: Sync stats (created/updated counts)
- Warning: Unparseable requirement lines
- Error: Invalid revision blocks, missing specs

**Metrics** (for future):
- Sync duration by artifact type
- Requirements per spec histogram
- Lifecycle status distribution

### Security & Compliance

**File System Access**:
- Registry writes atomic (temp file + rename)
- UTF-8 encoding enforced for YAML files
- Path traversal prevented via relative path validation

**Data Integrity**:
- UID uniqueness enforced
- Lifecycle field lists maintain sorted order
- Specs lists deduplicated

### Verification Coverage

See `supekku:verification.coverage@v1` block above for detailed test coverage mapping.

### Acceptance Gates

- All tests pass (pytest)
- Ruff linting passes with zero warnings
- Pylint score meets threshold
- Sync idempotency verified (sync twice produces identical registry)
- Memory usage <100MB for large workspace test

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

**Upstream Dependencies**:
- SPEC-123: SpecRegistry for spec iteration during sync
- SPEC-115: Change artifact models and registries
- SPEC-TBD (core.repo): Repository root detection
- SPEC-TBD (core.spec_utils): Markdown file loading
- SPEC-TBD (blocks): Relationship/revision block parsing

**Downstream Consumers**:
- SPEC-110: CLI commands (list requirements, sync, set-status)
- SPEC-120: Formatters for requirement display
- SPEC-125: Workspace validation (lifecycle completeness)

### Risks & Mitigations

**Risk**: Requirement pattern matching too strict
- Mitigation: Case-insensitive, tolerates bold/italic markers, broad whitespace handling

**Risk**: Registry merge conflicts in concurrent edits
- Mitigation: Atomic writes, single source of truth (specs), rerun sync to rebuild

**Risk**: Large workspace performance degradation
- Mitigation: Stream processing, early filtering, lazy loading where possible

### Known Gaps / Debt

- Requirement dependencies/relationships not modeled (future: requirements.depends_on field)
- No requirement version history (future: audit trail of status changes)
- Pattern matching doesn't support multi-line requirements (acceptable trade-off for simplicity)
- No validation that requirement UIDs in change artifacts exist in registry (future: workspace validator check)

### Open Decisions / Questions

- Should requirements have explicit version numbers? (Current: no, rely on lifecycle tracking)
- Should requirement movement be auditable beyond introduced field? (Current: no, sufficient for now)
- Should status transitions be constrained (e.g., pending → in-progress → live)? (Current: no, allow any transition)
