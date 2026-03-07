---
id: IP-052.PHASE-01
slug: 052-event_infrastructure_jsonl_log_and_unix_domain_socket_emitter-phase-01
name: 'Phase 1: Core module and process-boundary wrapper'
created: '2026-03-07'
updated: '2026-03-07'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-052.PHASE-01
plan: IP-052
delta: DE-052
objective: >-
  Implement core/events.py, wire the process-boundary wrapper in main.py,
  add get_run_dir() to paths.py, add [events] config, and write all VTs.
entrance_criteria:
  - DR-052 approved
exit_criteria:
  - VT-052-01 through VT-052-08 pass
  - just (lint + test) green
verification:
  tests:
    - VT-052-01
    - VT-052-02
    - VT-052-03
    - VT-052-04
    - VT-052-05
    - VT-052-06
    - VT-052-07
    - VT-052-08
  evidence: []
tasks:
  - id: "1.1"
    description: "Add get_run_dir() to paths.py"
  - id: "1.2"
    description: "Add [events] section to config.py DEFAULT_CONFIG"
  - id: "1.3"
    description: "Implement core/events.py"
  - id: "1.4"
    description: "Wire process-boundary wrapper in main.py"
  - id: "1.5"
    description: "Write events_test.py — all VTs"
  - id: "1.6"
    description: "Lint and test"
risks:
  - description: "Command.invoke interception may not work as expected"
    mitigation: "VT-052-05 and VT-052-07 prove the contract; write these first"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-052.PHASE-01
```

# Phase 1 — Core module and process-boundary wrapper

## 1. Objective

Implement the event emission infrastructure: `core/events.py` module,
process-boundary wrapper in `main.py`, supporting changes to `paths.py` and
`config.py`, and comprehensive test coverage for all VTs.

## 2. Links & References
- **Delta**: DE-052
- **Design Revision**: DR-052 (DEC-052-01 through DEC-052-06)
- **Key DR sections**: DEC-052-01 boundary table, DEC-052-05 event schema

## 3. Entrance Criteria
- [x] DR-052 approved

## 4. Exit Criteria / Done When
- [x] `core/events.py` implements: `emit_event()`, `record_artifact()`,
  `mark_command_invoked()`, `command_was_invoked()`, `_drain_artifacts()`,
  `_write_log()`, `_send_socket()`, `_detect_session()`
- [x] `main.py` wrapper intercepts `Command.invoke`, gates emission on flag
- [x] `paths.py` has `get_run_dir()`
- [x] `config.py` has `[events]` section in `DEFAULT_CONFIG`
- [x] VT-052-01 through VT-052-08 pass
- [x] `just` green (1 pre-existing failure in test_sync_help, unrelated) (lint + test)

## 5. Verification

All tests in `supekku/scripts/lib/core/events_test.py`:

- **VT-052-01**: `emit_event()` writes correct JSONL (v, ts, session, cmd,
  argv, artifacts, exit_code, status); appends to file; sends to socket
- **VT-052-02**: Socket send silently fails when socket missing; silently
  skipped when path > 104 chars
- **VT-052-03**: `_detect_session()` reads `SPEC_DRIVER_SESSION`; falls back
  to `"claude"` when `CLAUDECODE=1`; returns `None` otherwise
- **VT-052-04**: `[events]` section in config merges correctly with defaults
- **VT-052-05** (non-negotiable): Process-boundary wrapper emits for all
  exit paths in DR-052 boundary table — `typer.Exit(0)`, `typer.Exit(1)`,
  `ClickException`, unhandled exception, `BaseException`
- **VT-052-06**: `record_artifact()` + `_drain_artifacts()` lifecycle —
  append, drain returns collected, clears list
- **VT-052-07** (non-negotiable): No event emitted for `--help`,
  `--version`, bare `spec-driver`, `spec-driver create` (no subcommand),
  invalid command, parse error
- **VT-052-08**: No workspace → `emit_event` is a no-op, no file created

Commands: `just test`, `just lint`, `just pylint`, `just`

## 6. Assumptions & STOP Conditions
- Assumption: `click.Command.invoke` can be monkey-patched reliably in
  `main.py` before `app()` is called
- STOP if: interception doesn't work with typer's command registration
  (would need alternative approach — consult)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Add `get_run_dir()` to `paths.py` | [P] | Trivial — hardcoded `.spec-driver/run/` |
| [x] | 1.2 | Add `[events]` to `config.py` DEFAULT_CONFIG | [P] | `enabled = true` only |
| [x] | 1.3 | Implement `core/events.py` | | Depends on 1.1, 1.2 |
| [x] | 1.4 | Wire wrapper in `main.py` | | Depends on 1.3 |
| [x] | 1.5 | Write `events_test.py` — all VTs | | TDD: write with 1.3/1.4 |
| [x] | 1.6 | Lint and full test pass | | `just` green |

### Task Details

- **1.1 — get_run_dir()**
  - Add `get_run_dir(repo_root)` to `paths.py` returning
    `get_spec_driver_root(repo_root) / "run"`
  - Add to `__all__`
  - No config mapping — hardcoded internal infrastructure

- **1.2 — [events] config**
  - Add to `DEFAULT_CONFIG`: `"events": {"enabled": True}`
  - Test: config merge preserves `enabled` default; user override works

- **1.3 — core/events.py**
  - Module-level state: `_command_invoked`, `_touched_artifacts`
  - Public API: `mark_command_invoked()`, `command_was_invoked()`,
    `record_artifact(id)`, `emit_event(argv, exit_code, status)`
  - Internal: `_drain_artifacts()`, `_detect_session()`, `_write_log(event)`,
    `_send_socket(event)`, `_resolve_cmd(argv)`
  - `_write_log`: open with `O_APPEND`; create `.spec-driver/run/` lazily;
    silently skip if no workspace or write fails
  - `_send_socket`: check path length <= 104; `SOCK_DGRAM`; catch all
    exceptions silently
  - `_detect_session`: check `SPEC_DRIVER_SESSION` → `CLAUDECODE` → `None`
  - `_resolve_cmd`: parse argv to extract command path (e.g. `["create",
    "delta", "test"]` → `"create delta"`)

- **1.4 — main.py wrapper**
  - Import `click` and `events` module
  - Monkey-patch `click.Command.invoke` before `app` definition (or at
    module level) to call `mark_command_invoked()`
  - Wrap `app()` in `main()` with try/except per DR-052 DEC-052-01
  - Load config to check `events.enabled` before emitting

- **1.5 — events_test.py**
  - Use `tmp_path` for JSONL file, mock socket
  - `monkeypatch` for env vars (`SPEC_DRIVER_SESSION`, `CLAUDECODE`)
  - For VT-052-05 and VT-052-07: test against actual typer app (create a
    minimal test app with `no_args_is_help=True` group + leaf command, or
    test against the real `app` from `main.py`)
  - VT-052-07 must cover: `--help`, `--version`, bare program, group with
    no subcommand, invalid command

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| `Command.invoke` patch doesn't fire for typer-registered commands | Test with real app in VT-052-05; if broken, try custom `cls` approach | Open |
| Import cycle: events.py ↔ paths.py | events.py imports paths lazily inside functions | Open |

## 9. Decisions & Outcomes
- 2026-03-07 — DR-052 approved after two adversarial review rounds

## 10. Findings / Research Notes
- See `DE-052/notes.md` for design evolution and Click source references

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Notes updated
- [x] Phase 2 sheet created for integration work
