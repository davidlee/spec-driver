---
id: mem.concept.spec-driver.verification
name: Verification
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- verification
- evidence
summary: Three verification artifact types (VT, VA, VH) provide evidence that requirements
  are satisfied. Coverage blocks in specs track their status.
priority:
  severity: medium
  weight: 7
provenance:
  sources:
  - kind: doc
    ref: supekku/about/glossary.md
  - kind: doc
    note: Verification artifact status lifecycle
    ref: docs/delta-completion-workflow.md
---

# Verification

## Three Artifact Types

| Type | Name | How |
|------|------|-----|
| **VT** | Verification Test | Automated tests proving functionality |
| **VA** | Verification by Agent | Agent-generated analysis or test report |
| **VH** | Verification by Human | Manual testing, usability review, attestation |

## Coverage Blocks

Specs (typically PROD-*) track verification status in
`supekku:verification.coverage` YAML blocks:

```yaml
entries:
  - artefact: VT-001
    kind: VT
    requirement: PROD-005.FR-001
    status: planned      # planned → in_progress → passed | failed
    notes: Verify leaf package identification
```

## Status Lifecycle

```
planned → in_progress → passed | failed
```

## How Verification Feeds Traceability

1. Verification artifacts are executed (tests run, human reviews, agent analysis)
2. Coverage block entries updated to `passed` or `failed`
3. [[mem.concept.spec-driver.audit|Audits]] create `verifies`
   [[mem.concept.spec-driver.relations|relations]]
4. Sync populates `verified_by[]` in the requirements registry

## Posture Variance

- **Pioneer**: verification is informal
- **Settler**: VT artifacts are common; coverage blocks are adopted selectively
- **Town Planner**: all three types active; coverage blocks mandatory;
  verification artifacts must be executed and documented before delta closure
