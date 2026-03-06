---
id: mem.concept.spec-driver.ceremony.town-planner
name: Town Planner Ceremony Mode
kind: memory
status: active
memory_type: concept
updated: '2026-03-06'
verified: '2026-03-06'
confidence: high
tags:
- spec-driver
- ceremony
- town-planner
summary: 'High ceremony: full governance with revisions before deltas, evidence discipline,
  and explicit spec reconciliation after audit/contracts.'
priority:
  severity: medium
  weight: 7
provenance:
  sources:
  - kind: adr
    ref: ADR-004
---

# Town Planner Ceremony Mode

## Intent

Predictable governance, evidence discipline, and long-lived evergreen specs.
This is the closest to the [[mem.concept.spec-driver.philosophy|idealised form]].

## Activated Primitives

- **Full policy layer** — ADRs + standards + policies
- **[[mem.concept.spec-driver.spec]]** and requirements as the main source of intent
- **[[mem.concept.spec-driver.revision]]** — coordinated spec changes before code
- **[[mem.concept.spec-driver.delta]]** / [[mem.concept.spec-driver.plan]] / phases as primary delivery
- **[[mem.concept.spec-driver.audit]]** — conformance audits that project evidence back into coverage

## Typical Flow

```
revision (often with new requirements) -> delta + DR + IP + phase sheets -> implement -> audit/contracts -> patch specs -> closure
```

This is the full [[mem.pattern.spec-driver.core-loop]] with no shortcuts.

## How Specs Behave Here

Town Planner treats specs as canonical outputs after reconciliation, not
necessarily as the first edited artifact in delivery. During execution:

- Revision/DR/IP define intended changes.
- Audit/contracts establish observed behavior.
- Specs are patched after audit to match what was realised.

## Agent Guidance

- Always check for relevant accepted ADRs before starting work
- Use revision-first by default in this mode; if strict enforcement is desired,
  enforce via policy/doctrine (not convention alone)
- Evidence is not optional — [[mem.concept.spec-driver.verification]] artifacts
  must be executed and documented
- Explicitly reconcile specs after audit/contracts before closure
- Follow [[mem.pattern.spec-driver.delta-completion]] rigorously for closure
- The [[mem.concept.spec-driver.truth-model]] is strictly enforced: contracts
  are observed truth, specs are authoritative intent
