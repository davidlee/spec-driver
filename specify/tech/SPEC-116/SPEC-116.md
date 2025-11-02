---
id: SPEC-116
slug: frontmatter-metadata-registry
name: supekku/scripts/lib/core/frontmatter_metadata Specification
created: '2025-11-02'
updated: '2025-11-03'
status: draft
kind: spec
responsibilities:
- Provide metadata-driven frontmatter validation schema definitions for all artifact kinds
- Define field schemas with types, patterns, enums, and validation rules using BlockMetadata
- Maintain artifact-specific metadata extending base frontmatter schema
- Enable JSON Schema generation from metadata for tooling and documentation
- Support dual-validation compatibility between new metadata-driven and legacy validators
aliases:
- frontmatter-metadata
- frontmatter-registry
packages:
- supekku/scripts/lib/core/frontmatter_metadata
sources:
- language: python
  identifier: supekku/scripts/lib/core/frontmatter_metadata
  module: supekku.scripts.lib.core.frontmatter_metadata
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

# SPEC-116 – supekku/scripts/lib/core/frontmatter_metadata

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-116
requirements:
  primary:
    - SPEC-116.FR-001
    - SPEC-116.FR-002
    - SPEC-116.FR-003
    - SPEC-116.FR-004
    - SPEC-116.FR-005
    - SPEC-116.FR-006
    - SPEC-116.NF-001
    - SPEC-116.NF-002
    - SPEC-116.NF-003
  collaborators: []
interactions:
  - spec: SPEC-TBD
    type: uses
    description: Uses blocks.metadata (BlockMetadata, FieldMetadata) for schema definition structure
  - spec: SPEC-TBD
    type: uses
    description: Uses blocks.metadata.MetadataValidator for runtime validation
  - spec: SPEC-TBD
    type: used_by
    description: Used by frontmatter validators across all artifact creation and validation workflows
  - spec: SPEC-TBD
    type: used_by
    description: Used by JSON Schema generators for documentation and tooling integration
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: SPEC-116
capabilities:
  - id: base-schema-definition
    name: Base Frontmatter Schema Definition
    responsibilities:
      - Define common frontmatter fields (id, name, slug, kind, status, lifecycle, dates)
      - Specify field types, patterns, and validation rules for base schema
      - Provide examples for minimal and complete frontmatter usage
      - Support relationship edges with type enums and target validation
    requirements:
      - SPEC-116.FR-001
      - SPEC-116.NF-001
    summary: |
      Defines BASE_FRONTMATTER_METADATA containing the core fields common to all
      spec-driver artifacts, including identity, lifecycle, ownership, and relationship edges.
    success_criteria:
      - Base schema validates all common frontmatter fields consistently
      - All artifact-specific schemas successfully extend base schema
      - Examples in base schema are valid and comprehensive

  - id: artifact-specific-schemas
    name: Artifact-Specific Schema Definitions
    responsibilities:
      - Define metadata for each artifact kind (spec, prod, delta, requirement, etc.)
      - Extend base schema with artifact-specific fields
      - Document field purposes, patterns, and validation rules per artifact
      - Maintain consistency in field naming and type patterns across artifacts
    requirements:
      - SPEC-116.FR-002
      - SPEC-116.FR-003
      - SPEC-116.NF-002
    summary: |
      Provides 14 artifact-specific metadata modules (spec, prod, delta, design_revision,
      policy, standard, verification, problem, risk, requirement, issue, audit, plan, phase/task).
      Each extends BASE_FRONTMATTER_METADATA with domain-specific fields.
    success_criteria:
      - Each artifact kind has dedicated metadata module
      - All artifact schemas properly extend base schema
      - Field definitions are consistent and complete

  - id: metadata-registry
    name: Frontmatter Metadata Registry
    responsibilities:
      - Maintain centralized registry mapping artifact kinds to metadata definitions
      - Provide lookup function for retrieving metadata by kind
      - Handle fallback to base metadata for unknown kinds
      - Support shared schemas for related artifact types (phase/task share plan schema)
    requirements:
      - SPEC-116.FR-004
      - SPEC-116.NF-003
    summary: |
      Implements FRONTMATTER_METADATA_REGISTRY dictionary and get_frontmatter_metadata()
      function providing centralized access to all metadata definitions.
    success_criteria:
      - Registry contains entries for all 14 artifact kinds
      - Lookup function returns correct metadata for valid kinds
      - Fallback to base metadata works for unknown kinds
      - Shared schemas properly mapped (phase/task → plan)

  - id: validation-support
    name: Validation Support Infrastructure
    responsibilities:
      - Enable metadata-driven validation via MetadataValidator
      - Support dual-validation compatibility testing with legacy validators
      - Provide clear error messages for validation failures
      - Enable JSON Schema generation from metadata
    requirements:
      - SPEC-116.FR-005
      - SPEC-116.NF-001
    summary: |
      Metadata definitions support runtime validation through MetadataValidator and
      enable JSON Schema generation for tooling. Comprehensive tests ensure compatibility
      between new metadata-driven and legacy validation approaches.
    success_criteria:
      - All metadata schemas validate correct data
      - All metadata schemas reject invalid data consistently
      - Dual-validation tests pass for all artifact types
      - Generated JSON Schema matches metadata definitions

  - id: comprehensive-testing
    name: Comprehensive Testing Coverage
    responsibilities:
      - Test each metadata module with valid and invalid cases
      - Verify dual-validation compatibility with legacy validators
      - Test edge cases (empty fields, wrong types, missing required fields)
      - Ensure test coverage for all artifact kinds
    requirements:
      - SPEC-116.FR-006
      - SPEC-116.NF-003
    summary: |
      Each metadata module has corresponding *_test.py file with comprehensive test
      coverage including valid cases, invalid cases, edge cases, and dual-validation
      compatibility verification.
    success_criteria:
      - Each metadata module has dedicated test file
      - Tests cover valid, invalid, and edge cases
      - Dual-validation tests confirm compatibility
      - All tests pass consistently
