---
id: mem.pattern.spec-driver.create-phase-convention
name: Create Phase Preserves Plan Convention
kind: memory
status: active
memory_type: pattern
created: "2026-03-21"
updated: "2026-03-21"
verified: "2026-03-21"
confidence: high
tags: [spec-driver, phases, sharp-edge]
summary: "create phase materializes the next planned phase using the plan's existing ID spelling and skips equivalent duplicate phase entries."
priority:
  severity: high
  weight: 9
scope:
  commands:
    - uv run spec-driver create phase
    - spec-driver create phase
  paths:
    - supekku/scripts/lib/changes/creation.py
    - supekku/scripts/lib/changes/creation_test.py
    - supekku/scripts/lib/blocks/plan.py
provenance:
  sources:
    - kind: code
      note: create_phase now parses both dotted and hyphenated phase IDs, selects the first planned-but-unmaterialized phase, and dedupes equivalent plan entries
      ref: supekku/scripts/lib/changes/creation.py
    - kind: code
      note: regression coverage for hyphenated and dotted plans
      ref: supekku/scripts/lib/changes/creation_test.py
    - kind: delta
      note: design rationale for compatibility-first phase creation
      ref: DE-105
---

# Create Phase Preserves Plan Convention

## Summary

- Treat phase identity as `(plan_id, sequence number)`, not a raw string.
- When `supekku:plan.overview@v1` already lists phases, `create phase` should
  materialize the first planned phase that does not yet have a corresponding
  `phases/phase-NN.md` file.
- Preserve the spelling already used by the owning plan entry:
  `IP-###-P##` stays hyphenated, `IP-###.PHASE-##` stays dotted.
- When updating the plan overview, do not append a second entry for an
  equivalent logical phase.

## Context

This avoids two recurring footguns:

- hand-authored hyphenated plans used to get a dotted duplicate when
  `create phase` ran
- metadata lookup used to miss the intended plan entry because it compared phase
  IDs by exact string instead of logical phase identity
