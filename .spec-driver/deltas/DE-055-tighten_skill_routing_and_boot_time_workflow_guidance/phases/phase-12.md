---
id: IP-055.PHASE-12
slug: 055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-12
name: IP-055 Phase 12
created: '2026-03-08'
updated: '2026-03-08'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-12
plan: IP-055
delta: DE-055
objective: >-
  Tighten the DR authoring loop so it borrows the useful progressive-disclosure
  and challenge patterns from brainstorming without importing full universal
  ceremony.
entrance_criteria:
  - A new DE-055 follow-up has been approved to improve the DR writing loop.
  - The current draft-design-revision skill only covers triage and section-by-section drafting.
exit_criteria:
  - draft-design-revision tells the planning agent to keep the loop progressive and code-adjacent where useful.
  - draft-design-revision requires an internal adversarial review before the DR is treated as coherent.
  - The skill offers an external adversarial-review prompt only after local feedback is integrated.
  - The skill requires DE reconciliation before offering `/plan-phases` or new phase-sheet work.
verification:
  tests:
    - uv run spec-driver skills sync
  evidence:
    - Packaged and installed draft-design-revision wording reflects the stronger DR loop.
    - DE-055 bundle records the new review-loop decisions and phase tracking.
tasks:
  - id: 12.1
    title: Extend draft-design-revision with progressive disclosure and code-adjacent specificity
    status: done
  - id: 12.2
    title: Add adversarial self-review and optional external-review prompt handoff
    status: done
  - id: 12.3
    title: Require DE reconciliation before planning handoff
    status: done
  - id: 12.4
    title: Update DE-055 structured artefacts and notes for the new DR loop
    status: done
risks:
  - description: The DR loop could become too heavyweight if the new review pass is phrased like a universal mandatory ceremony.
    mitigation: Keep the wording targeted to DR authoring and preserve the external adversarial pass as optional after local integration.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-12
```

# Phase 12 - Tighten DR review loop and delta reconciliation

## 1. Objective
Strengthen the DR-writing loop with a sharper progressive-disclosure pattern,
code-adjacent specificity, and explicit review/reconciliation steps before
planning work begins.

## 2. Links & References
- **Delta**: DE-055
- **Design Revision Sections**:
  - Architecture Intent
  - Code Impact Summary
  - Design Decisions & Trade-offs
  - Open Questions
- **Specs / PRODs**:
  - `PROD-002`
  - `PROD-011`
  - `SPEC-151`
- **Support Docs**:
  - `supekku/skills/draft-design-revision/SKILL.md`
  - `/tmp/superpowers/skills/brainstorming/SKILL.md`
  - `DR-055.md`

## 3. Entrance Criteria
- [x] Follow-up scope for the DR loop has been approved under DE-055
- [x] Existing draft-design-revision wording has been reviewed against the requested loop changes

## 4. Exit Criteria / Done When
- [x] Progressive-disclosure and code-adjacent specificity guidance added
- [x] Internal adversarial review and optional external-review prompt added
- [x] DE reconciliation required before planning handoff
- [x] DE/IP/phase docs and notes updated to match

## 5. Verification
- Tests to run: `uv run spec-driver skills sync`
- Tooling/commands:
  - `sed -n '1,260p' supekku/skills/draft-design-revision/SKILL.md`
  - `sed -n '1,260p' .spec-driver/skills/draft-design-revision/SKILL.md`
- Evidence to capture:
  - synced installed skill reflects the updated DR loop
  - DE-055 artefacts record the new accepted design direction

## 6. Assumptions & STOP Conditions
- Assumptions:
  - the strongest immediate value is skill guidance, not new runtime enforcement
  - optional external review should remain optional and not block local DR coherence
- STOP when:
  - the skill starts absorbing generic review or audit semantics beyond DR authoring
  - the requested loop changes imply a broader redesign of planning workflow outside DE-055

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 12.1 | Extend draft-design-revision with progressive disclosure and code-adjacent specificity | [ ] | Keep the loop section-scoped rather than whole-file-by-default |
| [x] | 12.2 | Add adversarial self-review and optional external-review prompt handoff | [ ] | Internal pass is required; external prompt is optional after integration |
| [x] | 12.3 | Require DE reconciliation before planning handoff | [ ] | Prevent DE/DR drift before IP and phase planning |
| [x] | 12.4 | Update DE-055 structured artefacts and notes | [ ] | Phase, IP, DR, and DE now capture the new loop |

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| DR review loop turns into mandatory heavyweight ceremony | keep the self-review specific to DR quality and leave the external reviewer as an optional prompt | active |

## 9. Decisions & Outcomes
- `2026-03-08` - Extend `draft-design-revision` with progressive disclosure, code-adjacent examples, an internal adversarial review pass, optional external-review prompt handoff, and DE reconciliation before planning. Rationale: these are the highest-value brainstorming imports for DR quality without imposing universal ceremony.

## 10. Findings / Research Notes
- The existing DR loop already had triage and section-by-section drafting, but it still let the design feel "done" before any explicit challenge pass.
- A short code sketch often resolves ambiguity faster than another paragraph of abstract design prose.
- DE reconciliation belongs in the DR loop because planning off a stale delta recreates drift immediately.

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
