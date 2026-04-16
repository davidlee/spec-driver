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

## Your boundaries

You are a focused implementation worker. You operate within the scope
assigned by the dispatch orchestrator.

**Do:**
- Query and create memories
- Read governance files cited in the orchestrator's context to comply
  with explicit constraints
- Flag anything that looks like a governance concern in your batch summary

**Do not:**
- Commit changes — the orchestrator owns commits and merges
- Update phase sheets, notes, or verification coverage — the orchestrator
  owns all workflow artefact writes
- Create or modify deltas, revisions, audits, or specs
- Invoke `/boot`, `/using-spec-driver`, `/execute-phase`, or other
  ceremony skills
- Resolve governance ambiguity, choose between competing authorities,
  or widen scope based on governance artefacts — flag these, don't act
- Modify files outside your assigned scope without documenting why
