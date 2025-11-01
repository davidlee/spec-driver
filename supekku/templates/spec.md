# {{ spec_id }} – {{ name }}

{{ spec_relationships_block }}

{{ spec_capabilities_block }}

{{ spec_verification_block }}

## 1. Intent & Summary
{% if kind == 'prod' -%}
- **Problem / Purpose**: <Why this exists for users, market, or business.>
{% else -%}
- **Scope / Boundaries**: <What systems/components are in or out.>
{% endif -%}
- **Value Signals**: <Key outcomes, success metrics, or operational targets.>
- **Change History**: <Latest delta/audit/revision influencing this spec.>

## 2. Stakeholders & Journeys
{% if kind == 'prod' -%}
- **Personas / Actors**: <Role – goals, pains, expectations.>
{% else -%}
- **Systems / Integrations**: <External systems, contracts, constraints.>
{% endif -%}
- **Primary Journeys / Flows**: Given–When–Then narratives or sequence steps.
- **Edge Cases & Non-goals**: <Scenarios we deliberately exclude; failure/guard rails.>

## 3. Responsibilities & Requirements
- **Capability Overview**: Expand each capability in the YAML block (behaviour, FR/NF links).
- **Functional Requirements (FR)**: `{{ spec_id }}.FR-001` – statement – verification.
- **Non-Functional Requirements (NF)**: code – statement – measurement.
{% if kind == 'prod' -%}
- **Success Metrics / Signals**: <Quantifiable indicators.>
{% else -%}
- **Operational Targets**: <Quantifiable indicators.>
{% endif %}
## 4. Solution Outline
{% if kind == 'prod' -%}
- **User Experience / Outcomes**: <Desired behaviours, storyboards, acceptance notes.>
{% else -%}
- **Architecture / Components**: tables or diagrams covering components, interfaces, data/state.
{% endif -%}
- **Data & Contracts**: Key entities, schemas, API/interface snippets relevant to both audiences.

## 5. Behaviour & Scenarios
- **Primary Flows**: Step lists linking actors/components/requirements.
- **Error Handling / Guards**: Edge-case branching, fallback behaviour, recovery expectations.
{% if kind == 'spec' -%}
- **State Transitions**: Diagrams or tables if stateful.
{% endif %}
## 6. Quality & Verification
- **Testing Strategy**: Mapping of requirements/capabilities to test levels; reference testing companion if present.
{% if kind == 'prod' -%}
- **Research / Validation**: UX research, experiments, hypothesis tracking.
{% endif -%}
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
