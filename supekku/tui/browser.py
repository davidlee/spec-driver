"""Browser screen — 3-panel artifact browser (DEC-053-14)."""

from __future__ import annotations

from textual.screen import Screen

from supekku.scripts.lib.core.artifact_view import (
  ArtifactSnapshot,
  ArtifactType,
)
from supekku.tui.widgets.artifact_list import ArtifactList, ArtifactSelected
from supekku.tui.widgets.preview_panel import PreviewPanel
from supekku.tui.widgets.type_selector import TypeSelected, TypeSelector


class BrowserScreen(Screen):
  """3-panel artifact browser screen (DEC-053-14, DEC-053-16)."""

  def __init__(self, snapshot: ArtifactSnapshot, **kwargs) -> None:
    super().__init__(**kwargs)
    self._snapshot = snapshot

  def compose(self):
    counts = self._snapshot.counts_by_type()
    yield TypeSelector(counts=counts, id="type-selector")
    yield ArtifactList(id="artifact-panel")
    yield PreviewPanel(id="preview-panel")

  def on_type_selected(self, message: TypeSelected) -> None:
    """Handle type selection — populate artifact list."""
    message.stop()
    art_type = message.artifact_type
    entries = self._snapshot.all_entries(type_filter=art_type)
    artifact_list = self.query_one("#artifact-panel", ArtifactList)
    artifact_list.show_entries(entries, art_type)
    preview = self.query_one("#preview-panel", PreviewPanel)
    preview.clear_preview()

  def on_artifact_selected(self, message: ArtifactSelected) -> None:
    """Handle artifact selection — show preview."""
    message.stop()
    preview = self.query_one("#preview-panel", PreviewPanel)
    preview.show_artifact(message.entry.path)

  def refresh_snapshot(self, art_type: ArtifactType) -> None:
    """Re-collect a single type and update the UI."""
    self._snapshot.refresh(art_type)
    counts = self._snapshot.counts_by_type()
    type_selector = self.query_one("#type-selector", TypeSelector)
    type_selector.refresh_counts(counts)
