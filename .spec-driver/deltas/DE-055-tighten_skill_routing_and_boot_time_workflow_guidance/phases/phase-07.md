---
id: IP-055.PHASE-07
slug: "055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-07"
name: IP-055 Phase 07
created: "2026-03-07"
updated: "2026-03-07"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-07
plan: IP-055
delta: DE-055
objective: >-
  Harden preflight and handoff skill guidance so implementation readiness
  requires a critical assessment of assumptions, unresolved questions, and
  tensions rather than a shallow entrance-criteria summary.
entrance_criteria:
  - A concrete multi-phase handover failure mode has been captured from live use.
  - preflight is already the bounded research skill used ahead of implementation.
  - continuation and next already own fresh-agent handoff prompts.
exit_criteria:
  - preflight requires an explicit critical-assessment section before readiness claims.
  - continuation and next preserve unresolved assumptions, questions, and tensions in handoffs.
  - execute-phase makes unresolved ambiguity from preflight a consult trigger before improvisation.
  - DE-055 artefacts record the motivating case and resulting workflow change.
verification:
  tests:
    - uv run spec-driver skills sync
  evidence:
    - Packaged skill text for preflight, continuation, next, and execute-phase reflects the stronger contract.
    - Notes capture the DE-053 case study and the resulting design decision.
tasks:
  - id: 7.1
    title: Tighten preflight readiness criteria around critical assessment
    status: done
  - id: 7.2
    title: Make handoff skills preserve unresolved assumptions and tensions
    status: done
  - id: 7.3
    title: Record the case study and workflow change in DE-055 artefacts
    status: done
risks:
  - description: Preflight could become too heavy and drift back into a broad planning ritual
    mitigation: Keep the requirement focused on surfacing assumptions and tensions without turning every preflight into open-ended design work
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-07
```

# Phase 7 - Harden preflight and handoff critical assessment

## 1. Objective

Require implementation-bound preflight and handoff prompts to surface the
remaining unknowns before anyone claims the work is ready to execute.

## 2. Links & References

- **Delta**: DE-055
- **Design Revision Sections**:
  - Problem & Constraints
  - Design Decisions & Trade-offs
  - Open Questions
- **Specs / PRODs**:
  - `PROD-002`
  - `PROD-011`
  - `SPEC-151`
- **Support Docs**:
  - `supekku/skills/preflight/SKILL.md`
  - `supekku/skills/continuation/SKILL.md`
  - `supekku/skills/next/SKILL.md`
  - `supekku/skills/execute-phase/SKILL.md`

## 3. Entrance Criteria

- [x] A concrete handover/preflight failure mode was captured from live use
- [x] The work remains within DE-055's guidance-layer scope

## 4. Exit Criteria / Done When

- [x] preflight requires a critical assessment before readiness claims
- [x] continuation and next preserve unresolved assumptions and tensions
- [x] execute-phase routes unresolved ambiguity from preflight into consult
- [x] DE-055 notes and plan state capture the new guidance

## 5. Verification

- Tests to run: none beyond skill sync/propagation for this wording change
- Tooling/commands:
  - `uv run spec-driver skills sync`
  - `sed -n '1,220p' .spec-driver/skills/preflight/SKILL.md`
  - `sed -n '1,220p' .spec-driver/skills/continuation/SKILL.md`
  - `sed -n '1,120p' .spec-driver/skills/next/SKILL.md`
  - `sed -n '1,220p' .spec-driver/skills/execute-phase/SKILL.md`
- Evidence to capture:
  - updated packaged and installed skill wording
  - notes entry describing the DE-053 case study and resulting contract change

## 6. Assumptions & STOP Conditions

- Assumptions:
  - the right fix is stronger guidance, not a new runtime gate
- STOP when:
  - the change would turn preflight into a full design-planning ceremony instead of bounded critical assessment

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                      | Parallel? | Notes                                                                 |
| ------ | --- | ---------------------------------------------------------------- | --------- | --------------------------------------------------------------------- |
| [x]    | 7.1 | Tighten preflight readiness criteria around critical assessment  | [ ]       | readiness now depends on naming assumptions, questions, and tensions  |
| [x]    | 7.2 | Make handoff skills preserve unresolved assumptions and tensions | [ ]       | continuation and next no longer imply a flat ready-to-proceed handoff |
| [x]    | 7.3 | Record the case study and workflow change in DE-055 artefacts    | [ ]       | notes and plan state updated in the same change-set                   |

## 8. Risks & Mitigations

| Risk                                                  | Mitigation                                                                          | Status |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------- | ------ |
| preflight becomes too ceremonial for bounded research | keep the critical-assessment output short and tied to implementation readiness only | active |

## 9. Decisions & Outcomes

- `2026-03-07` - Treat implementation readiness as a critical-assessment outcome, not as a synonym for "I can start coding". Rationale: the DE-053 handover showed that entrance criteria and scope summary alone can hide unresolved design choices.

## 10. Findings / Research Notes

- A good handover can still be misleading if it preserves artefact references but drops the unresolved questions hidden in those artefacts.
- The right place to catch that failure mode is preflight, with continuation and next preserving the context into fresh-agent handoffs.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
