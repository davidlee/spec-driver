---
id: PROD-004
slug: frontmatter-metadata-validation
name: Frontmatter Metadata Validation
created: '2025-11-02'
updated: '2025-11-02'
status: draft
kind: prod
aliases: []
relations:
  - type: implements
    target: SPEC-036
    nature: Replaces imperative validation with metadata-driven validation
  - type: enables
    target: PROD-003
    nature: Provides validation infrastructure for policy/standard frontmatter
guiding_principles:
  - Metadata as single source of truth for validation logic
  - Declarative schemas enable agent understanding via JSON Schema
  - Consistency across all artifact kinds (specs, deltas, policies, etc.)
  - Backward compatibility during migration to prevent breakage
assumptions:
  - Phases 1-5 metadata migration patterns are proven and stable
  - All 11 frontmatter kinds documented in supekku/about/frontmatter-schema.md
  - Existing code uses FrontmatterValidationResult and can be gradually migrated
  - JSON Schema output will benefit agents and future external tooling
---

# PROD-004 – Frontmatter Metadata Validation

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-004
requirements:
  primary:
    - PROD-004.FR-001
    - PROD-004.FR-002
    - PROD-004.FR-003
    - PROD-004.FR-004
    - PROD-004.FR-005
    - PROD-004.FR-006
    - PROD-004.NF-001
    - PROD-004.NF-002
    - PROD-004.NF-003
  collaborators: []
interactions:
  - with: SPEC-036
    nature: Replaces imperative frontmatter_schema.py validator with metadata-driven system
  - with: PROD-003
    nature: Provides validation foundation for policy and standard frontmatter schemas
  - with: PROD-001
    nature: Improved metadata validation supports spec creation workflow
  - with: PROD-002
    nature: Improved metadata validation supports delta creation workflow
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-004
capabilities:
  - id: metadata-driven-validation
    name: Metadata-Driven Frontmatter Validation
    responsibilities:
      - Validate frontmatter using declarative metadata definitions
      - Support all 11 frontmatter kinds with kind-specific schemas
      - Generate consistent, detailed validation error messages
      - Maintain compatibility with existing validation API
    requirements:
      - PROD-004.FR-001
      - PROD-004.FR-002
      - PROD-004.NF-001
    summary: >-
      Replaces imperative validation code with metadata-driven validation,
      enabling consistent validation across all artifact kinds. Each frontmatter
      kind (spec, delta, requirement, verification, problem, risk, policy,
      standard, etc.) has a declarative schema that drives validation behavior.
    success_criteria:
      - All 11 frontmatter kinds validate correctly via metadata
      - Validation errors are clear and actionable
      - No regressions from imperative validator behavior
  - id: json-schema-generation
    name: JSON Schema Generation for Agents
    responsibilities:
      - Generate JSON Schema from frontmatter metadata definitions
      - Enable agents to understand frontmatter structure and constraints
      - Support CLI access to schemas for all frontmatter kinds
      - Provide examples within schemas for agent guidance
    requirements:
      - PROD-004.FR-003
      - PROD-004.FR-004
      - PROD-004.NF-002
    summary: >-
      Agents writing YAML frontmatter benefit from accurate JSON Schema
      documentation generated directly from metadata definitions. This ensures
      agents understand required fields, valid enum values, nested structures,
      and validation patterns without manual documentation drift.
    success_criteria:
      - JSON Schema output matches metadata definition exactly
      - Agents can query schemas via CLI commands
      - Schema examples demonstrate valid frontmatter structure
      - Zero documentation drift between metadata and schemas
  - id: gradual-migration
    name: Gradual Migration Path
    responsibilities:
      - Support dual implementation period during migration
      - Maintain backward compatibility with existing code
      - Enable opt-in migration per code path
      - Deprecate imperative validator only after full migration
    requirements:
      - PROD-004.FR-005
      - PROD-004.FR-006
      - PROD-004.NF-003
    summary: >-
      Migration from imperative to metadata-driven validation happens gradually
      without breaking existing code. Both validators coexist during transition,
      allowing each call site to opt into new validation independently. Full
      deprecation occurs only after all code paths migrate successfully.
    success_criteria:
      - No breaking changes during migration period
      - Each code path opts in independently
      - Dual-validation tests confirm behavioral equivalence
      - Clear deprecation warnings before removal
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-004
entries:
  - artefact: VT-001
    kind: VT
    requirement: PROD-004.FR-001
    status: planned
    notes: Comprehensive test suite covering all 11 frontmatter kinds with valid/invalid cases
  - artefact: VT-002
    kind: VT
    requirement: PROD-004.FR-002
    status: planned
    notes: Kind-specific validation tests ensuring unique field requirements enforced
  - artefact: VT-003
    kind: VT
    requirement: PROD-004.FR-003
    status: planned
    notes: JSON Schema generation tests for all frontmatter kinds
  - artefact: VT-004
    kind: VT
    requirement: PROD-004.FR-004
    status: planned
    notes: CLI integration tests for schema show frontmatter.* commands
  - artefact: VT-005
    kind: VT
    requirement: PROD-004.FR-005
    status: planned
    notes: Backward compatibility tests comparing old and new validator outputs
  - artefact: VT-006
    kind: VT
    requirement: PROD-004.NF-001
    status: planned
    notes: Dual-validation pattern tests ensuring zero behavioral regressions
