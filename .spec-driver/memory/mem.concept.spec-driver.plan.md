---
id: mem.concept.spec-driver.plan
name: Implementation Plans
kind: memory
status: active
memory_type: concept
updated: "2026-03-06"
verified: "2026-03-06"
confidence: high
tags: [spec-driver, plan, phases]
summary: Implementation Plans (IP-*) break delta execution into verifiable phases with entrance/exit criteria. Phase sheets track detailed task progress.
priority:
  severity: medium
  weight: 6
provenance:
  sources:
    - kind: adr
      ref: ADR-004
    - kind: code
      ref: supekku/cli/create.py
    - kind: code
      ref: supekku/scripts/lib/changes/creation.py
    - kind: code
      ref: supekku/scripts/lib/changes/creation.py
---

# Implementation Plans

## Role in the Loop

The IP is the **plan** step of the [[mem.pattern.spec-driver.core-loop]].
It decomposes a [[mem.concept.spec-driver.delta|delta]] into phases that can
be verified independently.

Phase sheets are created just-in-time during execution, not all scaffolded up
front.

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
uv run spec-driver create phase "Phase name" --plan IP-XXX   # create next phase sheet
```

## Posture Variance

Posture affects how formally plans are expressed and enforced, but the main
question is execution scope.

- Significant or multi-step changes should usually have an IP or equivalent
  planning artefact.
- Phase sheets are appropriate when execution benefits from just-in-time
  decomposition and explicit verification checkpoints.
- When deltas are active, IPs and phase sheets normally live inside the delta bundle.
- When deltas are not active, equivalent planning records may live in cards or
  other local planning docs.
