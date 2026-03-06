---
id: mem.signpost.spec-driver.file-map
name: Spec-Driver File Map
kind: memory
status: active
memory_type: signpost
updated: '2026-03-06'
verified: '2026-03-06'
tags:
- spec-driver
- navigation
- files
summary: Key spec-driver files and directories (specs, deltas, revisions, audits,
  templates, registries, contracts, memories).
scope:
  paths:
  - .spec-driver/templates
  - .spec-driver/registry
  - .spec-driver/workflow.toml
  - specify
  - change
  - backlog
  - memory
  - .contracts
provenance:
  sources:
  - kind: doc
    ref: .spec-driver/README.md
  - kind: doc
    ref: supekku/about/lifecycle.md
---

# Spec-Driver File Map

## Canonical Locations
- Specs: `specify/product/PROD-XXX/`, `specify/tech/SPEC-XXX/`
- Deltas: `change/deltas/DE-XXX-*/`
- Revisions: `change/revisions/RE-XXX-*/`
- Audits: `change/audits/AUD-XXX.md`
- Backlog: `backlog/{issues|problems|improvements|risks}/`
- Memories: `memory/`

## Tooling & Metadata
- Templates: `.spec-driver/templates/`
- Registries: `.spec-driver/registry/`
- Ceremony config: `.spec-driver/workflow.toml`

## Contracts (Derived)
- Canonical generated contracts: `.contracts/`
- Compatibility view: `specify/tech/by-package/**/contracts/`

Contracts are derived and safe to regenerate.

## Related
- [[mem.signpost.spec-driver.ceremony]]
- [[mem.concept.spec-driver.spec]]
- [[mem.concept.spec-driver.delta]]
- [[mem.concept.spec-driver.revision]]
- [[mem.concept.spec-driver.audit]]
