# Delta Completion Workflow

## Overview

This document describes the complete workflow for closing out deltas and marking requirements as satisfied in spec-driver.

## Key Artifacts and Their Relationships

### 1. PROD Spec (Product Specification)
- Defines requirements in markdown text (FR-xxx, NF-xxx)
- Contains `verification.coverage` YAML block listing verification artifacts
- Requirements themselves don't have status in the PROD spec

**Example:**
```yaml
```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-005
entries:
  - artefact: VT-001
    kind: VT
    requirement: PROD-005.FR-001
    status: planned  # or: in_progress, passed, failed
    notes: Verify leaf package identification
```

### 2. Delta Document
- Located in `change/deltas/DE-XXX-slug/DE-XXX.md`
- Has frontmatter with `status` field: `draft`, `in_progress`, `completed`
- Contains `delta.relationships` YAML block linking to requirements

**Example:**
```yaml
---
id: DE-002
status: completed  # Update when all phases complete
---

```yaml supekku:delta.relationships@v1
schema: supekku.delta.relationships
version: 1
delta: DE-002
specs:
  primary:
    - PROD-005
requirements:
  implements:
    - PROD-005.FR-001
    - PROD-005.FR-002
phases:
  - id: IP-002.PHASE-01
  - id: IP-002.PHASE-02
```
```

### 3. Implementation Plan (IP)
- Located in same directory as delta: `DE-XXX/IP-XXX.md`
- Contains `plan.overview` YAML block
- Has "Success Criteria" section with checkboxes

**Example:**
```yaml
```yaml supekku:plan.overview@v1
schema: supekku.plan.overview
version: 1
plan: IP-002
delta: DE-002
phases:
  - id: IP-002.PHASE-01
    name: Phase 01 - Foundation
    objective: Implement package detection logic
```

## Success Criteria:
- [x] Package detection implemented
- [x] All tests passing
```

### 4. Phase Documents
- Located in `DE-XXX/phases/phase-NN.md`
- Contains `phase.overview` YAML block
- Tracks detailed progress and completion

**Example:**
```yaml
```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-002.PHASE-01
plan: IP-002
delta: DE-002
```

**Phase Status**: ✅ **COMPLETE**
```

### 5. Requirements Registry
- Located at `.spec-driver/registry/requirements.yaml`
- **This is the source of truth for requirement status**
- Tracked automatically by sync, but may need manual updates

**Example:**
```yaml
requirements:
  PROD-005.FR-001:
    label: FR-001
    title: Leaf Python Package Identification
    status: implemented  # pending, in_progress, implemented, verified
    implemented_by:
      - DE-002
    verified_by:
      - VT-001
```

## Delta Completion Workflow

### Step 1: During Implementation

As you work through phases:

1. **Mark phase complete in phase sheet**:
   - Update exit criteria checkboxes
   - Add completion summary at bottom
   - Set phase status: `✅ **COMPLETE**`

2. **Update IP success criteria**:
   - Check off completed items in IP-XXX.md
   - Verify all checkboxes marked

### Step 2: Mark Delta Complete

When all phases are done:

1. **Update delta frontmatter status**:
   ```yaml
   status: completed  # was: draft or in_progress
   ```

2. **Verify delta.relationships block**:
   - Ensure all implemented requirements listed
   - Ensure phase IDs use proper format: `{id: "IP-XXX.PHASE-NN"}`

### Step 3: Update Verification Artifacts

In the PROD spec (`specify/product/PROD-XXX/PROD-XXX.md`):

1. **Update verification.coverage block**:
   ```yaml
   entries:
     - artefact: VT-001
       status: passed  # was: planned
     - artefact: VT-002
       status: passed
   ```

### Step 4: Update Requirements Registry

**This is the critical step that updates requirement status!**

Edit `.spec-driver/registry/requirements.yaml`:

```yaml
PROD-005.FR-001:
  status: implemented  # was: pending
  implemented_by:
    - DE-002  # Add delta ID
  verified_by: []  # Leave empty unless standalone audit files exist
