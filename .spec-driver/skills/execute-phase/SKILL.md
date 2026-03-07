---
name: execute-phase
description: Mandatory execution skill for any delta/IP implementation phase. Use it before code changes, move the owning delta to in-progress, keep notes current, and surface blockers early.
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
2. Read DR + IP + phase sheet before coding. `/preflight`
3. Ensure the owning delta frontmatter says `status: in-progress` before implementation work proceeds. If it still says `draft`, update it first.
4. Implement phase tasks (code/tests/docs) in small coherent units.
5. After each meaningful unit, run `/notes`.
6. If you encounter unexpected obstacles, tradeoffs, or policy ambiguity, stop and `/consult`.
7. Keep verification evidence current as work progresses (`planned` -> `in-progress` -> `verified` as appropriate).
8. When exit criteria are met, hand off to `/audit-change` for verification and spec reconciliation.

Outcomes:
- Phase objectives are implemented with traceable evidence.
- Delta lifecycle state matches reality during implementation, not only at closure.
- Notes and handoff state stay current throughout execution.
