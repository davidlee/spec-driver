```yaml supekku:plan.overview@v1
schema: supekku.plan.overview
version: 1
plan: {{ plan_id }}
delta: {{ delta_id }}
revision_links:
  aligns_with: []
specs:
  primary: []
  collaborators: []
requirements:
  targets: []
phases:
  - id: {{ plan_id }}.PHASE-01
    name: Phase 01 - <Working Title>
    objective: >-
      Short description of the phase outcome.
    entrance_criteria: []
    exit_criteria: []
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: {{ plan_id }}
entries:
  - artefact: VT-XXX
    kind: VT|VA|VH
    requirement: SPEC-YYY.FR-001
    phase: {{ plan_id }}.PHASE-01
    status: planned|in-progress|verified
    notes: >-
      Link to evidence (test run, audit, validation artefact).
```

## 1. Summary
- **Delta**: {{ delta_id }} - <title>
- **Specs Impacted**: SPEC-002, PROD-YYY
- **Problems / Issues**: ISSUE-123, PROB-456
- **Desired Outcome**: <one-line description of the end state>

## 2. Context & Constraints
- **Current Behaviour**: <brief note or link to audit finding>
- **Target Behaviour**: <reference spec section / requirement IDs>
- **Dependencies**: <other deltas, releases, ops windows>
- **Constraints**: <time, rollout, tech debt>

## 3. Gate Check
- [ ] Backlog items linked and prioritised
- [ ] Spec(s) updated or delta specifies required changes
- [ ] Test strategy identified (unit/integration/system)
- [ ] Workspace/config changes assessed


> Tip: Plan phases up front, then create the phase sheet for the current phase only. Update later phases when you are ready to execute them.

## 4. Phase Overview
| Phase | Objective | Entrance Criteria | Exit Criteria / Done When | Phase Sheet |
| --- | --- | --- | --- | --- |
| Phase 0 - Research & Validation | Confirm assumptions, gather refs | Delta accepted, backlog reviewed | Open questions resolved, risks logged | `phases/phase-01.md` |
| Phase 1 - Design Revision Application | Apply design revision changes | Phase 0 complete | Code + tests updated, local checks passing | `phases/phase-02.md` |
| Phase 2 - Verification & Cleanup | Run verification suite, update docs | Phase 1 complete, CI green | All gates passed, docs updated | `phases/phase-03.md` |

*Adjust/add phases as needed; every phase must have clear gates. Phase sheets are authored one at a time using `supekku/templates/phase-sheet-template.md`.*

## 5. Phase Detail Snapshot
- **Research Notes**: `{{ delta_id }}/notes.md` (Phase 0 output)
- **Design Revision**: `{{ delta_id }}/DR-XXX.md`
- **Active Phase Sheet**: <link once created>
- **Parallelisable Work**: Flag tasks with `[P]` inside phase sheets
- **Plan Updates**: Update this plan when phase outcomes change (new risks, scope adjustments)

## 6. Testing & Verification Plan
- **Updated Suites**: <list unit/integration/system tests>
- **New Cases**: <outline key scenarios>
- **Tooling/Fixtures**: <mention new helpers/mocks>
- **Rollback Plan**: <if applicable>
- **Verification Coverage**: Cross-check `supekku:verification.coverage@v1` entries against phases and requirements.

## 7. Risks & Mitigations
| Risk | Mitigation | Owner |
| --- | --- | --- |
| e.g. `.viceignore` misconfiguration | Provide defaults, add logging | Dev |

## 8. Open Questions & Decisions
- [ ] Question/decision placeholder (resolve before exit)

## 9. Progress Tracking
- [ ] Phase 0 complete
- [ ] Phase 1 complete
- [ ] Phase 2 complete
- [ ] Verification gates passed

## 10. Notes / Links
- Audit reference: AUD-XXX (pending)
- Supporting docs: <links>
```
