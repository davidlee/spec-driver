---
name: close-change
description: Close a delta safely - satisfy coverage gates, complete the delta command, and verify owning-record lifecycle updates.
---
You are executing formal closure, not just marking work done.

Inputs:
- Completed implementation phases/tasks
- Coverage/evidence updates in owning artifacts
- Target delta ID (`DE-XXX`)

Process:
1. Pre-check:
   - Phase/IP criteria complete
   - Specs patched to match contracts + audit findings
   - Relevant verification coverage statuses updated (typically `verified` where required)
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

Semantics:
- Closure happens after audit/contracts-driven spec reconciliation, not before.
- Closure should update owning records and requirement lifecycle to current states (for this codebase, typically `active`, not legacy `implemented`).
- Prefer deterministic, repeatable close-out over manual ad-hoc edits.

Outcomes:
- Delta is completed.
- Lifecycle/evidence state is coherent across delta/spec/registry surfaces.
