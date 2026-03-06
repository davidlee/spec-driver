---
id: mem.signpost.spec-driver.file-map
name: Spec-Driver File Map
kind: memory
status: active
memory_type: signpost
updated: '2026-03-07'
verified: '2026-03-07'
tags:
- spec-driver
- navigation
- files
summary: Key spec-driver files and directories under consolidated .spec-driver/ layout
  with backward-compat symlinks at old paths.
scope:
  paths:
  - .spec-driver
  - .contracts
provenance:
  sources:
  - kind: doc
    ref: .spec-driver/README.md
  - kind: delta
    ref: DE-049
---

# Spec-Driver File Map

## Canonical Locations (under `.spec-driver/`)
- Specs: `.spec-driver/product/PROD-XXX/`, `.spec-driver/specs/tech/SPEC-XXX/`
- Deltas: `.spec-driver/deltas/DE-XXX-*/`
- Revisions: `.spec-driver/revisions/RE-XXX-*/`
- Audits: `.spec-driver/audits/AUD-XXX.md`
- Backlog: `.spec-driver/backlog/{issues|problems|improvements|risks}/`
- Memories: `.spec-driver/memory/`
- Skills: `.spec-driver/skills/` (canonical install; agent targets are symlinks)
- Decisions: `.spec-driver/decisions/ADR-XXX-*.md`
- Policies: `.spec-driver/policies/`
- Standards: `.spec-driver/standards/`

## Backward-Compat Symlinks
Compat symlinks inside `specify/` and `change/` point into `.spec-driver/`:
- `specify/tech` → `.spec-driver/specs/tech`
- `specify/decisions` → `.spec-driver/decisions`
- `change/deltas` → `.spec-driver/deltas`
- etc.

Agent target dirs are symlinks to the canonical skills dir:
- `.claude/skills` → `.spec-driver/skills`
- `.agents/skills` → `.spec-driver/skills`

## Tooling & Metadata
- Agent docs: `.spec-driver/agents/`
- Templates: `.spec-driver/templates/`
- Registries: `.spec-driver/registry/`
- Ceremony config: `.spec-driver/workflow.toml`
- Skills allowlist: `.spec-driver/skills.allowlist`

## Contracts (Derived)
- Canonical generated contracts: `.contracts/`

Contracts are derived and safe to regenerate.

## Related
- [[mem.signpost.spec-driver.ceremony]]
- [[mem.concept.spec-driver.spec]]
- [[mem.concept.spec-driver.delta]]
- [[mem.concept.spec-driver.revision]]
- [[mem.concept.spec-driver.audit]]
