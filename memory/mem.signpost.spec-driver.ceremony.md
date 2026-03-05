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
summary: Check workflow.toml for the active ceremony mode, then read the corresponding
  mode memory for operational guidance. Ceremony is advisory; enforcement comes from
  explicit command gates.
priority:
  severity: high
  weight: 9
scope:
  commands:
  - uv run spec-driver validate
  paths:
  - .spec-driver/workflow.toml
  - supekku/scripts/lib/core/config.py
provenance:
  sources:
  - kind: code
    note: Workflow config loading (advisory posture selection)
    ref: supekku/scripts/lib/core/config.py
  - kind: code
    note: Completion gate path that enforces coverage independently of ceremony
    ref: supekku/scripts/complete_delta.py
  - kind: doc
    note: Ceremony and strict-mode framing
    ref: change/deltas/DE-038-canonical_workflow_alignment/DR-038.md
---

# Ceremony Mode Selection

## Start Here
- [[mem.signpost.spec-driver.overview]]

## How to Determine

Read `.spec-driver/workflow.toml`:

```toml
ceremony = "pioneer"   # pioneer | settler | town_planner
```

## Then Read

- `pioneer` → [[mem.concept.spec-driver.ceremony.pioneer]]
- `settler` → [[mem.concept.spec-driver.ceremony.settler]]
- `town_planner` → [[mem.concept.spec-driver.ceremony.town-planner]]

## Important

Ceremony mode chooses guidance posture. It does not currently enforce command
sequencing at runtime.

Current enforcement comes from concrete gates such as:
- coverage verification in `complete delta` (see [[mem.fact.spec-driver.coverage-gate]])
- explicit flags and command checks (`--force`, `--skip-update-requirements`, etc.)

## Quick Summary

| Mode | Focus | Specs Are | Primary Work Unit |
|------|-------|-----------|-------------------|
| Pioneer | Ship and learn | Aspirational | Cards |
| Settler | Delta-first delivery | Converging toward truth | Deltas |
| Town Planner | Full governance | Truth | Revisions → Deltas |

Each mode is a point on the path toward the
[[mem.concept.spec-driver.philosophy|idealised form]]. Projects move between
modes as they mature — this is convergence, not "more process."
