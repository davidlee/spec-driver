---
name: doctrine
description: "Loads project governance rules (ADRs, policies, standards, conventions) and checks current work against them. Use when starting a task, making architectural choices, or when unsure whether a decision aligns with accepted project decisions."
---

Read the project doctrine hook and apply governance constraints to the current task.

## Workflow

1. Read `@.spec-driver/hooks/doctrine.md` to load project-specific conventions.
2. List accepted ADRs, required policies, and required standards:
   - `uv run spec-driver list adrs -s accepted`
   - `uv run spec-driver list policies -s required`
   - `uv run spec-driver list standards -s required`
3. Read any ADR, policy, or standard that could apply to the current task.
4. Before proceeding, verify the planned approach does not violate:
   - Accepted architectural decisions (ADRs)
   - Required policies (e.g., code reuse, module boundaries)
   - Required standards (e.g., CLI patterns, lint governance)
   - Project conventions from the doctrine hook
5. If the current work conflicts with any governance artefact, stop and raise the conflict with the user before proceeding.

## Anti-patterns

- **Assumption**: acting without checking governance artefacts first.
- **Duplication**: reimplementing functionality that already exists (see POL-001).
- **Boundary violation**: coupling modules that should remain independent (see POL-003).
- **Guesswork**: making architectural choices without reading relevant ADRs.
