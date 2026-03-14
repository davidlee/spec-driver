---
id: mem.pattern.events.cli-middleware
name: Event emission via process-boundary wrapper
kind: memory
status: active
memory_type: pattern
created: "2026-03-07"
updated: "2026-03-07"
tags:
  - architecture
  - events
  - cli
summary: CLI event emission uses a process-boundary wrapper in main() to emit
  events after every command, rather than scattering explicit emit_event() calls
  in each command function. result_callback is unsound because all commands exit
  via raise typer.Exit(), which bypasses it.
---

# Event emission via process-boundary wrapper

## Summary

CLI event emission wraps `app()` in `main()` with try/except to capture all
exit paths. This is the only reliable hook point because every command in the
codebase exits via `raise typer.Exit()` (306 instances, zero normal returns),
and Click's `result_callback` only fires on normal return.

## Pattern

Two mechanisms work together:

1. **Command-invocation flag**: `Command.invoke` is intercepted to set
   `_command_invoked = True` when a leaf command body runs. Help paths,
   no-args-is-help on groups, parse errors, and completion never reach
   `Command.invoke`, so the flag stays `False`.

2. **Process-boundary wrapper**: `main()` wraps `app()` with try/except.
   Only emits if the flag is set.

```python
# In cli/main.py
click.Command.invoke = _tracking_invoke  # sets mark_command_invoked()

def main() -> None:
    try:
        app()
    except SystemExit as exc:
        if command_was_invoked():
            _emit(sys.argv, exc.code)
        raise
    except BaseException:
        if command_was_invoked():
            _emit(sys.argv, 1)
        raise
```

Artifact enrichment is opt-in via `record_artifact()` calls in domain-layer
creation functions (not CLI commands).

## Why not result_callback

Click's `result_callback` fires inside `Group.invoke()` on normal return.
`typer.Exit` propagates out of `invoke()` and is caught at a higher level,
completely bypassing `_process_result()`. Since this codebase uses
`raise typer.Exit()` universally (306 instances, zero normal returns), the
callback would never fire.

## Why not sys.argv heuristics

Checking `sys.argv` for `--help` or bare program name misses nested group
`no_args_is_help` cases. `spec-driver create` (no subcommand) has
`["create"]` in argv — not bare, no `--help` — but is a help path because
the `create` group has `no_args_is_help=True`. The flag approach is correct
for all cases because it detects whether a leaf command body actually ran.

## Rationale

- **Skinny CLI**: avoids adding `emit_event()` to command functions
- **Automatic coverage**: new commands emit events without author action
- **All exit paths covered**: SystemExit, exceptions, interrupts
- **Correct exclusions**: only leaf-command invocations produce events

## Exclusions (intentionally not logged)

- `--help` / `--version` (Click eager parameters, before invoke)
- `no_args_is_help` on any group (e.g. bare `spec-driver create`)
- Parse errors / invalid commands
- Shell completion callbacks

## References

- DR-052 DEC-052-01: full boundary contract with exit-path table
- DE-052: event infrastructure delta
- mem.pattern.cli.skinny: skinny CLI pattern
- IMPR-009: TUI dashboard (event consumer)
