---
id: TEMPLATE-spec-tech
slug: tech-spec-template
name: Tech Spec Template
created: 2024-06-08
updated: 2024-06-08
status: draft
kind: guidance
packages: []
aliases:
  - Tech Spec Template
---

# SPEC-XXX - <System, Subsystem Or Component Name>

<!--
  Structured relationships block (edit YAML, regenerate any rendered table if applicable).
  `primary` should list requirements owned by this spec; `collaborators` references foreign requirements this spec contributes to.
  Extend `interactions` as needed (depends_on/collaborates_with/obsoletes/etc.).
-->
```yaml supekku:spec.relationships@v1
schema: supekku.spec.relationships
version: 1
spec: SPEC-XXX
requirements:
  primary:
    - SPEC-XXX.FR-001
  collaborators: []
interactions:
  - type: depends_on
    spec: SPEC-YYY
    summary: >-
      Brief rationale for dependency.
```

<!--
  Capabilities block records structured responsibilities and links to requirements.
  `id` should be stable (kebab-case). Keep prose below for richer explanation.
-->
```yaml supekku:spec.capabilities@v1
schema: supekku.spec.capabilities
version: 1
spec: SPEC-XXX
capabilities:
  - id: capability-example
    name: Example capability
    responsibilities:
      - <responsibility-id-from-frontmatter>
    requirements:
      - SPEC-XXX.FR-001
    summary: >-
      Short paragraph summarising the capability.
    success_criteria:
      - Measure executed successfully.
```

## 1. Intent & Summary
- **Purpose**: <One paragraph describing the desired outcome>
- **Scope**: <Boundaries, inclusions/exclusions>
- **Guiding Principles**: <Bullet list; mirrors frontmatter>
- **Reference Materials**: <Inline links to doc/reference/* or other guidance useful for implementers>
- **Change History**:
  - Latest Delta: DE-XXX (link)
  - Latest Audit: AUD-XXX (link)

## 2. Context & Dependencies
- **External Actors / Systems / Components** (summarise; structured details belong in the YAML block above if machine-readable form is needed):
  | Actor/System/Component | Contract | Responsibility | Notes |
  | --- | --- | --- | --- |
- **Related SPECs / PROD**: narrate key relationships, referencing entries from `interactions`.
- **Constitution References (ADRs / Policies / Standards)**:
  | Artefact | Type | Constraint Summary | Link |
  | --- | --- | --- | --- |
  > List every ADR, policy, or standard constraining this system.
- **Decisions**:
  - Decision ID (link) - summary of constraint

## 3. Responsibilities & Capabilities
Use prose to elaborate on items defined in the `supekku:spec.capabilities@v1` block:
- **Capability (capability-example)** - description, success criteria, related FR/NF
- …

## 4. Architecture Overview
- **Runtime Diagram**: <link/embed C4-ish diagram>
- **Components**:
  | Component | Responsibility | Interfaces | State/Storage | Failure Modes |
  | --- | --- | --- | --- | --- |
  > Include interface or schema snippets when they clarify behaviour better than prose (e.g. Go interface, protobuf message).
- **Data & Schema**:
  - Data Model Name: fields, constraints, lifecycle
- **Integration Contracts**:
  - Contract ID: request/response schema, invariants (embed schema/interface definitions when compact).

## 5. Behaviour
- **Primary Flows**:
  - Flow Name: step-by-step narrative referencing components/contracts
- **Edge Cases & Guards**:
  - Scenario → expected behaviour, fallback (include guard/pseudocode snippets when clearer).
- **State Transitions** (if applicable): state diagram or table

## 6. Quality & Operational Requirements
- **Functional Requirements (FR)**:
  - FR code - statement - linked PROD requirement (if any)
- **Non-Functional Requirements (NF)**:
  - NF code - statement - measurement (SLO/SLA)
- **Observability**: metrics, logs, alerts, dashboards
- **Security & Compliance**: authn/z, data handling, etc.

## 7. Testing Strategy
- **Test Guidance & Conventions**: Libraries, frameworks, naming/structure rules, reusable helpers/factories.
- **Test Strategy**: Mapping of scenarios to test levels (unit/component/integration/system); heuristics for mocks vs real infra.
- **Test Suite Inventory**:
  | Suite/File | Purpose | Key Cases | Notes |
  | --- | --- | --- | --- |
  > Document cases in plain English, grouped to mirror actual suite structure.
- **Test Infrastructure & Amenities**: Helpers, fixtures, matchers, data builders, known gaps/opportunities.
- **Coverage Expectations**: Required coverage or focus areas; emphasise critical behaviours.
  > For exhaustive inventories, use the companion template `tech-testing-template.md`.

## 8. Verification
- **Coverage Map**:
  | Requirement | Verification Artefact (VT/VA/VH) | Status |
  | --- | --- | --- |
- **Audit Status**:
  - Last Audit: AUD-XXX - patch level summary
  - Open audit findings: links with short notes

## 9. Backlog Hooks
- **Open Issues/Problems**:
  - ISSUE-XXX - summary
  - PROB-YYY - summary
- **Pending Decisions/Hypotheses**:
  - ID - description - owner - due date

## 10. Risks & Assumptions
- Active Risks: RISK-XXX - description - mitigation
- Assumptions: list items; note what happens if invalidated

## 11. Implementation Notes (for agents)
- Environment/bootstrap prerequisites
- Known limitations/debt
- Checklist for modifying this system (e.g., "run VT-210 after changes", "update SPEC-XXX responsibilities if…")

## Appendices (Optional)
- Glossary
- Detailed API examples
- Migration notes or historical context
