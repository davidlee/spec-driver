---
id: mem.system.dispatch.architecture
name: Dispatch sub-agent orchestration
kind: memory
status: active
memory_type: system
created: '2026-04-16'
updated: '2026-04-16'
verified: '2026-04-16'
confidence: high
tags:
- dispatch
- skills
- sub-agents
- orchestration
summary: 'How /dispatch works: orchestrator skill + dispatch-worker agent + sub-driver tourist skill. Key constraints and design decisions.'
priority:
  severity: high
  weight: 8
scope:
  paths:
    - .spec-driver/skills/dispatch/SKILL.md
    - .spec-driver/skills/sub-driver/SKILL.md
    - .claude/agents/dispatch-worker.md
provenance:
  sources:
    - kind: delta
      ref: DE-132
    - kind: design_revision
      ref: DR-132
---

# Dispatch sub-agent orchestration

## Architecture

Three files, two roles:

| File | Role | Content |
|------|------|---------|
| `.spec-driver/skills/dispatch/SKILL.md` | Orchestrator skill (user-invocable) | Reads IP, batches tasks, assembles context, dispatches workers, reviews, merges |
| `.claude/agents/dispatch-worker.md` | Worker agent definition | System prompt, tools, model, permissionMode, skills: frontmatter |
| `.spec-driver/skills/sub-driver/SKILL.md` | Tourist skill (injected into worker) | Glossary, memory commands, governance boundaries |

## Key constraints

- **Workers are non-interactive** — cannot ask user questions
- **Workers don't commit** — leave changes in worktree; orchestrator merges
- **Workers don't write artefacts** — return structured summary only; orchestrator updates phase sheets/notes/verification
- **Workers don't get CLAUDE.md or .claude/rules/** — all context via agent body + injected skills + orchestrator prompt
- **Sequential by default** — parallelism only with positive evidence of disjointness
- **Verification commands mandatory** — orchestrator must provide from project config, worker doesn't guess

## Injected skills (via agent `skills:` frontmatter)

- `sub-driver` (~600 tokens) — glossary, memory commands, boundaries
- `retrieving-memory` (~885 tokens) — memory query patterns
- `capturing-memory` (~1254 tokens) — memory creation patterns
- Total: ~3k tokens injected at startup

## Design reference

Full design: [[DR-132]] (10 decisions, DEC-132-01 through DEC-132-10)
Delta: [[DE-132]] (in-progress, P03 VH tests pending)

## Pending work

- VH-001/002/003 deferred to first real use
- IMPR-028: phase sheet dispatch annotations for `/plan-phases`
- IMPR-029: per-skill agent target filtering
