---
id: mem.concept.spec-driver.relations
name: Relations and Traceability
kind: memory
status: active
memory_type: concept
updated: '2026-03-06'
verified: '2026-03-06'
confidence: high
tags:
- spec-driver
- relations
- traceability
summary: 'Relations link artefacts via frontmatter. Traceability arrays are automatic
  via sync. Requirement lifecycle is derived from coverage and revisions, not edited
  directly in the registry.'
priority:
  severity: high
  weight: 8
provenance:
  sources:
  - kind: doc
    note: Traceability semantics
    ref: supekku/about/lifecycle.md
  - kind: code
    ref: supekku/scripts/lib/requirements/registry.py
  - kind: code
    ref: supekku/scripts/lib/blocks/relationships.py
---

# Relations and Traceability

## Core Principle

**Traceability is automatic. Lifecycle is derived.**

These are parallel systems:

### 1. Traceability Arrays (Automatic via sync)

```yaml
implemented_by: [DE-002, DE-005]
verified_by: [AUD-001, AUD-003]
```

Populated automatically by `uv run spec-driver sync` from relations and
evidence sources.

### 2. Requirement Lifecycle (Derived)

```yaml
status: pending | in-progress | active | retired
```

Derived during sync from coverage blocks and revision lifecycle payloads.
The registry is derived. Do not treat manual registry edits as the normal path.

## Relation Types

| Type | From | To | Meaning |
|------|------|----|---------|
| `implements` | Delta | Requirement | Delta delivers this requirement |
| `verifies` | Audit | Requirement | Audit confirms this requirement |
| `relates_to` | Any | Any | General association |
| `supersedes` | Any | Any | Replaces an older artefact |

## How It Works

1. Add `implements` relations in [[mem.concept.spec-driver.delta|delta]] frontmatter
2. Run `uv run spec-driver sync` — populates `implemented_by[]` in requirements registry
3. After [[mem.concept.spec-driver.audit|audit]], `verifies` relations populate `verified_by[]`
4. Coverage and revision data drive lifecycle status during sync

## The Requirements Registry

`.spec-driver/registry/requirements.yaml` is a **derived view** of requirements,
traceability, and lifecycle. Specs, revisions, and coverage remain the canonical inputs.
