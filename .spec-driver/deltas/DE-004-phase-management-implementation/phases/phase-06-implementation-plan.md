# Phase 06 Implementation Plan: Simplify plan.overview

## Context

**Problem**: Significant duplication between `plan.overview` phases array and `phase.overview` blocks in phase sheets.

**Current Behavior**:
- `show delta --json` already reads from phase files (confirmed)
- Display uses phase.overview as canonical source
- plan.overview duplicates all phase metadata unnecessarily

**Solution**: Simplify plan.overview to store only phase IDs, making phase.overview the single source of truth.

## Target Schema

### Simplified plan.overview@v1

```yaml
schema: supekku.plan.overview
version: 1
plan: IP-004
delta: DE-004
revision_links:
  aligns_with: []
specs:
  primary:
    - PROD-006
  collaborators: []
requirements:
  targets:
    - PROD-006.FR-001
    - PROD-006.FR-002
  dependencies: []
phases:
  - id: IP-004.PHASE-01
  - id: IP-004.PHASE-02
  - id: IP-004.PHASE-03
  - id: IP-004.PHASE-04
  - id: IP-004.PHASE-05
  - id: IP-004.PHASE-06
```

**Key Change**: `phases` array contains only `{id: string}` objects, no metadata.

## Implementation Tasks

### 1. Update JSON Schema Definition

**File**: `supekku/scripts/lib/blocks/plan_metadata.py`

**Symbol**: `PLAN_OVERVIEW_METADATA` (line ~40)

**Current phases field** (lines ~85-130):
**Changes to make**:

```python
"phases": FieldMetadata(
  type="array",
  required=True,
  min_items=1,
  description="Ordered list of phase IDs (metadata in phase.overview blocks)",
  items=FieldMetadata(
    type="object",
    description="Phase ID reference",
    properties={
      "id": FieldMetadata(
        type="string",
        required=True,
        description="Phase ID (e.g., IP-001.PHASE-01)",
      ),
      # REMOVE: name, objective, entrance_criteria, exit_criteria
    },
  ),
),
```

**Also update the example** (lines ~150-175):
```python
"phases": [
  {"id": "PLN-001-P01"},
  {"id": "PLN-001-P02"},
  # Remove all metadata fields from example
],
```

**Key**: Remove `name`, `objective`, `entrance_criteria`, `exit_criteria` from properties dict.
Only keep `id` as required field.

### 2. Update Phase Creation Logic

**File**: `supekku/scripts/lib/changes/creation.py`

**Function**: `create_phase()` or wherever plan metadata is updated

**Changes**:
- When adding phase to plan.overview, only write `{id: phase_id}`
- Remove code that copies name/objective/criteria to plan
- Keep phase ordering logic (append to phases array)

**Test Impact**: `VT-PHASE-006` tests likely need updates

### 3. Update Parsers/Validators

**File**: `supekku/scripts/lib/blocks/plan.py` and `plan_metadata.py`

**Changes**:
- Update parser to handle both old format (with metadata) and new format (ID-only) for backward compatibility
- Validation should accept ID-only phases
- Consider migration helper: if old format found, warn but continue

**Backward Compatibility Strategy**:
```python
# Parser should handle both:
# Old: {id: X, name: Y, objective: Z, ...}
# New: {id: X}
# Just extract ID either way, ignore other fields if present
```

### 4. Update Formatters

**File**: `supekku/scripts/lib/formatters/change_formatters.py`

**Function**: `_format_plan_overview()` and `_enrich_phase_data()`

**Current Behavior**: Already reads from phase files (confirmed)

**Changes Needed**:
- Verify it doesn't rely on plan.overview metadata
- Likely just needs phase IDs to locate files
- May need to handle None/missing fields gracefully during transition

**Testing**: Run `show delta DE-004` before and after changes to ensure identical output

### 5. Update Templates

**File**: `.spec-driver/templates/implementation-plan-template.md`

**Changes**:
```yaml
phases:
  - id: PLAN-ID.PHASE-01
  - id: PLAN-ID.PHASE-02
  # Add more as needed
```

Remove example metadata from phases array.

### 6. Update Schema Documentation

**File**: JSON schema for plan.overview (metadata system)

**Changes**:
- Update `description` field to reflect simplified structure
- Update `examples` array in JSON schema
- Ensure `schema show plan.overview --format=yaml-example` shows new format

### 7. Update Tests

