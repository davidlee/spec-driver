```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: {{ phase_id }}
plan: {{ plan_id }}
delta: {{ delta_id }}
objective: >-
  Short statement of what this phase achieves.
entrance_criteria: []
exit_criteria: []
verification:
  tests: []
  evidence: []
tasks: []
risks: []
```

# Phase N - <Name>

## 1. Objective
<What this phase achieves>

## 2. Links & References
- **Delta**: {{ delta_id }}
- **Design Revision Sections**: <bullets>
- **Specs / PRODs**: <list requirement IDs>
- **Support Docs**: <links to reference material>

## 3. Entrance Criteria
- [ ] Item 1
- [ ] Item 2

## 4. Exit Criteria / Done When
- [ ] Outcome 1
- [ ] Outcome 2

## 5. Verification
- Tests to run (unit/integration/system)
- Tooling/commands (`go test ./...`, scripts, etc.)
- Evidence to capture (logs, screenshots, audit snippets)

## 6. Assumptions & STOP Conditions
- Assumptions: …
- STOP when: <condition that requires human check-in>

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [ ] | 1.1 | High-level activity | [ ] |  |

### Task Details
- **1.1 Description**
  - **Design / Approach**: …
  - **Files / Components**: …
  - **Testing**: …
  - **Observations & AI Notes**: …
  - **Commits / References**: …

*(Repeat detail blocks per task as needed)*

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |

## 9. Decisions & Outcomes
- `YYYY-MM-DD` - Decision summary (include rationale)

## 10. Findings / Research Notes
- Use for code spelunking results, links, screenshots, etc.

## 11. Wrap-up Checklist
- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Spec/Delta/Plan updated with lessons
- [ ] Hand-off notes to next phase (if any)
