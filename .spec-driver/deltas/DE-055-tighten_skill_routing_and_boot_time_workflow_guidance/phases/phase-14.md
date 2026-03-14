---
id: IP-055.PHASE-14
slug: "055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-14"
name: IP-055 Phase 14
created: "2026-03-09"
updated: "2026-03-09"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-14
plan: IP-055
delta: DE-055
objective: >-
  Make delta close-out explicitly revisit any originating backlog entries so
  closure leaves backlog state and traceability in sync with the completed work.
entrance_criteria:
  - A DE-055 follow-up has been approved to improve backlog follow-through during delta closure.
  - Current close-change guidance has been reviewed alongside delta-completion memory and backlog-status ambiguity.
exit_criteria:
  - close-change explicitly checks for originating backlog entries during closure.
  - close-change nudges status/note/link updates for those backlog entries.
  - the guidance tells the agent to `/consult` instead of inventing non-canonical backlog statuses.
verification:
  tests:
    - uv run spec-driver skills sync
  evidence:
    - Packaged and installed close-change wording reflects backlog follow-through.
    - Delta-completion memory includes the backlog step.
tasks:
  - id: 14.1
    title: Add backlog follow-through to close-change
    status: done
  - id: 14.2
    title: Update delta-completion memory with backlog step and ambiguity guardrail
    status: done
  - id: 14.3
    title: Update DE-055 structured artefacts and notes
    status: done
risks:
  - description: Close-out guidance could imply a canonical backlog status model that the repo has not actually defined yet.
    mitigation: phrase the step as a nudge plus `/consult` escalation when the correct backlog transition is unclear.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-14
```

# Phase 14 - Nudge backlog updates during delta closure

## 1. Objective

Ensure delta closure explicitly checks whether any originating backlog entries
need follow-through updates before the work is treated as fully closed.

## 2. Links & References

- **Delta**: DE-055
- **Design Revision Sections**:
  - Design Decisions & Trade-offs
  - Open Questions
- **Specs / PRODs**:
  - `PROD-002`
  - `PROD-011`
  - `SPEC-151`
- **Support Docs**:
  - `supekku/skills/close-change/SKILL.md`
  - `.spec-driver/memory/mem.pattern.spec-driver.delta-completion.md`
  - `.spec-driver/backlog/issues/ISSUE-009-status-fields-lack-enums-and-need-systematic-review/ISSUE-009.md`

## 3. Entrance Criteria

- [x] Follow-up scope for close-out backlog nudging has been approved
- [x] Existing close-change guidance and backlog-status ambiguity have been reviewed together

## 4. Exit Criteria / Done When

- [x] close-change checks for originating backlog entries
- [x] close-change nudges backlog status/note/link updates
- [x] close-change routes backlog-status ambiguity to `/consult`
- [x] DE/IP/phase notes record the change

## 5. Verification

- Tests to run: `uv run spec-driver skills sync`
- Tooling/commands:
  - `sed -n '1,260p' supekku/skills/close-change/SKILL.md`
  - `sed -n '1,260p' .spec-driver/skills/close-change/SKILL.md`
  - `uv run spec-driver show memory mem.pattern.spec-driver.delta-completion --raw`
- Evidence to capture:
  - synced installed close-change reflects backlog follow-through
  - delta-completion memory includes backlog step and ambiguity guardrail

## 6. Assumptions & STOP Conditions

- Assumptions:
  - close-change is the right place for this nudge because it owns formal delta closure
  - the repo still lacks a stable enough backlog-status vocabulary for stronger automation
- STOP when:
  - the needed behavior would require inventing or hard-coding backlog lifecycle semantics
  - the correct originating-backlog linkage cannot be discovered from current delta artifacts

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID   | Description                                | Parallel? | Notes                                    |
| ------ | ---- | ------------------------------------------ | --------- | ---------------------------------------- |
| [x]    | 14.1 | Add backlog follow-through to close-change | [ ]       | pre-check plus post-check nudge          |
| [x]    | 14.2 | Update delta-completion memory             | [ ]       | add backlog step and ambiguity guardrail |
| [x]    | 14.3 | Update DE-055 artefacts and notes          | [ ]       | keep the delta bundle aligned            |

## 8. Risks & Mitigations

| Risk                                                            | Mitigation                                                        | Status |
| --------------------------------------------------------------- | ----------------------------------------------------------------- | ------ |
| Close-out wording implies unsupported backlog status automation | keep the wording at nudge level and route ambiguity to `/consult` | active |

## 9. Decisions & Outcomes

- `2026-03-09` - Add backlog follow-through to `close-change` and delta-completion guidance, but keep it advisory where backlog status semantics are still unsettled. Rationale: originating backlog items should not silently drift stale after delta closure.

## 10. Findings / Research Notes

- `close-change` is the narrowest workflow surface that already owns formal delta closure.
- `ISSUE-009` remains the blocker on any stronger, status-specific backlog automation.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