**Files to check**:
- `supekku/scripts/lib/changes/creation_test.py` (VT-PHASE-006)
- `supekku/scripts/lib/formatters/change_formatters_test.py`
- `supekku/scripts/lib/blocks/plan_test.py` (if exists)

**Changes**:
- Update test fixtures to use ID-only format
- Add backward compatibility tests (old format still works)
- Update assertions that check plan.overview structure

### 8. Migration for Existing Files

**Files to update manually**:
- `change/deltas/DE-004-phase-management-implementation/IP-004.md`
- Any other existing IP files

**Process**:
1. Backup current file
2. Remove metadata from phases array, keep only IDs
3. Verify `show delta` still works correctly
4. Test `create phase` adds new phase correctly

### 9. Update Documentation

**Files**:
- `PROD-006.md` (if it shows plan.overview example)
- Any ADRs or docs mentioning phase metadata in plans
- Update glossary if it describes plan.overview structure

## Testing Strategy

### Unit Tests
- [ ] Plan parser accepts ID-only phases
- [ ] Plan parser accepts old format (backward compat)
- [ ] Validator enforces `id` field required
- [ ] Validator allows ID-only format
- [ ] create_phase() writes only ID to plan

### Integration Tests
- [ ] Create new phase → plan.overview updated with ID only
- [ ] show delta → displays full phase metadata (from phase files)
- [ ] show delta --json → includes full phase.overview data
- [ ] schema show plan.overview → shows simplified example

### Manual Testing
- [ ] Update IP-004.md to simplified format
- [ ] Run `uv run spec-driver show delta DE-004`
- [ ] Verify output identical to before
- [ ] Run `uv run spec-driver create phase "Test" --plan IP-004`
- [ ] Verify plan.overview only has ID for new phase

### Backward Compatibility
- [ ] Old format plans still parse correctly
- [ ] Old format plans display correctly
- [ ] Migration path documented

## Files Checklist

### Must Change
- [ ] `supekku/scripts/lib/blocks/plan_metadata.py` - PLAN_OVERVIEW_METADATA phases field
- [ ] `supekku/scripts/lib/changes/creation.py` - create_phase function
- [ ] `.spec-driver/templates/implementation-plan-template.md` - template phases array
- [ ] `supekku/scripts/lib/changes/creation_test.py` - VT-PHASE-006 tests

### Likely Change
- [ ] `supekku/scripts/lib/blocks/plan.py` (parser)
- [ ] `supekku/scripts/lib/blocks/plan_metadata.py` (if separate)

### Verify No Change Needed
- [ ] `supekku/scripts/lib/formatters/change_formatters.py` (already reads phase files)
- [ ] Phase template (phase.md) - no changes needed

### Update After Implementation
- [ ] IP-004.md (this plan itself)
- [ ] Any other existing IP files
- [ ] PROD-006.md examples (if applicable)

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Breaking existing IPs | Maintain backward compatibility in parser |
| Formatter breaks | Test thoroughly; formatter already uses phase files |
| Schema validation too strict | Allow old format, warn on validation |
| Tests assume old structure | Update fixtures systematically |

## Definition of Done

- [ ] JSON schema updated and `schema show plan.overview` shows simplified format
- [ ] `create_phase` writes only ID to plan.overview
- [ ] Backward compatibility: old format plans still work
- [ ] All tests passing (including VT-PHASE-006)
- [ ] IP-004.md migrated to new format
- [ ] `show delta DE-004` output unchanged from before migration
- [ ] Template updated
- [ ] Linters passing

## Implementation Order

1. **Update JSON schema** - `supekku/scripts/lib/blocks/plan_metadata.py` (defines target)
2. **Update parser for backward compat** - `supekku/scripts/lib/blocks/plan.py` (read both formats)
3. **Update create_phase** - `supekku/scripts/lib/changes/creation.py` (write new format)
4. **Update tests** - `supekku/scripts/lib/changes/creation_test.py` (new assertions)
5. **Update template** - `.spec-driver/templates/implementation-plan-template.md`
6. **Test manually with DE-004** - Verify `show delta` still works
7. **Migrate IP-004.md** - Convert to ID-only format
8. **Run full test suite** - `just test && just lint`
9. **Update documentation** - Schema examples

## Notes

- Display already works correctly (reads from phase files)
- Main work is schema + creation logic
- Backward compatibility is key for smooth transition
- Could add migration command later: `spec-driver migrate plan IP-004` to auto-convert
