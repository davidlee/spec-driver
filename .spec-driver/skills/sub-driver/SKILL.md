---
name: sub-driver
description: >
  Lightweight spec-driver fluency for dispatch workers. Provides the minimum
  vocabulary, commands, and boundaries needed to navigate a spec-driver project
  without full boot ceremony. Loaded via skills: frontmatter in dispatch-worker
  agent definition.
---

Read `.spec-driver/agents/exec.md` for invocation conventions.

## Glossary

| Term | Meaning |
|------|---------|
| DE-xxx | Delta — a scoped change bundle |
| DR-xxx | Design revision — architecture patch for a delta |
| IP-xxx | Implementation plan — phased execution plan |
| Phase (IP-xxx-P0N) | One phase of an IP, with tasks and exit criteria |
| FR-xxx | Functional requirement (behavioural, testable) |
| NF-xxx | Non-functional requirement (quality: perf, reliability) |
| VT | Verification Test — automated test proving functionality |
| VA | Verification by Agent — agent-generated test report or analysis |
| VH | Verification by Human — manual verification requiring user sign-off |

## Spec-driver commands you may use

### Memories

Query before touching unfamiliar files:
```
spec-driver list memories -p <file-path> [-c "<command context>"] [--match-tag <tag>]
```

View a memory:
```
spec-driver view memory <memory-id>
```

Create a memory for durable findings:
```
spec-driver create memory "<name>" --type <fact|pattern|gotcha> [--summary "..."] [--tag ...]
```

### Phase sheet updates

Phase sheets are markdown files with YAML frontmatter. Update task status
by editing the task table directly (status column: `[ ]`, `[WIP]`, `[x]`,
`[blocked]`).

Append findings to the phase sheet's "Findings / Research Notes" section
or to the delta's `notes.md`.

### Finding your artefacts

```
spec-driver find card <delta-id>
```

## Your boundaries

You are a focused implementation worker. You operate within the scope
assigned by the dispatch orchestrator.

**Do:**
- Query and create memories
- Update phase sheet task statuses and notes
- Read governance files if the orchestrator's context mentions them
- Flag anything that looks like a governance concern (ADR/policy/standard
  territory) in your batch summary

**Do not:**
- Create or modify deltas, revisions, audits, or specs
- Invoke `/boot`, `/using-spec-driver`, `/execute-phase`, or other
  ceremony skills
- Make governance decisions — flag them, don't resolve them
- Modify files outside your assigned scope without documenting why
