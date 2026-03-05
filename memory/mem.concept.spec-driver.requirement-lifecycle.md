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
- status
summary: Agent-facing model for requirement lifecycle, coverage statuses, traceability,
  and corner-case guidance grounded in PROD-008/009 and current implementation.
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
  - uv run spec-driver complete delta
provenance:
  sources:
  - kind: doc
    ref: supekku/about/lifecycle.md
  - kind: spec
    ref: specify/product/PROD-008/PROD-008.md
    note: Capture/deliver/observe lifecycle (§2)
  - kind: spec
    ref: specify/product/PROD-009/PROD-009.md
    note: Lifecycle semantics and evidence overlay (§2, §4)
  - kind: code
    ref: supekku/scripts/lib/requirements/registry.py
  - kind: code
    ref: supekku/scripts/lib/requirements/lifecycle.py
  - kind: code
    ref: supekku/scripts/lib/blocks/verification.py
  - kind: code
    ref: supekku/scripts/lib/changes/lifecycle.py
  - kind: delta
    ref: DE-043
    note: Coverage validation fix and lifecycle guidance (DEC-043-03)
links:
  missing:
  - raw: PROB-002
---

# Requirement Lifecycle Guidance

## Summary

- Requirements are canonical in SPEC/PROD markdown; the registry is derived.
- Requirement lifecycle status is derived from coverage entries on sync.
- Coverage status and requirement status are distinct enums; do not mix them.
- See `supekku/about/lifecycle.md` for code-truth details.

## 1. Three Status Vocabularies

These are **distinct enums in distinct domains**. Never cross-apply.

| Domain | Module | Values | Governs |
| --- | --- | --- | --- |
| Requirement lifecycle | `requirements/lifecycle.py` | `pending`, `in-progress`, `active`, `retired` | Requirement record status in registry |
| Coverage entry status | `blocks/verification.py` | `planned`, `in-progress`, `verified`, `failed`, `blocked` | Individual coverage entries in spec/plan/audit blocks |
| Change artifact lifecycle | `changes/lifecycle.py` | `draft`, `pending`, `in-progress`, `completed`, `deferred` | Delta, revision, audit status |

Unknown coverage statuses are **excluded from derivation with a warning** (DE-043).
See [[mem.fact.spec-driver.status-enums]] for the canonical reference.

## 2. Changing an Established Requirement

Requirements are spec-owned. Changes flow through governance, never direct registry edits.

- **Semantic change** (meaning/scope shifts): create a spec revision (RE-XXX) that
  retires the old requirement and introduces a new one with traceability.
- **Editorial change** (wording/clarification): update the spec directly within a delta;
  the requirement ID is preserved.
- **Move between specs**: use revision `action: move` with source and destination spec.
- **Partial fulfillment**: split into two requirements or keep `in-progress` with mixed
  coverage evidence; do not invent new statuses.

## 3. Backlog → Spec Transit

Requirements don't "migrate" from backlog into specs. The flow is:

1. **Backlog** captures pain: issues, problems, improvements record observed gaps.
2. **Delta scoping**: when a backlog item is scoped into a delta, the delta's
   applies-to specs are identified.
3. **Spec update**: the delta's implementation introduces the formal requirement
   in the owning spec's frontmatter and coverage block (`status: planned`).
4. **Traceability**: the delta's `relations` link back to the originating backlog item.

The requirement is **authored fresh in the spec** — it is not moved from backlog.
Backlog items are closed/linked, not promoted.

## 4. When Are Lifecycle Transitions Expected?

From PROD-008 §2, the capture → deliver → observe cycle:

| Phase | What happens | Coverage status transition |
| --- | --- | --- |
| **Capture** | Requirement authored in spec, coverage entry added | → `planned` |
| **Deliver** | Delta implements; IP marks VT/VA/VH progress | `planned` → `in-progress` → `verified` |
| **Observe** | Audit inspects the system against spec coverage | `verified` may → `failed` if drift found |

- Delta close copies final coverage status back to the owning spec's coverage block.
- Validation raises warnings until spec block is updated or issue resolved.
- Evidence overlay (PROD-009): later evidence outranks earlier; audits outrank deltas
  at equal timestamps.

## Golden Path

1. Add requirement to spec + coverage entry `status: planned`.
2. Create delta referencing the requirement.
3. Update plan/spec coverage to `in-progress` then `verified` as work completes.
4. Run `uv run spec-driver sync` and `uv run spec-driver validate`.
5. Use audits when needed; reconcile drift warnings.

## Related

- [[mem.fact.spec-driver.status-enums]]
- [[mem.fact.spec-driver.requirement-bundle-files]]
- [[mem.signpost.spec-driver.lifecycle-start]]
- [[PROB-002]]
