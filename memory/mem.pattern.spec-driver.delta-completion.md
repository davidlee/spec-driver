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
  artifacts, post-audit spec reconciliation, completion command, sync, and validation.'
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
  - kind: code
    note: Canonical completion command behavior
    ref: supekku/scripts/complete_delta.py
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

## Step 3: Audit + Contracts

- Execute required verification and audit activities.
- Reconcile implementation against contracts and audit findings.
- Ensure coverage evidence is explicit and consistent.

## Step 4: Patch Specs to Match Observed Truth

In owning specs/plans, update coverage/status entries using valid statuses:

- `planned`
- `in-progress`
- `verified`
- `failed`
- `blocked`

Do this before formal closure so specs reflect realised behavior.

## Step 5: Complete the Delta

Use the completion command as the canonical close-out path:

```bash
uv run spec-driver complete delta DE-XXX --dry-run
uv run spec-driver complete delta DE-XXX
```

Notes:
- Fix any reported coverage gate failures, then retry.
- Use `--force` only with explicit justification and documented follow-up work.

## Step 6: Sync and Validate

```bash
uv run spec-driver sync                     # populates traceability arrays
uv run spec-driver validate                 # checks structural integrity
```

## Verify

```bash
uv run spec-driver list requirements --spec PROD-XXX   # should reflect current lifecycle (typically 'active')
uv run spec-driver show delta DE-XXX                    # should show 'completed'
```

## Common Mistakes

- Completing delta before reconciling specs with audit/contracts
- Using invalid coverage statuses (for example `passed` instead of `verified`)
- Bypassing coverage gates with `--force` without documented follow-up
- Using wrong phase ID format (`phases: [phase-01]` instead of
  `phases: [{id: "IP-XXX.PHASE-01"}]`)
- Marking delta complete with unchecked IP success criteria
