---
id: PROD-008
slug: requirements-lifecycle-coherence
name: Requirements Lifecycle Coherence
created: '2025-11-03'
updated: '2025-11-03'
status: draft
kind: prod
aliases: []
relations: []
guiding_principles:
  - Keep a single canonical source of truth for requirement status.
  - Make lifecycle shifts observable to both humans and agents.
  - Prefer explicit handoffs (spec ⇄ delta ⇄ audit) over implicit updates.
assumptions:
  - Specs remain the authoritative artefact for long-lived requirements.
  - Implementation plans exist for every delta that edits a requirement.
  - Audits will continue to be produced after major releases.
---

# PROD-008 – Requirements Lifecycle Coherence

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: PROD-008
requirements:
  primary:
    - PROD-008.FR-001
    - PROD-008.FR-002
    - PROD-008.FR-003
  collaborators:
    - SPEC-036.FR-004
interactions: []
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: PROD-008
capabilities:
  - id: lifecycle-contract
    name: Requirements Lifecycle Contract
    responsibilities:
      - lifecycle-contract-governance
    requirements:
      - PROD-008.FR-001
      - PROD-008.FR-002
      - PROD-008.FR-003
    summary: >-
      Establishes the canonical lifecycle for requirements and the roles
      played by specs, deltas, implementation plans, and audits in keeping
      that lifecycle accurate.
    success_criteria:
      - Every closed delta updates the owning spec coverage block.
      - Audits surface any drift between observed and documented status.
```

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: PROD-008
entries:
  - artefact: VH-201
    kind: VH
    requirement: PROD-008.FR-001
    status: planned
    notes: Initial lifecycle walkthrough to confirm handoff steps with stakeholders.
  - artefact: VA-320
    kind: VA
    requirement: PROD-008.FR-002
    status: planned
    notes: Validation session exercising `uv run spec-driver close-delta` checklist.
  - artefact: VT-902
    kind: VT
    requirement: PROD-008.FR-003
    status: planned
    notes: Integration test to ensure registry sync highlights spec vs audit drift.
```

## 1. Intent & Summary
- **Problem / Purpose**: Requirements regularly fall out of sync between specs, the registry, deltas, and audits. This spec defines a single lifecycle contract so humans and agents always know which artefact is authoritative.
- **Value Signals**: Registry accuracy ≥ 99%, zero “unknown” requirement states after delta close, audits raise actionable drift within one business day.
- **Guiding Principles**: Frontmatter declares ownership and context; coverage blocks publish verified evidence; deltas and plans describe execution and must hand updates back into specs; audits observe reality and trigger reconciliation.
- **Change History**: Initial draft assembled while adding verification coverage parser (2025-11-03).

## 2. Stakeholders & Journeys
- **Personas / Actors**:
  - *Spec authors*: need a reliable checklist for promoting requirements through the lifecycle and knowing which metadata to update.
  - *Implementation agents*: need authoritative instructions for updating specs when wrapping a delta.
  - *Auditors*: need to confirm the documented state matches reality and flag deviations.
- **Primary Journeys / Flows**:
  1. **Capture** – Given we introduce a new requirement, when we author a spec frontmatter entry and add it to the coverage block with `status: planned`, then the registry marks the requirement as “introduced”.
  2. **Deliver** – Given a delta implements the requirement, when the implementation plan marks the VT/VA/VH as `in-progress` and later `verified`, then the delta close checklist must copy that status into the spec coverage block.
  3. **Observe** – Given an audit inspects the system, when it records `status: failed` for a requirement, then validation raises a warning until either the spec block is updated or the issue is resolved.
- **Edge Cases & Non-goals**:
  - We do **not** attempt to model requirements that live exclusively in experiments (handled outside the registry).
  - Temporary or spike requirements should remain in the backlog, not the spec.

## 3. Responsibilities & Requirements

### Capability Overview

The lifecycle contract capability ensures every lifecycle transition has an owning artefact, an associated check, and a responsible role. The responsibilities list below details the specific behaviours we expect from each participant.

### Functional Requirements


- **FR-001**: The specs frontmatter and coverage block MUST be the authoritative record of each requirement’s lifecycle state and supporting evidence.
  *Verification*: VH-201 – Lifecycle walkthrough confirming spec updates after delta closure.
- **FR-002**: Every delta that changes requirement behaviour MUST provide an implementation plan documenting planned VT/VA/VH artefacts and promote the final state back into the owning spec coverage block before completion.
  *Verification*: VA-320 – Validation session exercising the delta close checklist.
