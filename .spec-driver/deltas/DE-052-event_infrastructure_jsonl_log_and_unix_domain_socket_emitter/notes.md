# Notes for DE-052

## DR-052 approval — 2026-03-07

Design approved after two rounds of adversarial review (13 findings total,
all resolved).

**Residual risk accepted at approval**: DEC-052-01 depends on intercepting
`click.Command.invoke`. This is the sharpest edge in the design — most
likely to break on future Click/Typer upgrades. VT-052-05 (all exit paths)
and VT-052-07 (help/no-args exclusion) are **non-negotiable regression
coverage**. They must prove the interception contract exactly as specified
in the DR boundary table, and must break loudly if Click changes the
`Command.invoke` dispatch path.

## Design evolution

1. **v1 (initial)**: `result_callback` on typer app — found unsound (all
   commands use `raise typer.Exit()`, bypassing callback entirely)
2. **v2 (post-review round 1)**: process-boundary try/except in `main()`,
   `sys.argv` heuristic for help exclusion — found to misclassify nested
   group `no_args_is_help` paths
3. **v3 (approved)**: process-boundary try/except gated by
   `_command_invoked` flag set via `Command.invoke` interception —
   correctly handles all help/parse/completion paths

## Key references from review

- Click `Command.invoke` at core.py:1232 — leaf command callback invocation
- Click `Group.parse_args` at core.py:1803 — `NoArgsIsHelpError` raised
  before invoke for `no_args_is_help=True` groups
- Click `BaseCommand.main` at core.py:1380-1426 — exception → `sys.exit()`
  conversion (all paths end in SystemExit in standalone mode)
- 306 instances of `raise typer.Exit()` across CLI files, zero normal returns

## New agent onboarding

You are implementing DE-052: structured event emission for the spec-driver CLI.

### What this delta does

Every leaf-command CLI invocation (e.g. `spec-driver create delta "foo"`)
emits a JSONL event to `.spec-driver/run/events.jsonl` and fire-and-forgets a
UDP datagram to `.spec-driver/run/tui.sock`. Help, completion, and parse-error
paths do not emit. This enables a future TUI (IMPR-009) to follow agent
activity in real time.

### Read these first (in order)

1. **DE-052.md** — scope, objectives, schema, acceptance criteria
2. **DR-052.md** — the approved design. Pay special attention to:
   - DEC-052-01: the process-boundary wrapper and `_command_invoked` flag
     (this is the core mechanism and the sharpest edge)
   - DEC-052-05: the v1 event schema
   - DEC-052-03: session attribution via `startup.sh`
3. **IP-052.md** — phase plan. You're executing Phase 1 or Phase 2.
4. **phases/phase-01.md** or **phases/phase-02.md** — your active phase
   sheet with tasks, exit criteria, and verification expectations

### Architecture in one paragraph

`core/events.py` owns all emission logic (JSONL write, socket send, session
detection, artifact collection). `cli/main.py` monkey-patches
`click.Command.invoke` to set a `_command_invoked` flag, then wraps `app()`
in try/except to emit at the process boundary — but only if the flag is set.
This correctly excludes all help/no-args/parse/completion paths because they
never reach `Command.invoke`. `record_artifact()` in `events.py` lets
domain-layer creation functions enrich events with artifact IDs. The
`startup.sh` hook extracts Claude Code's `session_id` from stdin JSON and
exports it as `SPEC_DRIVER_SESSION` via `CLAUDE_ENV_FILE`.

### Critical constraints

- **Stdlib only** — no new runtime dependencies
- **Fail-silent** — event emission errors must never cause a CLI command to fail
- **VT-052-05 and VT-052-07 are non-negotiable** — they prove the
  `Command.invoke` interception contract and must break loudly on
  Click/Typer changes

### Things that went wrong during design (so you don't repeat them)

1. `result_callback` doesn't work — every command exits via
   `raise typer.Exit()`, which bypasses it entirely
2. `sys.argv` heuristics for help detection fail — nested groups with
   `no_args_is_help=True` (e.g. `spec-driver create`) look like real
   commands in argv but are help paths
3. `"interrupted"` status is undetectable — Click converts
   `KeyboardInterrupt` → `Abort` → `sys.exit(1)` before the wrapper sees it

### Relevant memories

- `mem.pattern.events.cli-middleware` — the process-boundary wrapper pattern
- `mem.pattern.cli.skinny` — why emission is centralised, not per-command