```

## 1. Intent & Summary

### Problem / Purpose

Frontmatter validation currently uses imperative code (`frontmatter_schema.py`) which:
- Only validates base fields common to all artifacts
- Lacks kind-specific validation (all kinds use same base rules)
- Cannot generate JSON Schema for agent consumption
- Hides validation logic in procedural code rather than declarative metadata

This creates friction for:
- **Developers** extending frontmatter schemas (must edit validation code)
- **Agents** writing YAML frontmatter (no schema documentation available)
- **Architects/Team Leads** understanding validation rules (buried in code)
- **Tooling maintainers** keeping documentation synchronized with implementation

The metadata-driven approach proven in Phases 1-5 (YAML block validators) provides:
- Declarative schemas as single source of truth
- JSON Schema generation for agent guidance
- Self-documenting validation logic
- Consistency across all validation

### Value Signals

**Developer Productivity**:
- Reduce time to add new frontmatter kinds from hours to minutes
- Zero documentation drift between schemas and validation
- Clear validation errors guide corrections

**Agent Effectiveness**:
- Agents receive accurate JSON Schema for all frontmatter kinds
- Reduced validation failures when agents write frontmatter YAML
- Self-service schema discovery via CLI

**System Quality**:
- Comprehensive kind-specific validation (not just base fields)
- 275-440 tests across 11 schemas ensuring correctness
- Backward compatibility maintained throughout migration

### Guiding Principles

1. **Metadata as truth**: Validation logic lives in metadata definitions, not imperative code
2. **Declarative over imperative**: Schemas describe constraints; engine enforces them
3. **Consistency across kinds**: All 11 frontmatter kinds follow same metadata pattern
4. **Agent-friendly**: JSON Schema enables agent understanding and reduces errors
5. **Gradual migration**: No breaking changes; dual implementation until fully migrated

### Change History

- **2025-11-02**: Initial specification created following Phases 1-5 metadata migration pattern
- Based on proven approach from revision block validator (Phase 5)
- Addresses TODO items in supekku/scripts/lib/TODO.md lines 60-94

## 2. Stakeholders & Journeys

### Personas / Actors

**Developer (extending schemas)**:
- **Goals**: Add new frontmatter kind or extend existing kind with minimal friction
- **Pains**: Currently must edit imperative validation code, easy to introduce bugs
- **Expectations**: Declarative metadata definition that self-validates

**Agent (writing frontmatter YAML)**:
- **Goals**: Generate valid frontmatter for specs, deltas, policies, etc.
- **Pains**: No JSON Schema documentation available, trial-and-error validation
- **Expectations**: Accurate schema via CLI query before writing YAML

**Architect/Team Lead (understanding system)**:
- **Goals**: Understand validation rules for governance and tooling decisions
- **Pains**: Validation logic buried in procedural code, hard to extract rules
- **Expectations**: Readable metadata definitions serving as documentation

**Maintainer (ensuring quality)**:
- **Goals**: Prevent regressions during migration, ensure comprehensive validation
- **Pains**: Risk of breaking existing code during validator replacement
- **Expectations**: Dual-validation tests confirming behavioral equivalence

### Primary Journeys / Flows

**Journey 1: Agent queries schema before writing frontmatter**

**Given** an agent needs to create a delta artifact with frontmatter
**When** agent runs `spec-driver schema show frontmatter.delta --format=json-schema`
**Then** agent receives complete JSON Schema including:
- Required fields (id, name, slug, kind, status, created, updated, applies_to, context_inputs)
- Optional fields (summary, tags, relations, risk_register, outcome_summary)
- Field types, patterns, and nested structures
- Enum values for status, kind, relation types
- Examples demonstrating valid structure

**Journey 2: Developer adds new frontmatter kind**

**Given** a developer needs to add frontmatter validation for a new artifact kind
**When** developer creates `supekku/scripts/lib/core/frontmatter_metadata/newkind.py`
**Then** developer:
1. Defines `NEWKIND_FRONTMATTER_METADATA` using FieldMetadata composition
2. Includes base fields via `**BASE_FRONTMATTER_METADATA.fields`
3. Adds kind-specific fields with types, constraints, descriptions
4. Registers in `FRONTMATTER_METADATA_REGISTRY`
5. Writes dual-validation tests confirming behavior
6. Validation works immediately without touching imperative code

**Journey 3: Existing code migrates to metadata validation**

**Given** existing code uses `validate_frontmatter()` imperative validator
**When** maintainer opts into metadata-driven validation
**Then**:
1. Call `validate_frontmatter_metadata(frontmatter, kind)` instead
2. Receive identical `FrontmatterValidationResult` (compatible API)
3. Run dual-validation tests confirming no regressions
4. Validation logic now driven by metadata, not imperative code

### Edge Cases & Non-goals

**Edge Cases**:
- **Nested structures**: Relations array with object items requiring type/target fields
- **Date formats**: Accept both ISO string and date objects (pre-processor normalizes)
- **Optional fields**: Different kinds have different optional field sets
- **Conditional requirements**: Some fields required only for specific kinds (e.g., `delta_ref` for design_revision)

**Non-goals**:
- **Target validation**: Validating relation targets exist in registry (separate concern)
- **Graph validation**: Cross-artifact consistency checks (separate from frontmatter validation)
- **Custom validators**: Complex logic beyond metadata capabilities (minimize, document exceptions)
- **External tool integration**: While JSON Schema enables this, we don't build integrations yet

## 3. Responsibilities & Requirements

### Capability Overview

This product delivers three core capabilities:

1. **Metadata-Driven Frontmatter Validation**: Replaces imperative validation with declarative schemas covering all 11 frontmatter kinds. Each kind (spec, delta, requirement, verification, problem, risk, policy, standard, etc.) has metadata defining required fields, types, patterns, and nested structures.

2. **JSON Schema Generation for Agents**: Enables agents to query JSON Schema for any frontmatter kind via CLI. Schema output includes examples, field descriptions, and complete constraint information, eliminating documentation drift.

3. **Gradual Migration Path**: Supports dual implementation during transition, maintaining backward compatibility. Existing code continues working while opt-in migration happens incrementally per code path.

### Functional Requirements

- **FR-001**: System MUST validate frontmatter for all 11 kinds using metadata definitions
  - Kinds: base, spec, prod, delta, requirement, verification, design_revision, problem, issue, audit, plan/phase/task
  - Each kind has dedicated metadata in `supekku/scripts/lib/core/frontmatter_metadata/{kind}.py`
  - Validation driven by `BlockMetadata` with `FieldMetadata` definitions
  - *Verification*: VT-001 - Comprehensive test suite covering all kinds

- **FR-002**: System MUST enforce kind-specific required fields and constraints
  - Example: `kind: delta` requires `applies_to`, `context_inputs` beyond base fields
  - Example: `kind: verification` requires `verification_kind`, `covers`, `procedure`
  - Example: `kind: requirement` requires `requirement_kind`, `rfc2119_level`
  - Conditional validation based on kind field value
  - *Verification*: VT-002 - Kind-specific validation tests

- **FR-003**: System MUST generate JSON Schema from frontmatter metadata definitions
  - Use `JSONSchemaGenerator` from metadata engine
  - Output compliant with JSON Schema Draft 2020-12
  - Include examples, descriptions, and complete constraint information
  - *Verification*: VT-003 - JSON Schema generation tests

- **FR-004**: CLI MUST support `schema show frontmatter.{kind}` commands for all kinds
  - Example: `spec-driver schema show frontmatter.spec --format=json-schema`
  - Example: `spec-driver schema show frontmatter.delta --format=yaml-example`
  - Return formatted JSON Schema or YAML example
  - *Verification*: VT-004 - CLI integration tests

- **FR-005**: System MUST maintain backward compatibility during migration
  - New `validate_frontmatter_metadata()` returns compatible `FrontmatterValidationResult`
  - Existing `validate_frontmatter()` remains available during transition
  - Both validators produce equivalent results for same input
  - *Verification*: VT-005 - Backward compatibility tests

- **FR-006**: System MUST support gradual per-call-site opt-in migration
  - Each code path chooses when to migrate independently
  - No forced migration or breaking changes
  - Deprecation warnings only after full ecosystem migration
  - *Verification*: VT-005 - Migration path tests

### Non-Functional Requirements

- **NF-001**: Validation behavior MUST match imperative validator (zero regressions)
  - Dual-validation test pattern: same input validates with both, assert same errors
  - 275-440 tests covering all schemas with valid/invalid cases
  - *Measurement*: VT-006 - Dual-validation pattern across all test suites

- **NF-002**: JSON Schema generation MUST complete in <100ms per kind
  - Schema cached after first generation
  - Agent queries return immediately
  - *Measurement*: Performance tests during VT-003

- **NF-003**: Migration MUST not break existing code at any point
  - All existing tests pass throughout migration phases
  - No changes to public API signatures until deprecation
  - *Measurement*: Continuous test suite execution during migration

### Success Metrics / Signals

- **Adoption**: All 11 frontmatter kinds validated via metadata (not imperative code)
- **Quality**: Zero validation regressions from imperative validator
- **Agent Effectiveness**: JSON Schema available for all kinds via CLI
- **Developer Experience**: New frontmatter kinds added in <30 minutes (vs. hours)
- **Test Coverage**: 275-440 tests passing with dual-validation pattern

## 4. Solution Outline

### User Experience / Outcomes

**For Developers**:
- Add new frontmatter kind: Create single metadata file with declarative schema
- No touching imperative validation code, no risk of breaking unrelated kinds
- Tests guide via dual-validation pattern (compare old vs. new)

**For Agents**:
- Query schema before writing: `spec-driver schema show frontmatter.delta --format=json-schema`
- Receive accurate, complete schema with examples
- Reduce validation errors through upfront understanding

**For Architects/Team Leads**:
- Read metadata definitions to understand validation rules
- Schema serves as living documentation
- No code archaeology required to extract constraints

### Data & Contracts

**Frontmatter Metadata Registry** (`supekku/scripts/lib/core/frontmatter_metadata/__init__.py`):

```python
FRONTMATTER_METADATA_REGISTRY: dict[str, BlockMetadata] = {
  "base": BASE_FRONTMATTER_METADATA,
  "spec": SPEC_FRONTMATTER_METADATA,
  "prod": PROD_FRONTMATTER_METADATA,
  "delta": DELTA_FRONTMATTER_METADATA,
  "requirement": REQUIREMENT_FRONTMATTER_METADATA,
  "verification": VERIFICATION_FRONTMATTER_METADATA,
  "design_revision": DESIGN_REVISION_FRONTMATTER_METADATA,
  "problem": PROBLEM_FRONTMATTER_METADATA,
  "risk": RISK_FRONTMATTER_METADATA,
  "issue": ISSUE_FRONTMATTER_METADATA,
  "audit": AUDIT_FRONTMATTER_METADATA,
  "plan": PLAN_FRONTMATTER_METADATA,
  "phase": PHASE_FRONTMATTER_METADATA,
  "task": TASK_FRONTMATTER_METADATA,
  "policy": POLICY_FRONTMATTER_METADATA,
  "standard": STANDARD_FRONTMATTER_METADATA,
}

