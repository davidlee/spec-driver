---
id: SPEC-OR-PROD-XXX
slug: descriptive-kebab-case-name
name: "Descriptive Capability Name"
created: 'YYYY-MM-DD'
updated: 'YYYY-MM-DD'
status: draft
kind: product|spec
aliases: []
relations: []
guiding_principles:
  - <Principle 1>
assumptions: []
hypotheses: []
decisions: []
---

# SPEC/PROD-XXX – Descriptive Capability Name

```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-OR-PROD-XXX
requirements:
  primary:
    - <FR/NF codes owned by this spec>
  collaborators: []
interactions: []
```

```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: SPEC-OR-PROD-XXX
capabilities:
  - id: <kebab-case-id>
    name: <Human-readable capability>
    responsibilities: []
    requirements: []
    summary: >-
      <Short paragraph describing what this capability ensures.>
    success_criteria:
      - <How you know this capability is upheld.>
```

## 1. Intent & Summary

### Problem / Purpose *(product focus)*
- <Describe the user/market problem and desired outcome.>

### Scope / Boundaries *(tech focus)*
- <List inclusions, exclusions, system edges.>

### Value Signals
- <Key metrics or qualitative indicators of success.>

### Change History
- <Reference latest delta, audit, or revision touching this spec.>

## 2. Stakeholders & Journeys

### Personas / Actors *(product)*
- <Role name – goals, pains, expectations.>

### Systems / Integrations *(tech)*
- <External systems, APIs, queues, contracts.>

### Primary Journeys / Flows

### Capability Overview
- <Narrative expanding each capability in the YAML block; reference FR/NF codes.>

### Functional Requirements (FR)
- `SPEC-XXX.FR-001` / `PROD-XXX.FR-001` – <Statement> – *Verification*: <How we test>.

### Non-Functional Requirements (NF)
- `SPEC-XXX.NF-001` / `PROD-XXX.NF-001` – <Statement> – *Measurement*: <Metric or instrumentation>.

### Success Metrics / Operational Targets
- <Quantitative metrics or outcome thresholds.>

## 4. Solution Outline

### User Experience / Outcomes *(product)*
- <Desired behaviours, storyboards, acceptance context.>

### Architecture / Components *(tech)*
- <Component list/table, diagrams, interface notes.>

### Data & Contracts
- <Key entities, schemas, request/response shapes shared between product and tech narratives.>

## 5. Behaviour & Scenarios

### Primary Flows
- <Step-by-step flows tying actors/components/requirements.>

### Error Handling & Guards
- <Fallbacks, guard conditions, resilience expectations.>

### State Transitions *(if stateful)*
- <Tables or diagrams of state evolution.>

## 6. Quality & Verification

### Testing Strategy
- <Map requirements/capabilities to unit/component/integration/system coverage; link testing companion if present.>

### Research & Validation *(product)*
- <UX studies, experiments, hypothesis status updates.>

### Observability & Compliance
- <Metrics, alerts, logging, security/privacy requirements.>

### Acceptance Gates
- <Launch or readiness criteria aligned to FR/NF and metrics.>

## 7. Backlog Hooks & Dependencies

### Related Specs / Products
- <Summarise dependencies, collaboration boundaries.>

### Linked Work
- <Deltas, revisions, issues, problems, hypotheses with short notes.>

### Risks & Mitigations
- <Risk ID – description – likelihood/impact – mitigation strategy.>

### Open Decisions & Questions
- <Outstanding clarifications or choices agents must resolve.>

## 8. Implementation Notes (Agents & Operators)

### Setup & Bootstrap
- <Commands, tooling, environment prerequisites.>

### Workflow Guidance
- <Registry sync steps, validation commands, coordination notes.>

### Known Gaps & Debt
- <Areas needing follow-up, monitoring, or planned deltas.>

## Appendices (Optional)

### Supporting Materials
- <Glossary, detailed research, extended API examples, migration history, anything that doesn’t fit the core flow.>
