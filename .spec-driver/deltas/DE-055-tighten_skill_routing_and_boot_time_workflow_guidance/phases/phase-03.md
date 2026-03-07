---
id: IP-055.PHASE-03
slug: 055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-03
name: IP-055 Phase 03
created: '2026-03-07'
updated: '2026-03-07'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-03
plan: IP-055
delta: DE-055
objective: >-
  Strengthen execute-phase so implementation work must move the owning delta to
  in-progress before coding begins, reducing lifecycle drift before close-out.
entrance_criteria:
  - The DE-055 bundle records the draft-status completion failure mode.
  - execute-phase is the accepted governing skill for delta/IP implementation.
exit_criteria:
  - The packaged execute-phase skill text makes the draft-to-in-progress transition explicit and hard to skip.
  - The installed execute-phase skill reflects the packaged wording after sync.
  - DE-055 notes record the decision to prefer guidance-layer enforcement here over a completion gate change.
verification:
  tests:
    - uv run spec-driver skills sync
  evidence:
    - Installed execute-phase skill text matches the packaged source.
    - Notes capture the rationale and scope of the guidance-only change.
tasks:
  - id: 3.1
    title: Strengthen execute-phase description and process wording
    status: done
  - id: 3.2
    title: Sync installed skills and verify execute-phase propagation
    status: done
  - id: 3.3
    title: Record lifecycle-guidance decision in DE-055 notes and plan state
    status: done
risks:
  - description: Guidance may still be bypassed if agents ignore execute-phase entirely
    mitigation: Make the skill description stricter now; evaluate routing/boot reinforcements separately
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-03
```

# Phase 3 - Strengthen execute-phase lifecycle guidance

## 1. Objective
Strengthen the implementation-facing skill so agents must align delta lifecycle
state with reality before coding starts.

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
  - `supekku/skills/execute-phase/SKILL.md`
  - `.spec-driver/skills/execute-phase/SKILL.md`
  - `.spec-driver/agents/workflow.md`
  - `supekku/scripts/complete_delta.py`

## 3. Entrance Criteria
- [x] Draft-status completion was identified as an open DE-055 failure mode
- [x] Preflight narrowed the highest-value next move to lifecycle guidance vs completion gating

## 4. Exit Criteria / Done When
- [x] Packaged execute-phase skill is stricter about mandatory invocation and `status: in-progress`
- [x] Installed execute-phase skill has been refreshed and verified
- [x] DE-055 notes and plan state reflect the decision and resulting changes

## 5. Verification
- Tests to run: none beyond sync/propagation for this doc-only skill change
- Tooling/commands:
  - `uv run spec-driver skills sync`
  - `sed -n '1,120p' .spec-driver/skills/execute-phase/SKILL.md`
- Evidence to capture:
  - synced installed skill wording
  - notes entry summarising the rationale

## 6. Assumptions & STOP Conditions
- Assumptions:
  - The immediate fix should strengthen guidance, not change runtime completion semantics.
- STOP when:
  - broader lifecycle enforcement beyond execute-phase is needed, because that would require a separate design decision.

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 3.1 | Strengthen execute-phase description and process wording | [ ] | Mandatory invocation and lifecycle transition now explicit |
| [x] | 3.2 | Sync installed skills and verify execute-phase propagation | [ ] | `uv run spec-driver skills sync` refreshed installed skills and AGENTS output |
| [x] | 3.3 | Record lifecycle-guidance decision in notes and plan state | [ ] | DE-055 artefacts updated in the same change-set |

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Guidance alone may not prevent all lifecycle drift | Keep runtime gating as a separate follow-up question instead of mixing concerns here | active |

## 9. Decisions & Outcomes
- `2026-03-07` - Prefer strengthening execute-phase guidance first. Rationale: the harm occurs during implementation drift, not only at close-out, and execute-phase is already the intended lifecycle handoff point.

## 10. Findings / Research Notes
- `execute-phase` already mentioned moving the delta to `in-progress`, but the instruction was easy to miss.
- `complete_delta.py` still accepts `draft`, which remains a separate runtime-gate question rather than the chosen fix for this phase.

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
