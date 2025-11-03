# Enhancement: Phase Tracking Data in JSON Output

**Date**: 2025-11-03
**Context**: Post-completion enhancement to DE-004

## Summary

Enhanced `show delta --json` output to include detailed task and criteria status from `phase.tracking@v1` blocks.

## Changes

### Before
```json
{
  "tasks_completed": 8,
  "tasks_total": 8
}
```

### After
```json
{
  "tasks": [
    "[x] Define phase.tracking@v1 schema",
    "[x] Implement tracking block parser",
    "[/] Update documentation",
    "[!] Fix blocked dependency",
    "[ ] Pending task"
  ],
  "task_status": {
    "pending": 1,
    "in_progress": 1,
    "completed": 2,
    "blocked": 1,
    "total": 5
  },
  "entrance_criteria": [
    "[x] Phase 01 complete",
    "[ ] User approval received"
  ],
  "exit_criteria": [
    "[x] Tests passing",
    "[ ] Documentation updated"
  ]
}
```

## Checkbox Format

- `[x]` - completed
- `[/]` - in_progress
- `[!]` - blocked
- `[ ]` - pending

## Implementation

**File**: `supekku/scripts/lib/formatters/change_formatters.py:198`
**Function**: `_enrich_phase_data()`

### Logic
1. Parse `phase.tracking@v1` block from phase file
2. Extract tasks with status → convert to checkbox format
3. Count tasks by status → build `task_status` object
4. Extract entrance/exit criteria → format with completion checkboxes
5. Add to phase data for JSON serialization

### Backward Compatibility
- Phases without tracking blocks fall back to regex checkbox counting
- Returns old format (`tasks_completed`, `tasks_total`) for compatibility

## Testing

- All existing tests pass (29 formatter tests)
- Ruff lint clean
- Verified with DE-004 phase-05 (has tracking block)

## Benefits

1. **Visibility**: See individual task status, not just aggregates
2. **Actionability**: Identify blocked/in-progress tasks at a glance
3. **Criteria tracking**: Monitor entrance/exit criteria completion
4. **Consistency**: Checkbox format matches markdown conventions
5. **Structured data**: `task_status` object enables filtering/reporting

## Future Enhancements

- Filter deltas by task status (e.g., `--has-blocked-tasks`)
- Summary across all phases (total tasks by status)
- Visual rendering in TUI/web interface
