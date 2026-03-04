---
id: mem.concept.spec-driver.requirement-lifecycle
name: Requirement Lifecycle Guidance
kind: memory
status: active
memory_type: concept
updated: '2026-03-05'
verified: '2026-03-05'
tags:
- spec-driver
- lifecycle
- requirements
- coverage
summary: Agent-facing model for requirement lifecycle, coverage statuses, and traceability
  grounded in current implementation.
scope:
  paths:
  - supekku/about/lifecycle.md
  - supekku/scripts/lib/requirements/registry.py
  - supekku/scripts/lib/requirements/lifecycle.py
  - supekku/scripts/lib/blocks/verification.py
  - supekku/scripts/lib/changes/lifecycle.py
  commands:
  - uv run spec-driver sync
  - uv run spec-driver validate
provenance:
  sources:
  - kind: doc
    ref: supekku/about/lifecycle.md
  - kind: code
    ref: supekku/scripts/lib/requirements/registry.py
  - kind: code
    ref: supekku/scripts/lib/requirements/lifecycle.py
  - kind: code
    ref: supekku/scripts/lib/blocks/verification.py
  - kind: code
    ref: supekku/scripts/lib/changes/lifecycle.py
---

# Requirement Lifecycle Guidance

## Summary
- Requirements are canonical in SPEC/PROD markdown; the registry is derived.
- Requirement lifecycle status is derived from coverage entries on sync.
- Coverage status and requirement status are distinct enums; do not mix them.
 - See `supekku/about/lifecycle.md` for code-truth details.

## Canonical Status Sets
- Requirement lifecycle: `pending`, `in-progress`, `active`, `retired`.
- Coverage status: `planned`, `in-progress`, `verified`, `failed`, `blocked`.
- Change artifact lifecycle: `draft`, `pending`, `in-progress`, `completed`, `deferred`.

## Golden Path (Current Truth)
1. Add requirement to spec + coverage entry `status: planned`.
2. Create delta referencing the requirement.
3. Update plan/spec coverage to `in-progress` then `verified` as work completes.
4. Run `uv run spec-driver sync` and `uv run spec-driver validate`.
5. Use audits when needed; reconcile drift warnings.

## Edge Case Guidance
- Changing an established requirement: use a revision; modify/retire and introduce a
  new requirement if semantics change.
- Requirement moves between specs: use revision `action: move` with destination.
- Partial fulfillment: split into two requirements or keep one requirement
  `in-progress` with mixed coverage evidence; do not invent new statuses.
- Requirement detail files under `requirements/` are supplemental only; lifecycle
  is driven by the spec markdown and coverage blocks.

## Related
- [[mem.fact.spec-driver.requirement-bundle-files]]
- [[mem.signpost.spec-driver.lifecycle-start]]
- [[PROB-002]]
