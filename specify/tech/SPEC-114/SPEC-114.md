---
id: SPEC-114
slug: supekku-scripts-lib-blocks-metadata
name: supekku/scripts/lib/blocks/metadata Specification
created: '2025-11-02'
updated: '2025-11-02'
status: draft
kind: spec
responsibilities:
- Define declarative metadata schemas for block validation
- Validate YAML blocks against metadata definitions at runtime
- Generate JSON Schema Draft 2020-12 from metadata for agent/tooling consumption
- Support complex validation patterns (enums, patterns, nested objects, conditionals)
- Provide path-aware, developer-friendly error messages
aliases: []
packages:
- supekku/scripts/lib/blocks/metadata
sources:
- language: python
  identifier: supekku/scripts/lib/blocks/metadata
  module: supekku.scripts.lib.blocks.metadata
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

# SPEC-114 – supekku/scripts/lib/blocks/metadata

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-114
requirements:
  primary:
    - SPEC-114.FR-001
    - SPEC-114.FR-002
    - SPEC-114.FR-003
    - SPEC-114.FR-004
    - SPEC-114.FR-005
    - SPEC-114.FR-006
    - SPEC-114.NF-001
    - SPEC-114.NF-002
    - SPEC-114.NF-003
  collaborators: []
interactions:
  - spec: SPEC-TBD
    type: used_by
    description: Used by schema_registry for block schema definitions
  - spec: SPEC-TBD
    type: used_by
    description: Used by block parsers to validate frontmatter blocks
  - spec: SPEC-TBD
    type: used_by
    description: JSON Schema output consumed by Claude Code agents for structured block generation
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: SPEC-114
capabilities:
  - id: declarative-schema-definition
    name: Declarative Schema Definition
    responsibilities:
      - Provide dataclass-based schema definitions via FieldMetadata, ConditionalRule, BlockMetadata
      - Support field types (string, int, bool, enum, const, object, array)
      - Support field constraints (required, pattern, enum_values, const_value, min_items, max_items)
      - Enable nested object schemas via properties attribute
      - Enable conditional validation rules (if field X=Y then fields Z required)
    requirements:
      - SPEC-114.FR-001
      - SPEC-114.FR-002
      - SPEC-114.NF-001
    summary: |
      Provides Python dataclasses for defining block schemas declaratively. A single metadata
      definition serves as the source of truth for both runtime validation and JSON Schema generation.
    success_criteria:
      - All supported field types are validated correctly
      - Nested object schemas work to arbitrary depth
      - Conditional rules express if/then validation logic
      - Metadata instances are immutable and validated at construction

  - id: runtime-validation-engine
    name: Runtime Validation Engine
    responsibilities:
      - Validate parsed YAML data against BlockMetadata schemas
      - Detect missing required fields, type mismatches, pattern violations
      - Evaluate conditional rules (if/then logic)
      - Generate path-aware ValidationError objects with expected/actual values
      - Support nested field validation with dot-notation paths
    requirements:
      - SPEC-114.FR-003
      - SPEC-114.FR-004
      - SPEC-114.NF-002
    summary: |
      MetadataValidator validates data against schemas at runtime, producing structured errors
      with precise paths (e.g., "metadata.author", "tags[1]") for developer-friendly diagnostics.
    success_criteria:
      - All validation errors include path, message, and expected/actual values where applicable
      - Nested field validation works correctly
      - Conditional rules are evaluated properly
      - Empty error list indicates valid data

  - id: json-schema-generation
    name: JSON Schema Generation
    responsibilities:
      - Transform BlockMetadata into JSON Schema Draft 2020-12
      - Generate schema ID, properties, required fields, examples
      - Translate field types to JSON Schema types
      - Translate conditional rules to allOf/if/then structures
      - Output schemas consumable by agents and validation tooling
    requirements:
      - SPEC-114.FR-005
      - SPEC-114.FR-006
      - SPEC-114.NF-003
    summary: |
      metadata_to_json_schema() generates standards-compliant JSON Schema from metadata definitions,
      enabling agent consumption and validation tool integration.
    success_criteria:
      - Generated schemas validate using standard JSON Schema validators
      - Schemas include $schema, $id, title, description, examples
      - Conditional rules translate to correct if/then structures
      - Schemas are deterministic (same input produces same output)
