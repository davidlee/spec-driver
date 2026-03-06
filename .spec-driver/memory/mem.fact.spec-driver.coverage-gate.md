---
id: mem.fact.spec-driver.coverage-gate
name: Delta Completion Coverage Gate
kind: memory
status: active
memory_type: fact
updated: '2026-03-03'
verified: '2026-03-03'
confidence: high
tags:
- spec-driver
- coverage
- verification
- delta
- completion
- sharp-edge
summary: complete delta requires verified parent-spec coverage for each delta requirement
  unless bypassed with force/disabled enforcement.
priority:
  severity: high
  weight: 10
scope:
  commands:
  - uv run spec-driver complete delta
  - complete delta
  paths:
  - supekku/scripts/lib/changes/coverage_check.py
  - supekku/scripts/complete_delta.py
  - supekku/cli/complete.py
provenance:
  sources:
  - kind: code
    note: Coverage enforcement switch and per-requirement checks
    ref: supekku/scripts/lib/changes/coverage_check.py
  - kind: code
    note: Completion orchestration and force/env bypass behavior
    ref: supekku/scripts/complete_delta.py
  - kind: code
    note: Canonical coverage status enum
    ref: supekku/scripts/lib/blocks/verification.py
---

# Delta Completion Coverage Gate

## Rule

`uv run spec-driver complete delta DE-XXX` checks each requirement in
`delta.applies_to.requirements` against the parent spec coverage block.

Normal completion requires:
- parent spec exists
- `supekku:verification.coverage@v1` block exists
- requirement entry exists in that block
- entry status is `verified`

## Default and Bypass

- Enforcement default: enabled (`SPEC_DRIVER_ENFORCE_COVERAGE=true` by default)
- Bypass 1: `--force` on completion command
- Bypass 2: `SPEC_DRIVER_ENFORCE_COVERAGE=false`

Bypass paths are non-canonical and should be documented with follow-up work.

## Valid Coverage Statuses

- `planned`
- `in-progress`
- `verified`
- `failed`
- `blocked`

## Common Failure Mode

Agents update implementation and phase/checklist items, then hit a late failure
on `complete delta` because parent spec coverage blocks were never populated to
`verified`.

Use [[mem.pattern.spec-driver.delta-completion]] as the close-out checklist.
