---
name: plan-phases
description: Plan execution for a delta - refine IP objectives/gates and create the next phase sheet with concrete tasks and verification expectations.
---
You are turning design intent into an executable phase plan.

Inputs:
- `DE-XXX.md`
- `DR-XXX.md` (when present)
- `IP-XXX.md`

Process:
1. Read DE/DR/IP together.
2. Confirm planning is not getting ahead of design:
   - `DR-XXX.md` is missing or blank, stop and run `/draft-design-revision` unless you have been **expicitly instructed** otherwise.
   - if `DR-XXX.md` exists but is stale relative to the current ask or DE scope, reconcile the DR first. Clarify with the user if ambiguous.
   - you MUST NOT treat IP or phase creation as a substitute for unresolved design.
   - if planning surfaces substantive new design problems, run `/draft-design-revision` to revise or append to the DR.
3. Refine `IP-XXX.md`:
   - Phase objectives
   - Entry/exit criteria per phase
   - Success criteria and verification expectations
4. Create the next phase:
   - `uv run spec-driver create phase "<phase name>" --plan IP-XXX`
5. Update the new phase sheet with:
   - Task breakdown
   - Assumptions/constraints
   - Verification steps (VT/VA/VH expectations)
6. If plan complexity or policy ambiguity emerges, `/consult`.
7. Hand off to `/execute-phase` for implementation only after DR, IP, and the active phase sheet tell the same story.

Outcomes:
- IP is execution-ready.
- A concrete next phase sheet exists with clear done criteria.
