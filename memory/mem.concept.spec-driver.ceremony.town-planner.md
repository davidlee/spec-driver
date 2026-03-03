---
id: mem.concept.spec-driver.ceremony.town-planner
name: Town Planner Ceremony Mode
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- ceremony
- town-planner
- seed
summary: 'High ceremony: full governance with revisions before deltas, evidence discipline,
  and specs as the evergreen source of truth.'
priority:
  severity: medium
  weight: 7
provenance:
  sources:
  - kind: doc
    note: Town Planner mode description
    ref: docs/commands-workflow.md
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
revision → spec/requirement updates → delta(s) → DR → IP/phases → implement → audit → closure
```

This is the full [[mem.pattern.spec-driver.core-loop]] with no shortcuts.

## How Specs Behave Here

Specs **are truth**. They describe what the system IS. When the system must
change, a [[mem.concept.spec-driver.revision]] captures that intent first,
the specs are updated, and then [[mem.concept.spec-driver.delta|deltas]] bring
the code into alignment. [[mem.concept.spec-driver.audit|Audits]] close the
loop by confirming that specs reflect what was realised.

## Agent Guidance

- Always check for relevant accepted ADRs before starting work
- Revisions precede deltas — do not create a delta without first capturing
  the spec change intent in a revision
- Evidence is not optional — [[mem.concept.spec-driver.verification]] artifacts
  must be executed and documented
- Follow [[mem.pattern.spec-driver.delta-completion]] rigorously for closure
- The [[mem.concept.spec-driver.truth-model]] is strictly enforced: contracts
  are observed truth, specs are authoritative intent
