---
id: ISSUE-025
name: Backlog list should hide resolved/implemented items by default and support pagination
created: '2025-11-08'
updated: '2025-11-08'
status: implemented
kind: issue
categories: [enhancement, ux]
severity: p2
impact: user
---

# Backlog list should hide resolved/implemented items by default and support pagination

## Problem

The `spec-driver list backlog` command currently shows all backlog items regardless of status, making it difficult to focus on actionable work. As backlogs grow, users need to:

- Focus on open/active items without manual filtering
- Exclude resolved/implemented items from prioritization workflows
- Manage large backlogs with pagination

## Current Behavior

```bash
uv run spec-driver list backlog
# Shows ALL items including resolved/implemented
# No pagination - can dump hundreds of items

uv run spec-driver list backlog -p
# Includes resolved/implemented items in prioritization editor
```

## Desired Behavior

### Default Filtering

Hide `resolved` and `implemented` status items by default:

```bash
uv run spec-driver list backlog
# Shows only open/active items

uv run spec-driver list backlog --all
# or: -a
# Shows all items including resolved/implemented
```

### Prioritization Filtering

Exclude resolved/implemented items from `-p/--prioritize` by default:

```bash
uv run spec-driver list backlog -p
# Opens only actionable items in editor
# Excludes resolved/implemented

uv run spec-driver list backlog -p --all
# Opens all items if explicitly requested
```

### Pagination

Support limiting results and paging through output:

```bash
uv run spec-driver list backlog
# Default: show first 20 items

uv run spec-driver list backlog --limit 50
# Show first 50 items

uv run spec-driver list backlog --pager
# or: -P
# Use typer's built-in pager for scrolling through results
```

## Implementation Notes

### CLI Changes

`supekku/cli/list.py` - `list_backlog()` command:

Add new flags:
- `--all / -a`: Include resolved/implemented items (default: False)
- `--limit`: Maximum items to display (default: 20)
- `--pager / -P`: Use typer pager for output (default: False)

### Filtering Logic

`supekku/scripts/lib/backlog/registry.py`:

Default filter should exclude:
- `status: resolved`
- `status: implemented`

When `--all` is passed, include all statuses.

### Prioritization Integration

When `--prioritize` is used:
- Apply same default filtering (exclude resolved/implemented)
- Only open filtered items in editor
- Respect `--all` flag if user explicitly wants to prioritize everything

### Pagination Implementation

Use Rich's console.pager for `--pager` flag:
```python
from rich.console import Console

console = Console()
if pager:
    with console.pager():
        console.print(output)
else:
    typer.echo(output)
```

Apply `--limit` before formatting:
```python
items = filtered_items[:limit] if limit else filtered_items
```

### Formatter Changes

`supekku/scripts/lib/formatters/backlog_formatters.py`:

Formatters should handle truncated lists appropriately.
Consider adding footer message when results are limited:
```
Showing 20 of 45 items. Use --limit or --all to see more.
```

## Acceptance Criteria

- [ ] `list backlog` excludes resolved/implemented by default
- [ ] `--all` / `-a` flag includes all statuses
- [ ] `--prioritize` excludes resolved/implemented by default (respects `--all`)
- [ ] `--limit N` limits output to N items (default: 20)
- [ ] `--pager` / `-P` uses typer pager for scrollable output
- [ ] Help text documents new flags clearly
- [ ] When results are limited, user is informed (e.g., "Showing X of Y")
- [ ] Tests cover new filtering and pagination behavior
- [ ] Backward compatibility: existing scripts work (just show fewer items by default)

## Related Issues

- Related to backlog registry implementation
- Complements ISSUE-024 (external ID support)

