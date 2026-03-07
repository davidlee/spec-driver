"""Track screen — live event view with artifact preview (DEC-054-01, DEC-059-02)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable

from supekku.tui.event_listener import DISPLAY_BUFFER_LIMIT
from supekku.tui.widgets.preview_panel import PreviewPanel
from supekku.tui.widgets.session_list import SessionList, SessionSelected
from supekku.tui.widgets.track_panel import TrackPanel

if TYPE_CHECKING:
  from supekku.scripts.lib.core.artifact_view import ArtifactSnapshot


class TrackScreen(Screen):
  """Track view: session list + event stream + artifact preview."""

  def __init__(self, snapshot: ArtifactSnapshot | None = None, **kwargs) -> None:
    super().__init__(**kwargs)
    self._snapshot = snapshot
    self._event_buffer: list[dict] = []
    self._session_filter: str | None = None
    self._mounted = False

  def compose(self):
    yield SessionList(id="session-list")
    with Vertical(id="track-right"):
      yield TrackPanel(id="track-panel")
      yield PreviewPanel(id="track-preview")

  def on_mount(self) -> None:
    """Set border titles and replay buffered events."""
    self.query_one("#session-list").border_title = "Sessions"
    self.query_one("#track-panel").border_title = "Events"
    self.query_one("#track-preview").border_title = "Preview"
    self._mounted = True
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
      self._update_preview_for_event(event)

  def _update_preview_for_event(self, event: dict) -> None:
    """Show preview for the event's first artifact, if resolvable."""
    artifacts = event.get("artifacts", [])
    if not artifacts or self._snapshot is None:
      return
    entry = self._snapshot.find_entry(artifacts[0])
    if entry is not None:
      preview = self.query_one("#track-preview", PreviewPanel)
      preview.show_artifact(entry.path)
      preview.border_title = str(entry.path)

  def _sync_widgets(self) -> None:
    """Replay buffered events into widgets (called after mount)."""
    session_list = self.query_one("#session-list", SessionList)
    panel = self.query_one("#track-panel", TrackPanel)
    last_artifact_event = None
    for event in self._event_buffer:
      session_list.register_event(event)
      if self._session_filter is None or event.get("session") == self._session_filter:
        panel.append_event(event)
        if event.get("artifacts"):
          last_artifact_event = event
    session_list.rebuild()
    if last_artifact_event is not None:
      self._update_preview_for_event(last_artifact_event)

  def on_session_selected(self, message: SessionSelected) -> None:
    """Handle session filter change — replay filtered events."""
    message.stop()
    self._session_filter = message.session_id
    panel = self.query_one("#track-panel", TrackPanel)
    panel.clear_and_replay(self._event_buffer, self._session_filter)

  @on(DataTable.RowHighlighted, "#track-panel")
  def _on_event_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
    """Update preview when cursor moves to a different event row."""
    panel = self.query_one("#track-panel", TrackPanel)
    artifact_id = panel.artifact_for_row(event.row_key.value)
    if artifact_id and self._snapshot is not None:
      entry = self._snapshot.find_entry(artifact_id)
      if entry is not None:
        preview = self.query_one("#track-preview", PreviewPanel)
        preview.show_artifact(entry.path)
        preview.border_title = str(entry.path)

  @on(DataTable.RowSelected, "#track-panel")
  def _on_event_row_selected(self, event: DataTable.RowSelected) -> None:
    """Navigate to artifact when user selects an event row."""
    panel = self.query_one("#track-panel", TrackPanel)
    artifact_id = panel.artifact_for_row(event.row_key.value)
    if artifact_id:
      self.app.action_navigate_artifact(artifact_id)

  @property
  def event_buffer(self) -> list[dict]:
    """Read-only access to the event buffer."""
    return self._event_buffer

  def auto_follow(self, session_id: str) -> None:
    """Auto-filter to a session and select it in the session list."""
    self._session_filter = session_id
    if self._mounted:
      panel = self.query_one("#track-panel", TrackPanel)
      panel.clear_and_replay(self._event_buffer, session_id)
