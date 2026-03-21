---
id: IP-103.PHASE-03
slug: "103-handover_and_review_orchestration-phase-03"
name: Handoff commands
created: "2026-03-21"
updated: "2026-03-21"
status: in-progress
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

- [ ] `create handoff --to <role>` writes valid `handoff.current.yaml`
- [ ] `create handoff` transitions state: implementing/changes_requested → awaiting_handoff
- [ ] `create handoff` clears `claimed_by` in state.yaml
- [ ] `create handoff` assembles required_reading from delta bundle paths
- [ ] `create handoff` captures git state (head, branch, worktree)
- [ ] `accept handoff` transitions to implementing (non-reviewer) or reviewing (reviewer)
- [ ] `accept handoff` writes `claimed_by` with `--identity` or `$USER` default
- [ ] `accept handoff` is idempotent for same identity
- [ ] `accept handoff` fails with error for different identity (claim guard)
- [ ] Write ordering: handoff.current.yaml first, state.yaml second
- [ ] Re-run `create handoff` produces same end state
- [ ] Lint clean, all tests passing

## 5. Tasks & Progress

| Status | ID  | Description | Notes |
|--------|-----|-------------|-------|
| [ ] | T01 | Handoff I/O module | `handoff_io.py` — read/write with validation, atomic writes |
| [ ] | T02 | Create handoff domain logic | Payload assembly from state + git + paths |
| [ ] | T03 | CLI `create handoff` command | Under `create` group |
| [ ] | T04 | Accept handoff domain logic | Claim guard check + state transition |
| [ ] | T05 | CLI `accept handoff` command | Under `accept` group or top-level |
| [ ] | T06 | Tests | Handoff I/O, domain, CLI integration, claim guard |
| [ ] | T07 | Lint and verify | ruff clean, all tests pass |

## 6. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Hand-off notes to Phase 04
