---
id: IP-055.PHASE-06
slug: "055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-06"
name: IP-055 Phase 06
created: "2026-03-07"
updated: "2026-03-07"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-06
plan: IP-055
delta: DE-055
objective: >-
  Distill DE-055 research and local doctrine into a short startup-facing
  reference for GPT agents creating or refining spec-driver skills.
entrance_criteria:
  - DE-055 research context, ADRs, and skill touchpoints have been read.
  - The new deliverable is treated as a bridge toward future memories, not a
    competing doctrine layer.
exit_criteria:
  - A concise startup-oriented reference exists in the DE-055 bundle.
  - The reference captures what to import, reject, and preserve for
    spec-driver skill work.
  - Notes and phase tracking record the rationale and likely future memory
    split.
verification:
  tests: []
  evidence:
    - gpt-skill-authoring-reference.md created in the DE-055 bundle
    - notes.md records the evergreen-reference rationale
tasks:
  - id: 6.1
    title: Synthesize doctrine and DE-055 findings into a short GPT startup guide
    status: done
  - id: 6.2
    title: Record how Superpowers guidance should be imported or adapted
    status: done
  - id: 6.3
    title: Capture likely future memory split for durable reuse
    status: done
risks:
  - description: The new reference could become another competing handbook
    mitigation: Keep it short, anchor it to ADR-004/ADR-005/PROD-016, and
      treat it as a seed for later memories
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-06
```

# Phase 6 - Draft evergreen GPT skill-authoring reference

## 1. Objective

Compress the DE-055 research and local doctrine into a startup-friendly
reference that future GPT agents can read before changing spec-driver skills.

## 2. Links & References

- **Delta**: DE-055
- **Design Revision Sections**:
  - Problem & Constraints
  - Architecture Intent
  - Design Decisions & Trade-offs
- **Specs / PRODs**:
  - `PROD-016`
- **Support Docs**:
  - `ADR-004`
  - `ADR-005`
  - `mem.pattern.spec-driver.core-loop`
  - `mem.pattern.installer.boot-architecture`
  - `mem.concept.spec-driver.posture`
  - `evidence-based-skill-development.md`

## 3. Entrance Criteria

- [x] DE-055 research inputs and local doctrine loaded
- [x] Current packaged skill boundaries reviewed
- [x] Need confirmed for a shorter, reusable startup-facing synthesis

## 4. Exit Criteria / Done When

- [x] Startup-facing reference created in the delta bundle
- [x] Imported vs rejected Superpowers patterns are explicit
- [x] Follow-up memory extraction path captured

## 5. Verification

- Tests to run: none; this phase is documentation synthesis
- Tooling/commands:
  - `uv run spec-driver list/show ...`
  - `sed`
  - `rg`
- Evidence to capture:
  - bundle document
  - notes entry linking the document to future memory work

## 6. Assumptions & STOP Conditions

- Assumptions:
  - A delta-bundle document is the right immediate output even if the final
    durable form becomes one or more memories.
- STOP when:
  - the synthesis starts duplicating canonical memory/skill/ADR content instead
    of routing to it

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                            | Parallel? | Notes                                          |
| ------ | --- | ---------------------------------------------------------------------- | --------- | ---------------------------------------------- |
| [x]    | 6.1 | Synthesize doctrine and DE-055 findings into a short GPT startup guide | [ ]       | New bundle doc created                         |
| [x]    | 6.2 | Record what to import, reject, and preserve from Superpowers           | [ ]       | Anchored to ADR-004, ADR-005, and PROD-016     |
| [x]    | 6.3 | Capture likely future memory split                                     | [ ]       | Added candidate split section to the new guide |

### Task Details

- **6.1 Description**
  - **Design / Approach**: Start from local doctrine and existing DE-055
    decisions, then compress only the parts that materially shape skill work.
  - **Files / Components**: `DE-055.md`, `DR-055.md`, `IP-055.md`, `notes.md`,
    packaged skill files, new guide
  - **Testing**: none
  - **Observations & AI Notes**: The main value is synthesis and prioritization,
    not adding new doctrine
  - **Commits / References**: uncommitted work

- **6.2 Description**
  - **Design / Approach**: Treat Superpowers as a source of transferrable skill
    design/testing patterns, not workflow doctrine.
  - **Files / Components**: `evidence-based-skill-development.md`, DE-055
    notes, new guide
  - **Testing**: none
  - **Observations & AI Notes**: Trigger-only descriptions and empirical testing
    transfer cleanly; universal ceremony does not
  - **Commits / References**: uncommitted work

- **6.3 Description**
  - **Design / Approach**: End with an explicit future memory split so the doc
    can later shrink instead of expanding into another handbook.
  - **Files / Components**: new guide, `notes.md`
  - **Testing**: none
  - **Observations & AI Notes**: The likely long-term shape is signpost +
    pattern + a few facts
  - **Commits / References**: uncommitted work

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |

## 9. Decisions & Outcomes

- `2026-03-07` - Create a startup-oriented synthesis doc in the DE-055 bundle
  now, then extract durable pieces into memories later. Rationale: the project
  needs immediate agent-facing guidance, but ADR-005 argues against letting
  another prose layer become permanent canon.

## 10. Findings / Research Notes

- The strongest imports from Superpowers are trigger-only descriptions,
  empirical skill testing, and explicit anti-rationalization structure for
  discipline skills.
- The main rejections are universal ceremony, handbook sprawl, and patterns
  that collapse local customization into packaged skills.
- DE-055 already established the most important local heuristics; this phase
  packages them for faster reuse.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to next phase (if any)
