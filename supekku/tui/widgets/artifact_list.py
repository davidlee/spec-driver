"""Artifact list widget — DataTable + Select status filter (DEC-053-13)."""

from __future__ import annotations

from textual import on
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import DataTable, Input, Select

from supekku.scripts.lib.core.artifact_view import (
  ArtifactEntry,
  ArtifactType,
)
from supekku.scripts.lib.formatters.theme import styled_text

# Columns shown in the artifact list (id, title, status).
_LIST_COLUMNS = ("ID", "Title", "Status")


class ArtifactSelected(Message):
  """Posted when the user selects an artifact row."""

  def __init__(self, entry: ArtifactEntry) -> None:
    super().__init__()
    self.entry = entry


class ArtifactList(Vertical):
  """Artifact list panel with status filter and fuzzy search."""

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self._entries: list[ArtifactEntry] = []
    self._current_type: ArtifactType | None = None
    self._search_text: str = ""

  def compose(self):
    yield Select[str](
      [],
      prompt="Status: all",
      allow_blank=True,
      id="status-filter",
    )
    yield Input(placeholder="/ search", id="search-input")
    yield DataTable(id="artifact-table", cursor_type="row")

  def on_mount(self) -> None:
    table = self.query_one("#artifact-table", DataTable)
    for col in _LIST_COLUMNS:
      table.add_column(col, key=col.lower())

  def show_entries(
    self,
    entries: list[ArtifactEntry],
    artifact_type: ArtifactType,
  ) -> None:
    """Populate the list with entries for a given type."""
    self._entries = entries
    self._current_type = artifact_type
    self._search_text = ""

    # Reset search input
    search = self.query_one("#search-input", Input)
    search.value = ""

    # Rebuild status filter options
    statuses = sorted({e.status for e in entries if e.status})
    status_select = self.query_one("#status-filter", Select)
    options = [(s, s) for s in statuses]
    status_select.set_options(options)
    status_select.clear()

    self._refresh_table()

  def _filtered_entries(self) -> list[ArtifactEntry]:
    """Apply status filter and search text to entries."""
    entries = self._entries
    status_select = self.query_one("#status-filter", Select)
    if not status_select.is_blank():
      entries = [e for e in entries if e.status == status_select.value]
    if self._search_text:
      term = self._search_text.lower()
      entries = [
        e
        for e in entries
        if term in e.id.lower() or term in e.title.lower() or term in e.status.lower()
      ]
    return entries

  def _refresh_table(self) -> None:
    table = self.query_one("#artifact-table", DataTable)
    table.clear()
    for entry in self._filtered_entries():
      id_style = f"{self._current_type.value}.id" if self._current_type else ""
      table.add_row(
        styled_text(entry.id, id_style),
        entry.title,
        entry.status,
        key=entry.id,
      )

  @on(Select.Changed, "#status-filter")
  def _on_status_changed(self, event: Select.Changed) -> None:
    event.stop()
    self._refresh_table()

  @on(Input.Changed, "#search-input")
  def _on_search_changed(self, event: Input.Changed) -> None:
    event.stop()
    self._search_text = event.value
    self._refresh_table()

  @on(DataTable.RowSelected, "#artifact-table")
  def _on_row_selected(self, event: DataTable.RowSelected) -> None:
    event.stop()
    row_key = event.row_key.value
    for entry in self._entries:
      if entry.id == row_key:
        self.post_message(ArtifactSelected(entry))
        break
