---
id: mem.pattern.spec-driver.delta-completion
name: Delta Completion
kind: memory
status: active
memory_type: pattern
updated: "2026-03-04"
verified: "2026-03-04"
confidence: high
tags: [spec-driver, delta, completion, verification]
summary: "Self-contained checklist for closing a delta: phase completion, verification artifacts, spec coverage prerequisites, completion command, sync, and validation."
priority:
  severity: high
  weight: 9
scope:
  commands: [uv run spec-driver complete delta, complete delta]
  paths:
    - supekku/scripts/complete_delta.py
    - supekku/scripts/lib/changes/coverage_check.py
    - supekku/cli/complete.py
provenance:
  sources:
    - kind: code
      note: Canonical completion command behavior and lifecycle updates
      ref: supekku/scripts/complete_delta.py
    - kind: code
      note: Coverage gate enforcement and bypass conditions
      ref: supekku/scripts/lib/changes/coverage_check.py
    - kind: code
      note: Coverage status vocabulary
      ref: supekku/scripts/lib/blocks/verification.py
    - kind: doc
      note: Canonical close-out framing for this delta
      ref: change/deltas/DE-038-canonical_workflow_alignment/DR-038.md
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

Coverage blocks (`supekku:verification.coverage@v1`) in parent specs must
contain each `applies_to.requirements` entry with `status: verified` before
normal completion.

In owning specs/plans, update coverage entries using valid statuses:

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

- Fix coverage gate failures (`missing_block`, `missing_entry`, `not_verified`,
  invalid requirement IDs, or missing parent specs), then retry.
- Requirements with status `retired` block normal requirement lifecycle updates.
- Use `--force` only with explicit justification and documented follow-up work.
- `SPEC_DRIVER_ENFORCE_COVERAGE=false` disables the coverage check, but this is
  a non-canonical bypass.
- `--skip-update-requirements` is also a non-canonical bypass path.
- Non-interactive runs do not require piped prompt answers:
  sync prompt defaults to `no`; completion and requirement-update confirmations
  default to `yes`.
- Completion can update revision sources for requirement lifecycle state and
  create completion revision updates for untracked requirements.

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
- Running `complete delta` before parent specs have verified coverage blocks
- Bypassing coverage gates with `--force`/disabled enforcement without documented follow-up
- Using wrong phase ID format (`phases: [phase-01]` instead of
  `phases: [{id: "IP-XXX.PHASE-01"}]`)
- Marking delta complete with unchecked IP success criteria
