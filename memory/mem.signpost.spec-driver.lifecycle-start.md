---
id: mem.signpost.spec-driver.lifecycle-start
name: Lifecycle Guidance Start Here
kind: memory
status: active
memory_type: signpost
updated: '2026-03-05'
verified: '2026-03-05'
tags:
- spec-driver
- lifecycle
- guidance
summary: Entry point for requirement lifecycle guidance and code-truth references.
scope:
  paths:
  - supekku/about/lifecycle.md
  - supekku/scripts/lib/requirements/registry.py
  - supekku/scripts/lib/requirements/lifecycle.py
  commands:
  - uv run spec-driver sync
  - uv run spec-driver validate
provenance:
  sources:
  - kind: doc
    ref: supekku/about/lifecycle.md
  - kind: memory
    ref: mem.concept.spec-driver.requirement-lifecycle
---

# Lifecycle Guidance Start Here

## Start Here
- `supekku/about/lifecycle.md` (code-truth lifecycle reference)
- [[mem.concept.spec-driver.requirement-lifecycle]] (agent-facing model)

## Sharp Edges
- [[mem.fact.spec-driver.requirement-bundle-files]]

## Problem Context
- [[PROB-002]]
