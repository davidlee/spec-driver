---
name: execute-phase
description: Execute an active implementation phase against DR/IP intent, keep notes current, and surface blockers early. You MUST use this skill when implementing a delta / IP.
---
You are executing one phase of planned work.

Inputs:
- Active phase sheet (`IP-XXX.PHASE-XX`)
- `IP-XXX.md`
- `DR-XXX.md` (when present, canonical design reference)
- `DE-XXX.md`

Process:
1. Confirm entry criteria are met for the active phase.
2. Read DR + IP + phase sheet before coding. `/preflight`
3. Ensure Delta status is in-progress (edit frontmatter)
4. Implement phase tasks (code/tests/docs) in small coherent units.
5. After each meaningful unit, run `/notes`.
6. If you encounter unexpected obstacles/tradeoffs/policy ambiguity, stop and `/consult`.
7. Keep verification evidence current as work progresses (`planned` -> `in-progress` -> `verified` as appropriate).
8. When exit criteria are met, hand off to `/audit-change` for verification and spec reconciliation.

Outcomes:
- Phase objectives are implemented with traceable evidence.
- Notes and handoff state stay current throughout execution.
