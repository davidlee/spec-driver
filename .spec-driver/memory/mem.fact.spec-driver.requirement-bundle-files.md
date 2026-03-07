---
id: mem.fact.spec-driver.requirement-bundle-files
name: Requirement Bundle Files Are Supplemental
kind: memory
status: active
memory_type: fact
updated: '2026-03-05'
verified: '2026-03-05'
tags:
- spec-driver
- requirements
- sharp-edge
summary: Requirement detail files under requirements/ are not consumed by sync; canonical
  identity and lifecycle remain in spec markdown.
scope:
  paths:
  - supekku/scripts/lib/requirements/registry.py
  - supekku/about/lifecycle.md
provenance:
  sources:
  - kind: code
    note: Requirements are extracted only from SPEC-/PROD- markdown files
    ref: supekku/scripts/lib/requirements/registry.py
  - kind: doc
    ref: supekku/about/lifecycle.md
---

# Requirement Bundle Files Are Supplemental

## Fact
Requirement detail files under `requirements/` inside a spec bundle are not
consumed by sync or lifecycle logic.

## Implication
- Requirement identity and lifecycle must still be present in the spec markdown
  (SPEC-/PROD- file) to be tracked.
- Treat `requirements/*.md` as supplemental narrative only.

## Related
- [[mem.concept.spec-driver.requirement-lifecycle]]
- [[PROB-002]]
