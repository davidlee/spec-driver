# YAML Code Block Handling in spec-driver: Comprehensive Analysis

**Analysis Date**: 2025-11-01  
**Codebase**: supekku spec-driver project  
**Focus**: Understanding existing YAML block parsing architecture and identifying gaps for verification.coverage blocks

---

## Executive Summary

The spec-driver codebase has **well-established patterns for parsing YAML code blocks** embedded in markdown files. Currently, **5 block types are fully implemented** with parsers, validators, and registry integration:

1. **`supekku:revision.change@v1`** - Detailed change tracking with requirement mappings (1,000+ lines, comprehensive)
2. **`supekku:spec.relationships@v1`** - Spec-to-requirement relationships
3. **`supekku:delta.relationships@v1`** - Delta-to-spec/requirement relationships
4. **`supekku:plan.overview@v1`** - Implementation plan overview
5. **`supekku:phase.overview@v1`** - Per-phase task tracking

The **`supekku:verification.coverage@v1` block is defined in templates and frontmatter-schema documentation** but **NOT YET IMPLEMENTED** in code.

This analysis identifies:
- The consistent architectural patterns for block handling
- Where verification.coverage blocks should fit
- What's reusable from existing implementations
- Key gaps and design decisions needed

---

## 1. Existing Code Block Architecture

### 1.1 Package Organization

```
supekku/scripts/lib/
├── changes/blocks/          # Change artifact blocks
│   ├── __init__.py
│   ├── delta.py             # Delta relationships
│   ├── plan.py              # Plan & phase overviews
│   ├── revision.py          # Revision change blocks (complex)
│   └── revision_test.py
├── specs/blocks.py          # Spec relationships
└── [Core, formatting, other modules...]
```

**Key insight**: Blocks are organized by **domain** (changes, specs) rather than all in one place. This supports separation of concerns.

### 1.2 Universal Block Pattern

Every block implementation follows this structure:

```python
# 1. Define marker, schema ID, and version
MARKER = "supekku:{domain}.{type}@v{version}"
SCHEMA = "supekku.{domain}.{type}"
VERSION = 1

# 2. Define dataclass(es) for parsed blocks
@dataclass(frozen=True)
class XyzBlock:
    raw_yaml: str           # Original YAML text for updates
    data: dict[str, Any]    # Parsed YAML

# 3. Define validator(s)
class XyzValidator:
    def validate(self, block: XyzBlock, **context) -> list[str] | list[ValidationMessage]:
        # Return errors or empty list if valid

# 4. Define regex pattern to find blocks
_PATTERN = re.compile(
    r"```(?:yaml|yml)\s+" + re.escape(MARKER) + r"\n(.*?)```",
    re.DOTALL,
)

# 5. Define extraction/loading functions
def extract_xyz(text: str, **context) -> XyzBlock | None:
    match = _PATTERN.search(text)
    if not match: return None
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        raise ValueError(...) from e
    return XyzBlock(raw_yaml=..., data=data)

def load_xyz(path: Path) -> XyzBlock | None:
    return extract_xyz(path.read_text(encoding="utf-8"))
```

This pattern is **highly consistent** across all implementations.

---

## 2. Detailed Implementation Review

### 2.1 `revision.py` (Most Complex)

**File**: `/home/david/dev/spec-driver/supekku/scripts/lib/changes/blocks/revision.py`  
**Lines**: ~1,020  
**Complexity**: HIGH

**Marker**: `supekku:revision.change@v1`

**Key Features**:
- Defines **full JSON Schema** (lines 26-253) documenting the structure
- **Comprehensive validator** with path-aware error messages (`ValidationMessage` dataclass)
- Handles complex nested structures (specs array, requirements array with lifecycle)
- Supports pattern validation for IDs (SPEC-123, RE-456, FR-789, etc.)
- **Regex-based block extraction** with exact position tracking (line offsets for updates)

**Schema Structure** (from JSON schema):
```yaml
schema: supekku.revision.change
version: 1
metadata:
  revision: RE-123  # Unique identifier
  prepared_by: optional
  generated_at: optional
specs:                # Array of spec changes
  - spec_id: SPEC-150
    action: created|updated|retired
    summary: optional
    requirement_flow: optional
    section_changes: optional
requirements:         # Array of requirement changes
  - requirement_id: SPEC-150.FR-001
    kind: functional|non-functional
    action: introduce|modify|move|retire
    summary: optional
    origin: array (for move actions)
    destination: object
    lifecycle: object
    text_changes: optional
```

