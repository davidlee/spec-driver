---
id: IP-006.PHASE-01
slug: standardize-cli-json-output-support-phase-01
name: IP-006 Phase 01 - Add JSON support to CLI commands
created: '2025-11-02'
updated: '2025-11-02'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-006.PHASE-01
plan: IP-006
delta: DE-006
objective: >-
  Add --json flag to create and list CLI commands with standardized output format
entrance_criteria:
  - Delta DE-006 approved
  - Existing --json pattern understood (create.py lines 58-79)
  - Standard JSON schema defined
exit_criteria:
  - All create subcommands (issue, problem, improvement, risk) support --json
  - List specs command supports --json shorthand
  - All tests passing (69 CLI tests)
  - Ruff and Pylint passing
  - ISSUE-007 resolved
verification:
  tests:
    - test_create_issue_json_output
    - test_create_problem_json_output
    - test_create_risk_json_output
  evidence:
    - Git commit 8f388ea
    - All 69 CLI tests passing
    - Ruff 100% clean
    - Pylint 10/10 score
tasks:
  - Add --json to create issue, problem, improvement, risk
  - Add --json shorthand to list specs
  - Write JSON output tests
  - Run full test suite
  - Resolve ISSUE-007
risks:
  - Breaking text output (mitigated - --json is opt-in)
  - Inconsistent JSON schema (mitigated - standard format defined)
```

# Phase N - <Name>

## 1. Objective
<What this phase achieves>

## 2. Links & References
- **Delta**: DE-006
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
