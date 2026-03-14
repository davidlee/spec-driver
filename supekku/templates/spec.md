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
- **Guiding Principles**: <Heuristics, applicable wisdom, what to optimise for.>
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

### Capability Overview

Expand each capability from the `supekku:spec.capabilities@v1` YAML block above, describing concrete behaviors and linking to specific functional/non-functional requirements.

### Functional Requirements

<!--
  Requirements MUST be parseable by the registry using this format:
  - **FR-NNN**: Requirement statement

  Each requirement should be:
  - Testable and unambiguous
  - Technology-agnostic (product specs) or implementation-specific (tech specs)
  - Linked to verification artifacts in the YAML block above
-->

{% if kind == 'prod' -%}

- **FR-001**: System MUST [specific user-facing capability]
  _Example_: System MUST allow users to create accounts with email and password
  _Verification_: VT-001 - User account creation flow test

- **FR-002**: Users MUST be able to [key interaction or workflow]
  _Example_: Users MUST be able to reset their password via email link
  _Verification_: VT-002 - Password reset flow test

- **FR-003**: System MUST [data or behavior requirement]
  _Example_: System MUST persist user preferences across sessions
  _Verification_: VT-003 - Preference persistence test

_Marking unclear requirements:_

- **FR-004**: System MUST [capability] [NEEDS CLARIFICATION: specific question about scope, security, or UX]
  _Example_: System MUST authenticate users via [NEEDS CLARIFICATION: email/password, SSO, OAuth2?]
  {% else -%}
- **FR-001**: Component MUST [specific technical capability]
  _Example_: Parser MUST handle JSON documents up to 10MB without memory overflow
  _Verification_: VT-001 - Large document parsing test

- **FR-002**: System MUST [integration or contract requirement]
  _Example_: API client MUST retry failed requests with exponential backoff (max 3 attempts)
  _Verification_: VT-002 - Retry behavior test

- **FR-003**: Component MUST [data handling or state management]
  _Example_: Cache MUST invalidate entries after 5 minutes TTL
  _Verification_: VT-003 - TTL expiration test
  {% endif -%}

### Non-Functional Requirements

{% if kind == 'prod' -%}

- **NF-001**: [Performance expectation from user perspective]
  _Example_: Search results MUST appear within 2 seconds for 95% of queries
  _Measurement_: VA-001 - Performance monitoring across 1000 user sessions

- **NF-002**: [Usability or accessibility requirement]
  _Example_: Interface MUST be fully navigable via keyboard only
  _Measurement_: VA-002 - Accessibility audit against WCAG 2.1 AA standards
  {% else -%}
- **NF-001**: [Performance constraint with specific metrics]
  _Example_: API endpoint MUST handle 1000 req/sec with p95 latency < 100ms
  _Measurement_: VA-001 - Load testing with sustained traffic

- **NF-002**: [Scalability or resource requirement]
  _Example_: Service MUST scale horizontally to 10 instances under load
  _Measurement_: VA-002 - Horizontal scaling test with traffic ramp

- **NF-003**: [Reliability or fault tolerance]
  _Example_: System MUST maintain 99.9% uptime over 30-day rolling window
  _Measurement_: VA-003 - Uptime monitoring and SLO tracking
  {% endif -%}

{% if kind == 'prod' -%}

### Success Metrics / Signals

- **Adoption**: [Quantifiable usage metric]
  _Example_: 80% of target users complete onboarding within first week
- **Quality**: [Error rate or satisfaction metric]
  _Example_: <5% of user sessions encounter errors
- **Business Value**: [Measurable business outcome]
  _Example_: Reduce support tickets by 40% compared to previous solution
  {% else -%}

### Operational Targets

- **Performance**: [Specific latency/throughput targets]
- **Reliability**: [Uptime or error rate targets]
- **Maintainability**: [Code quality or test coverage targets]
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
