---
name: using-spec-driver
description: Mandatory routing skill for ANY substantive work in a spec-driver project. Choose the governing skill before acting, and do not start implementation until the required delta/design/plan/phase artefacts exist.
---

You MUST choose the governing workflow skill before doing substantive work.

This skill is not optional process fluff. It is the routing layer for work in a
spec-driver repo.

If there is a reasonable chance that another spec-driver skill governs the
task, you MUST route through that skill before proceeding.

Do not respond, explore, inspect files, run commands, or start implementation
until you have decided which skill governs the task.

Do not rationalize your way around this.

If you skip routing because the task feels familiar, simple, urgent, or
"probably fine", you are doing it wrong.

Red-flag thoughts:

- "I can just inspect files first."
- "I already know the command shape."
- "This is small enough that I do not need workflow routing."
- "I will gather context first and decide later."

Those are routing failures. Stop and choose the governing skill.

Default stance:

- substantive work in this repo starts here
- if spec-driver entities or commands are involved, `/spec-driver` is usually first
- if you are unsure, route to the stricter skill first, not the looser one

Process:

1. Read the task and decide whether it touches spec-driver workflow, artefacts, or doctrine.
2. If the task involves creating, listing, finding, showing, editing, completing, or explaining spec-driver entities or CLI usage:
   - use `/spec-driver`
3. If the task asks "what is the right way here?", touches an unfamiliar subsystem, or risks assumption:
   - use `/retrieving-memory`
   - use `/doctrine` when governance, workflow posture, or local conventions matter
4. If the task is substantive new work and the path is not yet clear:
   - use `/preflight`
5. If code-changing intent is emerging and there is no governing change artefact yet:
   - use `/scope-delta`
   - use `/shape-revision` first only when governance or doctrine requires revision-first flow
6. If a delta exists but execution readiness is incomplete:
   - use `/shape-revision` when revision-first governance applies
   - if the work is non-trivial and the DR is missing, stale, or no longer matches the current ask, route to `/draft-design-revision` before `/plan-phases`
   - otherwise use `/scope-delta` and `/plan-phases` to make the bundle execution-ready
   - do not route to `/execute-phase` until the relevant DR/IP/phase sheet exists for the work being done
7. If a delta phase is already active and the needed planning artefacts exist:
   - use `/execute-phase` for delta/IP execution
   - use `/implement` only for well-defined work already grounded in the right artefacts
8. If implementation is complete and the task is now about evidence, reconciliation, or close-out:
   - use `/audit-change`
   - then use `/close-change` when closure conditions are met

Priority order:

1. `/spec-driver` when the task touches spec-driver entities or commands
2. `/retrieving-memory` and `/doctrine` when correctness depends on local truth
3. `/preflight` when the path is not yet clear
4. Workflow-shaping skills such as `/scope-delta`, `/shape-revision`, `/execute-phase`
5. Close-out skills such as `/audit-change` and `/close-change`

Guardrails:

- Do not guess entity IDs, command shapes, or file locations when `/spec-driver` should be used.
- Do not implement code-changing work without a governing card, delta, revision, or equivalent artefact appropriate to project posture.
- Do not treat IP or phase creation as a substitute for missing or stale non-trivial DR work.
- Do not jump from "there is a delta" to `/execute-phase` if DR/IP/phase creation is still the missing work.
- Do not treat plans as higher authority than doctrine, specs, or design revisions.
- Do not import stricter ceremony than the project has adopted.

Common failure modes:

- "I'll just inspect files first" - stop and decide whether `/spec-driver`, `/retrieving-memory`, or `/preflight` governs that exploration.
- "This is probably simple enough to skip workflow routing" - small tasks still need the right governing skill.
- "I already know the command shape" - use `/spec-driver` when the task is about spec-driver entities or commands.
- "I can start IP or phase planning now and fill in DR later" - not for non-trivial work; route to `/draft-design-revision` first.
- "There is a delta, so I can start implementing" - not until the relevant DR/IP/phase artefacts exist and `/execute-phase` is actually the right next step.

Customisation stance:

- Packaged skills should stay uniform across installs.
- Project-specific variation should come from generated guidance and `.spec-driver/hooks/*`, not ad hoc per-project skill forks.
- If local doctrine conflicts with a default routing choice, surface the conflict rather than silently improvising.
