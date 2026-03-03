---
id: mem.concept.spec-driver.relations
name: Relations and Traceability
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- relations
- traceability
summary: Relations link artefacts via frontmatter. Traceability (implemented_by, verified_by)
  is automatic via sync. Status is always manual.
priority:
  severity: high
  weight: 8
provenance:
  sources:
  - kind: doc
    note: Traceability semantics
    ref: supekku/about/lifecycle.md
  - kind: doc
    note: Requirements registry updates
    ref: docs/delta-completion-workflow.md
---

# Relations and Traceability

## Core Principle

**Status is manual. Traceability is automatic.**

These are two parallel systems that do not interfere:

### 1. Status (Manual)

```yaml
status: pending → in_progress → implemented → verified
```

You control this via direct edits. No automatic transitions.

### 2. Traceability Arrays (Automatic via sync)

```yaml
implemented_by: [DE-002, DE-005]   # deltas with "implements" relations
verified_by: [AUD-001, AUD-003]    # audits with "verifies" relations
```

Populated automatically by `uv run spec-driver sync` based on frontmatter
`relations:` blocks. Re-running sync is always safe — it never changes status,
only updates arrays.

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
4. Manually update requirement `status` in `.spec-driver/registry/requirements.yaml`

## The Requirements Registry

`.spec-driver/registry/requirements.yaml` is the **source of truth** for
requirement status. Sync populates traceability arrays; you manage status.
