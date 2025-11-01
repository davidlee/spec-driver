---
id: TEMPLATE-tech-testing
slug: tech-testing-template
name: Tech Testing Companion Template
created: 2024-06-08
updated: 2024-06-08
status: draft
kind: guidance
aliases:
  - Tech Testing Template
---

# Tech Spec Testing Companion Template

Use this template when a SPEC requires a dedicated testing document. It complements Section 7 of the system spec and can live alongside the SPEC bundle (e.g. `SPEC-101.tests.md`).

```markdown
# SPEC-XXX Testing Guide

## 1. Overview
- **Tech Spec**: SPEC-XXX - <name>
- **Purpose**: <Why this testing guide exists>
- **Test Owners**: <Teams/agents responsible>

## 2. Guidance & Conventions
- **Frameworks / Libraries**: <e.g. Go test, testify, cucumber>
- **Structure**: <Directory/package layout, naming conventions>
- **Factories & Helpers**: <List key fixtures/builders>
- **Mocking Strategy**: <Real infra vs in-memory vs fake services>

## 3. Strategy Matrix
| Scenario / Capability | Recommended Level | Rationale | Notes |
| --- | --- | --- | --- |
- Document how each behaviour ties to unit/component/integration/system tests.

## 4. Test Suite Inventory
For each suite/file:
- **Suite**: `path/to/test.go`
  - **Purpose**: <What it covers>
  - **Key Cases**:
    1. Description - Given/When/Then
    2. …
  - **Dependencies**: <Mocks, fixtures, infra requirements>

## 5. Regression & Edge Cases
- Enumerate regressions to guard against; specify dedicated tests.
- Highlight fragile areas needing extra assertions or property tests.

## 6. Infrastructure & Amenities
- How to run suites locally/in CI (commands, flags).
- Test data management (factories, seed data, snapshot practices).
- Known flakiness, mitigation steps, TODOs.

## 7. Coverage Expectations
- Target coverage (% or qualitative).
- Critical behaviours requiring exhaustive coverage.
- Observability hooks to verify during tests.

## 8. Backlog Hooks
- Outstanding test gaps (issue IDs, problem statements).
- Planned improvements to testing infrastructure.

## 9. Appendices (Optional)
- Advanced troubleshooting tips.
- Links to dashboards or CI job definitions.
```

**Usage Notes**
- Keep plain-language descriptions so agents can translate scenarios into code.
- When updating the SPEC’s Section 7, link to this document if it contains the detailed inventory.
- Ensure any new test helper/library is documented here to guide future implementation agents.
