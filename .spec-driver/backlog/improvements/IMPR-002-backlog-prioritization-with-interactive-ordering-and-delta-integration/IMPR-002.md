---
id: IMPR-002
name: Backlog prioritization with interactive ordering and delta integration
created: '2025-11-04'
updated: '2025-11-04'
status: implemented
kind: improvement
---

# Backlog prioritization with interactive ordering and delta integration

## Problem

Currently, backlog items (issues, improvements, problems) lack explicit prioritization mechanisms. Users cannot easily reorder items to reflect relative importance, making it difficult to communicate priorities and plan deltas based on priority order.

## Proposed Solution

### Interactive Prioritization Flag

Add a `--prioritize` (synonym: `--prioritise`) flag to `list backlog` (and `list issues`, `list improvements`, `list problems`) commands:

- Opens the list of backlog items as a markdown list in the user's `$EDITOR`
- User reorders items vertically to indicate priority
- Resulting ordering is preserved by the `list` command in its default view

**Filter Compatibility & Order Preservation:**

- `--prioritize` is **fully compatible with all filters** (kind, status, regexp, etc.)
- Shows **only the filtered subset** of items for explicit ordering
- **Preserves order of unspecified items** (those not shown due to filters):
  - Items excluded by filters retain their existing relative positions
  - Only shown items can be reordered relative to each other
  - Conflict resolution: explicitly ordered items take precedence over previously ordered items only where positions overlap
- **No-op guarantee**: If user makes no edits in `$EDITOR`, existing ordering remains completely unchanged
  - No reordering of shown items relative to excluded items
  - No side effects whatsoever

**Examples:**

```bash
# Order only open issues, preserve ordering of other items
spec-driver list issues --status open --prioritize

# Order only improvements, others unchanged
spec-driver list backlog --kind improvement --prioritize

# Order items matching "cli" in title, others unchanged
spec-driver list backlog --filter "cli" --prioritize

# Show all items for full reordering
spec-driver list backlog --prioritize
```

### Requirements in Backlog Items

Verify and document that backlog items can reference requirements that "live" in specs via metadata:

- Allows backlog items to act as prioritization mechanism for deltas implementing unimplemented requirements
- Backlog items can already be referenced in deltas (verify this is working correctly)

### Delta Creation from Backlog

Extend `create delta` command:

- Add `--from-backlog ITEM-ID` flag to create a delta directly from a backlog item
- Automatically populate delta metadata with backlog item context
- Link the delta back to the originating backlog item

## Benefits

- Clear prioritization mechanism for planning work
- Better traceability between backlog items, requirements, and deltas
- Streamlined workflow from backlog to implementation
- Maintains ordering consistency across filtered views

## Implementation Considerations

- Ordering storage mechanism (metadata file, frontmatter, or separate index)
- Algorithm for merging ordering when lists are filtered/partial
- Editor selection and fallback handling
- Validation of backlog item → requirement references
- Delta template population from backlog items

## Unsolved Questions

### Severity vs User Priority Interaction

How should the prioritization mechanism interact with severity fields (p1/p2/p3)?

**Possible approach:**
- Default ordering: severity takes precedence (p1 before p2 before p3) UNLESS user has explicitly assigned relative priority
- User-specified priority overrides severity-based ordering
- Items without explicit user priority fall back to severity-based ordering
- Items with neither user priority nor severity use ID-based ordering (current behavior)

### Ordering Modes

Default behavior once implemented:
- Priority-based ordering becomes the default (severity → user priority → ID fallback)
- Items naturally sort by importance/urgency rather than chronological ID

Add `--order-by-id` / `-o` flag to `list backlog` commands:
- Explicitly requests ID-based ordering (current behavior)
- Useful for chronological views or when working with specific ID ranges
- Provides escape hatch from priority-based ordering when needed
