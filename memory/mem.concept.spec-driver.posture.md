---
id: mem.concept.spec-driver.posture
name: Project Posture
kind: memory
status: active
memory_type: concept
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- posture
- ceremony
- seed
summary: The framework is permissive; the project chooses its constraints. Posture
  is configured via workflow.toml and enforced by agents and the validator.
priority:
  severity: high
  weight: 9
provenance:
  sources:
  - kind: doc
    note: Ceremony modes and closure contract
    ref: docs/commands-workflow.md
  - kind: doc
    note: Project posture configuration
    ref: .spec-driver/workflow.toml
---

# Project Posture

## The Flexibility Problem

Spec-driver defines an [[mem.concept.spec-driver.philosophy|idealised form]] —
a tight loop where specs are truth and every change is explicit. But not every
project is ready for that. Early-stage code needs speed. Legacy codebases need
gradual adoption. The framework must be flexible without muddying the ideal.

## How It Works

**The framework is permissive. The project chooses its constraints.**

Three things enforce the chosen posture:

1. **`workflow.toml`** — declares ceremony mode, enabled primitives, and toggles
2. **The validator** — enforces structural rules consistent with project config
3. **Agent discipline** — agents respect the project's posture, not the full
   framework vocabulary

## Ceremony Modes as Named Postures

Spec-driver defines three named postures (see [[mem.signpost.spec-driver.ceremony]]):

- **Pioneer** — ship and learn; cards and optional ADRs; specs are aspirational
- **Settler** — delta-first delivery; specs converging toward truth
- **Town Planner** — full governance; specs ARE truth; revisions before deltas

The transition from pioneer → settler → town-planner is convergence toward
the idealised form. It is not "more process" — it is specs becoming truth
rather than aspiration.

## What This Means for Agents

- Read `workflow.toml` to determine the active ceremony mode
- Only use primitives that are activated for the current mode
- Do not impose higher-ceremony workflows than the project has adopted
- When in doubt, follow [[mem.pattern.spec-driver.core-loop]] but respect
  which steps are optional for the current posture

## Kanban Cards

Cards (`T123-*.md`) are an escape hatch. Depending on posture, they may be:
- The primary work-tracking mechanism (pioneer)
- A lightweight complement to deltas (settler)
- A deprecated legacy artifact being phased out
- Mandated for specific task types by project convention

Check `workflow.toml [cards]` for the project's stance.
