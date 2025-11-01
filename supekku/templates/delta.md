---
id: DE-XXX
slug: descriptive-kebab-case-name
name: "Delta – Descriptive Change Title"
created: 'YYYY-MM-DD'
updated: 'YYYY-MM-DD'
status: draft
kind: delta
aliases: []
relations: []
applies_to:
  specs: []
  requirements: []
---

# DE-XXX – Descriptive Change Title

```yaml supekku:delta.relationships@v1
schema: supekku.delta.relationships
version: 1
delta: DE-XXX
revision_links:
  introduces: []
  supersedes: []
specs:
  primary: []
  collaborators: []
requirements:
  implements: []
  updates: []
  verifies: []
phases: []
```

## 1. Summary & Context
- **Product Spec(s)**: PROD-XXX – <link and summary>
- **Technical Spec(s)**: SPEC-YYY – <link and summary>
- **Implementation Plan**: [IP-XXX](./IP-XXX.md) – <execution status>
- **Change Drivers**: <Backlog issues, decisions, audits providing impetus>

## 2. Motivation
- <Why this delta exists; articulate user/system pain and desired target state>
- <Reference supporting research, ADRs, audits>

## 3. Scope & Objectives
- **Primary Outcomes**:
  - <Outcome 1 mapped to requirement>
  - <Outcome 2>
- **Operational Constraints**: <Time, risk, rollout, coupling limits>
- **Dependencies**: <Other deltas/spec updates that must land first>

## 4. Out of Scope
- <Explicitly defer adjacent work to future deltas or phases>

## 5. Approach Overview
- **System Touchpoints**: <Packages, services, data models>
- **Key Changes**:
  - <Change 1 – tie to SPEC responsibilities>
  - <Change 2>
- **Migration / Rollout Notes**: <Guarded releases, toggles, backfill requirements>

## 6. Verification Strategy
- **Requirements Coverage**: <How each requirement listed above will be verified>
- **Planned Artefacts**: <VT/VA/VH IDs expected from implementation plan phases>
- **Acceptance Criteria**: <Objective pass/fail gates before marking delta complete>

## 7. Risks & Mitigations
- **Risk**: <Description> – *Likelihood*: low|medium|high – *Impact*: low|medium|high – *Mitigation*: <Action>
- **Risk**: …

## 8. Follow-ups & Tracking
- **Future Phases / Deltas**: <What remains after this delta>
- **Backlog Items**: ISSUE-XXX, PROB-YYY – <Short note>
- **Open Decisions / Questions**: <Outstanding clarifications with owner + due date>

## 9. Implementation Notes
- <Environment setup, scripts, commands, coordination notes>
- <Links to design artefacts, diagrams, reference documentation>

> Replace placeholders with concrete details. Remove sections that do not apply rather than leaving empty headings.
