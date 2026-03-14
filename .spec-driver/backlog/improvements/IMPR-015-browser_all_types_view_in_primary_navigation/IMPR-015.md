---
id: IMPR-015
name: "Browser: All-types view in primary navigation"
created: "2026-03-10"
updated: "2026-03-10"
status: idea
kind: improvement
---

# Browser: All-types view in primary navigation

## Problem

The TUI browser only shows one artifact type at a time. The `/` search overlay
provides cross-type search but is transient. Users who want to browse all
artifacts together have no persistent view.

## Desired behaviour

Add an "All" entry above ADRs in the type selector. When selected, the artifact
list shows entries from all types, sorted by score or grouped by type, with
per-type ID styling.

## Considerations

- Artifact list column layout may need adjustment (type column added)
- Status filter would need to work across types
- Preview panel behaviour unchanged
- Could reuse the search index infrastructure from DE-087

## Related

- IMPR-011 (TUI polish, navigation, relational display)
- DE-087 (cross-artifact search overlay)