def get_frontmatter_metadata(kind: str) -> BlockMetadata:
  """Get metadata for frontmatter kind, fallback to base."""
  return FRONTMATTER_METADATA_REGISTRY.get(kind, BASE_FRONTMATTER_METADATA)
```

**Base Frontmatter Schema** (common fields):

```python
BASE_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.base",
  description="Base frontmatter fields for all artifacts",
  fields={
    "id": FieldMetadata(type="string", required=True, description="..."),
    "name": FieldMetadata(type="string", required=True, description="..."),
    "slug": FieldMetadata(type="string", required=True, description="..."),
    "kind": FieldMetadata(
      type="enum",
      required=True,
      enum_values=["spec", "prod", "delta", "requirement", ...],
      description="Artifact family/type",
    ),
    "status": FieldMetadata(type="string", required=True, description="..."),
    "created": FieldMetadata(
      type="string",
      required=True,
      pattern=r"^\d{4}-\d{2}-\d{2}$",
      description="ISO-8601 date",
    ),
    "updated": FieldMetadata(type="string", required=True, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    "relations": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        properties={
          "type": FieldMetadata(
            type="enum",
            required=True,
            enum_values=["implements", "verifies", "depends_on", ...],
          ),
          "target": FieldMetadata(type="string", required=True),
        },
      ),
    ),
    # ... additional base fields (owners, tags, summary, etc.)
  },
)
```

**Kind-Specific Schema** (example: delta):

```python
DELTA_FRONTMATTER_METADATA = BlockMetadata(
  version=1,
  schema_id="supekku.frontmatter.delta",
  description="Frontmatter for delta artifacts",
  fields={
    **BASE_FRONTMATTER_METADATA.fields,  # Include all base fields
    "applies_to": FieldMetadata(
      type="array",
      required=True,
      items=FieldMetadata(type="string"),
      description="Spec/requirement IDs this delta applies to",
    ),
    "context_inputs": FieldMetadata(
      type="array",
      required=True,
      items=FieldMetadata(type="string"),
      description="Context sources informing this delta",
    ),
    "risk_register": FieldMetadata(
      type="array",
      required=False,
      items=FieldMetadata(
        type="object",
        properties={
          "id": FieldMetadata(type="string", required=True),
          "description": FieldMetadata(type="string", required=True),
          "likelihood": FieldMetadata(type="enum", enum_values=["low", "medium", "high"]),
          "impact": FieldMetadata(type="enum", enum_values=["low", "medium", "high"]),
          "mitigation": FieldMetadata(type="string", required=False),
        },
      ),
    ),
  },
  examples=[{
    "id": "DELTA-001",
    "name": "Add user authentication",
    "kind": "delta",
    "applies_to": ["SPEC-100"],
    "context_inputs": ["User research findings"],
    # ... complete example
  }],
)
```

**Validation API**:

```python
def validate_frontmatter_metadata(
  frontmatter: dict,
  kind: str | None = None,
) -> FrontmatterValidationResult:
  """Validate frontmatter using metadata-driven system."""
  # 1. Determine kind (from parameter or frontmatter["kind"])
  kind = kind or frontmatter.get("kind", "base")

  # 2. Get appropriate metadata
  metadata = get_frontmatter_metadata(kind)

  # 3. Validate using MetadataValidator
  validator = MetadataValidator(metadata)
  errors = validator.validate(frontmatter)

  if errors:
    raise FrontmatterValidationError(str(errors[0]))

  # 4. Return compatible result
  return FrontmatterValidationResult(
    id=frontmatter["id"],
    name=frontmatter["name"],
    slug=frontmatter["slug"],
    # ... etc
  )
