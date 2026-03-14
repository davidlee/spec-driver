---
name: execute-phase
description: Mandatory execution skill for any delta/IP implementation phase. Use it before code changes, move the owning delta to in-progress, keep notes current, reconcile structured execution docs, and surface blockers early.
---

This skill is mandatory for implementation work under a delta or implementation
plan.

Do not start coding, editing tests, or updating implementation docs for a
delta/IP phase until you have entered through `/execute-phase`.

If the delta still says `draft`, that is not harmless bookkeeping. Change it to
`in-progress` before implementation continues so the lifecycle truth matches the
actual state of work.

You are executing one phase of planned work.

Inputs:

- Active phase sheet (`IP-XXX.PHASE-XX`)
- `IP-XXX.md`
- `DR-XXX.md` (when present, canonical design reference)
- `DE-XXX.md`

Process:

1. Confirm entry criteria are met for the active phase.
2. Read DR + IP + phase sheet before coding and use `/preflight` to surface
   confirmed inputs, assumptions, unresolved questions, and tensions before
   implementation.
3. Identify the concrete files or components you expect to touch first and run
   `/retrieving-memory` against those paths before deep reading or editing so
   any `scope.globs` gotchas or patterns surface early.
4. Ensure the owning delta frontmatter says `status: in-progress` before implementation work proceeds. If it still says `draft`, update it first.
5. Implement phase tasks (code/tests/docs) in small coherent units.
6. After each meaningful unit, run `/notes`.
7. If that unit produced a durable gotcha, pattern, or subsystem fact worth
   future retrieval, run `/capturing-memory` or `/maintaining-memory` before
   moving on.
8. When execution changed phase/IP/DE/DR state, run `/update-delta-docs`.
9. Follow the repo's commit policy from doctrine. Bias toward frequent, small
   commits of `.spec-driver/**` changes and a clean repo. If `.spec-driver/**`
   edits and code edits are both accumulating, commit them together or
   separately based on what naturally gets committed first; do not let workflow
   artefacts drift in a stale uncommitted pile while waiting for the perfect
   bundle.
10. If `/preflight` or implementation reveals unresolved design ambiguity,
    unexpected obstacles, tradeoffs, or policy ambiguity, stop and `/consult`
    before improvising past it.
11. Keep verification evidence current as work progresses (`planned` -> `in-progress` -> `verified` as appropriate).
12. Before declaring the phase ready for audit, review the touched subsystems
    and notes once more for missed memory-capture candidates.
13. When exit criteria are met, hand off to `/audit-change` for verification and spec reconciliation.

Outcomes:

- Phase objectives are implemented with traceable evidence.
- Delta lifecycle state matches reality during implementation, not only at closure.
- Notes and structured execution artefacts stay current throughout execution.
