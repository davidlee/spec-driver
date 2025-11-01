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
  *Example*: System MUST allow users to create accounts with email and password
  *Verification*: VT-001 - User account creation flow test

- **FR-002**: Users MUST be able to [key interaction or workflow]
  *Example*: Users MUST be able to reset their password via email link
  *Verification*: VT-002 - Password reset flow test

- **FR-003**: System MUST [data or behavior requirement]
  *Example*: System MUST persist user preferences across sessions
  *Verification*: VT-003 - Preference persistence test

*Marking unclear requirements:*

- **FR-004**: System MUST [capability] [NEEDS CLARIFICATION: specific question about scope, security, or UX]
  *Example*: System MUST authenticate users via [NEEDS CLARIFICATION: email/password, SSO, OAuth2?]
{% else -%}
- **FR-001**: Component MUST [specific technical capability]
  *Example*: Parser MUST handle JSON documents up to 10MB without memory overflow
  *Verification*: VT-001 - Large document parsing test

- **FR-002**: System MUST [integration or contract requirement]
  *Example*: API client MUST retry failed requests with exponential backoff (max 3 attempts)
  *Verification*: VT-002 - Retry behavior test

- **FR-003**: Component MUST [data handling or state management]
  *Example*: Cache MUST invalidate entries after 5 minutes TTL
  *Verification*: VT-003 - TTL expiration test
{% endif -%}

### Non-Functional Requirements

{% if kind == 'prod' -%}
- **NF-001**: [Performance expectation from user perspective]
  *Example*: Search results MUST appear within 2 seconds for 95% of queries
  *Measurement*: VA-001 - Performance monitoring across 1000 user sessions

- **NF-002**: [Usability or accessibility requirement]
  *Example*: Interface MUST be fully navigable via keyboard only
  *Measurement*: VA-002 - Accessibility audit against WCAG 2.1 AA standards
{% else -%}
- **NF-001**: [Performance constraint with specific metrics]
  *Example*: API endpoint MUST handle 1000 req/sec with p95 latency < 100ms
  *Measurement*: VA-001 - Load testing with sustained traffic

- **NF-002**: [Scalability or resource requirement]
  *Example*: Service MUST scale horizontally to 10 instances under load
  *Measurement*: VA-002 - Horizontal scaling test with traffic ramp

- **NF-003**: [Reliability or fault tolerance]
  *Example*: System MUST maintain 99.9% uptime over 30-day rolling window
  *Measurement*: VA-003 - Uptime monitoring and SLO tracking
{% endif -%}

{% if kind == 'prod' -%}
### Success Metrics / Signals

- **Adoption**: [Quantifiable usage metric]
  *Example*: 80% of target users complete onboarding within first week
- **Quality**: [Error rate or satisfaction metric]
  *Example*: <5% of user sessions encounter errors
- **Business Value**: [Measurable business outcome]
  *Example*: Reduce support tickets by 40% compared to previous solution
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