```

## 1. Intent & Scope

### Purpose

The `frontmatter_metadata` package provides **metadata-driven schema definitions** for frontmatter validation across all spec-driver artifacts. It follows the metadata-driven validation pattern, where schemas are defined declaratively using `BlockMetadata` and `FieldMetadata` structures, enabling both runtime validation and JSON Schema generation for tooling integration.

This package serves as the **single source of truth** for frontmatter field definitions, replacing ad-hoc validation logic with centralized, declarative schemas.

### In Scope

- Base frontmatter schema common to all artifacts
- Artifact-specific metadata modules for 14 artifact kinds
- Centralized registry for metadata lookup by artifact kind
- Support for dual-validation compatibility testing
- Comprehensive test coverage for all metadata modules

### Out of Scope

- Actual validation logic implementation (delegated to `blocks.metadata.MetadataValidator`)
- JSON Schema generation implementation (delegated to schema generator tooling)
- Frontmatter parsing from markdown files (handled by frontmatter parsers)
- Artifact creation workflows (handled by CLI and creation scripts)

## 2. System Responsibilities

### R1: Base Schema Definition

Provide `BASE_FRONTMATTER_METADATA` defining common fields for all artifacts:
- Identity fields: `id`, `name`, `slug`, `kind`, `status`
- Lifecycle fields: `lifecycle`, `created`, `updated`
- Ownership fields: `owners`, `auditers`
- Discovery fields: `source`, `summary`, `tags`
- Relationship edges: `relations` with typed edges

### R2: Artifact-Specific Schemas

Provide metadata modules for each artifact kind:
- **spec**: Specifications with responsibilities, concerns, principles, hypotheses
- **prod**: Product specs with user problems, hypotheses, outcomes
- **delta**: Change bundles with applies_to, context_inputs, outcome_summary, risk_register
- **design_revision**: Architecture patches with current/target state
- **plan**: Implementation plans with phases and tasks
- **policy**: Standards and policies
- **standard**: Technical standards
- **verification**: Verification artifacts (VT, VH, VA)
- **requirement**: Requirements with lifecycle metadata
- **problem**: Problem statements from backlog
- **risk**: Risk register entries
- **issue**: Backlog issues
- **audit**: Audit reports

### R3: Centralized Registry

Maintain `FRONTMATTER_METADATA_REGISTRY` mapping artifact kinds to metadata:
- Dictionary structure: `{kind: BlockMetadata}`
- Lookup function: `get_frontmatter_metadata(kind) -> BlockMetadata`
- Fallback to base metadata for unknown kinds
- Shared schema support (phase/task → plan)

### R4: Validation Support

Enable metadata-driven validation:
- Metadata structures compatible with `MetadataValidator`
- Support for JSON Schema generation
- Clear field descriptions for error messages
- Comprehensive examples for each schema

### R5: Extensibility

Support schema evolution and extension:
- Artifact schemas extend base schema via dict unpacking
- Optional fields allow forward compatibility
- Relationship edges support additional fields beyond validated set
- Version metadata tracks schema versions

### R6: Testing Infrastructure

Provide comprehensive test coverage:
- Dual-validation tests comparing new and legacy validators
- Valid/invalid case testing for all schemas
- Edge case coverage (empty fields, wrong types, missing required)
- Test helpers for common validation patterns

## 3. Architecture & Design

### Package Structure

```
supekku/scripts/lib/core/frontmatter_metadata/
├── __init__.py           # Registry and public API
├── base.py              # BASE_FRONTMATTER_METADATA
├── spec.py              # SPEC_FRONTMATTER_METADATA
├── prod.py              # PROD_FRONTMATTER_METADATA
├── delta.py             # DELTA_FRONTMATTER_METADATA
├── design_revision.py   # DESIGN_REVISION_FRONTMATTER_METADATA
├── plan.py              # PLAN_FRONTMATTER_METADATA
├── policy.py            # POLICY_FRONTMATTER_METADATA
├── standard.py          # STANDARD_FRONTMATTER_METADATA
├── verification.py      # VERIFICATION_FRONTMATTER_METADATA
├── requirement.py       # REQUIREMENT_FRONTMATTER_METADATA
├── problem.py           # PROBLEM_FRONTMATTER_METADATA
├── risk.py              # RISK_FRONTMATTER_METADATA
├── issue.py             # ISSUE_FRONTMATTER_METADATA
├── audit.py             # AUDIT_FRONTMATTER_METADATA
├── base_test.py         # Base schema tests
├── spec_test.py         # Spec schema tests
└── ...                  # Additional *_test.py files
```

### Schema Definition Pattern

All metadata modules follow consistent pattern:

```python
from supekku.scripts.lib.blocks.metadata import BlockMetadata, FieldMetadata
from .base import BASE_FRONTMATTER_METADATA

