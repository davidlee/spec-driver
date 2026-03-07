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
