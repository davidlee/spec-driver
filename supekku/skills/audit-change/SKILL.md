---
name: audit-change
description: "Creates or updates an AUD audit artefact, dispositions every finding, reconciles specs and contracts, and hands off to closure. Use when post-implementation conformance checking is needed, when audit findings must be resolved, or when preparing a delta for close-out."
---

Runs the canonical audit reconciliation loop for a delta or discovery investigation.

## Inputs

- Delta/phase outputs, relevant specs, contracts, and verification artifacts.
- Owning delta/phase/DR context for post-implementation conformance work.

## Process

1. **Determine audit mode**: `conformance` (post-implementation, tied to a delta) or `discovery` (backfill/investigation). Identify the owning `DE-XXX` for delta work.
2. **Create the audit artefact**:
   - `uv run spec-driver create audit "<title>" --mode conformance --delta DE-XXX --spec SPEC-XXX --code-scope "path/"`
   - `uv run spec-driver create audit "<title>" --mode discovery --spec SPEC-XXX`
   - A standalone `AUD-*` is required for delta work; loose notes are not a substitute.
3. **Progress the lifecycle**: `draft` → `in-progress` → `completed`. Move to `completed` only after every finding is dispositioned.
4. **Gather evidence**: run tests/checks from the delta and verification plan. Update coverage blocks with valid statuses: `planned`, `in-progress`, `verified`, `failed`, `blocked`.
5. **Record findings** with structured `outcome` and machine-checkable `disposition` fields.
6. **Disposition each finding** using one of:
   - `aligned` — behavior is correct, no follow-up needed.
   - `spec_patch` — owning spec needs an in-scope correction.
   - `revision` — authority or requirement ownership must move.
   - `follow_up_delta` / `follow_up_backlog` — deferred to future work.
   - `tolerated_drift` — explicit unresolved drift with documented rationale.
7. **Route non-aligned findings** in preference order: `spec_patch` → `revision` → revision-led new spec. Do not pick `follow_up_*` to avoid inconvenient spec work, and do not pick `revision` when a patch suffices. If ambiguous, run `/consult`.
8. **Reconcile before handoff**: patch specs, create revisions, or file follow-up items as determined by dispositions.
9. **Validate**: run `uv run spec-driver sync` and `uv run spec-driver validate`. Confirm both pass before proceeding.
10. **Hand off**: route to `/close-change` only when the audit artefact, owning specs, and follow-up refs tell a coherent closure story. If blocking findings remain, do not hand off.
