---
id: mem.fact.tui.widget-selection
name: 'Widget selection: DataTable vs RichLog vs OptionList'
kind: memory
status: active
memory_type: fact
created: '2026-03-08'
updated: '2026-03-08'
tags:
- tui
- textual
- widgets
summary: When to use which Textual widget for list-like content in the TUI
scope:
  globs:
  - supekku/tui/**
---

# Widget selection: DataTable vs RichLog vs OptionList

## Decision heuristic

| Need | Widget | Why |
|---|---|---|
| Row selection (click/Enter/cursor) | **DataTable** | Built-in cursor, `RowSelected` message, `move_cursor()` |
| Append-only log, no selection needed | **RichLog** | `max_lines` auto-pruning, `write(Text)`, no row model |
| Categorical picker (small list) | **OptionList** | `OptionSelected` message, simple label+id options |

## DataTable specifics

- `add_row(*cells, key=...)` — key **must be unique** per table, returns `RowKey`
- Cells accept `rich.text.Text` objects (styled via `styled_text()`)
- `cursor_type="row"` for row-level selection
- No `max_lines` — prune manually: `remove_row(list(self.rows)[0])` when over cap
- `clear(columns=False)` clears rows only
- `row_count` property, `move_cursor(row=idx)` for programmatic selection

## Gotcha: duplicate row keys

If the logical ID isn't unique across rows (e.g. same artifact in multiple
events), use a sequential key (`evt-1`, `evt-2`, ...) and maintain a separate
mapping from row key → logical ID.

## Verified

2026-03-08 — DE-054 Phase 2. DataTable with `Text` cells, row pruning, and
sequential keys confirmed working in TrackPanel.
