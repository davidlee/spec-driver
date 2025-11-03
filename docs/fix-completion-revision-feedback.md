# Fix: Complete Delta Revision Creation Feedback

## Problem

When completing a delta with `spec-driver complete delta DE-XXX`, the command:
1. Creates a completion revision (RE-XXX) but doesn't tell the user
2. Has two similar prompts that are confusing:
   - "Proceed with completion?"
   - "Proceed with updates?"
3. User discovers revision was created only by noticing the directory created

## Analysis

### Current Flow

In `supekku/scripts/complete_delta.py`:

1. **Line 446**: "Proceed with completion?" → User confirms completing the delta
2. **Line 453**: `update_requirements_in_revision_sources()` is called
3. **Line 255**: Inside that function, "Proceed with updates?" → User confirms updating requirements
4. **Line 281**: `create_completion_revision()` is called for untracked requirements
5. **Line 202**: Function returns `revision_id` but it's **not captured or displayed**

### Root Causes

1. **Silent revision creation**: `create_completion_revision()` return value is ignored (line 280-287)
2. **Confusing prompts**:
   - "Proceed with completion?" is about completing the delta
   - "Proceed with updates?" is about updating requirements in revision files
   - User doesn't understand the difference
3. **No feedback**: No message about revision file path after creation

## Solution

### 1. Capture and Display Revision ID

**File**: `supekku/scripts/complete_delta.py`

**Change** in `update_requirements_in_revision_sources()`:

```python
# Line 279-287 - BEFORE
if untracked:
  try:
    create_completion_revision(
      delta_id=delta_id,
      requirements=sorted(untracked),
      workspace=workspace,
    )
  except (ValueError, OSError):
    return False

# AFTER
if untracked:
  try:
    revision_id = create_completion_revision(
      delta_id=delta_id,
      requirements=sorted(untracked),
      workspace=workspace,
    )
    # Display revision info
    revision_path = workspace.root / "change" / "revisions" / f"RE-{revision_id[-3:]}-{delta_id.lower()}-completion"
    print(f"\n✓ Created completion revision: {revision_id}")
    print(f"  Path: {revision_path.relative_to(workspace.root)}")
  except (ValueError, OSError) as e:
    print(f"Error creating completion revision: {e}")
    return False
```

### 2. Clarify Prompts

**Option A: Better prompt wording**

```python
# Line 446 - BEFORE
if not force and not prompt_yes_no("Proceed with completion?", default=False):

# AFTER
if not force and not prompt_yes_no("Mark delta as completed?", default=False):

# Line 255 - BEFORE
if not force and not prompt_yes_no("Proceed with updates?", default=True):

# AFTER
if not force and not prompt_yes_no(
  "Update requirement statuses to 'active' in revision files?",
  default=True
):
```

**Option B: Single combined prompt** (more radical)

Merge the two prompts since they're part of the same operation. Users shouldn't need to understand the internal details.

### 3. Make Revision Creation Optional (Future Enhancement)

Not for immediate implementation, but consider:

```python
# Add flag to complete_delta
--skip-revision-creation  # Skip creating completion revision for untracked requirements
```

Rationale: Some projects might want to manually track these or not need the revision.

## Implementation Tasks

1. [x] Capture `revision_id` from `create_completion_revision()`
2. [x] Build revision path from workspace + revision_id
3. [x] Display revision ID and relative path after creation
4. [x] Improve prompt wording for clarity
5. [ ] Add test for revision creation feedback (optional - manual testing sufficient)
6. [ ] Update documentation (if needed)

## Testing

- Verify revision ID and path displayed correctly
- Verify path is relative to workspace root
- Test with multiple untracked requirements
- Test with zero untracked requirements (no revision created)
- Verify --force mode still creates revision silently

## Architecture Notes

Follows **Skinny CLI Pattern** - orchestration logic stays in complete_delta.py,
creation logic stays in completion.py. Display logic added to orchestration layer.

Location of display logic is correct per AGENTS.md - not formatting (goes in formatters/),
but workflow feedback (belongs in script).