```

## 1. Intent and Scope

### 1.1 Purpose

The `supekku/scripts/lib/blocks/metadata` package provides a **metadata-driven validation system** for structured YAML blocks in spec-driver documents (deltas, revisions, audits, specs, requirements).

The core principle: **a single declarative metadata definition drives both runtime validation and JSON Schema generation**. This eliminates drift between validation logic and documentation, ensures consistency across block types, and provides agent-consumable schemas for structured block generation.

### 1.2 Out of Scope

- YAML parsing (handled upstream by block parsers)
- Block-specific business logic (handled by domain packages)
- Schema versioning and migration (future enhancement)
- Advanced JSON Schema features (oneOf, anyOf, not, etc.)

### 1.3 Key Design Decisions

1. **Pure dataclass schemas**: Metadata definitions are immutable Python dataclasses with validation at construction.
2. **Path-aware errors**: ValidationError objects include precise paths (dot-notation, array indices) for debugging.
3. **Dual output**: Single metadata definition produces both runtime validation and JSON Schema Draft 2020-12.
4. **Extensible field types**: Support common types (string, int, bool, enum, const, object, array) with room for future types.

## 2. Responsibilities

### R1: Schema Definition API

Provide dataclass-based API for defining block schemas:
- `FieldMetadata`: Single field definition with type, constraints, description
- `ConditionalRule`: If/then validation rule (if field X=Y, then fields Z required)
- `BlockMetadata`: Complete schema with version, schema_id, fields, rules, examples

**Invariants**:
- Field types must be valid (string, int, bool, enum, const, object, array)
- Enum fields must have enum_values, const fields must have const_value
- Object fields must have properties, array fields must have items
- Nested properties validated recursively

### R2: Runtime Validation

Validate parsed YAML data against schemas:
- Check required fields, type correctness, pattern matching
- Evaluate conditional rules
- Validate nested objects and arrays with array index tracking
- Produce ValidationError list (empty if valid)

**Invariants**:
- Root data must be dict/mapping
- All errors include path, message
- Validation is deterministic (same input/schema produces same errors)

### R3: JSON Schema Generation

Generate JSON Schema Draft 2020-12 from metadata:
- Include $schema, $id, title, description, examples
- Translate field types to JSON Schema types
- Translate conditional rules to allOf/if/then
- Support nested objects and array constraints

**Invariants**:
- Generated schemas are valid JSON Schema Draft 2020-12
- Schema generation is deterministic
- Schemas are consumable by standard validators (jsonschema, ajv, etc.)

## 3. Architecture

### 3.1 Module Structure

```
supekku/scripts/lib/blocks/metadata/
├── __init__.py              # Public API exports
├── schema.py                # FieldMetadata, ConditionalRule, BlockMetadata dataclasses
├── validator.py             # MetadataValidator, ValidationError
├── json_schema.py           # metadata_to_json_schema()
└── test_engine.py           # Comprehensive test suite
```

### 3.2 Data Flow

```
Block Definition (Python)
    ↓
BlockMetadata (immutable dataclass)
    ↓
    ├─→ MetadataValidator.validate(data) → list[ValidationError]
    └─→ metadata_to_json_schema() → dict (JSON Schema)
```

### 3.3 Key Abstractions

**FieldMetadata**: Describes a single field's type, constraints, and validation rules. Supports nesting via `properties` (for objects) and `items` (for arrays).

**ConditionalRule**: Expresses if/then logic: "if `condition_field` equals `condition_value`, then `requires` fields must be present". Supports nested paths (e.g., "metadata.revision").

**BlockMetadata**: Top-level schema definition binding version, schema_id, fields, conditional rules, and examples.

**MetadataValidator**: Stateless validator that walks data structure recursively, checking types, patterns, required fields, and conditional rules.

**ValidationError**: Structured error with path (dot-notation + array indices), message, expected, actual.

## 4. Interfaces

### 4.1 Public API

**schema.py**:
```python
@dataclass
class FieldMetadata:
  type: str  # string, int, bool, enum, const, object, array
  required: bool = False
  pattern: str | None = None
  const_value: Any | None = None
  enum_values: list[Any] | None = None
  properties: dict[str, FieldMetadata] | None = None
  items: FieldMetadata | None = None
  description: str = ""
  min_items: int | None = None
  max_items: int | None = None

