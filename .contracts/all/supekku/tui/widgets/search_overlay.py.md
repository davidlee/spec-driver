# supekku.tui.widgets.search_overlay

Modal search overlay — fzf-style cross-artifact fuzzy search.

Design reference: DR-087 DEC-087-03, DEC-087-04.

## Constants

- `_COLUMNS` - Column layout for results table.

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
- `__init__(self) -> None`
- @on(DataTable.RowSelected, #search-results) `_on_result_selected(self, event) -> None`
- @on(Input.Changed, #search-box) `_on_search_changed(self, event) -> None`
- `_update_results(self, query) -> None`

### SearchResult

Posted when the user selects a search result.

**Inherits from:** Message

#### Methods

- `__init__(self, entry) -> None`

### _SearchInput

Search input that forwards navigation keys to the results table.

**Inherits from:** Input

#### Methods

- `on_key(self, event) -> None`: Forward navigation keys to the results table.