- **FR-003**: Audits MUST reconcile observed behaviour against the spec coverage block and raise drift through validation warnings until the spec is corrected or follow-up work is scheduled.
  *Verification*: VT-902 – Automated registry sync test simulating audit failure vs spec state.
### Non-Functional Requirements

- **NF-001**: Lifecycle updates MUST propagate through the registry within one sync cycle (< 5 minutes) after a spec change.
  *Measurement*: VT-905 – Integration test exercising `uv run spec-driver sync`.
- **NF-002**: Validation warnings about lifecycle drift MUST be actionable, surfacing responsible artefacts and suggested remediation steps.
  *Measurement*: VA-322 – Expert review of validator messaging across sample drift scenarios.
### Success Metrics / Signals

- **Coverage Freshness**: ≥ 95% of requirements transition from `planned` to `verified` within 24 hours of delta completion.
- **Drift Resolution**: All audit-triggered drift warnings cleared or assigned to a follow-up delta within one business day.
- **Validation Confidence**: ≥ 90% of agents report that lifecycle guidance is “clear” or “very clear” in quarterly surveys.

## 4. Solution Outline
- **User Experience / Outcomes**: Spec authors always begin with frontmatter and coverage updates, agents rely on implementation plan templates, and audits provide crisp “here’s the drift” messaging. The workflow reads as: author spec → deliver via delta + plan → verify via coverage → observe via audit.
- **Data & Contracts**:
  - `supekku:verification.coverage@v1` — canonical mapping of requirement → VT/VA/VH artefacts.
  - `frontmatter.relations` — expresses dependencies and verification evidence at a coarse level.
  - Registry sync contracts (`.spec-driver/registry/*.yaml`) — store lifecycle projections driven by coverage blocks.

## 5. Behaviour & Scenarios
- **Primary Flows**:
  - *Introduce*: Author adds requirement to spec frontmatter + coverage (`status: planned`) → Registry marks “introduced”.
  - *Implement*: Delta plan sets coverage entry to `in-progress` → On completion, spec block becomes `verified` → Registry marks “implemented/verified”.
  - *Audit*: Audit coverage entry reports `failed` → Validation warning raised → Actionable follow-up logged → Spec coverage updated once fixed.
- **Error Handling / Guards**:
  - If a delta closes without spec updates, the validation CLI raises an error referencing the missing coverage update.
  - If an audit references unknown requirements, the registry sync surfaces a “missing mapping” warning requiring spec owners to review.

## 6. Quality & Verification
- **Testing Strategy**: Lifecycle integration tests exercise registry sync and validator warnings. Manual validation sessions confirm that agents following the delta close checklist update the spec correctly. Automated drift detection runs after each audit import.
- **Research / Validation**: Interview spec authors and auditors quarterly to confirm the workflow remains clear; capture feedback in backlog improvements.
- **Observability & Analysis**: Track lifecycle transition counts and drift warnings in the validation dashboard; alert if drift remains unresolved beyond 24 hours.
- **Security & Compliance**: Requirement metadata includes potential audit protocols—ensuring evidence storage aligns with governance policies.
- **Verification Coverage**: Managed via the coverage block; registry sync compares spec entries with plan/audit snapshots.
- **Acceptance Gates**: No delta closes without spec coverage update; registry sync shows 0 “unknown” states; latest audit has no outstanding drift on PROD-008 requirements.

## 7. Backlog Hooks & Dependencies
- **Related Specs / PROD**: SPEC-036 documents the metadata-driven validation engine that will consume these coverage blocks; PROD-001 captures broader spec authoring workflows.
- **Risks & Mitigations**:
  - *RISK-REQ-001*: Forgetting to update spec coverage after a delta close – *Mitigation*: Extend close checklist and add validator hard failure (Tracked in ISSUE-412).
  - *RISK-REQ-002*: Audit warnings ignored – *Mitigation*: Validation gating in CI and weekly lifecycle review ritual.
- **Known Gaps / Debt**: ISSUE-413 – “Automation to compare plan vs spec coverage”; PROB-128 – “Audit tooling should auto-open follow-up deltas”.
- **Open Decisions / Questions**:
  - Should audits automatically propose spec edits? *(Owner: david, Due: 2025-11-10)*
  - Can we auto-suggest coverage updates from registry diffs? *(Owner: automation-team, Due: 2025-11-17)*

## Appendices (Optional)
- Glossary, detailed research, extended API examples, migration history, etc.
