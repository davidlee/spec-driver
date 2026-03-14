---
id: IP-055.PHASE-04
slug: "055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-04"
name: IP-055 Phase 04
created: "2026-03-07"
updated: "2026-03-07"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-04
plan: IP-055
delta: DE-055
objective: >-
  Strengthen routing guidance so agents do not skip DR/IP/phase creation when a
  delta exists but the work is not yet execution-ready.
entrance_criteria:
  - Preflight confirmed the ordering gap lives primarily in using-spec-driver routing.
  - Existing workflow skills already encode the intended sequence in separate pieces.
exit_criteria:
  - using-spec-driver explicitly routes non-execution-ready delta work through shaping/planning rather than execute-phase.
  - Installed skills reflect the stronger routing wording after sync.
  - DE-055 notes and plan state capture the ordering decision and change scope.
verification:
  tests:
    - uv run spec-driver skills sync
  evidence:
    - Installed using-spec-driver skill text matches the packaged source.
    - Notes record the rationale for putting the ordering rule in routing.
tasks:
  - id: 4.1
    title: Strengthen using-spec-driver ordering guardrails
    status: done
  - id: 4.2
    title: Sync installed skills and verify propagation
    status: done
  - id: 4.3
    title: Record ordering decision in DE-055 artefacts
    status: done
risks:
  - description: Routing guidance may become repetitive or over-prescriptive
    mitigation: Keep the explicit ordering rule in using-spec-driver and avoid duplicating full workflow prose in multiple skills
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-04
```

# Phase 4 - Strengthen routing for DR-IP-phase ordering

## 1. Objective

Make the routing layer explicitly block premature implementation when DR/IP/phase
artefacts are still missing.

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
  - `supekku/skills/using-spec-driver/SKILL.md`
  - `supekku/skills/scope-delta/SKILL.md`
  - `supekku/skills/plan-phases/SKILL.md`
  - `supekku/skills/execute-phase/SKILL.md`
  - `.spec-driver/agents/workflow.md`

## 3. Entrance Criteria

- [x] Ordering gap identified as an active DE-055 failure mode
- [x] Preflight narrowed the fix to routing guidance rather than new runtime enforcement

## 4. Exit Criteria / Done When

- [x] using-spec-driver distinguishes planning work from execution-ready phase work
- [x] Installed using-spec-driver skill has been refreshed and verified
- [x] DE-055 notes and plan state reflect the new ordering guardrail

## 5. Verification

- Tests to run: none beyond sync/propagation for this skill-text change
- Tooling/commands:
  - `uv run spec-driver skills sync`
  - `sed -n '1,140p' .spec-driver/skills/using-spec-driver/SKILL.md`
- Evidence to capture:
  - synced installed skill wording
  - notes entry summarising the routing decision

## 6. Assumptions & STOP Conditions

- Assumptions:
  - The right fix is to strengthen routing rather than make execute-phase or boot carry the full ordering contract.
- STOP when:
  - stronger ordering would require new runtime gates or a broader workflow redesign.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                      | Parallel? | Notes                                                                         |
| ------ | --- | ------------------------------------------------ | --------- | ----------------------------------------------------------------------------- |
| [x]    | 4.1 | Strengthen using-spec-driver ordering guardrails | [ ]       | Missing DR/IP/phase work now routes before execute-phase                      |
| [x]    | 4.2 | Sync installed skills and verify propagation     | [ ]       | `uv run spec-driver skills sync` refreshed installed skills and AGENTS output |
| [x]    | 4.3 | Record ordering decision in DE-055 artefacts     | [ ]       | DE-055 artefacts updated in the same change-set                               |

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |

## 9. Decisions & Outcomes

- `2026-03-07` - Put the DR/IP/phase ordering guardrail in using-spec-driver. Rationale: routing is where agents choose the next governing skill, so that is the right point to stop premature execution.

## 10. Findings / Research Notes

- scope-delta, plan-phases, and execute-phase already encode the intended sequence.
- The main gap was that using-spec-driver treated "active delta phase or plan" as sufficient without explicitly routing missing planning work first.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