ARTIFACT_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.artifact_kind",
  description="Frontmatter fields for artifact_kind artifacts",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Extend base
    # Artifact-specific fields
    "custom_field": FieldMetadata(
      type="string",
      required=False,
      description="Purpose of this field"
    ),
  },
  examples=[
    # Valid examples demonstrating usage
  ]
)
```

### Field Type System

Supported field types from `BlockMetadata`:
- `string`: Text with optional pattern validation
- `int`: Integer values
- `bool`: Boolean flags
- `enum`: Fixed set of allowed values
- `const`: Fixed constant value
- `object`: Nested structure with properties
- `array`: List of items with item schema

### Extension Strategy

Artifact schemas extend base via dictionary unpacking:
```python
fields={
  **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
  # Add artifact-specific fields
}
```

This ensures:
- All base fields inherited automatically
- Artifact-specific fields added cleanly
- Base schema changes propagate to all artifacts
- No duplication of base field definitions

## 4. Interfaces & Contracts

### Public API

```python
# Main registry access
def get_frontmatter_metadata(kind: str | None = None) -> BlockMetadata:
    """Get metadata for frontmatter kind.

    Args:
      kind: Artifact kind or None for base

    Returns:
      BlockMetadata for specified kind, or base if not found
    """

# Registry dictionary
FRONTMATTER_METADATA_REGISTRY: dict[str, BlockMetadata]

# Individual metadata exports
BASE_FRONTMATTER_METADATA: BlockMetadata
SPEC_FRONTMATTER_METADATA: BlockMetadata
PROD_FRONTMATTER_METADATA: BlockMetadata
# ... etc for all artifact kinds
```

### Usage Pattern

```python
from supekku.scripts.lib.core.frontmatter_metadata import get_frontmatter_metadata
from supekku.scripts.lib.blocks.metadata import MetadataValidator

