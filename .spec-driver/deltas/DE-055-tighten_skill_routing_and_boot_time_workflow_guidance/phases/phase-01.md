---
id: IP-055.PHASE-01
slug: "055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-01"
name: IP-055 Phase 01
created: "2026-03-07"
updated: "2026-03-07"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-01
plan: IP-055
delta: DE-055
objective: >-
  Capture the governing doctrine, current skill-routing behaviour, relevant implementation
  touchpoints, and the main design options for stricter boot-time routing.
entrance_criteria:
  - Delta DE-055 exists.
  - Relevant ADRs, memories, and workflow skills have been read.
exit_criteria:
  - DR-055 records current behaviour, target direction, and open questions.
  - DE-055 and IP-055 contain concrete research and planning notes.
  - A recommendation exists for the routing-skill vs expanded-spec-driver boundary.
verification:
  tests: []
  evidence:
    - VA-055-001 research notes in notes.md and DR-055
    - VA-055-002 implementation-surface review in DR-055
tasks:
  - id: 1.1
    title: Gather governing doctrine and memory references
    status: done
  - id: 1.2
    title: Compare current skills with relevant /tmp/superpowers skills
    status: done
  - id: 1.3
    title: Inspect boot, install, and sync touchpoints
    status: done
  - id: 1.4
    title: Record decisions, open questions, and recommended boundary in delta artefacts
    status: done
risks:
  - description: Over-importing non-canonical superpowers workflow assumptions
    mitigation: Anchor all decisions to ADR-004, ADR-005, and posture guidance
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-01
```

# Phase 1 - Research current skill routing and boot chain

## 1. Objective

Capture enough doctrine, implementation context, and comparative research to make the routing design implementable without redoing this exploration.

## 2. Links & References

- **Delta**: DE-055
- **Design Revision Sections**:
  - Problem & Constraints
  - Architecture Intent
  - Code Impact Summary
  - Open Questions
- **Specs / PRODs**:
  - `SPEC-151`
  - `PROD-011`
  - `PROD-002`
  - `PROD-016`
- **Support Docs**:
  - `ADR-004`
  - `ADR-005`
  - `ADR-008`
  - `mem.pattern.spec-driver.core-loop`
  - `mem.concept.spec-driver.posture`
  - `mem.pattern.installer.boot-architecture`
  - `/tmp/superpowers/skills/using-superpowers/SKILL.md`

## 3. Entrance Criteria

- [x] Delta DE-055 created
- [x] Relevant doctrine and memories loaded
- [x] Current and reference skill files identified

## 4. Exit Criteria / Done When

- [x] Research sources captured in notes
- [x] Boot, install, and sync touchpoints identified
- [x] Recommended routing design recorded and agreed enough to begin implementation
- [x] Remaining governance/spec follow-ups identified

## 5. Verification

- Tests to run: none in this research phase
- Tooling/commands:
  - `uv run spec-driver list/show ...`
  - `uv run spec-driver create delta ...`
  - `uv run spec-driver create phase ...`
  - `rg` and `sed` for implementation-surface inspection
- Evidence to capture:
  - research notes in `notes.md`
  - decision framing in `DR-055.md`
  - planning state in `IP-055.md`

## 6. Assumptions & STOP Conditions

- Assumptions:
  - `spec-driver` should stay narrow unless evidence shows the split is failing.
  - Project-specific behaviour should continue to prefer hook stubs over bespoke skill forks.
- STOP when:
  - a design choice would violate ADR-004 or ADR-005 posture
  - routing customisation needs a new hook surface not obviously supported by current governance

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                          | Parallel? | Notes                                                                               |
| ------ | --- | -------------------------------------------------------------------- | --------- | ----------------------------------------------------------------------------------- |
| [x]    | 1.1 | Gather governing ADRs, memories, and current workflow skills         | [ ]       | Completed during session setup                                                      |
| [x]    | 1.2 | Review `/tmp/superpowers` routing and planning skills                | [ ]       | Focused on `using-superpowers`, `brainstorming`, `writing-plans`, `executing-plans` |
| [x]    | 1.3 | Inspect boot, install, and sync implementation surface               | [ ]       | Confirmed generated boot docs, synced skills, and hook ownership split              |
| [x]    | 1.4 | Record design boundary, risks, and open questions in delta artefacts | [ ]       | Completed in DE, DR, IP, and notes                                                  |

### Task Details

- **1.1 Description**
  - **Design / Approach**: Read governing doctrine first, then route research through memories.
  - **Files / Components**: ADR-004, ADR-005, ADR-008, `mem.pattern.spec-driver.core-loop`, `mem.concept.spec-driver.posture`
  - **Testing**: none
  - **Observations & AI Notes**: Canon is delta-first and posture-aware; skills own procedure.
  - **Commits / References**: uncommitted work

- **1.2 Description**
  - **Design / Approach**: Extract transferrable routing discipline from `superpowers` without importing conflicting workflow doctrine.
  - **Files / Components**: `/tmp/superpowers/skills/using-superpowers/SKILL.md` and related reference skills
  - **Testing**: none
  - **Observations & AI Notes**: Strongest import is early governing-skill selection; weakest fit is universal ceremony.
  - **Commits / References**: uncommitted work

- **1.3 Description**
  - **Design / Approach**: Confirm where boot references, managed skills, and user-owned hook seams are implemented.
  - **Files / Components**: `supekku/scripts/lib/skills/sync.py`, `supekku/scripts/install.py`, `supekku/templates/agents/boot.md`, `PROD-016`
  - **Testing**: none
  - **Observations & AI Notes**: install model already separates generated guidance from user-owned hooks.
  - **Commits / References**: uncommitted work

- **1.4 Description**
  - **Design / Approach**: Persist the research outcome into the delta so implementation can resume from artifacts rather than chat history.
  - **Files / Components**: `DE-055.md`, `DR-055.md`, `IP-055.md`, `notes.md`
  - **Testing**: none
  - **Observations & AI Notes**: still need final decision on routing-skill boundary and customisation seam.
  - **Commits / References**: uncommitted work

## 8. Risks & Mitigations

| Risk                                                    | Mitigation                                          | Status |
| ------------------------------------------------------- | --------------------------------------------------- | ------ |
| Research drifts into broad workflow redesign            | Keep scope pinned to routing and boot-time guidance | active |
| Customisation seam becomes inconsistent with `PROD-016` | Treat generated vs user-owned split as a guardrail  | active |

## 9. Decisions & Outcomes

- `2026-03-07` - Current leaning is to keep `spec-driver` narrow and add routing as a separate concern linked from boot. Rationale: preserves the skill's proven CLI-first function and avoids a monolithic workflow meta-skill.
- `2026-03-07` - Optional brainstorming and adversarial review are worth capturing as future composable patterns, but they should not block the initial routing-skill implementation.

## 10. Findings / Research Notes

- `spec-driver` currently does the right thing when the task clearly involves entities or commands; the main missing piece is stronger up-front routing.
- `using-superpowers` is valuable as a posture example, not as doctrine to copy directly.
- `PROD-016` section 5 already captures the generated-guidance plus user-owned hook split and is a likely governance anchor for the customisation principle.
- User feedback confirms two high-value optional patterns to revisit after routing: brainstorming for design-authoring and adversarial review for fresh-agent challenge passes over design docs.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec, delta, and plan updated with lessons
- [x] Hand-off notes to next phase recorded via phase-02 creation
