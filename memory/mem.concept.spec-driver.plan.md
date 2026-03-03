---
id: mem.concept.spec-driver.plan
name: Implementation Plans
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- plan
- phases
summary: Implementation Plans (IP-*) break delta execution into verifiable phases
  with entrance/exit criteria. Phase sheets track detailed task progress.
priority:
  severity: medium
  weight: 6
provenance:
  sources:
  - kind: doc
    ref: supekku/about/glossary.md
  - kind: doc
    note: Implementation Planning section
    ref: supekku/about/processes.md
  - kind: doc
    note: Phase document structure
    ref: docs/delta-completion-workflow.md
---

# Implementation Plans

## Role in the Loop

The IP is the **plan** step of the [[mem.pattern.spec-driver.core-loop]].
It decomposes a [[mem.concept.spec-driver.delta|delta]] into phases that can
be verified independently.

## Structure

```
change/deltas/DE-XXX-slug/
  IP-XXX.md          # The plan: phases overview, success criteria
  phases/
    phase-01.md      # Phase sheet: tasks, assumptions, verification
    phase-02.md
```

### Plan (IP-XXX.md)

- `supekku:plan.overview` YAML block listing phases
- Success criteria checklist
- Overall entrance/exit criteria

### Phase Sheets (phase-NN.md)

- `supekku:phase.overview` YAML block
- Per-task breakdown with status
- Phase-level entrance/exit criteria
- Completion summary

## Commands

```bash
uv run spec-driver create phase --plan IP-XXX   # create next phase sheet
```

## Posture Variance

- **Pioneer**: no IPs — work is tracked in cards
- **Settler**: optional — used when execution is non-trivial
- **Town Planner**: expected for multi-step changes
