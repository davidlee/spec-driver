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
2. Refine `IP-XXX.md`:
   - Phase objectives
   - Entry/exit criteria per phase
   - Success criteria and verification expectations
3. Create the next phase:
   - `uv run spec-driver create phase "<phase name>" --plan IP-XXX`
4. Update the new phase sheet with:
   - Task breakdown
   - Assumptions/constraints
   - Verification steps (VT/VA/VH expectations)
5. If plan complexity or policy ambiguity emerges, `/consult`.
6. Hand off to `/execute-phase` for implementation.

Outcomes:
- IP is execution-ready.
- A concrete next phase sheet exists with clear done criteria.
