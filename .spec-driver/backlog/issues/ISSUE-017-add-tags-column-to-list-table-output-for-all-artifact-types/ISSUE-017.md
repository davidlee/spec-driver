---
id: ISSUE-017
name: Add Tags column to list table output for all artifact types
created: '2025-11-04'
updated: '2025-11-04'
status: resolved
kind: issue
categories: [ux, cli]
severity: p3
impact: user
---

# Add Tags column to list table output for all artifact types

## Problem

All artifact list commands (`list adrs`, `list specs`, `list deltas`, etc.) support `--tag` filtering, but the table output doesn't include a Tags column. This creates a discoverability gap - users can't see which tags are available without using `--json` or `show` commands.

## Current Behavior

Table output shows: `ID | Title | Status | Updated`

Example:
```bash
uv run spec-driver list adrs
# ID      │Title                                 │Status   │Updated
# ADR-001 │Example Decision                      │accepted │2025-11-04
```

## Expected Behavior

Table output should include tags: `ID | Title | Status | Tags | Updated`

Example:
```bash
uv run spec-driver list adrs
# ID      │Title                │Status   │Tags            │Updated
# ADR-001 │Example Decision     │accepted │security, auth  │2025-11-04
```

## Scope

Affected formatters (all need Tags column added):
- ✅ `policy_formatters.py` - Being fixed in DE-010
- ✅ `standard_formatters.py` - Being fixed in DE-010
- ❌ `decision_formatters.py` - ADRs
- ❌ `spec_formatters.py` - Specs (SPEC/PROD)
- ❌ `change_formatters.py` - Deltas, revisions, audits
- ❌ `requirement_formatters.py` - Requirements
- ❌ `backlog_formatters.py` - Issues, problems, improvements

## Implementation Notes

Pattern to follow (from DE-010 fix):
1. Add "Tags" to columns list in `_format_as_table()`
2. Update `_prepare_*_row()` to include formatted tags
3. Update `_calculate_column_widths()` to include tags column width
4. Format tags as comma-separated list (or empty string if no tags)
5. Add tests for tag display in formatters_test.py

## Severity

**P3** - Usability improvement, workaround exists (use --json or show command)

## Related

- DE-010 - Fixes this for policies and standards
- All artifact types have tag filtering but inconsistent display
