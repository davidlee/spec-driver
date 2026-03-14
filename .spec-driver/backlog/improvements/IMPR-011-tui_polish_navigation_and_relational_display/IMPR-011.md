---
id: IMPR-011
name: "TUI polish, navigation, and relational display"
created: "2026-03-07"
updated: "2026-03-07"
status: open
kind: improvement
relations:
  - type: follows-up
    target: DE-053
  - type: related-to
    target: IMPR-009
---

# TUI polish, navigation, and relational display

Follow-up improvements to the TUI artifact browser (DE-053 MVP).

## High-value features

- **Relational display & navigation**: Show referenced artifacts (relations,
  applies_to, implements, etc.) in a panel or overlay. Navigate to related
  artifacts by selecting them. This is the single biggest feature gap vs
  the reference implementation.
- **Embedded sub-entities**: Surface DR decisions, IP phases, and phase
  tasks inline or as expandable sections when viewing deltas/plans.
- **Frontmatter/content/both toggle**: View mode cycling for the preview
  panel — raw frontmatter, rendered content, or both.

## Navigation & keybindings

- **Faster type switching**: Number keys (1-9) or vim-style j/k to jump
  between artifact types without tabbing to the sidebar.
- **Arrow keys in table while search focused**: Currently works (up/down/enter).
  Consider Escape to clear search and return focus to table.
- **Scroll hints**: Make it more discoverable that Tab cycles focus and
  that the preview panel is keyboard-scrollable.

## Visual polish

- **Styling closer to lazyspec reference**: Better use of colour, spacing,
  and typography. The Textual gallery shows what's achievable.
- **Status/tag badges**: Inline styled badges for status and tags in the
  artifact list (like the `[accepted]` `[tui]` badges in lazyspec).
- **Column auto-sizing**: ID column width could adapt per artifact type
  (ADR IDs are short, SPEC IDs are longer).

## Minor UX

- **Resizable split**: Allow resizing the list/preview allocation (Textual
  doesn't have native split panes, may need a custom widget).
- **Escape from preview**: Return focus to the artifact list.
- **Empty state messaging**: Show a helpful message when no artifacts match
  the current filter/search instead of an empty table.
