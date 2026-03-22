# supekku.tui.widgets.session_list

Session list widget — session discovery and filtering (DEC-054-04).

## Classes

### SessionInfo

Metadata for a discovered session.

#### Methods

- @property `parsed_ts(self) -> <BinOp>`: Most recent parsed timestamp, or None.
- `update(self, ts) -> None`: Update with a new event timestamp.

### SessionList

Discovers sessions from events and lets the user filter by session.

**Inherits from:** OptionList

#### Methods

- `detect_active_session(self) -> <BinOp>`: Return session ID if exactly one session is recently active (DEC-059-01).

Returns None if no sessions, no recent activity, or multiple active sessions.
- `on_option_list_option_selected(self, event) -> None`: Post SessionSelected message when user picks a session.
- `rebuild(self) -> None`: Rebuild the option list ordered by most-recent-event-first.
- `register_event(self, event) -> None`: Update session metadata from an event.

### SessionSelected

Posted when the user selects a session filter.

**Inherits from:** Message
