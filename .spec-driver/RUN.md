# Spec-Driver Operational Guide

Quick reference for common operational workflows.

## Delta Completion Workflow

### Overview

When completing a delta that implements requirements, you must update the parent spec's coverage blocks to reflect verification status. This ensures the spec remains the authoritative source of truth for requirement lifecycle states (per PROD-008).

### Prerequisites

- Delta has been fully implemented
- All verification artifacts (VT/VA/VH) have been executed
- Implementation plan coverage block tracks current status

### Step-by-Step Process

#### 1. Review Implementation Plan Coverage

Check the IP coverage block to see which requirements were verified:

```bash
uv run spec-driver show delta DE-XXX --json | jq '.coverage'
```

Or manually inspect the IP file:
```yaml
# In change/deltas/DE-XXX/IP-XXX.md
```yaml supekku:verification.coverage@v1
entries:
  - artefact: VT-902
    kind: VT
    requirement: PROD-008.FR-001
    status: verified  # ← Check these statuses
```

#### 2. Update Parent Spec Coverage Blocks

For each requirement in the delta's `applies_to.requirements`, update the parent spec:

**Before (planned/in-progress):**
```yaml
# In specify/product/PROD-008/PROD-008.md
```yaml supekku:verification.coverage@v1
entries:
  - artefact: VT-902
    kind: VT
    requirement: PROD-008.FR-001
    status: planned  # ← Not verified yet
    notes: Registry sync integration test
```

**After (verified):**
```yaml
# In specify/product/PROD-008/PROD-008.md
```yaml supekku:verification.coverage@v1
entries:
  - artefact: VT-902
    kind: VT
    requirement: PROD-008.FR-001
    status: verified  # ← Updated to verified
    notes: Registry sync integration test
```

**Valid statuses:** planned, in-progress, verified, failed, blocked

#### 3. Attempt Delta Completion

Run the completion command:

```bash
uv run spec-driver complete delta DE-XXX
```

**If coverage check passes:**
- Proceeds to final confirmation
- Updates delta status to `completed`
- Transitions requirements to `live` status (if enabled)

**If coverage check fails:**
```
ERROR: Cannot complete DE-XXX - coverage verification required

The following requirements need verified coverage in their specs:

  PROD-008.FR-001 (in specify/product/PROD-008/PROD-008.md)
    Current status: planned
    Action: Update coverage block status to 'verified'

Example coverage update:
```yaml supekku:verification.coverage@v1
entries:
  - artefact: VT-902
    kind: VT
    requirement: PROD-008.FR-001
    status: verified  # ← Update this
    notes: Description of verification
```

To bypass this check (emergency only):
  uv run spec-driver complete delta DE-XXX --force
```

#### 4. Fix Coverage and Retry

Update the spec coverage blocks as indicated, then re-run:

```bash
uv run spec-driver complete delta DE-XXX
```

### Emergency Override

For urgent situations where coverage updates must be deferred:

```bash
uv run spec-driver complete delta DE-XXX --force
```

⚠️ **Warning:** Using `--force` bypasses coverage verification. Create a follow-up task to update coverage blocks.

### Disabling Enforcement

To disable coverage enforcement globally (not recommended):

```bash
export SPEC_DRIVER_ENFORCE_COVERAGE=false
uv run spec-driver complete delta DE-XXX
```

### Troubleshooting

**"Spec not found in workspace"**
- Verify spec ID in requirement (e.g., `PROD-008.FR-001` → spec `PROD-008`)
- Check spec file exists in `specify/product/` or `specify/tech/`

**"Spec has no coverage block"**
- Legacy spec without coverage
- Add coverage block (see example above)
- Or use `--force` and document as technical debt

**"Requirement not found in coverage block"**
- Coverage entry missing for this requirement
- Add entry to spec coverage block

**"Coverage status is 'failed' or 'blocked'"**
- Tests or verification failed
- Fix the issue before completing delta
- Update status to 'verified' once fixed

## Coverage Block Maintenance

### Adding Coverage Entries

When introducing new requirements in a spec:

```yaml
```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-100
entries:
  - artefact: VT-100
    kind: VT
    requirement: SPEC-100.FR-001
    status: planned
    notes: Unit test for feature X
```

### Verification Artifact Kinds

- **VT** (Verification Test): Automated test (unit, integration, e2e)
- **VA** (Verification by Agent): Agent-generated analysis or test report
- **VH** (Verification by Human): Manual testing, attestation, acceptance

### Status Lifecycle

```
planned → in-progress → verified
                     ↓
                  failed/blocked → (fix) → verified
```

## Related Documentation

- **PROD-008**: Requirements Lifecycle Coherence (coverage contract)
- **PROD-009**: Requirement Lifecycle Semantics (status precedence)
- **SPEC-122**: Requirements Registry Infrastructure
- **AGENTS.md**: Agent-specific checklists and workflows

## Quick Reference Commands

```bash
# Show delta details with coverage
uv run spec-driver show delta DE-XXX --json | jq '.coverage'

# Complete delta (with coverage check)
uv run spec-driver complete delta DE-XXX

# Complete delta (force, skip coverage check)
uv run spec-driver complete delta DE-XXX --force

# Complete delta (dry-run preview)
uv run spec-driver complete delta DE-XXX --dry-run

# Check delta status
uv run spec-driver show delta DE-XXX

# List all deltas
uv run spec-driver list deltas

# Sync all registries
just supekku::sync-all
```
