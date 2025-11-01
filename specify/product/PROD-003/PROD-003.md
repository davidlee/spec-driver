---
id: PROD-003
slug: support-cli-workflows-by-providing-artefact-package-paths
name: support CLI workflows by providing artefact & package paths
created: '2025-11-01'
updated: '2025-11-01'
status: draft
kind: prod
aliases: []
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

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-OR-PROD-XXX
entries:
  - artefact: VT-XXX
    kind: VT|VA|VH
    requirement: SPEC-OR-PROD-XXX.FR-001
    status: planned|in-progress|verified
    notes: >-
      Optional context or evidence pointer (link to CI job, audit finding, etc.).
```

## 1. Intent & Summary
- **Problem / Purpose** *(product)*: <Why this exists for users, market, or business.>
- **Scope / Boundaries** *(tech)*: <What systems/components are in or out.>
- **Value Signals**: <Key outcomes, success metrics, or operational targets.>
- **Change History**: <Latest delta/audit/revision influencing this spec.>

## 2. Stakeholders & Journeys
- **Personas / Actors** *(product)*: <Role – goals, pains, expectations.>
- **Systems / Integrations** *(tech)*: <External systems, contracts, constraints.>
- **Primary Journeys / Flows**: Given–When–Then narratives or sequence steps.
- **Edge Cases & Non-goals**: <Scenarios we deliberately exclude; failure/guard rails.>

## 3. Responsibilities & Requirements
- **Capability Overview**: Expand each capability in the YAML block (behaviour, FR/NF links).
- **Functional Requirements (FR)**: `SPEC-XXX.FR-001` / `PROD-XXX.FR-001` – statement – verification.
- **Non-Functional Requirements (NF)**: code – statement – measurement.
- **Success Metrics / Signals** *(product)* or **Operational Targets** *(tech)*: <Quantifiable indicators.>

## 4. Solution Outline
- **User Experience / Outcomes** *(product)*: <Desired behaviours, storyboards, acceptance notes.>
- **Architecture / Components** *(tech)*: tables or diagrams covering components, interfaces, data/state.
- **Data & Contracts**: Key entities, schemas, API/interface snippets relevant to both audiences.

## 5. Behaviour & Scenarios
- **Primary Flows**: Step lists linking actors/components/requirements.
- **Error Handling / Guards**: Edge-case branching, fallback behaviour, recovery expectations.
- **State Transitions** *(tech)*: Diagrams or tables if stateful.

## 6. Quality & Verification
- **Testing Strategy**: Mapping of requirements/capabilities to test levels; reference testing companion if present.
- **Research / Validation** *(product)*: UX research, experiments, hypothesis tracking.
- **Observability & Analysis**: Metrics, telemetry, analytics dashboards, alerting.
- **Security & Compliance**: Authn/z, data handling, privacy, regulatory notes.
- **Verification Coverage**: Keep `supekku:verification.coverage@v1` entries aligned with FR/NF ownership and evidence.
- **Acceptance Gates**: Launch criteria tying back to FR/NF/metrics.

## 7. Backlog Hooks & Dependencies
- **Related Specs / PROD**: How they collaborate or depend.
- **Risks & Mitigations**: Risk ID – description – likelihood/impact – mitigation.
- **Known Gaps / Debt**: Link backlog issues (`ISSUE-`, `PROB-`, `RISK-`) tracking outstanding work.
- **Open Decisions / Questions**: Outstanding clarifications for agents or stakeholders.

## Appendices (Optional)
- Glossary, detailed research, extended API examples, migration history, etc.

