"""Track screen — 2-panel live event view (DEC-054-01, DEC-054-04)."""

from __future__ import annotations

from textual import on
from textual.screen import Screen
from textual.widgets import DataTable

from supekku.tui.event_listener import DISPLAY_BUFFER_LIMIT
from supekku.tui.widgets.session_list import SessionList, SessionSelected
from supekku.tui.widgets.track_panel import TrackPanel


class TrackScreen(Screen):
  """2-panel track view: session list + event stream."""

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self._event_buffer: list[dict] = []
    self._session_filter: str | None = None
    self._mounted = False

  def compose(self):
    yield SessionList(id="session-list")
    yield TrackPanel(id="track-panel")

  def on_mount(self) -> None:
    self.query_one("#session-list").border_title = "Sessions"
    self.query_one("#track-panel").border_title = "Events"
    self._mounted = True
    # Replay any events buffered before mount
    if self._event_buffer:
      self._sync_widgets()

  def add_event(self, event: dict) -> None:
    """Buffer an event and display it if it passes the session filter."""
    self._event_buffer.append(event)
    while len(self._event_buffer) > DISPLAY_BUFFER_LIMIT:
      self._event_buffer.pop(0)

    if not self._mounted:
      return

    session_list = self.query_one("#session-list", SessionList)
    session_list.register_event(event)
    session_list.rebuild()

    if self._session_filter is None or event.get("session") == self._session_filter:
      self.query_one("#track-panel", TrackPanel).append_event(event)

  def _sync_widgets(self) -> None:
    """Replay buffered events into widgets (called after mount)."""
    session_list = self.query_one("#session-list", SessionList)
    panel = self.query_one("#track-panel", TrackPanel)
    for event in self._event_buffer:
      session_list.register_event(event)
      if self._session_filter is None or event.get("session") == self._session_filter:
        panel.append_event(event)
    session_list.rebuild()

  def on_session_selected(self, message: SessionSelected) -> None:
    """Handle session filter change — replay filtered events."""
    message.stop()
    self._session_filter = message.session_id
    panel = self.query_one("#track-panel", TrackPanel)
    panel.clear_and_replay(self._event_buffer, self._session_filter)

  @on(DataTable.RowSelected, "#track-panel")
  def _on_event_row_selected(self, event: DataTable.RowSelected) -> None:
    """Navigate to artifact when user selects an event row."""
    panel = self.query_one("#track-panel", TrackPanel)
    artifact_id = panel.artifact_for_row(event.row_key.value)
    if artifact_id:
      self.app.action_navigate_artifact(artifact_id)
