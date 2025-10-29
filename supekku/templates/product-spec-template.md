---
id: TEMPLATE-spec-product
slug: product-spec-template
name: Product Spec Template
created: 2024-06-08
updated: 2024-06-08
status: draft
kind: guidance
aliases:
  - Product Spec Template
---

# Product Spec Template

Use this template for PROD specs describing product intent, user value, and hypotheses.

## ⚡ Quick Guidance
- ✅ Ground everything in user problems, desired outcomes, and business value.
- ✅ Link to problems, hypotheses, decisions, and related system specs.
- 🎯 Keep requirements testable and measurable.
- 📎 Remove sections that do not apply; avoid "N/A" placeholders.

```markdown
# PROD-XXX - <Product Capability>

## 1. Intent & Summary
- **Problem Statement(s)**: <Link to PROB-XXX and summarise>
- **Value Proposition**: <Why this matters for users/business>
- **Guiding Principles**: <Key heuristics>
- **Reference Materials**: <Links to research, briefs, etc>
- **Change History**: Latest delta/audit influencing this PROD.

## 2. Personas & Scenarios
- Persona → primary goals
- Core user journeys (Given/When/Then)
- Edge cases & non-goals

## 3. Requirements
- **Functional (FR)**: FR code - statement - verification idea
- **Non-Functional (NF)**: NF code - quality expectation - measurement
- **Success Metrics / Signals**: KPIs, telemetry, qualitative indicators

## 4. Hypotheses & Assumptions
- Hypothesis ID - statement - validation approach - status
- Critical assumptions and what invalidation implies

## 5. Dependencies & Collaborators
- Related PRODs/SPECs, ADRs, policies, decisions, risks

## 6. Verification & Validation
- Research/experiments, surveys, analytics required
- Acceptance checkpoints, launch criteria

## 7. Backlog Hooks
- Open issues/problems/opportunities
- Planned deltas or initiatives

## 8. Risks & Mitigations
- Product risks, user risks, operational concerns

## Appendices (Optional)
- Detailed research summaries, market analysis, UX artifacts
```
