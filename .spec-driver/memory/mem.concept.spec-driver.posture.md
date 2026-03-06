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
summary: The framework is permissive; the project chooses its constraints. Posture
  is configured via workflow.toml. Ceremony mode is advisory; runtime enforcement
  comes from explicit command gates and validations.
priority:
  severity: high
  weight: 9
scope:
  commands:
  - uv run spec-driver sync
  - uv run spec-driver validate
  paths:
  - .spec-driver/workflow.toml
  - supekku/scripts/lib/core/config.py
provenance:
  sources:
  - kind: code
    note: Workflow configuration loading only
    ref: supekku/scripts/lib/core/config.py
  - kind: code
    note: Completion and coverage enforcement path
    ref: supekku/scripts/complete_delta.py
  - kind: code
    note: Coverage gate implementation
    ref: supekku/scripts/lib/changes/coverage_check.py
  - kind: doc
    note: Canonical posture wording for this delta
    ref: change/deltas/DE-038-canonical_workflow_alignment/DR-038.md
---

# Project Posture

## The Flexibility Problem

Spec-driver defines an [[mem.concept.spec-driver.philosophy|idealised form]] —
a tight loop where change is explicit and specs are reconciled to truth before
closure. But not every
project is ready for that. Early-stage code needs speed. Legacy codebases need
gradual adoption. The framework must be flexible without muddying the ideal.

## How It Works

**The framework is permissive. The project chooses its constraints.**

Posture has distinct layers:

1. **`workflow.toml`** — declares ceremony mode and related preferences.
2. **Runtime gates** — commands enforce specific rules (for example coverage
   checks in `complete delta`) independently of ceremony.
3. **Validator checks** — structural/schema integrity checks.
4. **Agent discipline** — agents respect the project's posture, not the full
   framework vocabulary

Ceremony mode itself does not branch command behavior today.

## Ceremony Modes as Named Postures

Spec-driver defines three named postures (see [[mem.signpost.spec-driver.ceremony]]):

- **Pioneer** — ship and learn; cards and optional ADRs; specs are aspirational
- **Settler** — delta-first delivery; specs converging toward truth
- **Town Planner** — full governance; revision-driven delivery with mandatory audit/reconciliation before closure

`strict_mode` is a documented future contract for hard-failing non-canonical
paths, but it is not implemented as runtime branching in this delta.

The transition from pioneer → settler → town-planner is convergence toward
the idealised form. It is not "more process" — it is specs becoming truth
rather than aspiration.

## What This Means for Agents

- Read `workflow.toml` to determine the active ceremony mode
- Treat ceremony as guidance strength, not command-level enforcement
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
