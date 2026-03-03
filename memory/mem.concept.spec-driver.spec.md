---
id: mem.concept.spec-driver.spec
name: Specifications
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- spec
- requirements
- seed
summary: Tech Specs (SPEC-*) and Product Specs (PROD-*) define system behaviour, architecture,
  and product intent. In the idealised form, specs are truth.
priority:
  severity: high
  weight: 8
provenance:
  sources:
  - kind: doc
    note: Key Artifacts section
    ref: supekku/about/README.md
  - kind: doc
    ref: supekku/about/glossary.md
  - kind: doc
    note: Spec Creation section
    ref: supekku/about/processes.md
---

# Specifications

## Role in the Loop

Specs are the **specify** step of the [[mem.pattern.spec-driver.core-loop]].
They define the desired end-state of the system.

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
uv run spec-driver create spec --type product "Feature"    # product spec
```

## The Posture Spectrum

In the [[mem.concept.spec-driver.philosophy|idealised form]], **specs are truth**
— they describe what the system IS. But this depends on
[[mem.concept.spec-driver.posture]]:

- **Pioneer**: specs are aspirational or absent
- **Settler**: specs are converging toward truth
- **Town Planner**: specs ARE truth — deviations are defects

## Taxonomy

- **Assembly spec**: cross-unit integration/functional slice. Human-authored.
- **Unit spec**: 1:1 with a code unit. Often auto-maintained. Being
  deprecated in favour of [[mem.concept.spec-driver.contract|contracts]].
