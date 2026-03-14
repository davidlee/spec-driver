---
id: IMPR-010
name: 'Backlog prioritize UX: status-aware checkboxes and status toggling'
created: '2026-03-07'
updated: '2026-03-07'
status: open
kind: improvement
relations:
- type: depends_on
  target: ISSUE-009
---

# Backlog prioritize UX: status-aware checkboxes and status toggling

## Problem

`spec-driver list backlog -p` renders markdown checkboxes for each item, but
they don't reflect item status. The checkboxes are purely for priority ordering
— checking/unchecking has no semantic meaning.

## Desired Behaviour

1. **Checkboxes reflect current status**: items in terminal statuses (resolved,
   done, implemented, mitigated, closed) render as `[x]`; in-progress items
   as `[-]` or `[/]`; open/new items as `[ ]`.

2. **Toggling updates status**: when a user checks or unchecks a box in the
   editor, the change is written back to the item's frontmatter status field.

## Status mapping (proposed)

Pending ISSUE-009 (status enum definitions), a reasonable default:

| Checkbox | Statuses                                                  |
| -------- | --------------------------------------------------------- |
| `[ ]`    | open, captured, idea, suspected, identified               |
| `[-]`    | in-progress, triaged, analyzed, planned, confirmed        |
| `[x]`    | done, resolved, implemented, closed, mitigated, validated |

## Dependencies

- **ISSUE-009**: Without status enums, the checkbox-to-status mapping is
  fragile. Ideally enums land first so the mapping is derived, not hardcoded.
  However, a pragmatic first pass could use the theme styles as the source of
  truth for status classification.

## Scope notes

- Read path (display current status as checkbox) is straightforward.
- Write path (toggling checkbox updates frontmatter) requires deciding what
  status to transition _to_ when a box is checked — e.g. does checking an
  issue set it to `resolved` or `done`? This needs per-kind default targets.
- The priority editor already parses markdown checkboxes; the infrastructure
  is partially there.

## Related

- ISSUE-009: Status fields lack enums and need systematic review
- `supekku/scripts/lib/formatters/theme.py:68-84`: current styled statuses
- `supekku/scripts/lib/backlog/priority.py`: editor/prioritize logic