**Patterns Used**:
- Compiled regex patterns for ID validation (`_REQUIREMENT_ID`, `_SPEC_ID`, etc.)
- Conditional validation (e.g., "destination required only for move action")
- Helper methods for code reuse (`_require_key`, `_disallow_extra_keys`, `_validate_spec`, etc.)

**Test Coverage**: 10+ test cases in `revision_test.py`

**Usage**: 
- `requirements/registry.py:359` - loads revision blocks to update requirement lifecycle
- `changes/discovery.py:69` - discovers revisions during sync
- `changes/updater.py:67` - applies revision updates

---

### 2.2 `spec/blocks.py` (Relationships)

**File**: `/home/david/dev/spec-driver/supekku/scripts/lib/specs/blocks.py`  
**Lines**: ~146  
**Complexity**: MEDIUM

**Marker**: `supekku:spec.relationships@v1`

**Key Features**:
- Simple validator (returns list of error strings)
- No JSON schema (just runtime validation)
- Handles optional lists (primary, collaborators, interactions)

**Schema Structure**:
```yaml
schema: supekku.spec.relationships
version: 1
spec: SPEC-123
requirements:
  primary: [SPEC-123.FR-001, ...]
  collaborators: [...]
interactions:
  - type: string
    spec: string
    ...
```

**Patterns Used**:
- Basic type checking (isinstance for dict, list, str)
- Entry validation in nested structures

**Test Coverage**: Part of spec registry tests

**Usage**:
- `requirements/registry.py:402` - updates requirement specs array

---

### 2.3 `delta.py` (Delta Relationships)

**File**: `/home/david/dev/spec-driver/supekku/scripts/lib/changes/blocks/delta.py`  
**Lines**: ~125  
**Complexity**: MEDIUM-LOW

**Marker**: `supekku:delta.relationships@v1`

**Key Features**:
- Similar to spec relationships
- Handles optional phases array
- Specs/requirements can be dicts with lists of IDs

**Schema Structure**:
```yaml
schema: supekku.delta.relationships
version: 1
delta: DE-123
specs: optional dict
requirements: optional dict
phases: optional list of {id, ...}
```

**Patterns Used**:
- Similar to spec.relationships but slightly more complex

---

### 2.4 `plan.py` (Plan & Phase Overviews)

**File**: `/home/david/dev/spec-driver/supekku/scripts/lib/changes/blocks/plan.py`  
**Lines**: ~137  
**Complexity**: LOW

**Markers**: 
- `supekku:plan.overview@v1`
- `supekku:phase.overview@v1`

**Key Features**:
- Two separate but parallel extraction functions
- Enhanced error formatting with line numbers and context
- No formal schema, just flexible YAML

**Special Features**:
```python
def _format_yaml_error(error, yaml_content, source_path, block_type):
    # Helpful error context with line numbers and snippets
```

**Patterns Used**:
- Better error reporting than other blocks
- Could be reused for verification.coverage

---

## 3. Integration Points with Registries

### 3.1 Where Blocks Get Used

**Revision blocks**:
```python
# requirements/registry.py:359
blocks = load_revision_blocks(file)
for block in blocks:
    data = block.parse()
    if validator.validate(data):  # Returns list of validation messages
        continue
    for requirement in data.get("requirements", []):
        created, updated = self._apply_revision_requirement(requirement, ...)
```

**Spec relationships**:
```python
# requirements/registry.py:402
block = extract_relationships(body)
if not block or validator.validate(block, spec_id=spec_id):
    return
data = block.data
requirements = data.get("requirements", {})
# ... update requirement.specs array
```

**Pattern**: Load → Parse → Validate → Apply to Registry

---

## 4. Current Verification.Coverage Block Definition

### 4.1 From Templates and Frontmatter Schema

**Locations**:
- `/home/david/dev/spec-driver/supekku/templates/spec-template.md` (lines 44-55)
- `/home/david/dev/spec-driver/supekku/templates/audit-template.md` (lines 52-63)
- `/home/david/dev/spec-driver/supekku/about/frontmatter-schema.md` (lines 193-216)
- `/home/david/dev/spec-driver/supekku/templates/implementation-plan-template.md`

**Marker**: `supekku:verification.coverage@v1`

