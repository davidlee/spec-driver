# DE-023 Implementation Notes

## Status: Phase 1 & 2 - COMPLETE

### What Was Done

1. **PROD-013 created** (`specify/product/PROD-013/PROD-013.md`)
   - CLI Artifact File Access spec
   - Includes CLI flag audit (Section 7)
   - Defines FR-001 through FR-007, NF-001, NF-002

2. **DE-022 created** (Phase 1 of PROD-013 - `--path` flag)
   - Delta bundle complete but NOT implemented yet
   - Can be done independently of DE-023

3. **DE-023 implemented** (Phase 2 of PROD-013 - `view`/`edit` commands)
   - `supekku/cli/common.py`: Added `get_pager()`, `get_editor()`, `open_in_pager()`, `open_in_editor()`
   - `supekku/cli/view.py`: New file with 8 subcommands (spec, delta, revision, requirement, adr, policy, standard, card)
   - `supekku/cli/edit.py`: New file with 8 subcommands (same structure)
   - `supekku/cli/main.py`: Registered both command groups
   - `supekku/cli/view_test.py`: 9 tests
   - `supekku/cli/edit_test.py`: 9 tests

### Tests Status

All 18 new tests pass:
```bash
uv run pytest supekku/cli/view_test.py supekku/cli/edit_test.py -v
# 18 passed
```

### Completed Tasks (2026-02-05)

1. ~~**Run full lint** (`just lint`)~~ ✓ Passed
2. ~~**Run full test suite** (`just test`)~~ ✓ 1542 passed
3. ~~**Update phase sheet** with completion status~~ ✓ Done
4. ~~**Manual verification**~~ ✓ Both view and edit commands work

### Key Implementation Detail

`typer.Exit` inherits from `RuntimeError`, so exception handlers must catch `typer.Exit` first and re-raise:

```python
try:
  ...
  open_in_pager(path)
except typer.Exit:
  raise  # MUST be before RuntimeError handler
except RuntimeError as e:
  typer.echo(f"Error: {e}", err=True)
  raise typer.Exit(EXIT_FAILURE) from e
```

### Files Modified

```
supekku/cli/common.py          # +4 functions (pager/editor helpers)
supekku/cli/view.py            # NEW - 250 lines
supekku/cli/edit.py            # NEW - 250 lines
supekku/cli/view_test.py       # NEW - 150 lines
supekku/cli/edit_test.py       # NEW - 150 lines
supekku/cli/main.py            # +2 imports, +2 app.add_typer() calls
```

### Commands Now Available

```bash
spec-driver view adr ADR-001      # Opens in $PAGER
spec-driver view adr 001          # Shorthand - also works!
spec-driver view adr 1            # Single digit - works too!
spec-driver view spec PROD-013    # Opens in $PAGER
spec-driver view delta DE-023     # Opens in $PAGER
spec-driver view delta 23         # Shorthand works
spec-driver edit adr ADR-001      # Opens in $EDITOR
spec-driver edit spec PROD-013    # Opens in $EDITOR
spec-driver edit delta DE-023     # Opens in $EDITOR
# ... same for: revision, requirement, policy, standard, card
```

## Phase 2 - Numeric ID Shorthand (2026-02-05)

Added support for numeric shorthand IDs for artifact types with unambiguous prefixes:

| Type | Prefix | Example |
|------|--------|---------|
| ADR | `ADR-` | `001` → `ADR-001` |
| Delta | `DE-` | `23` → `DE-023` |
| Revision | `RE-` | `1` → `RE-001` |
| Policy | `POL-` | `42` → `POL-042` |
| Standard | `STD-` | `7` → `STD-007` |

Spec/Requirement/Card unchanged (ambiguous prefixes).

**Implementation**: Added `normalize_id()` function to `common.py`, called from view.py and edit.py for the applicable artifact types.

**Tests**: 9 new tests added (27 total for view/edit)
