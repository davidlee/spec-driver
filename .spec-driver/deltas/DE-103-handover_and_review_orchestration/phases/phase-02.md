---
id: IP-103.PHASE-02
slug: "103-handover_and_review_orchestration-phase-02"
name: State machine and core commands
created: "2026-03-21"
updated: "2026-03-21"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-103.PHASE-02
plan: IP-103
delta: DE-103
objective: >-
  Implement the 7-state workflow state machine with explicit CLI-driven
  transitions, core CLI commands (phase start, workflow status, block/unblock),
  state.yaml reading/writing with schema validation, and workflow.toml config
  loader extensions for [workflow] and [review] sections.
entrance_criteria:
  - Phase 01 complete (schemas registered)
exit_criteria:
  - State machine module with all 7 states and transitions per DR-102 §4
  - state.yaml writer validates output against schema before writing
  - state.yaml reader loads and validates existing state
  - CLI phase start initialises workflow/state.yaml (planned → implementing)
  - CLI workflow status reads state.yaml and prints human-readable summary
  - CLI block/unblock transitions to/from blocked (previous state preserved)
  - workflow.toml config loader supports [workflow] and [review] sections
  - All transitions reject invalid source states
  - Lint clean, tests passing
verification:
  tests:
    - VT-103-002 state machine transition tests
    - VT-103-003 CLI command output and state transition tests (partial — phase start, workflow status, block/unblock)
  evidence: []
tasks:
  - id: T01
    description: Create supekku/scripts/lib/workflow/ package — state machine module
  - id: T02
    description: Create state.yaml reader/writer with schema validation
  - id: T03
    description: Extend workflow.toml config loader with [workflow] and [review] defaults
  - id: T04
    description: CLI command — phase start
  - id: T05
    description: CLI command — workflow status
  - id: T06
    description: CLI commands — block / unblock
  - id: T07
    description: Tests for state machine, reader/writer, CLI commands
  - id: T08
    description: Lint and verify
risks:
  - description: CLI command routing may conflict with existing `create phase` command
    mitigation: New `phase` and `workflow` are separate Typer groups — no collision with `create phase`
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-103.PHASE-02
```

# Phase 02 — State machine and core commands

## 1. Objective

Implement the workflow state machine (7 states, explicit CLI-driven transitions)
and the core CLI commands that mutate or read workflow state: `phase start`,
`workflow status`, `block`/`unblock`. This includes state.yaml file I/O with
schema validation and workflow.toml config loader extensions.

## 2. Links & References

- **Delta**: DE-103
- **Design Revision**: DR-102 §4 (state machine), §5 (CLI commands), §9 (workflow.toml config)
- **Specs**: PROD-011
- **Existing code**: `supekku/scripts/lib/blocks/workflow_metadata.py` (Phase 01 schemas)

## 3. Entrance Criteria

- [x] Phase 01 complete (all 7 schemas defined and registered)

## 4. Exit Criteria / Done When

- [x] State machine module implements all 7 states and transitions from DR-102 §4
- [x] Invalid transitions are rejected with clear errors
- [x] `state.yaml` writer validates output against `WORKFLOW_STATE_METADATA` before writing
- [x] `state.yaml` reader loads and validates existing state files
- [x] Atomic writes (write-to-temp + rename) for state.yaml
- [x] `spec-driver phase start` initialises `workflow/state.yaml` (planned → implementing)
- [x] `spec-driver workflow status` reads and renders human-readable summary
- [x] `spec-driver block` / `spec-driver unblock` transitions to/from blocked
- [x] `unblock` restores previous state (saved in state.yaml)
- [x] `workflow.toml` loader has `[workflow]` and `[review]` section defaults
- [x] Lint clean, all tests passing

## 5. Verification

- `uv run pytest supekku/scripts/lib/workflow/ -v`
- `uv run pytest supekku/cli/workflow_test.py -v` (or wherever CLI tests land)
- `uv run ruff check supekku/scripts/lib/workflow/ supekku/cli/workflow.py`
- Manual: `uv run spec-driver phase start` / `uv run spec-driver workflow status` against a test delta

## 6. Assumptions & STOP Conditions

- Assumptions:
  - The `MetadataValidator` from Phase 01 is sufficient for validating state.yaml output
  - New CLI command groups (`phase`, `workflow`) coexist with existing `create phase` command
  - `block`/`unblock` are top-level commands (DR-102 §5 table)
- STOP when: CLI routing conflict with existing commands (consult before proceeding)

## 7. Tasks & Progress

| Status | ID  | Description                                                    | Notes                                                                         |
| ------ | --- | -------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| [x]    | T01 | Create `supekku/scripts/lib/workflow/` package — state machine | `state_machine.py` — 7 states, transition table, claim guard                  |
| [x]    | T02 | State.yaml reader/writer with validation                       | `state_io.py` — atomic writes, MetadataValidator, init/update helpers         |
| [x]    | T03 | Extend `workflow.toml` config loader                           | Already done — `[workflow]` + `[review]` in DEFAULT_CONFIG + section comments |
| [x]    | T04 | CLI `phase start` command                                      | `phase_app` group in `workflow.py`; auto-discovers plan/phase                 |
| [x]    | T05 | CLI `workflow status` command                                  | `workflow_app` group; human-readable output                                   |
| [x]    | T06 | CLI `block` / `unblock` commands                               | Top-level via main.py; previous-state preservation                            |
| [x]    | T07 | Tests                                                          | 25 state machine + 22 state I/O + 19 CLI = 66 tests                           |
| [x]    | T08 | Lint and verify                                                | ruff clean, all tests pass                                                    |

## 8. Risks & Mitigations

| Risk                                                          | Mitigation                                                  | Status |
| ------------------------------------------------------------- | ----------------------------------------------------------- | ------ |
| CLI routing conflict with `create phase`                      | `phase start` is a separate Typer group from `create phase` | open   |
| MetadataValidator may not validate all state.yaml constraints | Command-level validation supplements schema validation      | open   |

## 9. Decisions & Outcomes

- 2026-03-21 — `workflow.py` CLI delegates directly to `state_machine.py` and
  `state_io.py`. The other agent created an `operations.py` domain layer
  (skinny CLI pattern) but it's unused — kept for potential future refactor.
- 2026-03-21 — `previous_state` field added to workflow.state schema metadata
  to support block/unblock persistence.
- 2026-03-21 — `phase start` auto-discovers the latest phase by sorting
  `phases/phase-*.md` numerically. `--phase` override available.
- 2026-03-21 — `block`/`unblock` registered as top-level commands per DR-102 §5.
  Also available under `workflow` group.
- 2026-03-21 — Config loader already had `[workflow]` and `[review]` sections
  with correct defaults — no additional work needed (T03).

## 10. Findings / Research Notes

- Two agents ran concurrently on Phase 02 — other agent created `operations.py`,
  modified `main.py`, `workflow_metadata.py`, `config.py`. Changes were
  complementary; merged cleanly.
- `flake.lock`/`flake.nix` had unrelated changes from the other session — left
  as-is (not Phase 02 scope).

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (66 tests, lint clean)
- [x] Notes updated
- [ ] Hand-off notes to Phase 03