**Defined Schema**:
```yaml
schema: supekku.verification.coverage
version: 1
subject: SPEC-123        # Spec, product, plan, audit, etc.
entries:
  - artefact: VT-210     # Verification test/activity
    kind: VT|VA|VH       # Test (VT), Validation (VA), Human Review (VH)
    requirement: SPEC-123.FR-001
    phase: IP-123.PHASE-02    # Optional: link to implementation phase
    status: planned|in-progress|verified|failed|blocked
    notes: >-
      Optional context, evidence links, or validation results.
```

**Design Characteristics**:
- `subject` - identifies the owning artefact (multiple types supported)
- `entries` - array of verification mappings
- Each entry links a VT/VA/VH artefact to a requirement
- Phase links are optional (for planning context)
- Status tracks verification progress
- Notes for evidence/traceability

**Usage Context** (from templates):
- Kept current during spec development
- Updated as VT/VA/VH artefacts are executed
- Cross-checked against phases during implementation
- Referenced in audit findings

---

## 5. Well-Factored Patterns (Reusable)

### 5.1 Extraction Pattern

All blocks use the **same regex-based extraction**:
```python
_PATTERN = re.compile(
    r"```(?:yaml|yml)\s+" + re.escape(MARKER) + r"\n(.*?)```",
    re.DOTALL,
)

def extract_xyz(text):
    match = _PATTERN.search(text)
    if not match: return None
    raw = match.group(1)
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Must parse to mapping")
    return XyzBlock(raw_yaml=raw, data=data)
```

**Candidate for shared utility?** YES - but all current implementations have minor variations (error messages, source path handling).

### 5.2 Validation Pattern

**Two approaches used**:

**Approach A** (simpler): Return `list[str]` of error messages
```python
def validate(self, block) -> list[str]:
    errors = []
    if block.data.get("schema") != EXPECTED_SCHEMA:
        errors.append("wrong schema")
    return errors
```

Used by: `DeltaRelationshipsValidator`, `RelationshipsBlockValidator`

**Approach B** (richer): Return `list[ValidationMessage]` with path context
```python
def validate(self, data) -> list[ValidationMessage]:
    messages = []
    self._check_root(data, messages)  # Recursive validation
    return messages
```

Used by: `RevisionBlockValidator`

**Trade-off**: 
- Approach A: Simpler, but harder to pinpoint exact location of error
- Approach B: More complex, but better for detailed error reporting

### 5.3 ID Pattern Validation

```python
_REQUIREMENT_ID = re.compile(r"^SPEC-\d{3}(?:-[A-Z0-9]+)*\.(FR|NF)-[A-Z0-9-]+$")
_SPEC_ID = re.compile(r"^SPEC-\d{3}(?:-[A-Z0-9]+)*$")
_REVISION_ID = re.compile(r"^RE-\d{3,}$")
_DELTA_ID = re.compile(r"^DE-\d{3,}$")

def _is_requirement_id(value: str) -> bool:
    return bool(_REQUIREMENT_ID.match(value))
```

**Pattern**: Define once, test many times. Centralized, reusable.

For **verification.coverage**, we'd need:
- `_VT_ID` = `r"^VT-\d{3,}$"` (verification test)
- `_VA_ID` = `r"^VA-\d{3,}$"` (validation activity)
- `_VH_ID` = `r"^VH-\d{3,}$"` (human review)

### 5.4 Data Structure Updates

**RevisionChangeBlock** includes methods for updating content:
```python
@dataclass
class RevisionChangeBlock:
    marker: str
    language: str
    yaml_content: str
    content_start: int
    content_end: int
    source_path: Path | None = None
    
    def replace_content(self, original: str, new_yaml: str) -> str:
        """Replace block content in original string."""
        return original[:self.content_start] + new_yaml + original[self.content_end:]
    
    def formatted_yaml(self, data: dict | None = None) -> str:
        """Format data as canonical YAML."""
        dumped = yaml.safe_dump(payload, sort_keys=False, indent=2, ...)
        return dumped + "\n" if not dumped.endswith("\n") else dumped
```

This is **essential for in-place block updates** during operations. Verification.coverage blocks will need similar support.

---

## 6. Identified Gaps

### 6.1 No Verification.Coverage Implementation

**Status**: Defined in templates/schema docs, NOT coded

**Missing**:
- [ ] Parser/extractor
- [ ] Dataclass model
- [ ] Validator
- [ ] Test coverage
- [ ] Registry integration (not needed for read-only blocks, but may be needed later)

