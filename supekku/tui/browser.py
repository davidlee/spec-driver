"""Browser screen — 3-panel artifact browser (DEC-053-14)."""

from __future__ import annotations

from pathlib import Path

from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable

from supekku.scripts.lib.core.artifact_view import (
  ArtifactEntry,
  ArtifactSnapshot,
  ArtifactType,
)
from supekku.tui.widgets.artifact_list import ArtifactList, ArtifactSelected
from supekku.tui.widgets.bundle_tree import BundleFileSelected, BundleTree
from supekku.tui.widgets.preview_panel import PreviewPanel
from supekku.tui.widgets.type_selector import TypeSelected, TypeSelector


class BrowserScreen(Screen):
  """3-panel artifact browser screen (DEC-053-14, DEC-053-16)."""

  BINDINGS = [
    Binding("f", "focus_files", "Files", show=False),
  ]

  def __init__(self, snapshot: ArtifactSnapshot, **kwargs) -> None:
    super().__init__(**kwargs)
    self._snapshot = snapshot
    self._selected_entry: ArtifactEntry | None = None

  def compose(self):
    counts = self._snapshot.counts_by_type()
    with Vertical(id="left-column", classes="bundle-column"):
      yield TypeSelector(counts=counts, id="type-selector")
      yield BundleTree(id="bundle-tree")
    with Vertical(id="right-column"):
      yield ArtifactList(id="artifact-panel")
      yield PreviewPanel(id="preview-panel")

  def on_mount(self) -> None:
    """Set border titles and select the first type on startup."""
    self.query_one("#type-selector").border_title = "Types"
    self.query_one("#artifact-panel").border_title = "Artifacts"
    self.query_one("#preview-panel").border_title = "Preview"

    first_type = next(iter(ArtifactType))
    entries = self._snapshot.all_entries(type_filter=first_type)
    self.query_one("#artifact-panel", ArtifactList).show_entries(entries, first_type)
    self.query_one("#type-selector", TypeSelector).highlighted = 0

  def on_type_selected(self, message: TypeSelected) -> None:
    """Handle type selection — populate artifact list, clear tree (DEC-061-06)."""
    message.stop()
    art_type = message.artifact_type
    entries = self._snapshot.all_entries(type_filter=art_type)
    artifact_list = self.query_one("#artifact-panel", ArtifactList)
    artifact_list.show_entries(entries, art_type)
    artifact_list.border_title = art_type.plural
    preview = self.query_one("#preview-panel", PreviewPanel)
    preview.clear_preview()

    # Clear bundle tree on type change
    self.query_one("#left-column").remove_class("has-bundle")
    self.query_one("#bundle-tree", BundleTree).clear_bundle()

  def on_artifact_selected(self, message: ArtifactSelected) -> None:
    """Handle artifact selection — show preview, toggle tree (DEC-061-06)."""
    message.stop()
    self._selected_entry = message.entry
    preview = self.query_one("#preview-panel", PreviewPanel)
    preview.show_artifact(message.entry.path)
    preview.border_title = message.entry.id

    left = self.query_one("#left-column")
    tree = self.query_one("#bundle-tree", BundleTree)
    if message.entry.bundle_dir:
      tree.show_bundle(message.entry.bundle_dir, message.entry.path)
      tree.border_title = "Files"
      left.add_class("has-bundle")
    else:
      tree.clear_bundle()
      left.remove_class("has-bundle")

  def on_bundle_file_selected(self, message: BundleFileSelected) -> None:
    """Handle file selection in bundle tree — update preview (DEC-061-02)."""
    message.stop()
    preview = self.query_one("#preview-panel", PreviewPanel)
    preview.show_artifact(message.path)
    preview.border_title = message.path.name

  def action_focus_files(self) -> None:
    """Focus the bundle tree if visible (DEC-061-03)."""
    tree = self.query_one("#bundle-tree", BundleTree)
    if tree.display:
      tree.focus()

  @property
  def selected_entry(self) -> ArtifactEntry | None:
    """Currently selected artifact entry, or None."""
    return self._selected_entry

  def navigate_to_artifact(
    self, artifact_id: str, *, file_path: str | None = None
  ) -> bool:
    """Navigate to an artifact by ID, optionally selecting a file.

    DEC-054-06, DEC-061-04.

    Returns True if navigation succeeded, False if artifact not found.
    """
    entry = self._snapshot.find_entry(artifact_id)
    if entry is None:
      return False

    art_type = entry.artifact_type

    # Switch type selector
    type_selector = self.query_one("#type-selector", TypeSelector)
    idx = type_selector.get_option_index(art_type.value)
    type_selector.highlighted = idx

    # Populate artifact list for this type
    entries = self._snapshot.all_entries(type_filter=art_type)
    artifact_list = self.query_one("#artifact-panel", ArtifactList)
    artifact_list.show_entries(entries, art_type)
    artifact_list.border_title = art_type.plural

    # Select the target row
    table = artifact_list.query_one("#artifact-table", DataTable)
    for row_idx, row_key in enumerate(table.rows):
      if row_key.value == artifact_id:
        table.move_cursor(row=row_idx)
        break

    # Show bundle tree and select specific file if provided
    self._selected_entry = entry
    left = self.query_one("#left-column")
    tree = self.query_one("#bundle-tree", BundleTree)
    if entry.bundle_dir:
      tree.show_bundle(entry.bundle_dir, entry.path)
      tree.border_title = "Files"
      left.add_class("has-bundle")
      if file_path:
        resolved = Path(file_path)
        if not resolved.is_absolute() and entry.bundle_dir:
          resolved = entry.bundle_dir.parent.parent / file_path
        tree.select_file(resolved)
    else:
      tree.clear_bundle()
      left.remove_class("has-bundle")

    # Update preview — prefer file_path if resolvable
    preview = self.query_one("#preview-panel", PreviewPanel)
    if file_path:
      target = Path(file_path)
      if not target.is_absolute() and entry.bundle_dir:
        target = entry.bundle_dir.parent.parent / file_path
      if target.is_file():
        preview.show_artifact(target)
        preview.border_title = target.name
        return True
    preview.show_artifact(entry.path)
    preview.border_title = entry.id

    return True

  def refresh_snapshot(self, art_type: ArtifactType) -> None:
    """Re-collect a single type and update the UI."""
    self._snapshot.refresh(art_type)
    counts = self._snapshot.counts_by_type()
    type_selector = self.query_one("#type-selector", TypeSelector)
    type_selector.refresh_counts(counts)

    # Re-populate artifact list if the changed type is currently displayed
    artifact_list = self.query_one("#artifact-panel", ArtifactList)
    if artifact_list.current_type == art_type:
      entries = self._snapshot.all_entries(type_filter=art_type)
      artifact_list.show_entries(entries, art_type)

    # Re-resolve selected entry and refresh preview/tree (DEC-061-06)
    if (
      self._selected_entry is not None
      and self._selected_entry.artifact_type == art_type
    ):
      fresh = self._snapshot.find_entry(self._selected_entry.id)
      if fresh is not None:
        self._selected_entry = fresh

      preview = self.query_one("#preview-panel", PreviewPanel)
      preview.show_artifact(self._selected_entry.path)

      if fresh is not None and fresh.bundle_dir is not None:
        tree = self.query_one("#bundle-tree", BundleTree)
        tree.show_bundle(fresh.bundle_dir, fresh.path)
