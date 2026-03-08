"""Track screen — live event view with artifact preview (DEC-054-01, DEC-059-02)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer

from supekku.tui.event_listener import DISPLAY_BUFFER_LIMIT
from supekku.tui.widgets.bundle_tree import BundleFileSelected, BundleTree
from supekku.tui.widgets.preview_panel import PreviewPanel
from supekku.tui.widgets.session_list import SessionList, SessionSelected
from supekku.tui.widgets.track_panel import TrackPanel

if TYPE_CHECKING:
  from supekku.scripts.lib.core.artifact_view import ArtifactSnapshot


class TrackScreen(Screen):
  """Track view: session list + event stream + artifact preview."""

  BINDINGS = [
    Binding("f", "focus_files", "Files"),
  ]

  def __init__(self, snapshot: ArtifactSnapshot | None = None, **kwargs) -> None:
    super().__init__(**kwargs)
    self._snapshot = snapshot
    self._event_buffer: list[dict] = []
    self._session_filter: str | None = None
    self._mounted = False

  def compose(self):
    with Vertical(id="track-left", classes="bundle-column"):
      yield SessionList(id="session-list")
      yield BundleTree(id="bundle-tree", tab_target="#track-panel")
    with Vertical(id="track-right"):
      yield TrackPanel(id="track-panel")
      yield PreviewPanel(id="track-preview")
    yield Footer()

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

    # Refresh tree if new event touches the currently displayed bundle (DEC-061-09)
    self._refresh_tree_for_event(event)

  def _refresh_tree_for_event(self, event: dict) -> None:
    """Repopulate tree if event references the currently displayed bundle."""
    tree = self.query_one("#bundle-tree", BundleTree)
    if tree.bundle_dir is None or self._snapshot is None:
      return
    artifacts = event.get("artifacts", [])
    if not artifacts:
      return
    entry = self._snapshot.find_entry(artifacts[0])
    if entry is not None and entry.bundle_dir == tree.bundle_dir:
      tree.show_bundle(tree.bundle_dir, entry.path)

  def _update_preview_for_event(self, event: dict) -> None:
    """Show preview for the event's file path or first artifact (DEC-061-04)."""
    preview = self.query_one("#track-preview", PreviewPanel)

    # Prefer file path from event argv
    argv = event.get("argv", [])
    if len(argv) > 1 and self._snapshot is not None:
      resolved = self._resolve_event_path(argv[1])
      if resolved is not None and resolved.is_file():
        preview.show_artifact(resolved)
        preview.border_title = resolved.name
        return

    # Fallback to artifact ID resolution
    artifacts = event.get("artifacts", [])
    if not artifacts or self._snapshot is None:
      return
    entry = self._snapshot.find_entry(artifacts[0])
    if entry is not None:
      preview.show_artifact(entry.path)
      preview.border_title = entry.id

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

  def _resolve_event_path(self, rel_path: str) -> Path | None:
    """Resolve an event-relative path against the snapshot root."""
    if not self._snapshot or not rel_path:
      return None
    root = getattr(self._snapshot, "_root", None)
    if root is None:
      return None
    resolved = Path(root) / rel_path
    return resolved if resolved.exists() else None

  @on(DataTable.RowHighlighted, "#track-panel")
  def _on_event_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
    """Update preview and tree when cursor moves to a different event row."""
    panel = self.query_one("#track-panel", TrackPanel)
    preview = self.query_one("#track-preview", PreviewPanel)
    tree = self.query_one("#bundle-tree", BundleTree)
    left = self.query_one("#track-left")

    # Resolve file path for preview
    file_path = panel.file_path_for_row(event.row_key.value)
    if file_path and self._snapshot is not None:
      resolved = self._resolve_event_path(file_path)
      if resolved is not None and resolved.is_file():
        preview.show_artifact(resolved)
        preview.border_title = resolved.name

    # Resolve artifact entry for tree (DEC-061-09: skip-if-same)
    artifact_id = panel.artifact_for_row(event.row_key.value)
    entry = (
      self._snapshot.find_entry(artifact_id)
      if artifact_id and self._snapshot is not None
      else None
    )

    if entry is not None and entry.bundle_dir:
      if tree.bundle_dir != entry.bundle_dir:
        tree.show_bundle(entry.bundle_dir, entry.path)
        tree.border_title = "Files"
        left.add_class("has-bundle")
      # Highlight specific file if available
      if file_path:
        resolved = self._resolve_event_path(file_path)
        if resolved is not None:
          tree.select_file(resolved)
    elif tree.bundle_dir is not None:
      tree.clear_bundle()
      left.remove_class("has-bundle")

    # Preview fallback to artifact ID (when no file path resolved above)
    if (not file_path or not self._snapshot) and entry is not None:
      preview.show_artifact(entry.path)
      preview.border_title = entry.id

  @on(DataTable.RowSelected, "#track-panel")
  def _on_event_row_selected(self, event: DataTable.RowSelected) -> None:
    """Navigate to artifact when user selects an event row (DEC-061-04)."""
    panel = self.query_one("#track-panel", TrackPanel)
    artifact_id = panel.artifact_for_row(event.row_key.value)
    if artifact_id:
      file_path = panel.file_path_for_row(event.row_key.value) or None
      self.app.action_navigate_artifact(artifact_id, file_path=file_path)

  def on_bundle_file_selected(self, message: BundleFileSelected) -> None:
    """Handle file selection in bundle tree — update preview (DEC-061-07)."""
    message.stop()
    preview = self.query_one("#track-preview", PreviewPanel)
    preview.show_artifact(message.path)
    preview.border_title = message.path.name

  def action_focus_files(self) -> None:
    """Focus the bundle tree if visible (DEC-061-07)."""
    tree = self.query_one("#bundle-tree", BundleTree)
    if tree.display:
      tree.focus()

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