### 6.2 No Shared Block Utilities

**Current state**: Each block type duplicates extraction logic

**Opportunity**: Create shared utilities in `core/` for:
- Regex pattern matching
- YAML parsing with error formatting
- Common validation helpers

**Rationale**: 6 block types (5 existing + 1 needed), each with ~20% duplicate code

### 6.3 No Standardized Error Reporting

**Existing**: Inconsistent error handling across blocks
- `DeltaRelationshipsValidator`: `list[str]`
- `RevisionBlockValidator`: `list[ValidationMessage]`
- `RelationshipsBlockValidator`: `list[str]`

**Gap**: No shared convention. Each consumer has slightly different error handling.

### 6.4 No Registry Consumption of Verification.Coverage

**Current**: Verification.coverage blocks are read during audits/plans but NOT integrated into:
- Requirement registry (lifecycle tracking)
- Spec registry
- Verification artefact registry

**Gap**: Can't query "which requirements are verified by which VT/VA/VH artefacts" programmatically.

### 6.5 No Aggregation/Reporting

**Current**: Blocks are parsed, validated, applied
**Gap**: No rollup queries like:
- "What's the verification coverage % for SPEC-123?"
- "Which requirements lack verification plans?"
- "Show VT/VA/VH status by phase"

---

## 7. Architectural Decisions for Verification.Coverage

### 7.1 Read-Only vs Mutable

**Question**: Will verification.coverage blocks be updated programmatically?

**Current model**: 
- Revision blocks: MUTABLE (agents update during revisions)
- Spec relationships: READ-ONLY (declarative, not updated)
- Delta relationships: READ-ONLY

**Recommendation for verification.coverage**:
- **Initially READ-ONLY** (parsed for analysis)
- **Plan for mutability** later (position tracking, formatters like RevisionChangeBlock)

### 7.2 Validator Complexity

**Question**: How complex should validation be?

**Current examples**:
- Simple (delta.py): 30 lines
- Complex (revision.py): 500+ lines

**Recommendation**:
- Start with **intermediate** (100-150 lines)
- Include:
  - Schema/version checking
  - Required field validation
  - ID format validation (VT/VA/VH, requirement IDs)
  - Optional field type checking
- Avoid conditional logic (move/introduce/retire patterns) for now

### 7.3 Registry Integration

**Question**: Should verification.coverage blocks integrate with registries?

**Current**:
- Revision blocks → Requirements registry (lifecycle updates)
- Spec relationships → Requirements registry (spec ownership)
- NO integration for plan/phase blocks

**Recommendation**:
- Create **lightweight VT/VA/VH registry** (read-only initially)
- Store: VT/VA/VH ID → {requirement, status, notes, subject}
- Use case: "What VT artefacts verify SPEC-123.FR-001?"

### 7.4 Testing Strategy

**Current test patterns**:
- Each block type has `_test.py` with 5-15 test cases
- Tests cover: extraction, validation, error handling
- No integration tests across blocks

**Recommendation for verification.coverage**:
```python
# test_coverage_blocks.py
- test_extract_valid_coverage_block()
- test_validator_requires_subject()
- test_validator_requires_schema_version()
- test_validator_validates_artefact_ids()
- test_validator_validates_requirement_ids()
- test_multiple_entries_in_block()
- test_missing_optional_fields()
- test_phase_link_optional()
```

---

## 8. Design Gaps & Questions

### Question 1: Spec Capabilities Blocks
**Observed**: Templates show `supekku:spec.capabilities@v1` (spec-template.md:29-42)
**Status**: DEFINED in template but NO implementation found
**Impact**: May need implementation alongside verification.coverage

### Question 2: Error Message Style
**Current**: Two styles (string list vs ValidationMessage)
**Impact**: Should verification.coverage use which? Recommend: **ValidationMessage for richer context**

### Question 3: Subject Types
**Spec**: "subject references SPEC-, PROD-, IP-, AUD-, etc."
**Gap**: No enum/list of valid subject types. Is it open-ended?
**Recommendation**: Document valid subject prefixes; validate against known registries

### Question 4: Phase References
**Spec**: "phase: IP-123.PHASE-02"
**Gap**: How to validate this? Only check format, or verify phase exists?
**Recommendation**: Format-only for now; registry integration can add existence checks later

