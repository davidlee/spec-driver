---
id: mem.pattern.skills.memory-retrieval-and-wrapup
name: Scoped memory retrieval and wrap-up capture
kind: memory
status: active
memory_type: pattern
updated: '2026-03-08'
verified: '2026-03-08'
tags: [skills, memory, workflow, retrieval, close-out]
summary: Before touching a subsystem, query memories with concrete file paths so glob-scoped records surface; during phase
  or delta wrap-up, promote durable findings into memories.
priority:
  severity: high
  weight: 8
scope:
  commands: [uv run spec-driver list memories, uv run spec-driver complete delta]
  paths:
  - supekku/skills/retrieving-memory/SKILL.md
  - supekku/skills/execute-phase/SKILL.md
  - supekku/skills/notes/SKILL.md
  - supekku/skills/capturing-memory/SKILL.md
  - supekku/skills/close-change/SKILL.md
provenance:
  sources:
  - kind: adr
    ref: ADR-005
  - kind: delta
    ref: DE-055
  - kind: doc
    note: Phase 10 follow-up notes
    ref: .spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/phases/phase-10.md
---

# Scoped memory retrieval and wrap-up capture

## Summary

- Before touching a subsystem, run `spec-driver list memories -p <concrete-file>...`
  so memories scoped by `scope.globs` can surface through those file paths.
- During execution, keep an eye out for durable facts, patterns, and gotchas.
- Before wrapping a phase or delta, review notes and findings and promote the
  reusable ones into a memory record instead of leaving them buried in notes.

## Context

- This is the skill-layer answer to the memory-effectiveness gap captured in
  `DE-055` phase 10.
- It does not replace a future runtime hook for proactive surfacing on every
  file read/write; it defines the current manual workflow.

## Procedure

- Pre-work retrieval:
  `uv run spec-driver list memories -p <target-file> -c "<planned command>" --match-tag <domain>`
- Execution:
  if a work unit reveals a durable invariant, workflow, or gotcha, note it and
  capture or maintain the memory before treating the unit as complete.
- Wrap-up:
  before `uv run spec-driver complete delta DE-XXX`, review `notes.md`, phase
  findings, and audit outputs for reusable guidance and record it.
