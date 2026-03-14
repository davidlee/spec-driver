# Notes for DE-068

## Phase 1 — complete ✓

Commit: `a8436fe` (code + .spec-driver artefacts together)

### What's done

- `core/frontmatter_writer.py` — `update_frontmatter_status()` primitive, 12 tests
- `core/enums.py` — expanded `ENUM_REGISTRY` with backlog kinds, drift, revision/audit aliases; added `validate_status_for_entity()`; 18 tests
- Consolidated `completion.py:_update_artifact_frontmatter_status()` and `complete_delta.py:update_delta_frontmatter()` onto shared primitive
- ISSUE-009 drift reconciled (current state section, scope, acceptance criteria)
- Both linters pass, pylint 10/10 on new/modified files

### Surprises

- `_change_statuses` as a named lambda triggered pylint `unnecessary-lambda-assignment` — converted to `def`
- Ruff import sorting caught out-of-order `frontmatter_writer` import in `complete_delta.py` after manual insertion

## Phase 2 — complete ✓

### What's done

- `cli/edit.py` rewritten: `--status`/`-s` option on all 16 subcommands (15 existing + new `edit drift`)
- Shared `_apply_status()` helper keeps per-command additions to 3 lines (`_apply_status(...)` + `return`)
- `StatusOption` type alias for consistency
- `edit drift` uses `"drift_ledger"` resolver key, `"drift"` for enum path
- Test classes added: `TestEditStatusFlag`, `TestEditStatusResolveArtifact`, `TestEditDrift`
- 30 edit tests pass, 3397 total tests pass
- Both linters pass; pylint 9.82/10 on edited files (edit.py: 0 messages)

### Fixes applied

- **Empty string hang**: root cause was `if status:` (falsy for `""`) falling through to `open_in_editor()`. Fixed by changing to `if status is not None:` + adding empty/whitespace validation in `_apply_status()`
- **typer.Exit ∈ RuntimeError**: discovered `typer.Exit` inherits from `RuntimeError` via Click's `Exit`. Commands with `except RuntimeError` but no `except typer.Exit: raise` would swallow exit signals. Added `except typer.Exit: raise` guard to all commands that were missing it
- **inconsistent-return-statements**: changed from `return _apply_status(...)` to `_apply_status(...); return` — eliminated 16 pylint warnings
- **Drift resolver key assertion**: test used exact `assert_called_once_with(..., None)` but `root` resolves to repo path. Relaxed to check positional args `[0]` and `[1]` only

### Gotchas documented

- `typer.Exit` inherits from `RuntimeError` — always guard with `except typer.Exit: raise` before `except RuntimeError` in typer commands
- Typer's `CliRunner.invoke()` may hang on empty string option values — pass `input=""` to prevent stdin blocking
