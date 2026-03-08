---
id: IP-055.PHASE-15
slug: 055-tighten_skill_routing_and_boot_time_workflow_guidance-phase-15
name: Require DR before IP handoff
created: '2026-03-09'
updated: '2026-03-09'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-055.PHASE-15
plan: IP-055
delta: DE-055
objective: >-
  Tighten routing and planning guidance so non-trivial deltas do not skip DR
  work and jump straight into IP or phase planning.
entrance_criteria:
  - Current DR/IP/routing skills reviewed for the DR-skip failure mode.
  - DE-055 follow-up approved.
exit_criteria:
  - using-spec-driver routes missing or stale non-trivial design into /draft-design-revision before /plan-phases.
  - plan-phases treats a missing or stale non-trivial DR as a stop condition, not a planning shortcut.
  - scope-delta no longer implies that creating an IP/phase can substitute for missing DR work.
  - DE-055 notes and design docs record the stronger DR-before-IP expectation.
verification:
  tests:
    - Manual review of packaged skill wording for using-spec-driver, scope-delta, and plan-phases.
  evidence: []
tasks:
  - id: 15.1
    title: Tighten routing and planning skill wording for DR-first handoff
    status: done
  - id: 15.2
    title: Reconcile DE-055 docs and notes with the stronger DR-before-IP rule
    status: done
risks:
  - description: Over-tightening may force DR ceremony onto trivial work that should stay lightweight.
    mitigation: Keep the rule scoped to non-trivial or stale-design work.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-055.PHASE-15
```

# Phase 15 - Require DR before IP handoff

## 1. Objective
Tighten routing and planning guidance so non-trivial work cannot treat IP or phase creation as a substitute for current design.

## 2. Links & References
- **Delta**: DE-055
- **Design Revision Sections**:
  - `DR-055` section 3, architecture intent
  - `DR-055` section 7, ordering and DR-loop decisions
- **Specs / PRODs**:
  - `PROD-002`
  - `PROD-011`
  - `SPEC-151`
- **Support Docs**:
  - `supekku/skills/using-spec-driver/SKILL.md`
  - `supekku/skills/scope-delta/SKILL.md`
  - `supekku/skills/plan-phases/SKILL.md`
  - `supekku/skills/draft-design-revision/SKILL.md`

## 3. Entrance Criteria
- [x] Current routing and planning wording reviewed for the DR-skip gap
- [x] DE-055 follow-up approved

## 4. Exit Criteria / Done When
- [x] Routing skill stops non-trivial work from jumping straight to IP/phase planning when DR is missing or stale
- [x] Planning skill treats missing/stale non-trivial DR as a stop condition
- [x] DE-055 docs/notes record the stronger DR-before-IP expectation

## 5. Verification
- Manual review of updated packaged skill wording
- Diff review for DE-055 docs and phase notes
- Capture verification in `notes.md`

## 6. Assumptions & STOP Conditions
- Assumptions:
  - Trivial work may still skip standalone DR if design is genuinely settled and lightweight.
  - The problem is specifically non-trivial work treating IP as a substitute for design.
- STOP when:
  - the wording would force DR ceremony onto obviously trivial maintenance work
  - a stronger runtime gate appears necessary instead of guidance-layer reinforcement

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 15.1 | Tighten `using-spec-driver`, `scope-delta`, and `plan-phases` around DR-before-IP routing | [ ] | Kept the rule scoped to missing/stale non-trivial design |
| [x] | 15.2 | Reconcile DE-055 notes and design docs with the stronger rule | [ ] | DE/DR/IP/notes now state that IP is not a substitute for DR |

### Task Details
- **15.1 Description**
  - **Design / Approach**: Make all three handoff skills agree that non-trivial or stale design routes into `/draft-design-revision` before planning.
  - **Files / Components**:
    - `supekku/skills/using-spec-driver/SKILL.md`
    - `supekku/skills/scope-delta/SKILL.md`
    - `supekku/skills/plan-phases/SKILL.md`
  - **Testing**: Manual wording review only.
  - **Observations & AI Notes**: Current gap is that `using-spec-driver` and `plan-phases` under-specify the DR requirement even though `draft-design-revision` itself is stronger.
  - **Commits / References**: None yet.
- **15.2 Description**
  - **Design / Approach**: Reconcile DE/IP/phase/notes so the new guidance is traceable.
  - **Files / Components**:
    - `DE-055.md`
    - `DR-055.md`
    - `IP-055.md`
    - `notes.md`
  - **Testing**: Diff review only.
  - **Observations & AI Notes**: Capture the specific anti-pattern: IP is not a substitute for current DR on non-trivial work.
  - **Commits / References**: None yet.

*(Repeat detail blocks per task as needed)*

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |

## 9. Decisions & Outcomes
- `2026-03-09` - Treat missing or stale non-trivial design as a routing/planning stop condition rather than letting agents jump from delta to IP. Rationale: the current failure mode is not lack of phase sheets, it is planning running ahead of design.
- `2026-03-09` - Verified that generated `.spec-driver/skills/*` copies were refreshed after the current install flow was rerun. Rationale: packaged skill edits do not help fresh-agent behavior until the generated surfaces match.

## 10. Findings / Research Notes
- `using-spec-driver` currently blocks `/execute-phase` without necessarily forcing `/draft-design-revision`.
- `plan-phases` treats `DR-XXX.md` as an input but does not currently stop when non-trivial design is missing or stale.
- `scope-delta` says to run `/draft-design-revision` for non-trivial work, but it still reads as advisory because `/plan-phases` can be reached too easily.

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Spec/Delta/Plan updated with lessons
- [x] Hand-off notes to next phase (if any)
