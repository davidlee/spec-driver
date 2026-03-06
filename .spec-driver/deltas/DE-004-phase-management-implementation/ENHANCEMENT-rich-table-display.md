# Enhancement: Rich Table Display for Phases

**Date**: 2025-11-03
**Context**: Post-completion UX improvement to DE-004

## Summary

Replaced inline phase display with Rich table formatting for much better readability and professional appearance.

## Changes

### Before (inline format)
```
Plan: IP-004 (6 phases)
  File: change/deltas/DE-004-phase-management-implementation/IP-004.md
  IP-004.PHASE-01: Implement `create phase` command with auto-numbering, met... [9/19 tasks - 47%]
    File: change/deltas/DE-004-phase-management-implementation/phases/phase-01.md
  IP-004.PHASE-04: Implement automatic plan frontmatter updates when creatin... [15/18 tasks - 83%]
    File: change/deltas/DE-004-phase-management-implementation/phases/phase-04.md
```

Issues:
- Truncated objectives at 60 chars (hard to read)
- Verbose phase IDs with plan prefix
- File paths clutter the display
- No visual structure

### After (Rich table format)
```
Plan: IP-004 (6 phases)
  File: change/deltas/DE-004-phase-management-implementation/IP-004.md
╭─────────┬────────────┬───────────────────────────────────────────────────────╮
│Phase    │Status      │Objective                                              │
├─────────┼────────────┼───────────────────────────────────────────────────────┤
│PHASE-01 │9/19 (47%)  │Implement `create phase` command with auto-numbering,  │
│         │            │metadata population, and template rendering. Covers    │
│         │            │core phase creation logic.                             │
│PHASE-05 │8✓          │Implement phase.tracking@v1 YAML block for structured  │
│         │            │completion tracking of entrance/exit criteria and      │
│         │            │tasks, replacing regex-based progress parsing.         │
│PHASE-06 │6✓ 2○       │Simplify plan.overview schema to eliminate duplication │
│         │            │(ID-only phases array), add JSON schema for            │
│         │            │phase.tracking@v1, execute verification artifacts, and │
│         │            │prepare DE-004 for completion.                         │
╰─────────┴────────────┴───────────────────────────────────────────────────────╯
```

## Improvements

1. **Cleaner Phase IDs**: `PHASE-01` instead of `IP-004.PHASE-01`
2. **Full Objectives**: No truncation - Rich auto-wraps to fit terminal
3. **Task Status Symbols**:
   - `✓` = completed tasks
   - `→` = in-progress tasks
   - `!` = blocked tasks
   - `○` = pending tasks
4. **Visual Structure**: Professional borders and alignment
5. **Compact Display**: Removed per-phase file paths (still in JSON)

## Status Display Logic

- **With tracking block**: Shows breakdown (e.g., `8✓`, `6✓ 2○`)
- **Without tracking** (backward compat): Shows old format (e.g., `9/19 (47%)`)
- **No tasks**: Shows `-`

## Implementation

**File**: `supekku/scripts/lib/formatters/change_formatters.py`
**Function**: `_format_plan_overview()`

Uses Rich table utilities from `table_utils.py`:
- `create_table()` - Creates table with standard styling
- `render_table()` - Renders to string with spec-driver theme

## Testing

- All 29 formatter tests passing
- Backward compatible with numeric phase IDs (0, 1, 2)
- Handles phases with/without tracking blocks
- Works with empty objectives

## Notes

- Phase sort order follows plan.overview metadata order (not filesystem)
- Consistent use of phase.tracking@v1 from now on will ensure predictable sorting
- Table width adapts to terminal size (Rich handles wrapping)
- No truncation means full context visible at a glance

## Future Enhancements

- Add phase status column (draft/in-progress/completed)
- Color-code status symbols (green ✓, yellow →, red !)
- Filter/sort options (`--phase-status=in-progress`)
- Expand/collapse mode for detailed vs summary view
