---
id: IMPR-014
name: 'Search overlay: show relation context for selected result'
created: '2026-03-10'
updated: '2026-03-10'
status: idea
kind: improvement
---

# Search overlay: show relation context for selected result

## Problem

When a search result appears because of a relation match (e.g. searching "DE-055"
surfaces DE-079), there's no way to see _why_ it matched — whether it's a
structured relationship or just a mention in the text.

## Desired behaviour

For the currently highlighted search result, show its indexed relations and their
types (e.g. `depends_on: DE-055`, `relates_to: PROD-010`). This helps users
understand cross-artifact connections without leaving the overlay.

## Related

- IMPR-011 (TUI polish, navigation, relational display)
- DE-087 (cross-artifact search — explicitly deferred relational navigation)
