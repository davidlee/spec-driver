---
name: update-delta-docs
description: Reconcile DE/IP/phase/DR execution artefacts during delta work. Use this when implementation changes structured execution state, not just notes.
---

This skill is for structured delta execution documentation.

Do not use it as a replacement for `/notes`.

Use `/notes` for compact implementation journaling on the current card.
Use `/update-delta-docs` when execution changed the structured artefacts that
govern or describe the work.

Inputs:

- `DE-XXX.md`
- `IP-XXX.md`
- Active phase sheet (`IP-XXX.PHASE-XX`)
- `DR-XXX.md` when design, risks, or execution assumptions changed
- `notes.md` for the companion execution log

Use this skill when any of the following became true:

- phase task/checklist/status state changed
- IP phase state or active phase changed
- DE scope, risks, dependencies, or open questions changed during execution
- DR target behavior or design rationale changed during execution
- verification state/evidence in execution artefacts changed

Process:

1. Read the active `DE`, `IP`, and phase sheet together.
2. Update the phase sheet first:
   - task statuses
   - entrance/exit criteria
   - verification evidence
   - decisions/findings from the current execution unit
3. Update `IP-XXX.md` next:
   - phase list/statuses
   - active phase reference
   - progress tracking where needed
4. Update `DE-XXX.md` if execution changed scope, dependencies, risks, or tracked open questions.
5. Update `DR-XXX.md` if execution changed design intent, tradeoffs, or code-impact assumptions.
6. Ensure `notes.md` remains consistent with the structured artefacts, but do not duplicate every detail.
7. If the required doc changes imply a broader design/workflow change than the active phase assumed, stop and `/consult`.

Outcomes:

- Delta execution artefacts stay coherent while work is in progress.
- Phase/IP/DE/DR state does not drift away from notes or implementation reality.
- `/notes` remains a lightweight execution log rather than a hidden structured-doc workflow.
