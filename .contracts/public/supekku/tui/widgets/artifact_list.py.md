# supekku.tui.widgets.artifact_list

Artifact list widget — DataTable + status cycle + fuzzy search.

## Classes

### ArtifactList

Artifact list panel with status filter and fuzzy search.

**Inherits from:** Vertical

#### Methods

- `compose(self)`
- @property `current_type(self) -> <BinOp>`: Currently displayed artifact type.
- `on_mount(self) -> None`
- `show_entries(self, entries, artifact_type) -> None`: Populate the list with entries for a given type.

### ArtifactSelected

Posted when the user selects an artifact row.

**Inherits from:** Message

### Changed

Posted when the status filter value changes.

**Inherits from:** Message

#### Methods

- @property `control(self) -> StatusCycler`: The StatusCycler that sent the message.

### StatusCycler

1-line status filter that cycles on click or keybinding.

**Inherits from:** Label

#### Methods

- `cycle(self) -> None`: Advance to the next status value.
- `on_click(self) -> None`
- `set_statuses(self, statuses) -> None`: Update the available status values.
- `watch_current(self, value) -> None`
