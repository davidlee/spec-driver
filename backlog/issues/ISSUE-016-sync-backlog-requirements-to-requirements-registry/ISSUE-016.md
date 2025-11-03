---
id: ISSUE-016
name: Sync backlog requirements to requirements registry
created: '2025-11-03'
updated: '2025-11-03'
status: open
kind: issue
categories:
  - process_gap
  - tooling_enhancement
severity: p2
impact: process
linked_deltas: []
related_requirements: []
---

# ISSUE-016 – Sync backlog requirements to requirements registry

## Problem Statement

Requirements defined in backlog issues (like ISSUE-013) are invisible to the requirements registry and tooling. This creates several problems:

1. **Discovery Gap**: Running `spec-driver list requirements` doesn't show requirements from backlog issues, only from specs
2. **Traceability Gap**: Can't easily see which requirements are implemented, verified, or orphaned when they live in issues
3. **Filtering Limitation**: No way to filter requirements by source kind (prod spec, tech spec, issue, problem, etc.)
4. **Migration Friction**: No tooling support for promoting requirements from backlog issues to formal specs
5. **Coverage Blind Spot**: Verification coverage tracking can't link to issue-based requirements

**Current State**:
- Requirements registry only syncs from `specify/product/` and `specify/tech/` specs
- Backlog issues can define requirements (e.g., `ISSUE-013.FR-013.001`) but they're orphaned
- No way to see the full picture of all requirements across the system

**Desired State**:
- Requirements registry includes all requirements from all sources (specs, issues, problems, improvements)
- Can filter by source kind: `--kind spec`, `--kind issue`, `--kind problem`, etc.
- Tooling to migrate requirements from backlog to specs when they mature
- Full traceability and coverage tracking across all requirement sources

## Context

**Discovery**: While completing DE-012, we defined requirements in ISSUE-013:
- FR-013.001: IP Schema Restoration
- FR-013.002: Phase Creation with Criteria Copy
- FR-013.003: Drift Detection Warning
- NF-013.001: Backward Compatibility

These requirements are properly structured and verified, but don't appear in `spec-driver list requirements` output.

**Impact**:
- Planners can't see complete requirement landscape
- Coverage analysis is incomplete
- Requirement migration requires manual work
- Inconsistent requirement discovery patterns

## Proposed Solution

### 1. Extend Requirements Registry to Sync Backlog Sources

Add backlog artifact scanning to `RequirementsRegistry.sync()`:

```python
# In requirements/registry.py
def sync(self):
  """Sync requirements from specs AND backlog artifacts."""
  self._sync_spec_requirements()    # Existing
  self._sync_issue_requirements()   # New
  self._sync_problem_requirements() # New
  # ... other backlog sources
```

**Requirement ID Pattern**:
- Specs: `SPEC-100.FR-001`, `PROD-005.NF-002`
- Issues: `ISSUE-013.FR-013.001`, `ISSUE-013.NF-013.001`
- Problems: `PROB-001.FR-001`
- Improvements: `IMP-001.FR-001`

### 2. Add Source Kind Metadata to Requirement Records

```python
@dataclass
class RequirementRecord:
  id: str
  spec_id: str  # Could be SPEC-100, ISSUE-013, PROB-001, etc.
  kind: str     # FR, NF, etc.
  statement: str
  source_kind: str  # NEW: "spec", "issue", "problem", "improvement"
  source_type: str  # NEW: "prod", "tech", "backlog"
  # ... existing fields
```

### 3. Add Filtering by Source

**CLI Support**:
```bash
# Show all requirements
spec-driver list requirements

# Show only spec-sourced requirements
spec-driver list requirements --source-kind spec

# Show only backlog-sourced requirements
spec-driver list requirements --source-kind issue

# Show prod specs only
spec-driver list requirements --source-type prod
```

### 4. Requirement Migration Tooling

**New Command**: `spec-driver migrate requirement`

```bash
# Migrate requirement from issue to spec
spec-driver migrate requirement ISSUE-013.FR-013.001 --to SPEC-114

# Would:
# 1. Extract requirement from ISSUE-013
# 2. Add to target spec (SPEC-114)
# 3. Update requirement ID references in deltas, verification coverage
# 4. Mark original as superseded/migrated
```

### 5. Registry Schema Updates

Update `.spec-driver/registry/requirements.yaml` to include:
```yaml
requirements:
  ISSUE-013.FR-013.001:
    id: ISSUE-013.FR-013.001
    spec_id: ISSUE-013
    kind: FR
    source_kind: issue
    source_type: backlog
    statement: "The plan.overview@v1 schema SHALL support..."
    status: verified
    introduced_by: ISSUE-013
    implemented_by: [DE-012]
    verified_by: [VT-SCHEMA-013-001]
    # ... etc
```

