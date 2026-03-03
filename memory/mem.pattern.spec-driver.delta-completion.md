---
id: mem.pattern.spec-driver.delta-completion
name: Delta Completion
kind: memory
status: active
memory_type: pattern
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- delta
- completion
- verification
- seed
summary: 'Self-contained checklist for closing a delta: phase completion, verification
  artifacts, requirements registry updates, sync, and validation.'
priority:
  severity: high
  weight: 9
provenance:
  sources:
  - kind: doc
    note: Complete workflow and checklist
    ref: docs/delta-completion-workflow.md
  - kind: doc
    note: Status lifecycle and traceability
    ref: supekku/about/lifecycle.md
---

# Delta Completion

## When to Use

After all implementation work for a [[mem.concept.spec-driver.delta]] is done.
This is the close-out procedure that updates all owning records.

## Step 1: Complete Phases

For each phase sheet (`change/deltas/DE-XXX-slug/phases/phase-NN.md`):

- Update exit criteria checkboxes
- Add completion summary
- Set phase status to complete

## Step 2: Close the Plan

In `IP-XXX.md`:

- Verify all success criteria checkboxes are checked
- Ensure `supekku:plan.overview` YAML lists all phase IDs

## Step 3: Close the Delta

In `DE-XXX.md`:

- Set frontmatter `status: completed`
- Verify `supekku:delta.relationships` block lists all implemented requirements
  and phase IDs (format: `{id: "IP-XXX.PHASE-NN"}`)

## Step 4: Update Verification

In the owning spec (typically `PROD-XXX.md`):

- Update `supekku:verification.coverage` entries to `status: passed`
  (see [[mem.concept.spec-driver.verification]])

## Step 5: Update Requirements Registry

**This is the most commonly missed step.**

Edit `.spec-driver/registry/requirements.yaml`:

```yaml
PROD-XXX.FR-001:
  status: implemented        # was: pending or in_progress
  implemented_by:
    - DE-XXX                 # add delta ID
  verified_by: []            # leave empty unless audit exists
```

Repeat for all requirements implemented by the delta.

## Step 6: Sync and Validate

```bash
uv run spec-driver complete delta DE-XXX    # attempts automated completion
uv run spec-driver sync                     # populates traceability arrays
uv run spec-driver validate                 # checks structural integrity
```

If `complete delta` requires `--force`, document the reason and create a
follow-up task for any skipped coverage updates.

## Verify

```bash
uv run spec-driver list requirements --spec PROD-XXX   # should show 'implemented'
uv run spec-driver show delta DE-XXX                    # should show 'completed'
```

## Common Mistakes

- Updating delta status but forgetting the requirements registry (Step 5)
- Not updating verification coverage entries in the spec (Step 4)
- Using wrong phase ID format (`phases: [phase-01]` instead of
  `phases: [{id: "IP-XXX.PHASE-01"}]`)
- Marking delta complete with unchecked IP success criteria
