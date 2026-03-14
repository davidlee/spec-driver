---
id: mem.signpost.spec-driver.skill-authoring
name: Skill authoring in spec-driver
kind: memory
status: active
memory_type: signpost
updated: "2026-03-07"
verified: "2026-03-07"
tags: [spec-driver, skills, workflow]
summary: "Start here before creating or refining spec-driver skills: boot, route early, keep packaged skills uniform, and use DE-055 as the current synthesis."
scope:
  commands:
    - uv run spec-driver install
    - uv run spec-driver create memory
  paths:
    - supekku/skills
    - .spec-driver/agents
    - .spec-driver/hooks
    - .spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance
provenance:
  sources:
    - kind: adr
      ref: ADR-004
    - kind: adr
      ref: ADR-005
    - kind: spec
      ref: PROD-016
    - kind: memory
      ref: mem.pattern.installer.boot-architecture
    - kind: delta
      ref: DE-055
---

# Skill authoring in spec-driver

## Summary

Start with `boot`, route through `using-spec-driver`, and treat packaged skills
as reusable procedural cores. Keep repo-specific behavior in generated agent
docs and hook files, not in per-project skill forks.

## Context

- Workflow canon: [[ADR-004]]
- Guidance hierarchy: [[ADR-005]]
- Generated vs user-owned customization model: [[PROD-016]]
- Boot/install projection model: [[mem.pattern.installer.boot-architecture]]
- Current synthesis and open questions: [[DE-055]]

Use the DE-055 guide first when you need the compressed working synthesis:
`.spec-driver/deltas/DE-055-tighten_skill_routing_and_boot_time_workflow_guidance/gpt-skill-authoring-reference.md`

## Start Here

1. Run `boot`.
2. Route through `using-spec-driver` before exploring.
3. Use `spec-driver` for entity and CLI work.
4. Retrieve memories before assuming local truth.
5. If the task changes skill workflow under a delta, ensure the needed
   `DE/DR/IP/phase` artifacts exist before editing.

## Guardrails

- Keep `spec-driver` narrow; do not turn it into a workflow meta-skill.
- Keep routing separate; early skill selection is the main useful import from
  Superpowers.
- Keep boot short and prescriptive.
- Descriptions should be trigger-only, not workflow summaries.
- Treat skills as testable guidance, not prose that merely sounds good.
- If local behavior differs by repo, prefer generated guidance or hooks over
  forking packaged skills.
