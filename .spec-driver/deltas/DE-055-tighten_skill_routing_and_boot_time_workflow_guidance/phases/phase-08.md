---
id: IP-055.PHASE-08
slug: 055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-08
name: IP-055 Phase 08
created: '2026-03-07'
updated: '2026-03-07'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-08
plan: IP-055
delta: DE-055
objective: >-
  Decompose the useful imports from Superpowers brainstorming into a generic
  question-resolution loop plus artifact-specific authoring guidance, and
  identify the shared high-leverage design-triage step.
entrance_criteria:
  - Superpowers brainstorming has already been reviewed as an optional future pattern.
  - DE-055 already distinguishes optional patterns from mandatory workflow doctrine.
exit_criteria:
  - DE-055 artefacts record the split between a generic loop and artifact-specific authoring guidance.
  - Likely first target skills for section-by-section authoring are identified.
  - The shared explicit design-triage pattern is captured as a high-leverage import candidate.
verification:
  tests: []
  evidence:
    - Notes capture the decomposition and rationale.
    - DR/DE/IP reflect the resulting design direction.
tasks:
  - id: 8.1
    title: Re-read brainstorming with decomposition in mind
    status: done
  - id: 8.2
    title: Record generic-loop versus artifact-guidance split in DE-055 artefacts
    status: done
  - id: 8.3
    title: Identify the shared design-triage pattern worth preserving
    status: done
risks:
  - description: The decomposition could be too abstract and lose the practical strengths of the original workflow
    mitigation: Preserve the concrete section-by-section authoring pattern in specific skills rather than forcing premature generalisation
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-08
```

# Phase 8 - Decompose brainstorming imports

## 1. Objective
Decide what should be imported from Superpowers brainstorming, and in what
shape, without bringing in its universal-ceremony posture.

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
  - `/tmp/superpowers/skills/brainstorming/SKILL.md`
  - `supekku/skills/draft-design-revision/SKILL.md`
  - `supekku/skills/shape-revision/SKILL.md`
  - `supekku/skills/scope-delta/SKILL.md`

## 3. Entrance Criteria
- [x] Brainstorming remains an optional future pattern, not a default workflow gate
- [x] Current DE-055 direction already favors narrow, composable skills

## 4. Exit Criteria / Done When
- [x] Generic decision-loop value is separated from artifact-specific authoring choreography
- [x] Likely first skills for section-by-section authoring imports are identified
- [x] The shared design-triage step is captured as a reusable pattern candidate

## 5. Verification
- Tests to run: none; this phase is design decomposition only
- Evidence to capture:
  - notes entry describing the split
  - DR/DE/IP updates reflecting the resulting design direction

## 6. Assumptions & STOP Conditions
- Assumptions:
  - the strongest imports can be preserved without importing the whole skill
- STOP when:
  - the decomposition starts inventing a generic framework before the first artifact-specific use proves out

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 8.1 | Re-read brainstorming with decomposition in mind | [ ] | distinguished generic loop from authoring choreography |
| [x] | 8.2 | Record generic-loop versus artifact-guidance split in DE-055 artefacts | [ ] | DR/DE/IP/notes updated together |
| [x] | 8.3 | Identify the shared design-triage pattern worth preserving | [ ] | explicit step-by-step triage of questions, risks, assumptions, and critical decisions captured |

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| useful section-by-section behavior gets lost in over-generalisation | embed it in DR/revision skills first instead of inventing a universal skill | active |

## 9. Decisions & Outcomes
- `2026-03-07` - Split optional brainstorming imports into a generic decision loop and artifact-specific authoring guidance. Rationale: the one-question-at-a-time closure pattern is broadly reusable, but section-by-section design presentation depends heavily on artifact type and is strongest first in DR/revision workflows.

## 10. Findings / Research Notes
- The strongest shared upstream step is explicit triage of open questions, risks, underspecified areas, assumptions, and critical design decisions before drafting.
- The section-by-section authoring pattern improves human steering and prevents foundational misunderstandings from being baked into a full design draft.

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
