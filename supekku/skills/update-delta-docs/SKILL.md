---
name: update-delta-docs
description: "Updates structured delta execution artefacts (DE, IP, phase sheets, DR) to reflect implementation progress. Use when task statuses, phase state, scope, risks, or verification evidence changed during execution — not for general note-taking (use /notes for that)."
---

Updates the structured artefacts that govern delta execution. Use `/notes` for compact implementation journaling; use this skill when execution changed the governing documents themselves.

## Triggers

Use this skill when any of these became true during execution:

- Phase task statuses or checklist items changed.
- IP phase state or active phase changed.
- DE scope, risks, dependencies, or open questions changed.
- DR target behavior or design rationale changed.
- Verification state or evidence in execution artefacts changed.

## Inputs

- `DE-XXX.md` — the delta definition.
- `IP-XXX.md` — the implementation plan.
- Active phase sheet (`IP-XXX.PHASE-XX`).
- `DR-XXX.md` — when design assumptions changed.
- `notes.md` — the companion execution log.

## Process

1. **Read together**: load the active `DE`, `IP`, and phase sheet to understand current state.
2. **Update phase sheet first**: task statuses, entrance/exit criteria, verification evidence, decisions from the current execution unit.
3. **Update IP next**: phase list/statuses, active phase reference, progress tracking.
4. **Update DE** if scope, dependencies, risks, or open questions changed.
5. **Update DR** if design intent, tradeoffs, or code-impact assumptions changed.
6. **Reconcile notes**: ensure `notes.md` stays consistent with structured artefacts without duplicating every detail.
7. **Escalate if needed**: if the required changes imply a broader design/workflow shift than the active phase assumed, stop and run `/consult`.
