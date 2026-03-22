---
id: IP-103.PHASE-05
slug: "103-handover_and_review_orchestration-phase-05"
name: "IP-103 Phase 05 — Phase complete, bridges, continuation refit"
created: "2026-03-21"
updated: "2026-03-21"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-103.PHASE-05
plan: IP-103
delta: DE-103
objective: >-
  Implement phase complete command with auto-handoff, bridge block
  read/write support, and continuation skill refit to invoke CLI.
entrance_criteria:
  - Phase 04 complete (review commands working, 138 workflow tests passing)
exit_criteria:
  - phase complete marks phase done, emits handoff per policy/bridge
  - notes-bridge and phase-bridge blocks can be written and read
  - continuation skill invokes CLI for structured handoff
  - feature-gated by workflow/state.yaml presence
  - all tests passing, ruff clean
verification:
  tests:
    - VT-103-006 continuation skill
    - VT-103-007 bridge blocks
  evidence: []
tasks:
  - id: "5.1"
    summary: "phase complete command — mark phase done, auto-handoff"
  - id: "5.2"
    summary: "Bridge block reader — parse phase-bridge from phase sheets"
  - id: "5.3"
    summary: "Continuation skill refit — invoke CLI for structured handoff"
risks:
  - id: R1
    summary: "Continuation skill refit must be feature-gated"
    mitigation: "Detect workflow/state.yaml; preserve old behaviour when absent"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-103.PHASE-05
```

# Phase 05 — Phase complete, bridges, continuation refit

## 1. Objective

Implement `phase complete` command with auto-handoff emission, bridge block
support for notes.md and phase sheets, and continuation skill refit.

## 2. Links & References

- **Delta**: DE-103
- **DR sections**: DR-102 §5 (`phase complete`), §6 (continuation skill), §7 (bridge blocks)
- **Specs**: PROD-011

## 3. Entrance Criteria

- [x] Phase 04 complete (review commands working, 138 workflow tests passing)

## 4. Exit Criteria / Done When

- [x] `phase complete` marks phase done and emits handoff per policy/bridge
- [x] Phase-bridge block can be parsed from phase sheets
- [x] Notes-bridge block can be written by handoff/phase-complete
- [x] Continuation skill invokes CLI, feature-gated
- [x] All tests passing, ruff clean

## 5. Tasks & Progress

| Status | ID  | Description              | Notes                                                 |
| ------ | --- | ------------------------ | ----------------------------------------------------- |
| [x]    | 5.1 | `phase complete` command | 8 CLI tests — auto-handoff per policy and bridge      |
| [x]    | 5.2 | Bridge block I/O         | 13 tests — extract/render notes-bridge + phase-bridge |
| [x]    | 5.3 | Continuation skill refit | skill updated to invoke CLI; feature-gated            |

## 6. Design Decisions

- `phase complete` is a compound operation: (1) update phase status in state.yaml,
  (2) optionally emit handoff. Handoff emission triggered by bridge `handoff_ready: true`
  or policy `auto_handoff_on_phase_complete = true`.
- Bridge blocks are fenced YAML in markdown. Parsing uses existing block
  extraction infrastructure if available, or simple regex extraction.
- Continuation skill: detect `workflow/state.yaml`, invoke `spec-driver create handoff`
  via CLI. No silent fallback to prose-only mode per DR-102 §6.