@dataclass
class ConditionalRule:
  condition_field: str  # Supports nested paths like "metadata.revision"
  condition_value: Any
  requires: list[str]
  description: str = ""

@dataclass
class BlockMetadata:
  version: int
  schema_id: str
  fields: dict[str, FieldMetadata]
  conditional_rules: list[ConditionalRule] = field(default_factory=list)
  description: str = ""
  examples: list[dict[str, Any]] = field(default_factory=list)
```

**validator.py**:
```python
@dataclass
class ValidationError:
  path: str
  message: str
  expected: str | None = None
  actual: str | None = None

class MetadataValidator:
  def __init__(self, metadata: BlockMetadata): ...
  def validate(self, data: dict[str, Any]) -> list[ValidationError]: ...
```

**json_schema.py**:
```python
def metadata_to_json_schema(metadata: BlockMetadata) -> dict[str, Any]:
  """Generate JSON Schema Draft 2020-12 from block metadata."""
```

### 4.2 Usage Example

```python
from supekku.scripts.lib.blocks.metadata import (
  BlockMetadata,
  FieldMetadata,
  ConditionalRule,
  MetadataValidator,
  metadata_to_json_schema,
)

# Define schema
metadata = BlockMetadata(
  version=1,
  schema_id="delta.metadata",
  description="Delta frontmatter block",
  fields={
    "id": FieldMetadata(type="string", required=True, pattern=r"^DE-\d{3}$"),
    "status": FieldMetadata(
      type="enum",
      required=True,
      enum_values=["planned", "active", "done"],
    ),
    "target": FieldMetadata(type="string", required=False),
  },
  conditional_rules=[
    ConditionalRule(
      condition_field="status",
      condition_value="active",
      requires=["target"],
      description="active deltas require target field",
    )
  ],
)

# Runtime validation
validator = MetadataValidator(metadata)
data = {"id": "DE-001", "status": "active"}  # Missing target
errors = validator.validate(data)
for error in errors:
  print(error)  # "target: is required when status=active"

# JSON Schema generation
schema = metadata_to_json_schema(metadata)
# schema is valid JSON Schema Draft 2020-12
```

## 5. Quality Requirements

### 5.1 Functional Requirements

**SPEC-114.FR-001**: Schema Definition API
- System SHALL provide FieldMetadata, ConditionalRule, BlockMetadata dataclasses
- System SHALL validate metadata consistency at construction (e.g., enum type requires enum_values)
- System SHALL support field types: string, int, bool, enum, const, object, array
- System SHALL support nested objects and arrays

**SPEC-114.FR-002**: Field Constraints
- System SHALL support required fields, patterns (regex), enum values, const values
- System SHALL support array constraints (min_items, max_items)
- System SHALL support nested object validation via properties
- System SHALL support array item validation via items

**SPEC-114.FR-003**: Runtime Validation
- System SHALL validate data against BlockMetadata schemas
- System SHALL detect missing required fields, type mismatches, pattern violations
- System SHALL evaluate conditional rules (if/then logic)
- System SHALL return empty list for valid data

**SPEC-114.FR-004**: Validation Errors
- System SHALL produce ValidationError objects with path, message, expected, actual
- System SHALL use dot-notation paths for nested fields (e.g., "metadata.author")
- System SHALL use array index notation for array items (e.g., "tags[1]")
- System SHALL format errors as human-readable strings via __str__

**SPEC-114.FR-005**: JSON Schema Generation
- System SHALL generate JSON Schema Draft 2020-12 from BlockMetadata
- System SHALL include $schema, $id, title, description, required, properties, examples
- System SHALL translate field types to JSON Schema types
- System SHALL translate array constraints to minItems/maxItems

**SPEC-114.FR-006**: Conditional Rules in JSON Schema
- System SHALL translate ConditionalRule to allOf/if/then structures
- System SHALL support top-level and nested condition fields
- System SHALL handle multiple conditional rules via allOf array

### 5.2 Non-Functional Requirements

**SPEC-114.NF-001**: Immutability
- Metadata definitions SHALL be immutable (dataclass frozen=True or equivalent)
- Validation SHALL be side-effect free (pure function behavior)

**SPEC-114.NF-002**: Error Quality
- Validation errors SHALL include precise paths for all failures
- Error messages SHALL be developer-friendly and actionable
- Errors SHALL include expected/actual values where applicable

**SPEC-114.NF-003**: Standards Compliance
- Generated JSON Schemas SHALL be valid JSON Schema Draft 2020-12
- Schemas SHALL be consumable by standard validators (jsonschema, ajv, etc.)
- Schema $id SHALL follow pattern: https://vice.supekku.dev/schemas/{schema-id}@v{version}.json

## 6. Testing Strategy

### 6.1 Test Coverage

Comprehensive test suite in `test_engine.py`:

**Field Type Tests** (8 test classes):
- StringFieldValidationTest: string type, pattern matching, optional fields
- EnumFieldValidationTest: enum constraints
- ConstFieldValidationTest: const value matching
- IntFieldValidationTest: integer type, boolean rejection
- BoolFieldValidationTest: boolean type
- ObjectFieldValidationTest: nested object validation, missing properties
- ArrayFieldValidationTest: array type, item validation, min/max items
- RequiredFieldValidationTest: required field enforcement

**Conditional Logic Tests**:
- ConditionalRuleValidationTest: if/then logic, nested conditions

**JSON Schema Tests**:
- JSONSchemaGenerationTest: all field types, constraints, conditional rules, metadata fields

**Integration Tests**:
- ComplexIntegrationTest: realistic decision metadata schema with all features

### 6.2 Test Execution

```bash
# Run all metadata tests
uv run pytest supekku/scripts/lib/blocks/metadata/test_engine.py -v