### Question 5: Verification Artefact Types
**Current**: "kind: VT|VA|VH"
**Gap**: What if we add VV (visual verification) or other types?
**Recommendation**: Use set validation, document extensibility in schema

---

## 9. Summary: What's Reusable vs What Needs Building

### Reusable (Copy-Paste Safe)

1. **Extraction pattern** from `delta.py` or `specs/blocks.py` (40 lines)
2. **ID validation patterns** from `revision.py` (20 lines)
3. **Error formatting** from `plan.py` (30 lines)
4. **Basic validation structure** from `specs/blocks.py` (50 lines)

### Needs Building

1. **ValidationMessage-style validator** (new, based on revision.py pattern)
2. **Test suite** (15-20 test cases)
3. **Registry integration** (if doing VT/VA/VH aggregation)
4. **Formatter functions** (for output/display)

### Nice-to-Have (Future Refactoring)

1. Shared `core/block_utils.py` for extraction/error handling
2. Standardized error reporting across all blocks
3. Registry aggregation queries

---

## 10. File Structure Recommendation

```
supekku/scripts/lib/
├── specs/
│   ├── blocks.py (existing)
│   ├── blocks_test.py (existing)
│   ├── verification.py          # NEW: verification.coverage parser
│   └── verification_test.py      # NEW: tests
├── changes/blocks/
│   ├── delta.py (existing)
│   ├── plan.py (existing)
│   ├── revision.py (existing)
│   └── [tests] (existing)
├── validation/
│   └── [existing modules]
└── [other modules]
```

**Rationale**: Verification.coverage relates to SPECS (verification of requirements within a spec), so it belongs in `specs/` alongside relationships and capabilities blocks.

---

## Appendix A: Block Comparison Table

| Block | Marker | Complexity | Validator Type | Mutable? | Tests | Registry Integration |
|-------|--------|-----------|-----------------|----------|-------|----------------------|
| revision.change | `supekku:revision.change@v1` | HIGH | ValidationMessage | YES | 10+ | YES (requirements) |
| spec.relationships | `supekku:spec.relationships@v1` | MEDIUM | String list | NO | Partial | YES (requirements) |
| delta.relationships | `supekku:delta.relationships@v1` | MEDIUM | String list | NO | Partial | NO |
| plan.overview | `supekku:plan.overview@v1` | LOW | None (format only) | NO | Minimal | NO |
| phase.overview | `supekku:phase.overview@v1` | LOW | None (format only) | NO | Minimal | NO |
| **verification.coverage** | **`supekku:verification.coverage@v1`** | **MEDIUM** | **TODO** | **NO (initially)** | **TODO** | **TODO** |

---

## Appendix B: ID Pattern Reference

```python
# Valid verification artefact IDs
VT-001, VT-123, VT-9999  # Verification Test

VA-001, VA-456            # Validation Activity (audits, experiments)

VH-001, VH-789            # Human Verification/Review

# Requirements (target of verification)
SPEC-001.FR-001           # Functional requirement
SPEC-001.NF-042           # Non-functional requirement
PROD-020.FR-001           # Product requirement

# Subject types (owner of verification block)
SPEC-123                  # Spec owns verifications
PROD-020                  # Product spec owns verifications
IP-456                    # Implementation plan owns verifications
AUD-789                   # Audit owns verifications
```

---

## Appendix C: Key File References

**Core block parsing**:
- `/home/david/dev/spec-driver/supekku/scripts/lib/changes/blocks/revision.py` (1,020 lines, most complex)
- `/home/david/dev/spec-driver/supekku/scripts/lib/specs/blocks.py` (146 lines, simple)
- `/home/david/dev/spec-driver/supekku/scripts/lib/changes/blocks/delta.py` (125 lines)
- `/home/david/dev/spec-driver/supekku/scripts/lib/changes/blocks/plan.py` (137 lines)

**Registry integration**:
- `/home/david/dev/spec-driver/supekku/scripts/lib/requirements/registry.py` (line 359, 402) - shows usage

**Schema documentation**:
- `/home/david/dev/spec-driver/supekku/about/frontmatter-schema.md` (lines 193-216)
- `/home/david/dev/spec-driver/supekku/templates/spec-template.md` (lines 44-55)
- `/home/david/dev/spec-driver/supekku/templates/audit-template.md` (lines 52-63)

**Tests**:
- `/home/david/dev/spec-driver/supekku/scripts/lib/changes/blocks/revision_test.py` (exemplary test patterns)

