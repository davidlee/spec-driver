---
name: close-change
description: Close a delta safely - satisfy coverage gates, complete the delta command, and verify owning-record lifecycle updates.
---
You are executing formal closure, not just marking work done.

Inputs:
- Completed implementation phases/tasks
- Coverage/evidence updates in owning artifacts
- Target delta ID (`DE-XXX`)
- Any originating backlog item IDs linked to the delta, if present

Process:
1. Pre-check:
   - Phase/IP criteria complete
   - Specs patched to match contracts + audit findings
   - Relevant verification coverage statuses updated (typically `verified` where required)
   - Inspect the delta for originating backlog entries; if any exist, decide what closure update each needs before the delta is completed
   - Review notes/phase findings for durable facts, patterns, or gotchas and
     run `/capturing-memory` or `/maintaining-memory` before closure if the
     delta taught future agents something reusable
   - Apply the repo's commit policy from doctrine so `.spec-driver` workflow
     artefacts are committed in small, clean increments rather than silently
     accumulating while waiting for a perfect code/workflow split
2. Preview:
   - `uv run spec-driver complete delta DE-XXX --dry-run`
3. Complete:
   - `uv run spec-driver complete delta DE-XXX`
4. If blocked on coverage, fix owning spec/plan coverage blocks and retry.
5. Use `--force` only when explicitly justified; record reason and follow-up work.
6. Post-check:
   - `uv run spec-driver sync`
   - `uv run spec-driver validate`
   - `uv run spec-driver show delta DE-XXX`
   - `uv run spec-driver list requirements --spec SPEC-XXX`
   - Revisit any originating backlog entries and update their status/notes/links so they reflect the completed delta
7. Print:
   Δ ∴ ⊤

Semantics:
- Closure happens after audit/contracts-driven spec reconciliation, not before.
- Closure should update owning records and requirement lifecycle to current states (for this codebase, typically `active`, not legacy `implemented`).
- Prefer deterministic, repeatable close-out over manual ad-hoc edits.
- Backlog follow-through matters, but this skill should not invent non-canonical backlog statuses; if the correct backlog transition is unclear, stop and `/consult`.

Outcomes:
- Delta is completed.
- Lifecycle/evidence state is coherent across delta/spec/registry surfaces.
- Durable workflow or subsystem guidance from the delta is either captured in
  memory or consciously rejected before close-out.
- Any originating backlog entries have been consciously updated or explicitly
  flagged for follow-up rather than silently drifting stale.
