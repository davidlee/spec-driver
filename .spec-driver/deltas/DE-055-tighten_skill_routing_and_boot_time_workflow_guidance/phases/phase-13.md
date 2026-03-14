---
id: IP-055.PHASE-13
slug: 055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-13
name: IP-055 Phase 13
created: '2026-03-08'
updated: '2026-03-08'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-13
plan: IP-055
delta: DE-055
objective: >-
  Make governance consultation explicit inside the DR authoring loop so
  relevant ADRs, policies, and standards shape both drafting and critical review.
entrance_criteria:
  - A DE-055 follow-up has been approved to pull doctrine into DR authoring.
  - The current draft-design-revision loop has progressive drafting and adversarial review but no explicit doctrine step.
exit_criteria:
  - draft-design-revision explicitly runs `/doctrine` before DR drafting.
  - the design triage and adversarial pass both call out ADR/policy/standard constraints.
  - the skill tells the agent to `/consult` if governance is ambiguous or conflicting.
verification:
  tests:
    - uv run spec-driver skills sync
  evidence:
    - Packaged and installed draft-design-revision wording reflects the doctrine step.
    - DE-055 bundle records the governance-aware DR loop.
tasks:
  - id: 13.1
    title: Add explicit doctrine consultation to draft-design-revision
    status: done
  - id: 13.2
    title: Extend the adversarial review checklist to include governance constraints
    status: done
  - id: 13.3
    title: Update DE-055 structured artefacts and notes for the governance-aware loop
    status: done
risks:
  - description: Governance wording could turn into boilerplate reading detached from the actual design surface.
    mitigation: tie `/doctrine` to relevant articles of truth for the current DR and route ambiguity to `/consult`.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-13
```

# Phase 13 - Add doctrine pass to DR authoring

## 1. Objective

Ensure DR drafting and critical review explicitly consult relevant ADRs,
policies, and standards before planning work begins.

## 2. Links & References

- **Delta**: DE-055
- **Design Revision Sections**:
  - Problem & Constraints
  - Architecture Intent
  - Design Decisions & Trade-offs
- **Specs / PRODs**:
  - `PROD-002`
  - `PROD-011`
  - `SPEC-151`
- **Support Docs**:
  - `supekku/skills/draft-design-revision/SKILL.md`
  - `.spec-driver/skills/doctrine/SKILL.md`
  - `.spec-driver/hooks/doctrine.md`

## 3. Entrance Criteria

- [x] Follow-up scope for governance-aware DR authoring has been approved
- [x] Current doctrine and draft-design-revision wording have been reviewed together

## 4. Exit Criteria / Done When

- [x] `/doctrine` is an explicit DR-loop step
- [x] Governance constraints are part of both triage and adversarial review
- [x] The skill routes governance ambiguity to `/consult`
- [x] DE/IP/phase notes record the new loop

## 5. Verification

- Tests to run: `uv run spec-driver skills sync`
- Tooling/commands:
  - `sed -n '1,260p' supekku/skills/draft-design-revision/SKILL.md`
  - `sed -n '1,260p' .spec-driver/skills/draft-design-revision/SKILL.md`
- Evidence to capture:
  - synced installed skill reflects the doctrine step
  - DE-055 artefacts record the governance-aware DR loop

## 6. Assumptions & STOP Conditions

- Assumptions:
  - `/doctrine` is the right existing skill to pull governance into DR authoring
  - the needed value is explicit consultation, not a new separate governance-review skill
- STOP when:
  - doctrine guidance proves too broad to identify relevant authorities for a DR without further skill changes
  - the change implies a larger redesign of governance routing beyond DR authoring

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID   | Description                                                        | Parallel? | Notes                                                                                  |
| ------ | ---- | ------------------------------------------------------------------ | --------- | -------------------------------------------------------------------------------------- |
| [x]    | 13.1 | Add explicit doctrine consultation to draft-design-revision        | [ ]       | run before drafting starts                                                             |
| [x]    | 13.2 | Extend the adversarial checklist to include governance constraints | [ ]       | missing or weakly applied ADR/policy/standard constraints now count as review failures |
| [x]    | 13.3 | Update DE-055 artefacts and notes                                  | [ ]       | bundle now records the governance-aware DR loop                                        |

## 8. Risks & Mitigations

| Risk                                                           | Mitigation                                                                                     | Status |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------ |
| Doctrine becomes a token ritual instead of a design constraint | require relevant authorities to shape triage and adversarial review, not just pre-read context | active |

## 9. Decisions & Outcomes

- `2026-03-08` - Pull `/doctrine` directly into `draft-design-revision` and make governance constraints part of the critical review checklist. Rationale: relevant ADRs, policies, and standards should shape the DR before it hardens into planning input.

## 10. Findings / Research Notes

- The existing `doctrine` skill is intentionally small, which makes it suitable as a reusable pre-draft governance pass.
- Governance consultation is most useful when attached to concrete design questions and review attacks, not when treated as passive background reading.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
