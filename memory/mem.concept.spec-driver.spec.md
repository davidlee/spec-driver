---
id: mem.concept.spec-driver.spec
name: Specifications
kind: memory
status: active
memory_type: concept
updated: '2026-03-06'
verified: '2026-03-06'
confidence: high
tags:
- spec-driver
- spec
- requirements
summary: Tech Specs (SPEC-*) and Product Specs (PROD-*) define system behaviour, architecture,
  and product intent. In high-rigor flows, canonical spec state is finalized after
  audit/contracts reconciliation.
priority:
  severity: high
  weight: 8
provenance:
  sources:
  - kind: adr
    ref: ADR-004
  - kind: adr
    ref: ADR-003
  - kind: code
    ref: supekku/cli/create.py
---

# Specifications

## Role in the Loop

Specs are the durable normative record in the
[[mem.pattern.spec-driver.core-loop]]. In high-rigor flow they become
canonical after explicit reconciliation, not by being edited aspirationally
ahead of implementation.

## Two Families

- **Tech Spec (SPEC-*)** — system responsibilities, architecture, behaviour,
  quality requirements, testing strategy. Lives in `specify/tech/SPEC-*/`.
- **Product Spec (PROD-*)** — user problems, hypotheses, success metrics,
  business value. Lives in `specify/product/PROD-*/`.

## Requirements

Specs contain requirements:
- **FR-*** (Functional Requirements) — testable behavioural requirements
- **NF-*** (Non-Functional Requirements) — quality requirements with measurement

Requirements have their own lifecycle tracked in the
[[mem.concept.spec-driver.relations|requirements registry]].

## Commands

```bash
uv run spec-driver create spec "Component Name"           # tech spec
uv run spec-driver create spec --kind product "Feature"    # product spec
```

## The Posture Spectrum

In the [[mem.concept.spec-driver.philosophy|high-rigor form]], specs are
canonical after closure reconciliation. During active delivery, intent and
observed behavior may diverge briefly. This depends on
[[mem.concept.spec-driver.posture]]:

- **Pioneer**: specs are aspirational or absent
- **Settler**: specs are converging toward truth
- **Town Planner**: specs are reconciled to truth after audit/contracts; unresolved deviations are defects

## Taxonomy

- **Assembly spec**: cross-unit integration/functional slice. Human-authored.
- **Unit spec**: 1:1 with a code unit. Often auto-maintained. Being
  deprecated in favour of [[mem.concept.spec-driver.contract|contracts]].
