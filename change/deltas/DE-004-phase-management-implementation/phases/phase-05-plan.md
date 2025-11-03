# Phase 05 Implementation Plan - Structured Progress Tracking

## Strategy

Implement `phase.tracking@v1` YAML block to replace regex-based task counting with structured data.

### Key Decisions
1. **Tracking block is OPTIONAL** - maintains backward compatibility
2. **Precedence**: tracking block > regex fallback
3. **Task status**: `pending | in_progress | completed | blocked`
4. **Criteria completion**: boolean (`true`/`false`)
5. **Location**: After phase.overview block in phase files

## Implementation Order

### 1. Schema Definition (Task 5.1)
**File**: `supekku/scripts/lib/blocks/plan.py`

Define tracking schema structure:
```python
@dataclass
class PhaseTrackingBlock:
    """Parsed phase.tracking@v1 YAML block."""
    schema: str
    version: int
    phase: str
    entrance_criteria: list[dict] = field(default_factory=list)  # [{item, completed}]
    exit_criteria: list[dict] = field(default_factory=list)      # [{item, completed}]
    tasks: list[dict] = field(default_factory=list)              # [{id, description, status}]
    raw_yaml: str = ""
```

### 2. Parser Implementation (Task 5.2)
**File**: `supekku/scripts/lib/blocks/plan.py`

Add extraction function:
```python
def extract_phase_tracking(content: str) -> Optional[PhaseTrackingBlock]:
    """Extract phase.tracking@v1 block from markdown content."""
    # Regex pattern similar to extract_phase_overview()
    # Return None if not found (backward compat)
```

### 3. Validator Implementation (Task 5.3)
**File**: `supekku/scripts/lib/blocks/plan.py`

Add validator class following existing pattern:
```python
class PhaseTrackingValidator:
    """Validates phase.tracking@v1 YAML blocks."""
    def validate(self, data: dict, file_path: str) -> list[str]:
        # Check required fields: schema, version, phase
        # Validate criteria: [{item: str, completed: bool}]
        # Validate tasks: [{id: str, description: str, status: enum}]
```

### 4. Formatter Enhancement (Task 5.4)
**File**: `supekku/scripts/lib/formatters/change_formatters.py`

Update `_enrich_phase_data()`:
```python
def _enrich_phase_data(phase_path: str) -> dict:
    # Try extract_phase_tracking() first
    # If found: calculate from tracking.tasks
    # Else: fallback to regex parsing (current behavior)
```

### 5. Tests (Task 5.5)
**File**: `supekku/scripts/lib/blocks/tracking_test.py` (new)

Test coverage:
- Parse valid tracking block
- Parse missing tracking block (returns None)
- Validate correct schema
- Validate missing required fields
- Validate invalid status enum
- Formatter uses tracking data when present
- Formatter falls back to regex when absent
- Progress calculation accuracy

### 6. Template Update (Task 5.6)
**File**: `supekku/templates/phase.md`

Add tracking block example with clear comments about optional nature.

### 7. Self-Dogfooding (Task 5.7)
Add tracking block to `phase-05.md` itself to verify functionality.

## Testing Strategy

### Unit Tests (VT-PHASE-007)
- Parser: extract tracking from markdown
- Validator: schema compliance
- Formatter: tracking data precedence
- Backward compat: phases without tracking still work

### Integration Tests
- Create phase with tracking block
- Show delta displays correct progress
- Existing phases (no tracking) still display

### Manual Tests
- `show delta DE-004` with phase-05 tracking block
- Verify task counts accurate
- Update tracking block, verify changes reflected

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Break existing phases | Make tracking optional, test backward compat |
| Complex YAML editing | Provide clear examples, validate strictly |
| Formatter complexity | Separate tracking vs regex code paths clearly |
| Performance | Cache parsed blocks in artifacts model if needed |

## Files Touched

1. `supekku/scripts/lib/blocks/plan.py` - schema, parser, validator
2. `supekku/scripts/lib/formatters/change_formatters.py` - enrichment logic
3. `supekku/templates/phase.md` - add tracking example
4. `supekku/scripts/lib/blocks/tracking_test.py` - new test file
5. `change/deltas/DE-004-phase-management-implementation/phases/phase-05.md` - add tracking block

## Success Criteria

- [ ] All VT-PHASE-007 tests passing
- [ ] Phase 05 has tracking block, shows accurate progress in `show delta`
- [ ] Existing phases (01, 04) without tracking still display correctly
- [ ] Full test suite passing (1163+ tests)
- [ ] Linters clean (`just lint`, `just pylint`)
- [ ] Template includes tracking example
- [ ] Backward compatibility verified

## Estimated Effort

- Schema/Parser/Validator: ~1-2 hours
- Formatter updates: ~1 hour
- Tests: ~1-2 hours
- Template/dogfood: ~30 min

Total: ~3-5 hours
