---
id: IP-012.PHASE-01
slug: restore-entry-exit-criteria-to-ip-schema-phase-01
name: IP-012 Phase 01
created: '2025-11-03'
updated: '2025-11-03'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-012.PHASE-01
plan: IP-012
delta: DE-012
objective: >-
  Describe the outcome for this phase.
entrance_criteria: []
exit_criteria: []
verification:
  tests: []
  evidence: []
tasks: []
risks: []
```

```yaml supekku:phase.tracking@v1
# OPTIONAL: Structured progress tracking (recommended for accurate status)
# When present, this block takes precedence over markdown checkboxes for completion calculation.
schema: supekku.phase.tracking
version: 1
phase: IP-012.PHASE-01
files:  # OPTIONAL: Phase-level file references
  references:
    - "path/to/reference/doc.md"  # Research/reference materials
    - "path/to/exemplar/code.py"  # Example code patterns
  context:
    - "path/to/similar/phase.md"  # Related phases, similar implementations
entrance_criteria:
  - item: "Describe entrance criterion 1"
    completed: false
  - item: "Describe entrance criterion 2"
    completed: false
exit_criteria:
  - item: "Describe exit criterion 1"
    completed: false
  - item: "Describe exit criterion 2"
    completed: false
tasks:
  - id: "1.1"
    description: "Task description"
    status: pending  # pending | in_progress | completed | blocked
    files:  # OPTIONAL: Track which files changed in this task
      added:
        - "path/to/new/file.py"
      modified:
        - "path/to/modified/file.py"
      removed: []
      tests:
        - "path/to/test_file.py"
  - id: "1.2"
    description: "Another task"
    status: pending
    files:
      added: []
      modified:
        - "path/to/another/file.py"
      removed: []
      tests: []
```

# Phase N - <Name>

## 1. Objective
<What this phase achieves>

## 2. Links & References
- **Delta**: DE-012
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
