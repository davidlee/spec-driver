# supekku.tui.widgets.artifact_list

Artifact list widget — DataTable + status cycle + fuzzy search.

## Constants

- `_ALL`
- `_LIST_COLUMNS` - Columns: (label, key, width). None width = auto-size to content.

## Classes

### ArtifactList

Artifact list panel with status filter and fuzzy search.

**Inherits from:** Vertical

#### Methods

- `compose(self)`
- @property `current_type(self) -> <BinOp>`: Currently displayed artifact type.
- `on_mount(self) -> None`
- `show_entries(self, entries, artifact_type) -> None`: Populate the list with entries for a given type.
- `__init__(self) -> None`
- `_filtered_entries(self) -> list[ArtifactEntry]`: Apply status filter and search text to entries.
- @on(DataTable.RowSelected, #artifact-table) `_on_row_selected(self, event) -> None`
- @on(Input.Changed, #search-input) `_on_search_changed(self, event) -> None`
- @on(StatusCycler.Changed, #status-filter) `_on_status_changed(self, event) -> None`
- `_refresh_table(self) -> None`

### ArtifactSelected

Posted when the user selects an artifact row.

**Inherits from:** Message

#### Methods

- `__init__(self, entry) -> None`

### Changed

Posted when the status filter value changes.

**Inherits from:** Message

#### Methods

- @property `control(self) -> StatusCycler`: The StatusCycler that sent the message.
- `__init__(self, status_cycler, value) -> None`

### StatusCycler

1-line status filter that cycles on click or keybinding.

**Inherits from:** Label

#### Methods

- `cycle(self) -> None`: Advance to the next status value.
- `on_click(self) -> None`
- `set_statuses(self, statuses) -> None`: Update the available status values.
- `watch_current(self, value) -> None`
- `__init__(self) -> None`

### \_SearchInput

Search input that forwards navigation keys to the artifact table.

**Inherits from:** Input

#### Methods

- `on_key(self, event) -> None`
