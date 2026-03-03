---
id: mem.signpost.spec-driver.ceremony
name: Ceremony Mode Selection
kind: memory
status: active
memory_type: signpost
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- ceremony
- seed
summary: Check workflow.toml for the active ceremony mode, then read the corresponding
  mode memory for operational guidance.
priority:
  severity: high
  weight: 9
provenance:
  sources:
  - kind: doc
    note: Ceremony modes section
    ref: docs/commands-workflow.md
  - kind: doc
    note: ceremony field
    ref: .spec-driver/workflow.toml
---

# Ceremony Mode Selection

## How to Determine

Read `.spec-driver/workflow.toml`:

```toml
ceremony = "pioneer"   # pioneer | settler | town_planner
```

## Then Read

- `pioneer` → [[mem.concept.spec-driver.ceremony.pioneer]]
- `settler` → [[mem.concept.spec-driver.ceremony.settler]]
- `town_planner` → [[mem.concept.spec-driver.ceremony.town-planner]]

## Quick Summary

| Mode | Focus | Specs Are | Primary Work Unit |
|------|-------|-----------|-------------------|
| Pioneer | Ship and learn | Aspirational | Cards |
| Settler | Delta-first delivery | Converging toward truth | Deltas |
| Town Planner | Full governance | Truth | Revisions → Deltas |

Each mode is a point on the path toward the
[[mem.concept.spec-driver.philosophy|idealised form]]. Projects move between
modes as they mature — this is convergence, not "more process."
