# Phase 06 Quick Start

## TL;DR

Simplify `plan.overview` schema to remove duplication. Change phases array from full metadata to ID-only.

## Files to Edit

1. **`supekku/scripts/lib/blocks/plan_metadata.py`** (line 85-130)
   - Remove `name`, `objective`, `entrance_criteria`, `exit_criteria` from phases items properties
   - Keep only `id` field
   - Update example (line 150+) to show ID-only format

2. **`supekku/scripts/lib/changes/creation.py`**
   - Find `create_phase()` function
   - Update plan metadata write to only add `{id: phase_id}`
   - Remove code that copies name/objective/criteria

3. **`supekku/scripts/lib/blocks/plan.py`**
   - Update parser to handle both old (with metadata) and new (ID-only) formats
   - Ensure backward compatibility

4. **`.spec-driver/templates/implementation-plan-template.md`**
   - Simplify phases array to: `- id: PLAN-ID.PHASE-01`

5. **`supekku/scripts/lib/changes/creation_test.py`**
   - Update VT-PHASE-006 test assertions
   - Verify only ID written to plan

## Before/After

### Before (Current - Duplicated)
```yaml
phases:
  - id: IP-004.PHASE-01
    name: Phase 01 - Create Phase Command
    objective: Implement create phase...
    entrance_criteria: [...]
    exit_criteria: [...]
```

### After (Simplified - ID Only)
```yaml
phases:
  - id: IP-004.PHASE-01
  - id: IP-004.PHASE-02
```

## Testing

```bash
# After changes:
just test  # All tests should pass
just lint  # Should be clean

# Manual verification:
uv run spec-driver show delta DE-004
# Output should be identical to before changes

# Create test phase:
uv run spec-driver create phase "Test Phase" --plan IP-004
# Check IP-004.md - new phase should have only ID
```

## Backward Compatibility

Parser must accept BOTH formats:
- Old: `{id: X, name: Y, objective: Z, ...}` → extract ID, ignore rest
- New: `{id: X}` → extract ID

## Full Details

See `phase-06-implementation-plan.md` for comprehensive guide.
