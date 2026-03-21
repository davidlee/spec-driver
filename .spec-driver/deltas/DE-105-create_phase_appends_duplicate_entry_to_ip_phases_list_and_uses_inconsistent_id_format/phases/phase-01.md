---
id: IP-105-P01
slug: create_phase_appends_duplicate_entry_to_ip_phases_list_and_uses_inconsistent_id_format-phase-01
name: IP-105 Phase 01
created: "2026-03-21"
updated: "2026-03-21"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-105-P01
plan: IP-105
delta: DE-105
objective: >-
  Repair create_phase() so it respects the owning plan's numbering and phase ID
  convention while keeping plan.overview updates idempotent.
entrance_criteria:
  - DE-105, DR-105, and IP-105 reconciled to the issue
  - Impacted create_phase code and tests inspected
exit_criteria:
  - create_phase uses plan-aware numbering and convention selection
  - plan.overview updates do not append equivalent duplicate phases
  - targeted creation tests pass locally
verification:
  tests:
    - VT-DE-105-UNIT
  evidence:
    - targeted pytest output for creation tests
tasks:
  - Add normalization helpers for phase numbering and equivalence
  - Update create_phase metadata lookup and plan mutation behavior
  - Add or update regression tests for hyphenated and dotted plans
risks:
  - Historical mixed conventions may still exist in unrelated consumers
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-105-P01
files:
  references:
    - supekku/scripts/lib/changes/creation.py
    - supekku/scripts/lib/changes/creation_test.py
  context:
    - supekku/scripts/lib/blocks/plan.py
entrance_criteria:
  - item: "DE-105, DR-105, and IP-105 reconciled to the issue"
    completed: true
  - item: "Impacted create_phase code and tests inspected"
    completed: true
exit_criteria:
  - item: "create_phase uses plan-aware numbering and convention selection"
    completed: true
  - item: "plan.overview updates do not append equivalent duplicate phases"
    completed: true
  - item: "targeted creation tests pass locally"
    completed: true
tasks:
  - id: "1"
    description: "Add normalization helpers for phase numbering and equivalence"
    status: completed
  - id: "2"
    description: "Update create_phase metadata lookup and plan mutation behavior"
    status: completed
  - id: "3"
    description: "Add or update regression tests for hyphenated and dotted plans"
    status: completed
```

# Phase 1 - Creation Path Repair

## Objective

Fix `create_phase()` so the phase it creates matches the plan it belongs to.

## Notes

- Preserve the current worktree's unrelated edits.
- Treat the plan overview as authoritative for phase sequence and metadata when
  it already contains phase entries.
- Verification:
  - `uv run pytest supekku/scripts/lib/changes/creation_test.py`
  - `uv run ruff check supekku/scripts/lib/changes/creation.py supekku/scripts/lib/changes/creation_test.py`
