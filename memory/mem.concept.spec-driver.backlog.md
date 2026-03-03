---
id: mem.concept.spec-driver.backlog
name: Backlog
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- backlog
summary: 'Work intake layer: issues, problems, improvements, and risks. Feeds delta
  scoping and prioritisation.'
priority:
  severity: medium
  weight: 5
provenance:
  sources:
  - kind: doc
    note: Backlog Capture section
    ref: supekku/about/processes.md
  - kind: doc
    ref: supekku/about/glossary.md
---

# Backlog

## Role in the Loop

The backlog is the **capture** step of the [[mem.pattern.spec-driver.core-loop]].
Need for change enters here before being scoped into
[[mem.concept.spec-driver.delta|deltas]].

## Four Item Types

| Type | Purpose | Command |
|------|---------|---------|
| **Issue** | Actionable defect or gap | `uv run spec-driver create issue "Title"` |
| **Problem** | User/system pain with evidence | `uv run spec-driver create problem "Title"` |
| **Improvement** | Opportunity to enhance | `uv run spec-driver create improvement "Title"` |
| **Risk** | Identified risk to track | `uv run spec-driver create risk "Title"` |

## Where They Live

All items under `backlog/` with subdirectories by type (`issues/`, `problems/`,
`improvements/`, `risks/`).

## Prioritisation

```bash
uv run spec-driver list backlog -p   # opens editor to reorder
```

## Posture Variance

- **Pioneer**: backlog is optional; cards may substitute
- **Settler/Town Planner**: backlog is the standard intake mechanism
