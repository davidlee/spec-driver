# Status-Based Stub Detection Analysis

**Date**: 2025-11-02
**Context**: Revising Task 1.2 stub detection approach based on user insight

## Current State

### Frontmatter Schema
- `status` is a **required** string field in spec frontmatter (`frontmatter.spec` schema)
- No enum constraint - any string value allowed
- Currently used values in codebase: `"draft"`, `"planned"`

### Spec Creation
- **Manual creation** (`supekku/scripts/lib/specs/creation.py:361`): Sets `status: "draft"`
- **Sync-generated** specs: Currently also use `"draft"` (no differentiation)

### Problem with Original Approach
The original plan (Task 1.2) was to:
- Compare spec body content against rendered template
- Use exact string matching with whitespace normalization
- Risk: False positives, brittle, requires complex normalization logic

## Proposed Solution: Status-Based Detection

### Approach
Use `status: "stub"` to explicitly mark auto-generated specs that haven't been manually edited.

### Implementation Changes Required

#### 1. Update Spec Creation for Sync
**File**: `supekku/scripts/lib/specs/creation.py` (or sync adapter code)

When sync auto-generates specs, set:
```python
"status": "stub"  # instead of "draft"
```

#### 2. Simplify Detection Logic
**File**: `supekku/scripts/lib/specs/detection.py` (new, simplified)

```python
def is_stub_spec(spec_path: Path, root: Path | None = None) -> bool:
    """Check if spec is a stub based on status field.

    Args:
        spec_path: Path to spec file
        root: Optional repo root

    Returns:
        True if status is "stub", False otherwise
    """
    frontmatter, _ = load_validated_markdown_file(spec_path)
    return frontmatter.get("status") == "stub"
```

#### 3. User Workflow
When users edit a stub spec:
- They can change `status: stub` → `status: draft` to indicate manual work
- Or: Backfill command automatically changes status after completion
- Provides explicit signal of which specs need attention

### Benefits

✅ **Simple**: Single field check, no content comparison
✅ **Explicit**: Clear semantic meaning
✅ **Fast**: O(1) operation, no template rendering needed
✅ **Reliable**: No false positives from whitespace/formatting differences
✅ **User-friendly**: Users can see at a glance which specs are stubs
✅ **Queryable**: Can easily list all stub specs: `status: stub`

### Drawbacks

⚠️ Requires users to remember to update status (or automation does it)
⚠️ Existing auto-generated specs with `status: draft` won't be detected as stubs
⚠️ Need migration strategy for existing stub specs

## Migration Strategy

### Option A: One-time Migration (Recommended)
1. Create migration script to identify likely stubs (body matches template)
2. Update those specs to `status: stub`
3. Run once, commit

### Option B: Hybrid Detection with Line Count (Recommended)
```python
def is_stub_spec(spec_path: Path) -> bool:
    frontmatter, body = load_validated_markdown_file(spec_path)

    # Explicit stub status
    if frontmatter.get("status") == "stub":
        return True

    # Pragmatic fallback: line count
    # Auto-generated tech specs are exactly 28 lines
    # Any human edit typically adds content, pushing >30 lines
    total_lines = spec_path.read_text().count('\n') + 1
    if total_lines <= 30:
        return True

    return False
```

**Rationale** (from user observation):
- All auto-generated tech specs: exactly 28 lines
- Manually created specs: 356-812 lines
- Template renders to ~28 lines with empty YAML blocks
- Using 30-line threshold accounts for minor human edits (typo fixes, etc.)
- Much cheaper than template rendering: O(1) file read vs Jinja2 processing

### Option C: Status Values as Enum
Add to schema (future):
```yaml
status:
  enum: ["stub", "draft", "review", "accepted", "deprecated"]
```

## Recommendations

1. **Adopt status-based approach** - much simpler and more reliable
2. **Update sync code** to set `status: "stub"` for auto-generated specs
3. **Implement hybrid detection with line count** (Option B) for backward compatibility
   - Primary: Check `status == "stub"`
   - Fallback: Line count ≤30 (pragmatic, fast, accounts for human error)
4. **Auto-update status** in backfill command: `stub` → `draft` after completion
5. **Update phase-01.md** with revised Task 1.2 implementation plan

### Why Line Count Works
- **Empirical data**: All tech stubs = 28 lines exactly
- **Safety margin**: 30-line threshold catches typo fixes without false negatives
- **Performance**: Single file read, no template rendering
- **Robust**: Works with existing specs immediately, no migration needed

## Files to Modify

### New Implementation
- `supekku/scripts/lib/specs/detection.py` - Simplified detection logic
- `supekku/scripts/lib/specs/detection_test.py` - Tests for status-based detection

### Updates Required
- Sync adapter code (wherever specs are auto-generated) - set `status: "stub"`
- `supekku/scripts/lib/specs/creation.py` - Add parameter for stub status?
- `change/deltas/DE-005-implement-spec-backfill/phases/phase-01.md` - Update Task 1.2

### Testing
- Test: Spec with `status: stub` → `is_stub_spec() == True`
- Test: Spec with `status: draft` → `is_stub_spec() == False`
- Test: Hybrid mode for backward compatibility

## Next Steps

1. ✅ Document findings (this file)
2. [ ] User approval of approach
3. [ ] Update phase-01.md Task 1.2 details
4. [ ] Implement simplified detection.py
5. [ ] Update sync code to use `status: "stub"`
6. [ ] Write tests
7. [ ] Optional: Migration script for existing stubs
