---
id: IP-055.PHASE-02
slug: 055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-02
name: IP-055 Phase 02
created: '2026-03-07'
updated: '2026-03-07'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-02
plan: IP-055
delta: DE-055
objective: >-
  Verify that the new routing skill is integrated correctly and decide the next
  composable follow-up patterns, especially brainstorming and adversarial review.
entrance_criteria:
  - using-spec-driver skill exists in package skills.
  - boot skill references using-spec-driver after startup.
  - skills sync has refreshed installed skills and AGENTS metadata.
exit_criteria:
  - Integration status is verified and recorded.
  - Remaining design choices for optional brainstorming and adversarial review are captured.
  - Next implementation step is explicit.
verification:
  tests: []
  evidence:
    - skills sync output recorded in notes
    - AGENTS.md exposes using-spec-driver
tasks:
  - id: 2.1
    title: Verify generated agent metadata and installed skill exposure
    status: done
  - id: 2.2
    title: Record implementation results back into delta notes and plan state
    status: in_progress
  - id: 2.3
    title: Decide whether to design optional brainstorming and adversarial review as follow-up skills or prompts
    status: todo
risks:
  - description: Routing skill lands, but its boundary remains ambiguous relative to spec-driver and boot
    mitigation: Keep verification focused on responsibility boundaries and recorded examples
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-02
```

# Phase 2 - Verify routing skill integration and decide follow-up patterns

## 1. Objective
Confirm the initial routing-skill implementation is exposed correctly and capture the next decisions around optional brainstorming and adversarial review.

## 2. Links & References
- **Delta**: DE-055
- **Design Revision Sections**:
  - Code Impact Summary
  - Design Decisions & Trade-offs
  - Open Questions
- **Specs / PRODs**:
  - `SPEC-151`
  - `PROD-011`
  - `PROD-002`
  - `PROD-016`
- **Support Docs**:
  - `.spec-driver/AGENTS.md`
  - `supekku/skills/using-spec-driver/SKILL.md`
  - `supekku/skills/boot/SKILL.md`

## 3. Entrance Criteria
- [x] Routing skill added to package skills
- [x] Allowlist updated
- [x] Skills sync completed successfully

## 4. Exit Criteria / Done When
- [x] Generated agent metadata exposes `using-spec-driver`
- [ ] Notes and phase state fully reflect the implementation
- [ ] Follow-up direction for brainstorming and adversarial review is explicit

## 5. Verification
- Tests to run: none yet beyond sync/integration checks
- Tooling/commands:
  - `uv run spec-driver skills sync`
  - `rg -n "using-spec-driver" .spec-driver/AGENTS.md .agents/skills .spec-driver/skills`
- Evidence to capture:
  - sync output
  - AGENTS hit confirming exposure
  - delta notes on next follow-up patterns

## 6. Assumptions & STOP Conditions
- Assumptions:
  - It is acceptable to land the routing skill before optional brainstorming or adversarial-review features are designed.
- STOP when:
  - follow-up patterns would require a larger workflow redesign instead of a composable addition

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Verify generated agent metadata and installed skill exposure | [ ] | `.spec-driver/AGENTS.md` now includes `using-spec-driver` |
| [WIP] | 2.2 | Record implementation results back into delta notes and plan state | [ ] | Updating notes and phase state |
| [ ] | 2.3 | Decide follow-up shape for optional brainstorming and adversarial review | [ ] | Pending |

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Verification remains too shallow and misses behaviour gaps | Add targeted tests if the routing surface grows beyond skills and sync wiring | active |

## 9. Decisions & Outcomes
- `2026-03-07` - Implemented the first routing-skill cut before deciding the optional follow-up patterns. Rationale: the routing gap was immediate and independent of those later additions.

## 10. Findings / Research Notes
- `using-spec-driver` now appears in `.spec-driver/AGENTS.md`.
- Boot now explicitly points to `/using-spec-driver` after startup.
- Brainstorming and adversarial review remain open as optional composable patterns, not blockers for the routing-skill cut.

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [WIP] Spec, delta, and plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
