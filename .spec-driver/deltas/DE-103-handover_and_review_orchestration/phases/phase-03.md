---
id: IP-103.PHASE-03
slug: "103-handover_and_review_orchestration-phase-03"
name: Handoff commands
created: "2026-03-21"
updated: "2026-03-21"
status: done
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-103.PHASE-03
plan: IP-103
delta: DE-103
objective: >-
  Implement create handoff and accept handoff CLI commands with claim guard,
  handoff payload assembly, and write-ordering per DR-102 §4/§5.
entrance_criteria:
  - Phase 02 complete (state machine, state I/O, core CLI commands)
exit_criteria:
  - create handoff writes handoff.current.yaml and transitions state to awaiting_handoff
  - create handoff assembles payload from state, phase, notes, git state
  - create handoff clears claimed_by (new handoff resets claim)
  - accept handoff transitions to implementing or reviewing based on to_role
  - accept handoff writes claimed_by with identity (claim guard)
  - accept handoff is idempotent for same identity
  - accept handoff fails if already claimed by different identity
  - Write ordering correct (handoff first, then state)
  - Re-run safety — idempotent end state
  - Lint clean, tests passing
verification:
  tests:
    - VT-103-003 CLI command output and state transition tests (create/accept handoff)
    - VT-103-004 Claim guard tests
    - VT-103-008 Write ordering and re-run safety
  evidence: []
tasks:
  - id: T01
    description: Implement handoff I/O module (read/write handoff.current.yaml)
  - id: T02
    description: Implement create handoff domain logic (payload assembly)
  - id: T03
    description: CLI create handoff command
  - id: T04
    description: Implement accept handoff domain logic (claim guard + transition)
  - id: T05
    description: CLI accept handoff command
  - id: T06
    description: Tests for handoff I/O, domain logic, CLI commands
  - id: T07
    description: Lint and verify
risks:
  - description: Handoff payload assembly requires git state — tests need subprocess mocking
    mitigation: Use existing git.py helpers; mock at subprocess level in tests
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-103.PHASE-03
```

# Phase 03 — Handoff commands

## 1. Objective

Implement `create handoff` and `accept handoff` CLI commands per DR-102 §4/§5.
`create handoff` assembles a structured payload from current workflow state and
writes `handoff.current.yaml`, transitioning to `awaiting_handoff`. `accept
handoff` claims the handoff with identity-based guard and transitions to
`implementing` or `reviewing` based on `to_role`.

## 2. Links & References

- **Delta**: DE-103
- **Design Revision**: DR-102 §3.2 (handoff schema), §4 (state machine — claim guard), §5 (CLI commands — write ordering)
- **Phase 02 code**: `supekku/scripts/lib/workflow/`, `supekku/cli/workflow.py`

## 3. Entrance Criteria

- [x] Phase 02 complete (state machine, state I/O, core CLI)

## 4. Exit Criteria / Done When

- [x] `create handoff --to <role>` writes valid `handoff.current.yaml`
- [x] `create handoff` transitions state: implementing/changes_requested → awaiting_handoff
- [x] `create handoff` clears `claimed_by` in state.yaml
- [x] `create handoff` assembles required_reading from delta bundle paths
- [x] `create handoff` captures git state (head, branch, worktree)
- [x] `accept handoff` transitions to implementing (non-reviewer) or reviewing (reviewer)
- [x] `accept handoff` writes `claimed_by` with `--identity` or `$USER` default
- [x] `accept handoff` is idempotent for same identity
- [x] `accept handoff` fails with error for different identity (claim guard)
- [x] Write ordering: handoff.current.yaml first, state.yaml second
- [x] Re-run `create handoff` produces same end state
- [x] Lint clean, all tests passing

## 5. Tasks & Progress

| Status | ID  | Description | Notes |
|--------|-----|-------------|-------|
| [x] | T01 | Handoff I/O module | `handoff_io.py` — read/write/build with validation, atomic writes |
| [x] | T02 | Create handoff domain logic | Payload assembly from state + git + paths in `workflow.py` |
| [x] | T03 | CLI `create handoff` command | Under `create` group, delegates to `workflow.create_handoff_command` |
| [x] | T04 | Accept handoff domain logic | Claim guard + transition in `workflow.py` |
| [x] | T05 | CLI `accept handoff` command | Under `accept` group via `accept_app` |
| [x] | T06 | Tests | 14 handoff I/O + 16 CLI = 30 tests |
| [x] | T07 | Lint and verify | ruff clean, 96 total workflow tests pass |

## 6. Decisions & Outcomes

- 2026-03-21 — `create handoff` registered as subcommand of `create` group
  (thin wrapper in `create.py` → delegates to `workflow.create_handoff_command`)
- 2026-03-21 — `accept handoff` registered under new `accept_app` Typer group
- 2026-03-21 — Git helpers `get_branch`, `has_uncommitted_changes`,
  `has_staged_changes` added to `supekku/scripts/lib/core/git.py`
- 2026-03-21 — `build_handoff` infers `next_activity_kind = "review"` when
  `to_role == "reviewer"`, defaults to `"implementation"` otherwise
- 2026-03-21 — `accept handoff` marks the handoff transition status as
  `"accepted"` but suppresses validation errors (state is authoritative)

## 7. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (30 new tests, 96 total workflow tests)
- [x] Notes updated
- [ ] Hand-off notes to Phase 04
