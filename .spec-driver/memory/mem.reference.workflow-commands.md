---
id: mem.reference.workflow-commands
name: Workflow orchestration CLI command reference
kind: memory
status: active
memory_type: pattern
created: '2026-03-21'
updated: '2026-03-21'
verified: '2026-03-21'
confidence: high
tags:
- workflow
- cli
summary: Quick reference for all workflow CLI commands, state transitions, and write ordering
scope:
  globs:
    - supekku/scripts/lib/workflow/**
    - supekku/cli/workflow.py
  commands:
    - phase start
    - phase complete
    - create handoff
    - accept handoff
    - review prime
    - review complete
    - review teardown
    - workflow status
    - block
    - unblock
provenance:
  sources:
    - "[[DR-102]]"
    - "[[DE-103]]"
---

# Workflow orchestration CLI command reference

## Commands

| Command | Effect | State transition |
|---------|--------|------------------|
| `spec-driver phase start <delta>` | Init `workflow/state.yaml`, update phase frontmatter to `in-progress` | planned → implementing |
| `spec-driver phase complete <delta>` | Update phase frontmatter to `completed`, mark state.yaml, auto-handoff | (phase frontmatter → completed, state.yaml → complete, optionally → awaiting_handoff) |
| `spec-driver create handoff <delta> --to <role>` | Write `handoff.current.yaml` | implementing/changes_requested → awaiting_handoff |
| `spec-driver accept handoff <delta> [--identity <name>]` | Claim + transition | awaiting_handoff → implementing/reviewing |
| `spec-driver review prime <delta>` | Generate `review-index.yaml` + `review-bootstrap.md` | (no state change) |
| `spec-driver review complete <delta> --status <status>` | Write `review-findings.yaml` | reviewing → changes_requested/approved |
| `spec-driver review teardown <delta>` | Delete reviewer state files | (no state change) |
| `spec-driver workflow status <delta>` | Display state | (read-only) |
| `spec-driver block <delta>` | Block workflow | * → blocked |
| `spec-driver unblock <delta>` | Restore previous state | blocked → (previous) |

## Key Patterns

- **Phase frontmatter sync** (DE-104): `phase start` and `phase complete` update phase sheet frontmatter (normative, lifecycle vocabulary: `in-progress`/`completed`) before `state.yaml` (transient, control-plane vocabulary: `in_progress`/`complete`). Two vocabularies for two domains.
- **Write ordering**: handoff first, then state. Findings first, then state. Frontmatter before state.yaml. Re-run safe.
- **Claim guard**: `accept handoff` checks `claimed_by`. Different identity → error. Same identity → idempotent.
- **Auto-teardown**: `review complete --status approved` deletes reviewer state per `[review].teardown_on` policy.
- **Phase-bridge**: Fenced YAML in phase sheets controls auto-handoff. `handoff_ready: false` suppresses.
- **Feature-gated**: All commands require `workflow/state.yaml`. Continuation skill detects presence.

## File Layout

```
workflow/
  state.yaml              # orchestration status
  handoff.current.yaml     # transition payload
  review-index.yaml        # reviewer bootstrap cache
  review-findings.yaml     # issue ledger
  review-bootstrap.md      # generated briefing
```

## Domain Modules

- `supekku/scripts/lib/workflow/state_machine.py` — 7 states, transition table
- `supekku/scripts/lib/workflow/state_io.py` — state.yaml read/write
- `supekku/scripts/lib/workflow/handoff_io.py` — handoff read/write/build
- `supekku/scripts/lib/workflow/review_io.py` — review-index + findings read/write/build
- `supekku/scripts/lib/workflow/staleness.py` — cache staleness evaluation
- `supekku/scripts/lib/workflow/bridge.py` — bridge block extraction/rendering
