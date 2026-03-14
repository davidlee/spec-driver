---
id: mem.concept.spec-driver.philosophy
name: Spec-Driver Philosophy
kind: memory
status: active
memory_type: concept
updated: "2026-03-06"
verified: "2026-03-06"
confidence: high
tags: [spec-driver, philosophy]
summary: "Spec-driver treats specifications as the evergreen source of truth for a system, but canonical spec finalization happens after implementation and audit reconciliation. Change is explicit, auditable, and agent-native. Start here."
priority:
  severity: high
  weight: 10
provenance:
  sources:
    - kind: adr
      ref: ADR-004
    - kind: adr
      ref: ADR-005
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

- **Revisions express intent first** — a [[mem.concept.spec-driver.revision]]
  generally introduces new/changed requirements and the intended direction.
- **Deltas + DR/IP/phases apply intent** — delivery artifacts drive code changes.
- **Audits + contracts establish observed truth** — they show what was actually
  realised.
- **Specs are reconciled last** — specs are patched to match observed truth and
  then become canonical again.

This is a closed cycle: intent → apply → observe → reconcile → canonical truth.

## Two Truth Views

- **Normative truth**: specs/revisions (what should hold after closure)
- **Observed truth**: contracts/audit evidence (what code currently does)

During active delivery, normative and observed truth may diverge briefly.
Closure exists to reconcile them deliberately.

## Three Tenets

1. No implementation without a spec-driver artefact
2. Guide the user invisibly in correct use of spec-driver
3. Pursue correctness, compact token-efficiency, and crisp, pragmatic rigour

## Agent-Native

Every artefact is structured markdown with machine-readable YAML frontmatter.
Workflows are deterministic. The process is designed to be automated by AI
agents as much as by humans.

## See Also

- [[mem.signpost.spec-driver.overview]] — quick overview
- [[mem.concept.spec-driver.posture]] — how projects adopt the philosophy gradually
- [[mem.pattern.spec-driver.core-loop]] — the operational workflow
- [[mem.signpost.spec-driver.ceremony]] — ceremony modes (pioneer/settler/town-planner)
