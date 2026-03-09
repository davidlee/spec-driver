---
id: ISSUE-047
name: 'Memory verification primitive: SHA-stamped attestation for staleness tracking'
created: '2026-03-09'
updated: '2026-03-09'
status: open
kind: issue
categories: [memory, traceability, verification]
severity: p2
impact: system
related:
- ISSUE-020
---

# Memory verification primitive: SHA-stamped attestation for staleness tracking

## Problem Statement

Spec-driver memories describe code, patterns, and conventions that evolve over time. Currently there is no mechanical way to assess whether a memory is still accurate — agents must re-read and reason about it every time, or trust blindly. Memories with `scope.paths` describe specific parts of the codebase, but there is no record of which codebase state they were validated against.

## Proposed Solution

Add a **verification primitive** to memory artifacts: when an agent attests that a memory is accurate, `spec-driver` stamps the current git HEAD SHA and timestamp into frontmatter. Combined with the memory's existing `scope.paths`, this enables mechanical staleness detection — count commits affecting scoped paths since the verified SHA.

### Mechanism

1. **`verified_sha`** (optional string) added to memory frontmatter schema
2. **`verified`** date field already exists; used alongside SHA
3. **`spec-driver edit memory <id> --verify`** — attestation only (content unchanged, SHA + date stamped)
4. **`spec-driver edit memory <id> --verify`** with content replacement — attestation + update
5. **New memories implicitly verified at creation** — `create memory` stamps SHA automatically
6. **`spec-driver list memories --stale`** — scope-aware staleness ranking using commit count since verified SHA

### Design Properties

- **Tool-enforced**: SHA comes from `git rev-parse HEAD` at write time, not agent-supplied
- **Scope-aware**: staleness computed against `scope.paths`, not globally
- **Minimal storage**: one SHA, one date — git provides history if needed
- **Trust model**: attestation, not proof — "an agent said this was accurate at commit X"

### Skill Integration

- `/retrieving-memory` and `/reviewing-memory` should consume staleness signals
- Scope calibration is skill-governed (choose the right scope, verify the memory entire or not at all)
- Unscoped memories require heavier reviewer burden — skills must account for this
- New memories are implicitly verified — skills should reinforce this expectation

### Relationship to ISSUE-020

This is a focused pilot of git SHA tracking for the memory subsystem specifically. If successful, the same mechanism has potential merit as a general-purpose frontmatter addition (ISSUE-020). The design should acknowledge future generalization without implementing it.

## Tensions

- Scope calibration is skill-governed, not tool-enforced — garbage-in-garbage-out if skills don't guide scope well
- Unscoped/widely-scoped memories can't participate in mechanical staleness — the skill layer must compensate
- "Verified" is agent attestation, not proof of correctness