```

Repeat for all requirements implemented by the delta.

### Step 5: Sync and Validate

```bash
uv run spec-driver sync
uv run spec-driver validate
```

Verify changes:
```bash
uv run spec-driver list requirements --spec PROD-XXX
uv run spec-driver show delta DE-XXX
```

## Common Pitfalls

### ❌ Updating Only Delta Status
**Problem**: Marking delta as `completed` but not updating requirements registry.

**Result**: Requirements still show as `pending`, breaking traceability.

**Fix**: Always update requirements registry (Step 4).

### ❌ Forgetting Verification Artifacts
**Problem**: Not updating verification.coverage status in PROD spec.

**Result**: VT/VA artifacts show as `planned` even though work is done.

**Fix**: Update PROD spec verification.coverage block (Step 3).

### ❌ Wrong Phase ID Format
**Problem**: Using `phases: [phase-01]` instead of `phases: [{id: "IP-XXX.PHASE-01"}]`

**Result**: Schema validation may fail or relationships break.

**Fix**: Always use object format with `id` field.

### ❌ Incomplete Success Criteria
**Problem**: Marking delta complete with unchecked IP success criteria.

**Result**: Unclear if all work actually done.

**Fix**: Review and check all success criteria boxes first.

## Requirement Status Lifecycle

```
pending         # Initial state, requirement defined but not worked on
    ↓
in_progress    # Delta implementing requirement is in progress
    ↓
implemented    # Delta implementing requirement is completed
    ↓
verified       # (Optional) Requirement verified in production/deployment
```

**Status Field Semantics**:
- `pending`: No delta assigned or delta is draft
- `in_progress`: Delta implementing this is in progress
- `implemented`: Delta is completed, verification artifacts passed
- `verified`: (Future) Actually verified in production

## Verification Artifact Status Lifecycle

```
planned        # Verification artifact defined in PROD spec
    ↓
in_progress   # Currently being executed/created
    ↓
passed        # Verification successful
(or)
failed        # Verification failed, needs rework
```

## Quick Checklist: Completing a Delta

- [ ] All phase sheets marked complete with status summaries
- [ ] IP success criteria all checked off
- [ ] Delta frontmatter: `status: completed`
- [ ] Delta relationships block: all phases listed with proper IDs
- [ ] PROD spec: verification.coverage entries marked `passed`
- [ ] Requirements registry: status updated to `implemented`
- [ ] Requirements registry: `implemented_by` includes delta ID
- [ ] Requirements registry: `verified_by` set to empty array `[]` (unless standalone audit files exist)
- [ ] Run `spec-driver sync` successfully
- [ ] Run `spec-driver validate` successfully
- [ ] Verify: `spec-driver list requirements --spec PROD-XXX` shows `implemented`
- [ ] Verify: `spec-driver show delta DE-XXX` shows completed status

## File Locations Reference

```
change/deltas/
  DE-XXX-slug/
    DE-XXX.md              # Delta document (update status here)
    IP-XXX.md              # Implementation plan (check success criteria)
    phases/
      phase-01.md          # Phase sheets (mark complete)
      phase-02.md
      ...

specify/product/
  PROD-XXX/
    PROD-XXX.md            # PROD spec (update verification.coverage)

.spec-driver/registry/
  requirements.yaml        # Requirements registry (UPDATE THIS!)
```

## Example: Complete DE-002 Workflow

1. ✅ Phases marked complete: `IP-002/phases/phase-01.md`, `phase-02.md`, `phase-03.md`
2. ✅ IP success criteria checked: All boxes in `IP-002.md` Section 9
3. ✅ Delta status: `DE-002.md` frontmatter `status: completed`
4. ✅ Verification artifacts: `PROD-005.md` verification.coverage all `status: passed`
5. ✅ Requirements registry updated:
   - PROD-005.FR-001 through FR-004: `status: implemented`, `implemented_by: [DE-002]`
   - PROD-005.NF-001, NF-002: `status: implemented`, `implemented_by: [DE-002]`
6. ✅ Sync and validate passing
7. ✅ `list requirements --spec PROD-005` shows all as `implemented`

**Result**: Complete traceability chain from requirements → delta → verification → implementation.
