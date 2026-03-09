# supekku.tui.widgets.track_panel

Track panel widget — DataTable event stream with row selection (DEC-054-07).

## Constants

- `SESSION_COLOUR_COUNT`

## Functions

- `format_timestamp(ts) -> str`: Extract HH:MM:SS from an ISO 8601 timestamp.
- `session_colour_index(session_id) -> int`: Deterministic colour index for a session ID (DEC-054-04).

## Classes

### TrackPanel

Scrolling event stream with row selection for artifact navigation.

**Inherits from:** DataTable

#### Methods

- `append_event(self, event) -> None`: Add a styled event row, pruning oldest if over capacity.
- `artifact_for_row(self, row_key_value) -> str`: Return the artifact ID associated with a row key, or empty string.
- `clear_and_replay(self, events, session_filter) -> None`: Clear table and replay filtered events from buffer.
- `file_path_for_row(self, row_key_value) -> str`: Return the file path associated with a row key, or empty string.
- `on_mount(self) -> None`
