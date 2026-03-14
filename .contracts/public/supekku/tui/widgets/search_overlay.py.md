# supekku.tui.widgets.search_overlay

Modal search overlay — fzf-style cross-artifact fuzzy search.

Design reference: DR-087 DEC-087-03, DEC-087-04.

## Classes

### SearchOverlay

Modal overlay for cross-artifact fuzzy search.

Opens with an empty search input.  Results update as the user types.
Enter selects a result and dismisses; Escape dismisses without selection.

**Inherits from:** ModalScreen[<BinOp>]

#### Methods

- `action_dismiss_overlay(self) -> None`: Dismiss overlay without selection.
- `compose(self) -> ComposeResult`
- `on_mount(self) -> None`: Set up results table columns.

### SearchResult

Posted when the user selects a search result.

**Inherits from:** Message
