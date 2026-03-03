---
id: mem.concept.spec-driver.philosophy
name: Spec-Driver Philosophy
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- philosophy
- seed
summary: Spec-driver treats specifications as the evergreen source of truth for a
  system. Change is explicit, auditable, and agent-native. Start here.
priority:
  severity: high
  weight: 10
provenance:
  sources:
  - kind: doc
    note: Core philosophy section
    ref: supekku/about/README.md
  - kind: doc
    note: Three tenets
    ref: supekku/about/dogma.md
---

# Spec-Driver Philosophy

## The Inverted Model

Traditional specs are disposable — written once, ignored as code evolves.
Spec-driver inverts this: specifications are **living documents** that co-evolve
with the codebase. They are the canonical source of truth for what the system
is and does.

## The Idealised Form

In its purest expression:

- **Specs are truth** — they describe what the system IS, not what we wish it were
- **Revisions express intent** — when truth must change, a [[mem.concept.spec-driver.revision]] captures that intent before code moves
- **Deltas apply intent to code** — a [[mem.concept.spec-driver.delta]] is the scoped mechanism for aligning code with revised specs
- **Audits reconcile** — a [[mem.concept.spec-driver.audit]] closes the loop, ensuring specs reflect what was actually realised

This is a closed cycle: truth → intent to change → change → reconcile back to truth.

## Three Tenets

1. No implementation without a spec-driver artefact
2. Guide the user invisibly in correct use of spec-driver
3. Pursue correctness, compact token-efficiency, and crisp, pragmatic rigour

## Agent-Native

Every artefact is structured markdown with machine-readable YAML frontmatter.
Workflows are deterministic. The process is designed to be automated by AI
agents as much as by humans.

## See Also

- [[mem.concept.spec-driver.posture]] — how projects adopt the philosophy gradually
- [[mem.pattern.spec-driver.core-loop]] — the operational workflow
- [[mem.signpost.spec-driver.ceremony]] — ceremony modes (pioneer/settler/town-planner)