# Run specific test class
uv run pytest supekku/scripts/lib/blocks/metadata/test_engine.py::StringFieldValidationTest -v
```

### 6.3 Quality Gates

- All tests must pass (`just test`)
- Linters must pass with zero warnings (`just lint`, `just pylint`)
- Test coverage for all field types, constraints, and edge cases
- Integration tests for realistic schemas

## 7. Implementation Notes

### 7.1 Type System Design

Field type validation is centralized in `MetadataValidator._validate_field()`:
- **string**: isinstance(value, str), optional pattern matching via re.match
- **int**: isinstance(value, int) and not isinstance(value, bool) (Python bool is subclass of int)
- **bool**: isinstance(value, bool)
- **enum**: value in enum_values
- **const**: value == const_value
- **object**: isinstance(value, dict), recursive validation of properties
- **array**: isinstance(value, list), recursive validation of items

### 7.2 Conditional Rules

Conditional rules support:
- Top-level fields: `condition_field="status"`
- Nested fields: `condition_field="metadata.revision"` (one level of nesting)
- Multiple required fields: `requires=["field1", "field2"]`

Nested path resolution via `_get_nested_value()` using dot-notation splitting.

### 7.3 JSON Schema Translation

Key mappings:
- `FieldMetadata(type="string", pattern="...")` → `{"type": "string", "pattern": "..."}`
- `FieldMetadata(type="enum", enum_values=[...])` → `{"enum": [...]}`
- `FieldMetadata(type="const", const_value=X)` → `{"const": X}`
- `FieldMetadata(type="array", items=..., min_items=N)` → `{"type": "array", "items": {...}, "minItems": N}`
- `ConditionalRule(...)` → `{"allOf": [{"if": {...}, "then": {...}}]}`

### 7.4 Error Path Construction

Validation paths are built recursively:
- Root fields: `"field_name"`
- Nested object fields: `"parent.child"`
- Array items: `"array_name[0]"`
- Nested array items: `"parent.array[1].field"`

## 8. Change History

| Date       | Version | Change                                                     |
|------------|---------|------------------------------------------------------------|
| 2025-11-02 | 1.0     | Initial specification backfill from existing implementation |

## 9. Future Enhancements

- **Schema versioning**: Support schema evolution with migration helpers
- **Advanced JSON Schema features**: oneOf, anyOf, not, dependencies
- **Custom validators**: Plugin system for domain-specific validation logic
- **Error localization**: Multilingual error messages
- **Performance optimization**: Caching for repeated validations
- **Schema inheritance**: Extend base schemas with additional fields
