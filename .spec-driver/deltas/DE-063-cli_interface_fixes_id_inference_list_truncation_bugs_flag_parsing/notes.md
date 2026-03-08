# Notes for DE-063

## P01 — Truncation fix (complete)

- Root cause: `truncate_text()` used `len(text)` on Rich markup strings,
  counting markup tags as visible characters.
- Fix: `add_row_with_truncation()` now uses `Text.from_markup()` for
  markup-aware width measurement and `Text.truncate()` for styled truncation.
- Removed dead `truncate_text()` (no callers after migration).
- Edge case guard: `max_width <= 3` truncates without ellipsis.
- Fixed 2 pre-existing test issues (help text assertion, fragile truncation test).
- 8 new tests, 3131 total passing.

## P02 — ID inference (complete)

- `PREFIX_TO_TYPE`: reverse mapping covering 14 prefix→type entries.
  Notably `IMPR` (not `IMP`), `RISK`, `T` for cards.
- `resolve_by_id()`: uses `build_artifact_index()` from resolve.py for O(1)
  cross-registry lookup (POL-001 reuse).
- `InferringGroup`: custom `typer.core.TyperGroup` subclass (not `click.Group`
  — Typer requires its own base class). Overrides `resolve_command()`.
- Hidden "inferred" commands in show.py and view.py. Show dispatches to
  existing per-type handlers for default/json output; handles --path/--raw
  directly (type-agnostic).
- `no_args_is_help=True` preserved alongside `cls=InferringGroup`.
- `build_artifact_index()` renamed from private `_build_artifact_index()`.
- 28 new tests (19 unit + 9 integration), 3159 total passing.

## ISSUE-042 — Flag parsing (wontfix)

- `-ri` breaking is standard POSIX short-option clustering. Workaround
  already documented in skill tips. Close as wontfix.

## Key discoveries

- Typer's `cls=` parameter requires a subclass of `typer.core.TyperGroup`,
  not `click.Group`. This is asserted at app construction time.
- `resolve_command()` signature in TyperGroup returns 3-tuple
  `(name, cmd, args)`, not 2-tuple as in older Click versions.
