---
id: mem.pattern.phase.contract-vs-progress
name: Phase contract vs progress separation
kind: memory
status: active
memory_type: pattern
created: "2026-03-22"
updated: "2026-03-22"
verified: "2026-03-22"
confidence: high
tags: [phase, frontmatter, dr-106, contract]
summary: >-
  Frontmatter records planning contract; markdown checkboxes track execution
  progress. Never conflate in structured data.
scope:
  globs:
    - supekku/scripts/lib/changes/phase_model.py
    - supekku/templates/phase.md
    - "**/.spec-driver/deltas/*/phases/*.md"
provenance:
  sources:
    - kind: delta
      note: DR-106 DEC-006 — contract vs progress split
      ref: DE-106
    - kind: adr
      note: ADR-010 — placement heuristic
      ref: ADR-010
---

# Phase contract vs progress separation

## Summary

Phase frontmatter carries the **planning contract** — what must be true.
Markdown body checkboxes track **execution progress** — whether it is true yet.

## Rule

- **Frontmatter** (structured): `plan`, `delta`, `objective`, `entrance_criteria`, `exit_criteria`
- **Markdown body** (prose): task tables, checkbox progress, research notes, decisions
- **No structured progress tracking in YAML.** If orchestration later needs machine-readable progress, model it deliberately — don't recover by reinstating blocks.

## Why

The `phase.tracking` block conflated "what must be true" with "is it true yet" by attaching `completed: true/false` to each criterion. This forced agents to maintain structured YAML for volatile progress state — the core authoring tax that DE-106 eliminated.

## See also

- [[DR-106]] §3a field analysis, DEC-006
- [[ADR-010]] placement heuristic
- [[mem.pattern.phase.canonical-fields]] canonical field set