## Requirements

### FR-016.001: Sync Backlog Requirements
**Statement**: The requirements registry SHALL sync requirements from backlog issues, problems, and improvements in addition to specs.

**Acceptance Criteria**:
- `RequirementsRegistry.sync()` discovers requirements in `backlog/issues/`, `backlog/problems/`, `backlog/improvements/`
- Requirements parsed from structured sections (same format as specs)
- Requirement IDs follow pattern: `{ARTIFACT_ID}.{KIND}-{NUMBER}`
- Registry tracks source_kind and source_type metadata

**Verification**: VT-SYNC-016-001 (unit tests for backlog requirement discovery)

### FR-016.002: Filter Requirements by Source
**Statement**: The `list requirements` command SHALL support filtering by source_kind and source_type.

**Acceptance Criteria**:
- `--source-kind {spec|issue|problem|improvement}` filters by artifact kind
- `--source-type {prod|tech|backlog}` filters by source type
- Multiple filters can be combined
- Default shows all sources

**Verification**: VT-FILTER-016-002 (CLI tests for filtering)

### FR-016.003: Requirement Migration Command
**Statement**: The system SHALL provide a command to migrate requirements from backlog artifacts to specs.

**Acceptance Criteria**:
- `migrate requirement SOURCE_ID --to TARGET_SPEC` migrates requirement
- Updates all references (deltas, verification coverage, etc.)
- Marks source as migrated/superseded
- Validates target spec exists
- Preserves verification history

**Verification**: VT-MIGRATE-016-003 (migration command tests)

### FR-016.004: Coverage Tracking for Backlog Requirements
**Statement**: Verification coverage tracking SHALL support backlog-sourced requirements.

**Acceptance Criteria**:
- Verification blocks can reference `ISSUE-XXX.FR-YYY` requirements
- `show delta --json` includes backlog requirement coverage
- Coverage validation works for all source kinds
- Status tracking (planned/verified/etc.) works uniformly

**Verification**: VT-COVERAGE-016-004 (coverage tracking tests)

### NF-016.001: Backward Compatibility
**Statement**: Registry changes MUST NOT break existing spec-only workflows.

**Acceptance Criteria**:
- Existing requirement IDs still work (`SPEC-100.FR-001`)
- Default `list requirements` behavior unchanged (shows all)
- Existing verification coverage continues working
- Migration is opt-in, not required

**Verification**: VT-COMPAT-016-001 (regression test suite)

## Affected Components

**Core**:
- `supekku/scripts/lib/requirements/registry.py` - Extend sync logic
- `supekku/scripts/lib/requirements/models.py` - Add source metadata
- `supekku/scripts/lib/backlog/registry.py` - Issue/problem discovery
- `.spec-driver/registry/requirements.yaml` - Schema extension

**CLI**:
- `supekku/cli/list.py` - Add filtering options
- New: `supekku/cli/migrate.py` - Requirement migration command

**Validation**:
- `supekku/scripts/lib/validation/validator.py` - Support backlog requirements
- `supekku/scripts/lib/changes/coverage_check.py` - Handle all source kinds

**Tests**:
- `supekku/scripts/lib/requirements/registry_test.py` - Sync tests
- `supekku/cli/migrate_test.py` - Migration tests
- Integration tests for end-to-end workflows

## Success Criteria

- [ ] `spec-driver list requirements` shows requirements from issues, problems, improvements
- [ ] Can filter by `--source-kind issue` to see only issue-based requirements
- [ ] ISSUE-013 requirements appear in registry and can be tracked
- [ ] `migrate requirement` command successfully moves requirements between artifacts
- [ ] Verification coverage works uniformly across all requirement sources
- [ ] All 1300+ existing tests still pass (backward compatibility)
- [ ] Documentation updated with backlog requirement patterns

## Notes

**Migration Strategy**:
- Phase 1: Read-only sync (discovery + display)
- Phase 2: Filtering support
- Phase 3: Migration tooling
- Phase 4: Advanced features (bulk migration, automatic promotion rules)

**Design Decisions**:
- Use same requirement format in backlog as in specs (consistency)
- Source kind/type as metadata, not separate registries (unified view)
- Migration preserves history via explicit links (traceability)

**Future Enhancements**:
- Automatic requirement promotion (issue → problem → spec)
- Requirement maturity lifecycle tracking
- Requirement coverage dashboards by source
- Orphaned requirement detection across all sources

