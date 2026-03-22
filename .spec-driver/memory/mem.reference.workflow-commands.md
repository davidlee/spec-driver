---
id: mem.reference.workflow-commands
name: Workflow orchestration CLI command reference
kind: memory
status: active
memory_type: pattern
created: "2026-03-21"
updated: "2026-03-22"
verified: "2026-03-22"
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
    - review finding resolve
    - review finding defer
    - review finding waive
    - review finding supersede
    - review finding list
    - workflow status
    - block
    - unblock
provenance:
  sources:
    - "[[DR-102]]"
    - "[[DE-103]]"
    - "[[DR-109]]"
    - "[[DE-109]]"
    - "[[DE-108]]"
---

# Workflow orchestration CLI command reference

## Commands

| Command                                                  | Effect                                                                 | State transition                                                                      |
| -------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `spec-driver phase start <delta>`                        | Init `workflow/state.yaml`, update phase frontmatter to `in-progress`  | planned → implementing                                                                |
| `spec-driver phase complete <delta>`                     | Update phase frontmatter to `completed`, mark state.yaml, auto-handoff | (phase frontmatter → completed, state.yaml → complete, optionally → awaiting_handoff) |
| `spec-driver create handoff <delta> --to <role>`         | Write `handoff.current.yaml`                                           | implementing/changes_requested → awaiting_handoff                                     |
| `spec-driver accept handoff <delta> [--identity <name>]` | Claim + transition                                                     | awaiting_handoff → implementing/reviewing                                             |
| `spec-driver review prime <delta>`                       | Generate review-index + bootstrap; set judgment_status: in_progress    | (no state change; sets judgment_status in review-index)                               |
| `spec-driver review complete <delta> --status <status>`  | Write findings round; enforce can_approve() guard on approved          | reviewing → changes_requested/approved                                                |
| `spec-driver review teardown <delta>`                    | Delete reviewer state files                                            | (no state change)                                                                     |
| `spec-driver review finding resolve <delta> <id>`        | Disposition finding as fixed (--resolved-at optional)                  | (finding status → resolved)                                                           |
| `spec-driver review finding defer <delta> <id>`          | Defer finding (--rationale required, --backlog-ref optional)           | (finding status remains open)                                                         |
| `spec-driver review finding waive <delta> <id>`          | Waive finding (--rationale required, --authority optional)             | (finding status → waived)                                                             |
| `spec-driver review finding supersede <delta> <id>`      | Supersede finding (--superseded-by required)                           | (finding status → superseded)                                                         |
| `spec-driver review finding list <delta>`                | List all findings across rounds (--round N filter)                     | (read-only)                                                                           |
| `spec-driver workflow status <delta>`                    | Display state                                                          | (read-only)                                                                           |
| `spec-driver block <delta>`                              | Block workflow                                                         | \* → blocked                                                                          |
| `spec-driver unblock <delta>`                            | Restore previous state                                                 | blocked → (previous)                                                                  |

## Key Patterns

- **Phase frontmatter sync** (DE-104): `phase start` and `phase complete` update phase sheet frontmatter (normative, lifecycle vocabulary: `in-progress`/`completed`) before `state.yaml` (transient, control-plane vocabulary: `in_progress`/`complete`). Two vocabularies for two domains.
- **Write ordering**: handoff first, then state. Findings first, then state. Frontmatter before state.yaml. Re-run safe.
- **Claim guard**: `accept handoff` checks `claimed_by`. Different identity → error. Same identity → idempotent.
- **Approval guard** (DE-109): `review complete --status approved` enforces `can_approve()` — blocks on open blocking findings, agent-waived blockers, deferred-without-backlog blockers.
- **Judgment status** (DE-109): `review prime` writes `judgment_status: in_progress` to review-index. `review complete` updates it to the outcome status.
- **Auto-teardown**: `review complete --status approved` deletes reviewer state per `[review].teardown_on` policy.
- **Phase-bridge**: Fenced YAML in phase sheets controls auto-handoff. `handoff_ready: false` suppresses.
- **Feature-gated**: All commands require `workflow/state.yaml`. Continuation skill detects presence.
- **Structured JSON output** (DE-108): All review commands, finding disposition commands, `workflow status`, and `review finding list` accept `--format json`. JSON output uses a versioned envelope (`version`, `command`, `status`, `exit_code`, `data`/`error`). Exit codes: 0=success, 1=unexpected, 2=precondition, 3=guard_violation. Full 40-char SHA in JSON; short SHA in human output. Envelope helpers in `supekku/cli/common.py`: `cli_json_success()`, `cli_json_error()`, `emit_json_and_exit()`.

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
- `supekku/scripts/lib/workflow/review_state_machine.py` — review lifecycle enums, Pydantic models, transition table, guards
- `supekku/scripts/lib/workflow/staleness.py` — cache staleness evaluation
- `supekku/scripts/lib/workflow/bridge.py` — bridge block extraction/rendering