```

## 5. Behaviour & Scenarios

### Primary Flows

**Flow 1: Validate spec frontmatter during creation**

1. User runs `spec-driver create spec "User Auth" --kind tech`
2. System generates frontmatter with required base + spec-specific fields
3. System calls `validate_frontmatter_metadata(frontmatter, kind="spec")`
4. Validator retrieves `SPEC_FRONTMATTER_METADATA` from registry
5. Validator checks all required fields present (id, name, slug, kind, status, created, updated, c4_level, packages, etc.)
6. Validator checks field types and patterns (dates match ISO format, etc.)
7. Validator checks nested structures (sources array has language/identifier, etc.)
8. If valid: returns `FrontmatterValidationResult`
9. If invalid: raises `FrontmatterValidationError` with specific field/constraint violated
10. System persists validated frontmatter to spec file

**Flow 2: Agent queries schema before writing delta frontmatter**

1. Agent needs to create delta artifact with custom frontmatter
2. Agent runs `spec-driver schema show frontmatter.delta --format=json-schema`
3. System retrieves `DELTA_FRONTMATTER_METADATA` from registry
4. System calls `JSONSchemaGenerator(DELTA_FRONTMATTER_METADATA).generate()`
5. System returns JSON Schema including:
   - Required fields: id, name, slug, kind, status, created, updated, applies_to, context_inputs
   - Optional fields: summary, tags, relations, risk_register, outcome_summary
   - Nested object schemas for relations and risk_register
   - Enum constraints for kind, status, relation types
   - Pattern constraints for dates
   - Examples demonstrating valid structure
6. Agent uses schema to construct valid frontmatter YAML
7. Agent writes frontmatter to delta file
8. Validation passes on first attempt (no trial-and-error)

**Flow 3: Developer adds new frontmatter kind**

1. Developer identifies need for new artifact kind "feature"
2. Developer creates `supekku/scripts/lib/core/frontmatter_metadata/feature.py`
3. Developer defines `FEATURE_FRONTMATTER_METADATA`:
   ```python
   FEATURE_FRONTMATTER_METADATA = BlockMetadata(
     schema_id="supekku.frontmatter.feature",
     fields={
       **BASE_FRONTMATTER_METADATA.fields,
       "feature_flag": FieldMetadata(type="string", required=True),
       "rollout_percentage": FieldMetadata(type="number", required=False),
       # ... feature-specific fields
     },
     examples=[{...}],
   )
   ```
4. Developer registers in `__init__.py`: `"feature": FEATURE_FRONTMATTER_METADATA`
5. Developer writes `feature_test.py` with dual-validation tests
6. Tests pass (no imperative code changes needed)
7. JSON Schema immediately available via `schema show frontmatter.feature`

### Error Handling / Guards

**Missing required field**:
- Input: `{"id": "SPEC-001", "name": "Test"}` (missing slug, kind, status, dates)
- Error: `FrontmatterValidationError: Missing required field: slug`
- Recovery: User adds missing field to frontmatter

**Invalid field type**:
- Input: `{"created": "tomorrow"}` (invalid date format)
- Error: `FrontmatterValidationError: Field 'created' does not match pattern ^\d{4}-\d{2}-\d{2}$`
- Recovery: User corrects to ISO format `"2025-11-02"`

**Invalid enum value**:
- Input: `{"kind": "unknown"}` (not in enum_values)
- Error: `FrontmatterValidationError: Field 'kind' must be one of: spec, prod, delta, ...`
- Recovery: User selects valid kind value

**Nested structure violation**:
- Input: `{"relations": [{"target": "SPEC-001"}]}` (missing required `type` field)
- Error: `FrontmatterValidationError: relations[0] missing required field: type`
- Recovery: User adds `type` field to relation object

**Unknown kind**:
- Input: `validate_frontmatter_metadata(fm, kind="nonexistent")`
- Behavior: Falls back to `BASE_FRONTMATTER_METADATA` (validates only base fields)
- Logging: Warning logged about unknown kind fallback

## 6. Quality & Verification

### Testing Strategy

**Dual-Validation Pattern** (prevents regressions):
- Each test validates same frontmatter with both old and new validators
- Assert both produce same errors (or both pass)
- Example:
  ```python
  def test_missing_slug_dual_validation():
    frontmatter = {"id": "SPEC-001", "name": "Test"}  # Missing slug

    # Old validator
    with pytest.raises(FrontmatterValidationError) as old_err:
      validate_frontmatter(frontmatter)

    # New validator
    with pytest.raises(FrontmatterValidationError) as new_err:
      validate_frontmatter_metadata(frontmatter, kind="spec")

    # Both should fail with similar message about missing slug
    assert "slug" in str(old_err.value).lower()
    assert "slug" in str(new_err.value).lower()
  ```

**Test Coverage Per Schema** (minimum per kind):
- Valid complete example: 1 test
- Valid minimal example: 1 test
- Missing required fields: 3-5 tests (one per required field)
- Invalid types: 5-10 tests (string vs. number, array vs. object, etc.)
- Invalid patterns/enums: 3-5 tests (date format, enum values, etc.)
- Nested structure validation: 5-10 tests (relations array, risk_register, sources, etc.)
- JSON Schema generation: 1 test (output valid JSON Schema)
- **Total**: ~25-40 tests per schema × 11 schemas = **275-440 tests**

**Test Levels**:
- **Unit**: Each metadata definition tested in isolation (e.g., `base_test.py`)
- **Integration**: Validator + metadata working together
- **Regression**: Dual-validation comparing old and new validators
- **CLI**: `schema show frontmatter.*` commands return valid schemas

### Research / Validation

Not applicable (internal tooling improvement, no user research needed).

### Observability & Analysis

**Validation Metrics**:
- Count of validation errors by kind (which kinds fail most often?)
- Count of validation errors by field (which fields cause most errors?)
- Validation latency per kind (performance monitoring)

**Migration Metrics**:
- Percentage of code paths migrated to metadata validation
- Count of dual-validation test failures (should be zero)
- Deprecation warning count (when old validator still used)

### Security & Compliance

**Input Validation**:
- Frontmatter is user-controlled YAML, but validation prevents injection
- No code execution from frontmatter values (pure data validation)
- Pattern matching prevents malicious date/ID formats

**No External Data**:
- Validation happens on local frontmatter only
- No network requests or external dependencies
- Registry lookup for relation targets is separate concern (not in scope)

### Verification Coverage

Aligned with `supekku:verification.coverage@v1` YAML block above.

### Acceptance Gates

**Phase 6A (Base) Complete When**:
- `BASE_FRONTMATTER_METADATA` defined with all common fields
- `base_test.py` has 25-40 tests passing
- Dual-validation tests confirm no regressions
- Ruff and Pylint pass

**Phase 6B-6D (Kind Schemas) Complete When**:
- All 11 kind metadata definitions created
- 275-440 tests passing across all schemas
- JSON Schema generation working for all kinds
- Ruff and Pylint pass

**Phase 6E (Integration) Complete When**:
- `validate_frontmatter_metadata()` API compatible with existing code
- All existing code paths continue working
- Opt-in migration proven with at least 2 code paths
- No test failures introduced

**Phase 6F (CLI) Complete When**:
- `spec-driver schema show frontmatter.{kind}` works for all kinds
- `--format=json-schema` and `--format=yaml-example` both supported
- CLI help documentation updated
- Examples included in all metadata definitions

**Overall Product Complete When**:
- All 11 frontmatter kinds validated via metadata
- JSON Schema available for all kinds via CLI
- Zero validation regressions (dual-validation tests passing)
- Migration path documented and proven
- Imperative validator deprecated (warnings in logs)

## 7. Backlog Hooks & Dependencies

### Related Specs / PROD

- **SPEC-036** (`supekku/scripts/lib/core/frontmatter_schema.py`): Current imperative validator being replaced
- **PROD-003** (Policy and Standard Management): Relies on frontmatter metadata validation for policy/standard frontmatter schemas

### Risks & Mitigations

- **RISK-001**: Breaking existing code during migration
  - **Likelihood**: Medium
  - **Impact**: High (stops development)
  - **Mitigation**: Dual implementation period, backward-compatible API, gradual opt-in migration, comprehensive dual-validation tests

- **RISK-002**: Incomplete schema documentation leads to validation drift
  - **Likelihood**: Medium
  - **Impact**: Medium (agents write invalid frontmatter)
  - **Mitigation**: Single source of truth (metadata definitions), JSON Schema generated from metadata (no manual docs), examples embedded in metadata

- **RISK-003**: Performance regression from metadata validation overhead
  - **Likelihood**: Low
  - **Impact**: Medium (slows CLI commands)
  - **Mitigation**: Metadata validation proven fast in Phases 1-5, cache metadata instances, validate only when needed, performance tests in VT suite

- **RISK-004**: Complex validation logic not expressible in metadata
  - **Likelihood**: Low
  - **Impact**: Low (falls back to imperative)
  - **Mitigation**: Document exceptions, minimize custom validators, prefer metadata extension over imperative code

### Known Gaps / Debt

- **ISSUE-001**: Frontmatter relation target validation not in scope (requires registry lookup, creates circular dependency) - deferred to graph validation work
- **ISSUE-002**: Status enum values differ by kind (spec vs. delta vs. policy) - initially use string type, can add conditional validation later
- **ISSUE-003**: External tool integration (IDE plugins, CI linters) not built yet - JSON Schema enables future work but not in scope

### Open Decisions / Questions

None - user provided clear answers during discovery:
- All 11 kinds will be implemented (not MVP subset)
- Replace/supplement imperative validator (minimize parallel implementations)
- Primary beneficiaries are developers, architects, and agents
- No external tool integrations yet (JSON Schema enables future work)

## Appendices

### Frontmatter Kinds Summary

| Kind | Frontmatter ID Pattern | Key Unique Fields |
|------|------------------------|-------------------|
| Base | N/A (all share) | id, name, slug, kind, status, created, updated, relations |
| Spec | SPEC-### | c4_level, packages, sources, concerns, responsibilities |
| Product | PROD-### | scope, problems, value_proposition, product_requirements |
| Delta | DELTA-### | applies_to, context_inputs, risk_register, outcome_summary |
| Requirement | REQ-### | requirement_kind, rfc2119_level, acceptance_criteria |
| Verification | VT/VA/VH-### | verification_kind, covers, procedure |
| Design Revision | REV-### | delta_ref, source_context, code_impacts, design_decisions |
| Problem | PROB-### | problem_statement, context, success_criteria |
| Risk | RISK-### | risk_statement, likelihood, impact, mitigation_strategy |
| Issue | ISSUE-### | categories, severity, impact, problem_refs |
| Audit | AUD-### | spec_refs, audit_window, findings, next_actions |
| Plan/Phase/Task | IP-### | objective, entrance_criteria, exit_criteria |
| Policy | POL-### | statement, rationale, scope, enforcement |
| Standard | STD-### | statement, rationale, scope, flexibility |

### Migration Timeline Reference

From `FRONTMATTER_METADATA_MIGRATION_PLAN.md`:

| Phase | Scope | Estimated Time |
|-------|-------|----------------|
| 6A | Base frontmatter schema | 3-4 hours |
| 6B | Spec frontmatter schema | 2-3 hours |
| 6C | Delta frontmatter schema | 2-3 hours |
| 6D | 8 remaining schemas (problem, risk, verification, requirement, design_revision, issue, audit, plan/phase/task) | 8-16 hours |
| 6E | Integration and migration (compatibility layer, opt-in migration) | 4-6 hours |
| 6F | JSON Schema CLI integration (`schema show frontmatter.*`) | 2-3 hours |
| **Total** | End-to-end | **21-35 hours** |

### References

- **Migration Plan**: `FRONTMATTER_METADATA_MIGRATION_PLAN.md`
- **Frontmatter Schema Docs**: `supekku/about/frontmatter-schema.md`
- **Current Validator**: `supekku/scripts/lib/core/frontmatter_schema.py`
- **TODO Notes**: `supekku/scripts/lib/TODO.md` (lines 60-94)
- **Metadata Engine**: `supekku/scripts/lib/blocks/metadata/`
- **Phase 5 Completion**: `PHASE_5_COMPLETE.md` (revision block validator pattern)