# Get metadata for artifact kind
metadata = get_frontmatter_metadata("spec")

# Use with validator
validator = MetadataValidator(metadata)
errors = validator.validate(frontmatter_dict)

if errors:
    # Handle validation errors
    for error in errors:
        print(f"Validation error: {error}")
```

## 5. System Invariants

### I1: Schema Completeness
- Every artifact kind in base `kind` enum has corresponding metadata module
- Registry contains entry for every supported artifact kind
- All metadata modules export properly structured `BlockMetadata`

### I2: Base Schema Inheritance
- All artifact-specific schemas include all base fields
- Base field definitions remain consistent across all artifacts
- Extension via dict unpacking preserves all base properties

### I3: Validation Consistency
- Metadata schemas produce same validation outcomes as legacy validators
- Dual-validation tests pass for all artifact kinds
- Error messages clear and actionable

### I4: Type Safety
- All field types match supported `FieldMetadata` types
- Enum fields define complete set of allowed values
- Required fields explicitly marked in metadata
- Pattern validation uses valid regex

### I5: Testing Coverage
- Every metadata module has corresponding test file
- Tests cover valid, invalid, and edge cases
- Dual-validation compatibility verified for all schemas

## 6. Quality Requirements

### Performance

**NF-001: Fast Metadata Lookup**
- `get_frontmatter_metadata()` completes in <1ms
- Registry lookup is O(1) dictionary access
- No runtime schema compilation overhead

### Maintainability

**NF-002: Clear Schema Definitions**
- Field descriptions explain purpose and usage
- Examples demonstrate valid usage patterns
- Schema structure follows consistent patterns
- Minimal code duplication across modules

### Reliability

**NF-003: Validation Correctness**
- Metadata schemas reject all invalid frontmatter
- Metadata schemas accept all valid frontmatter
- Dual-validation compatibility maintained
- No false positives or false negatives

## 7. Testing Strategy

### Test Organization

Each metadata module has dedicated test file following pattern:
```
{artifact}_test.py
  - Test valid minimal frontmatter
  - Test valid complete frontmatter
  - Test invalid cases (missing required, wrong types)
  - Test edge cases (empty arrays, etc.)
  - Dual-validation compatibility tests
```

### Dual-Validation Testing

Tests compare new metadata-driven validator with legacy validator:
```python
def _validate_both(self, data: dict) -> tuple[str | None, list[str]]:
    # Old validator
    old_error = None
    try:
        validate_frontmatter(data)
    except FrontmatterValidationError as e:
        old_error = str(e)

    # New validator
    new_validator = MetadataValidator(metadata)
    new_errors = [str(err) for err in new_validator.validate(data)]

    return old_error, new_errors
```

### Test Coverage Requirements

- All required fields tested for presence validation
- All enum fields tested for allowed values
- All pattern fields tested with valid/invalid patterns
- All object/array fields tested for structure validation
- Edge cases covered (empty strings, null values, wrong types)

## 8. Dependencies

### Upstream Dependencies

- `supekku.scripts.lib.blocks.metadata` - BlockMetadata, FieldMetadata, MetadataValidator
- Standard library: `dataclasses`, `typing`

### Downstream Consumers

- Frontmatter validators across all artifact workflows
- JSON Schema generators for documentation
- CLI validation in create/update commands
- Registry sync validation
- Workspace validator integrity checks

## 9. Change History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-02 | Initial specification created during backfill effort |

## 10. Related Artifacts

- **SPEC-TBD**: blocks.metadata specification (BlockMetadata, FieldMetadata, MetadataValidator)
- **SPEC-110**: supekku/cli specification (uses frontmatter validation)
- **SPEC-123**: SpecRegistry specification (validates spec frontmatter)
- **SPEC-117**: DecisionRegistry specification (validates ADR frontmatter)
- **SPEC-122**: RequirementsRegistry specification (validates requirement frontmatter)
- **SPEC-115**: ChangeRegistry specification (validates delta/revision/audit frontmatter)
