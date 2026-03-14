---
id: IP-055.PHASE-09
slug: 055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-09
name: IP-055 Phase 09
created: '2026-03-07'
updated: '2026-03-07'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-09
plan: IP-055
delta: DE-055
objective: >-
  Apply the first artifact-specific brainstorming import to DR authoring by
  strengthening draft-design-revision around explicit design triage and
  section-by-section validation.
entrance_criteria:
  - The brainstorming decomposition has identified DRs as the strongest first target.
  - draft-design-revision currently lacks explicit triage and iterative section validation.
exit_criteria:
  - draft-design-revision requires pre-draft triage of questions, risks, assumptions, and critical decisions.
  - draft-design-revision supports one-question-at-a-time closure and section-by-section DR validation.
  - DE-055 artefacts record the DR-first import and the remaining follow-up question for shape-revision or broader rollout.
verification:
  tests:
    - uv run spec-driver skills sync
  evidence:
    - Packaged and installed draft-design-revision wording reflect the stronger DR authoring contract.
    - Notes capture the rationale for choosing DRs as the first artifact-specific target.
tasks:
  - id: 9.1
    title: Strengthen draft-design-revision around explicit design triage
    status: done
  - id: 9.2
    title: Add section-by-section validation guidance for DR drafting
    status: done
  - id: 9.3
    title: Record the DR-first import in DE-055 artefacts
    status: done
risks:
  - description: The DR skill could become too heavy and drift toward a universal authoring framework
    mitigation: Keep the new structure narrowly tied to DR authoring and defer broader generalisation until shape-revision or another skill proves it out
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-09
```

# Phase 9 - Apply section-by-section authoring to draft-design-revision

## 1. Objective

Land the first artifact-specific authoring improvement from the brainstorming
decomposition in the DR workflow.

## 2. Links & References

- **Delta**: DE-055
- **Design Revision Sections**:
  - Design Decisions & Trade-offs
  - Open Questions
  - Code Impact Summary
- **Specs / PRODs**:
  - `PROD-002`
  - `PROD-011`
  - `SPEC-151`
- **Support Docs**:
  - `supekku/skills/draft-design-revision/SKILL.md`
  - `/tmp/superpowers/skills/brainstorming/SKILL.md`
  - `phases/phase-08.md`

## 3. Entrance Criteria

- [x] DRs have been identified as the strongest first target for section-by-section authoring guidance
- [x] draft-design-revision still needed explicit triage and validation structure

## 4. Exit Criteria / Done When

- [x] draft-design-revision requires explicit design-question triage before drafting
- [x] draft-design-revision supports one-question-at-a-time closure and section-by-section validation
- [x] DE-055 notes and plan state capture the DR-first import and remaining rollout question

## 5. Verification

- Tests to run: none beyond sync/propagation for this skill-text change
- Tooling/commands:
  - `uv run spec-driver skills sync`
  - `sed -n '1,220p' .spec-driver/skills/draft-design-revision/SKILL.md`
- Evidence to capture:
  - synced installed draft-design-revision wording
  - notes entry summarising the DR-first import

## 6. Assumptions & STOP Conditions

- Assumptions:
  - DR authoring benefits enough from the pattern to justify landing it before broader generalisation
- STOP when:
  - the skill starts absorbing implementation planning or turns into a generic framework instead of a DR runsheet

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                    | Parallel? | Notes                                                                                |
| ------ | --- | -------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------ |
| [x]    | 9.1 | Strengthen draft-design-revision around explicit design triage | [ ]       | questions, risks, assumptions, and critical decisions are now a named pre-draft step |
| [x]    | 9.2 | Add section-by-section validation guidance for DR drafting     | [ ]       | the skill now prefers iterative section closure over a full speculative draft        |
| [x]    | 9.3 | Record the DR-first import in DE-055 artefacts                 | [ ]       | notes, plan, and DR all updated in the same change-set                               |

## 8. Risks & Mitigations

| Risk                                | Mitigation                                                                                                            | Status |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------ |
| DR authoring becomes too ceremonial | keep the pattern focused on foundational sections and concrete design detail, not mandatory ritual for every sentence | active |

## 9. Decisions & Outcomes

- `2026-03-07` - Apply the first artifact-specific brainstorming import to `draft-design-revision`. Rationale: DRs benefit most from early correction of foundational assumptions and from concrete design detail before planning work begins.

## 10. Findings / Research Notes

- The one-question-at-a-time closure pattern is useful inside DR authoring when there are still unresolved design branches.
- Section-by-section validation is most valuable where early sections strongly constrain later ones.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
