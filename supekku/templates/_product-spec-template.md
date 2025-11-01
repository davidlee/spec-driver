---
id: TEMPLATE-spec-product
slug: product-spec-template
name: Product Spec Template
created: 2024-06-08
updated: 2025-11-01
status: draft
kind: guidance
aliases:
  - Product Spec Template
---

# Product Spec Template

Use this template for PROD specs describing product intent, user value, and measurable outcomes.

## ⚡ Quick Guidance
- ✅ Ground everything in user problems, desired outcomes, and business value.
- ✅ Link to problems, hypotheses, decisions, and related system specs.
- 🎯 Keep requirements testable and measurable with specific FR/NF codes.
- 📎 Remove sections that do not apply; avoid "N/A" placeholders.

```markdown
---
id: PROD-XXX
slug: descriptive-kebab-case-name
name: "Descriptive Product Capability Name"
created: 'YYYY-MM-DD'
updated: 'YYYY-MM-DD'
status: draft
kind: product
aliases: []
---

# PROD-XXX – Descriptive Product Capability Name

## 1. Intent & Summary
- **Problem Statement(s)**: <Link to PROB-XXX and summarise user/market pain>
- **Value Proposition**: <Why this matters for users and business>
- **Guiding Principles**:
  - <Principle 1>
  - <Principle 2>
- **Reference Materials**: <Links to research, briefs, market analysis>
- **Change History**: <Latest delta/audit/revision influencing this PROD>

## 2. Personas & Scenarios
- **Persona – <Role Name>**: <Primary goals and needs>
  - *Scenario*: Given <context>, when <action>, then <outcome>.
  - *Use Case UC-001*: <User can accomplish X with Y constraints>
- **Edge Cases & Non-Goals**:
  - <Feature/capability deliberately excluded>

## 3. Requirements

### Functional Requirements (FR)
- **PROD-XXX.FR-001** – <Behavioral requirement>. *Verification*: <How to test>.
- **PROD-XXX.FR-002** – <User capability>. *Verification*: <Acceptance criteria>.

### Non-Functional Requirements (NF)
- **PROD-XXX.NF-001** – <Quality expectation with target>. *Measurement*: <How to measure>.
- **PROD-XXX.NF-002** – <Performance/reliability goal>. *Measurement*: <Instrumentation>.

### Success Metrics / Signals
- <Metric>: ≥ <target> within <timeframe>
- <Qualitative signal from users/telemetry>

## 4. Hypotheses & Assumptions
- **PROD-XXX.HYP-01** – <Hypothesis statement>. *Validation*: <How to test>. *Status*: proposed|validated|invalid.
- **Assumption**: <Critical belief>. *Invalidation implication*: <What we'd need to change>.

## 5. Dependencies & Collaborators
- **Related Specs**: SPEC-YYY (<technical implementation>), PROD-ZZZ (<related product area>)
- **ADRs**: ADR-AAA (<architectural decision affecting this>)
- **Risks**: RISK-BBB (<threat to delivery>)

## 6. Verification & Validation
- **Research**: <Research IDs, usability studies, feasibility investigations>
- **Acceptance Criteria**:
  - All FR requirements have passing tests
  - Success metrics show <threshold> improvement
  - <Other launch gates>

## 7. Backlog Hooks
- **Issues**: ISSUE-XXX (<blocking bug>), ISSUE-YYY (<quality gap>)
- **Problems**: PROB-ZZZ (<user pain point driving this>)
- **Planned Deltas**: DE-AAA (<Phase 1>), DE-BBB (<Phase 2>)

## 8. Risks & Mitigations
- **Risk**: <Description of product/user/operational risk>
  - *Likelihood*: low|medium|high
  - *Impact*: low|medium|high
  - *Mitigation*: <Strategy to reduce risk>

## Appendices (Optional)
- <Detailed research summaries, market analysis, UX artifacts>
```

**Authoring Guidance**
- Use PROD-XXX.FR-NNN for functional requirements, PROD-XXX.NF-NNN for non-functional.
- Hypothesis IDs: PROD-XXX.HYP-NN; Decision IDs: PROD-XXX.DEC-NN.
- For phased delivery, add `phases` array to frontmatter (see vice/specify/product/PROD-001).
- For structured frontmatter approach (enables tooling), see supekku/about/frontmatter-schema.md.
- Remove sections that don't apply rather than leaving placeholders.
